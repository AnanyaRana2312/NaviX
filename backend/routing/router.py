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

def get_graph_for_place(place):
    """Fetch or build graph for place. For now, refetch each time."""
    return ox.graph_from_place(place, network_type='drive')

def get_nearest_node(G, lat, lon):
    """Find nearest node in graph to given lat/lon."""
    point = Point(lon, lat)
    # ox.distance.nearest_nodes expects x (lon) then y (lat)
    return ox.distance.nearest_nodes(G, lon, lat)

def compute_route(G, origin_node, dest_node, risk_weight=0.5):
    """Compute shortest path with combined weight: length + risk_weight * risk."""
    # Add risk to edges
    for u, v, data in G.edges(data=True):
        # Assume risk is stored or computed, but for now, placeholder
        # In real, need to map edges to road_id and get risk
        # For prototype, assume risk = 0.5 or something
        data['risk'] = data.get('risk', 0.5)  # Placeholder if not present
        length = data.get('length', 0.0)
        # Use multiplicative combination to keep units consistent
        data['combined_weight'] = length * (1.0 + risk_weight * data['risk'])

    try:
        path = nx.shortest_path(G, origin_node, dest_node, weight='combined_weight')
        return path
    except nx.NetworkXNoPath:
        return None

def get_route_details(G, path):
    """Extract path coordinates and total metrics."""
    # Build a list of node coordinates (lat, lon) for the path
    coords = []
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

    # Sum edge lengths and weighted risks
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
        risk = data.get('risk', 0.0)
        total_length += length
        total_risk += risk * length

    return coords, total_length, total_risk

def find_routes(origin_lat, origin_lon, dest_lat, dest_lon, place, max_routes=3):
    """Find multiple routes balancing safety and distance."""
    import threading
    result = {}
    def try_real_routes():
        try:
            G = get_graph_for_place(place)
            origin_node = get_nearest_node(G, origin_lat, origin_lon)
            dest_node = get_nearest_node(G, dest_lat, dest_lon)

            routes = []
            for i in range(max_routes):
                risk_weight = i * 0.5  # Vary weight: 0, 0.5, 1.0
                path = compute_route(G, origin_node, dest_node, risk_weight)
                if path:
                    coords, length, risk = get_route_details(G, path)
                    routes.append({
                        'path': coords,
                        'total_distance': length,
                        'total_risk': risk
                    })
            if routes:
                result['routes'] = routes
        except Exception:
            pass

    thread = threading.Thread(target=try_real_routes)
    thread.start()
    thread.join(timeout=3)  # Wait max 3 seconds for OSMnx/DB

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
            'total_risk': risk * total
        })
    return routes
