import osmnx as ox
import networkx as nx
from shapely.geometry import Point
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'navix')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def get_graph_for_bbox(north, south, east, west):
    """Fetch or build graph for bbox, using OSMnx disk cache to avoid re-downloading."""
    import pathlib
    cache_dir = str(pathlib.Path(__file__).resolve().parent.parent.parent / "cache")
    ox.settings.use_cache = True
    ox.settings.cache_folder = cache_dir
    return ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive')

def get_nearest_node(G, lat, lon):
    """Find nearest node in graph to given lat/lon using scipy cKDTree."""
    from scipy.spatial import cKDTree
    node_ids = list(G.nodes())
    # Build array of (lat, lon) from node attributes y=lat, x=lon
    coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in node_ids]
    tree = cKDTree(coords)
    _, idx = tree.query([lat, lon])
    return node_ids[idx]

def load_risk_scores_into_graph(G):
    """Load composite risk scores from DB and stamp them onto matching graph edges."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Join roads + risk_scores on road_id to get osm_id → composite_risk mapping
        cur.execute("""
            SELECT r.osm_id, rs.composite_risk
            FROM roads r
            JOIN risk_scores rs ON rs.road_id = r.id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Build lookup: osm_id (int) → risk score
        risk_lookup = {int(osm_id): risk for osm_id, risk in rows}

        # Stamp risk onto edges using osmid attribute stored by OSMnx
        for u, v, data in G.edges(data=True):
            osmid = data.get('osmid')
            # osmid can be a list (when multiple OSM ways merged) — use first
            if isinstance(osmid, list):
                osmid = osmid[0]
            if osmid is not None:
                data['risk'] = risk_lookup.get(int(osmid), 0.5)  # default 0.5 if not in DB
            else:
                data['risk'] = 0.5
    except Exception:
        # If DB is unavailable, leave edges with their default risk
        pass


def compute_route(G, origin_node, dest_node, risk_weight=0.5):
    """Compute shortest path with combined weight: length + risk_weight * risk."""
    for u, v, data in G.edges(data=True):
        # Risk is pre-loaded by load_risk_scores_into_graph(); default 0.5 if absent
        data['risk'] = data.get('risk', 0.5)
        length = data.get('length', 0.0)
        # Multiplicative combination keeps units consistent (meters-based)
        data['combined_weight'] = length * (1.0 + risk_weight * data['risk'])

    try:
        path = nx.shortest_path(G, origin_node, dest_node, weight='combined_weight')
        return path
    except nx.NetworkXNoPath:
        return None

def get_route_details(G, path):
    """Extract path coordinates, total metrics, and segment details."""
    # Build a list of node coordinates (lat, lon) for the path
    coords = []
    segments = []
    total_length = 0.0
    total_risk = 0.0

    # Append coordinates for every node in the path (simple, robust approach)
    for node in path:
        node_data = G.nodes.get(node, {})
        lat = node_data.get('y')
        lon = node_data.get('x')
        if lat is None or lon is None:
            # skip nodes without coords
            continue
        coords.append([lat, lon])

    # Sum edge lengths and weighted risks, and collect segment data
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        ed = G.get_edge_data(u, v)
        if not ed:
            continue
        # When graph is a MultiDiGraph, edge data is a dict of keys -> attr dict
        if isinstance(ed, dict):
            # Prefer the 0 key if present, otherwise pick the first entry
            if 0 in ed:
                data = ed[0]
            else:
                data = next(iter(ed.values()))
        else:
            data = ed

        length = data.get('length', 0.0)
        risk = data.get('risk', 0.5)
        
        # Format name and highway properly
        name = data.get('name')
        if isinstance(name, list):
            name = ", ".join(name)
        
        highway = data.get('highway')
        if isinstance(highway, list):
            highway = ", ".join(highway)
            
        osmid = data.get('osmid')
        if isinstance(osmid, list):
            osmid = osmid[0]

        segments.append({
            'id': i, # Sequential ID for the segment in this route
            'osm_id': int(osmid) if osmid is not None else None,
            'name': name,
            'highway': highway,
            'length_m': length,
            'risk_score': risk
        })

        total_length += length
        total_risk += risk * length

    return coords, total_length, total_risk, segments

def find_routes(origin_lat, origin_lon, dest_lat, dest_lon, place, max_routes=3):
    """Find multiple routes balancing safety and distance."""
    import threading
    result = {}
    def try_real_routes():
        try:
            buffer = 0.05
            north = max(origin_lat, dest_lat) + buffer
            south = min(origin_lat, dest_lat) - buffer
            east = max(origin_lon, dest_lon) + buffer
            west = min(origin_lon, dest_lon) - buffer
            
            G = get_graph_for_bbox(north, south, east, west)
            load_risk_scores_into_graph(G)  # stamp DB risk scores onto edges
            origin_node = get_nearest_node(G, origin_lat, origin_lon)
            dest_node = get_nearest_node(G, dest_lat, dest_lon)

            routes = []
            for i in range(max_routes):
                risk_weight = i * 0.5  # Vary weight: 0, 0.5, 1.0
                path = compute_route(G, origin_node, dest_node, risk_weight)
                if path:
                    coords, length, risk, segments = get_route_details(G, path)
                    routes.append({
                        'path': coords,
                        'total_distance': length,
                        'total_risk': risk,
                        'segments': segments
                    })
            if routes:
                result['routes'] = routes
        except Exception as e:
            print(f"[NaviX] Real routing failed: {e}")

    thread = threading.Thread(target=try_real_routes)
    thread.start()
    thread.join(timeout=300)  # OSMnx can take longer for large bboxes; increase timeout

    if 'routes' in result:
        return result['routes']

    # Minimal mock route: origin -> midpoint -> destination. Distances are
    # Euclidean approximations; risk uses a placeholder lower/higher values.
    mid_lat = (origin_lat + dest_lat) / 2.0
    mid_lon = (origin_lon + dest_lon) / 2.0
    mock_coords = [[origin_lat, origin_lon], [mid_lat, mid_lon], [dest_lat, dest_lon]]
    # Simple haversine-like approximate distances (very rough for demo)
    def approx_dist(a_lat, a_lon, b_lat, b_lon):
        from math import radians, cos, sin, asin, sqrt
        # Haversine
        r = 6371000.0
        dlat = radians(b_lat - a_lat)
        dlon = radians(b_lon - a_lon)
        a = sin(dlat/2)**2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return r * c

    d1 = approx_dist(origin_lat, origin_lon, mid_lat, mid_lon)
    d2 = approx_dist(mid_lat, mid_lon, dest_lat, dest_lon)
    total = d1 + d2
    # Mock risk: prefer middle route as safer for second route
    routes = []
    for i in range(max_routes):
        # linearly vary risk
        risk = 0.2 + 0.3 * i
        routes.append({
            'path': mock_coords,
            'total_distance': total,
            'total_risk': risk * total,
            'segments': []
        })
    return routes
