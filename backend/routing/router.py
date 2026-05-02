import osmnx as ox
import networkx as nx
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

def load_risk_scores_into_graph(G):
    """Load composite risk scores from DB and stamp them onto matching graph edges."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT r.osm_id, rs.composite_risk
            FROM roads r
            JOIN risk_scores rs ON rs.road_id = r.id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        risk_lookup = {int(osm_id): risk for osm_id, risk in rows}

        for u, v, data in G.edges(data=True):
            osmid = data.get('osmid')
            if isinstance(osmid, list):
                osmid = osmid[0]
            if osmid is not None:
                data['risk'] = risk_lookup.get(int(osmid), 0.5)
            else:
                data['risk'] = 0.5
    except Exception as e:
        print(f"[NaviX] Warning: Could not load DB risk scores ({e}). Using default risk.")
        for u, v, data in G.edges(data=True):
            if 'risk' not in data:
                data['risk'] = 0.5


def compute_route(G, origin_node, dest_node, risk_weight=0.5):
    """Compute shortest path with combined weight: length + risk_weight * risk."""
    for u, v, data in G.edges(data=True):
        data['risk'] = data.get('risk', 0.5)
        length = data.get('length', 0.0)
        data['combined_weight'] = length * (1.0 + risk_weight * data['risk'])

    try:
        path = nx.shortest_path(G, origin_node, dest_node, weight='combined_weight')
        return path
    except nx.NetworkXNoPath:
        return None

def get_route_details(G, path):
    """Extract path coordinates, total metrics, and segment details."""
    coords = []
    segments = []
    total_length = 0.0
    total_risk = 0.0

    for node in path:
        node_data = G.nodes.get(node, {})
        lat = node_data.get('y')
        lon = node_data.get('x')
        if lat is not None and lon is not None:
            coords.append([lat, lon])

    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        ed = G.get_edge_data(u, v)
        if not ed:
            continue
        
        if isinstance(ed, dict):
            data = ed[0] if 0 in ed else next(iter(ed.values()))
        else:
            data = ed

        length = data.get('length', 0.0)
        risk = data.get('risk', 0.5)
        
        name = data.get('name')
        if isinstance(name, list): name = ", ".join(name)
        
        highway = data.get('highway')
        if isinstance(highway, list): highway = ", ".join(highway)
            
        osmid = data.get('osmid')
        if isinstance(osmid, list): osmid = osmid[0]

        segments.append({
            'id': i,
            'osm_id': int(osmid) if osmid is not None else None,
            'name': name,
            'highway': highway,
            'length_m': length,
            'risk_score': risk
        })

        total_length += length
        total_risk += risk * length

    return coords, total_length, total_risk, segments

def find_routes(origin_lat=None, origin_lon=None, dest_lat=None, dest_lon=None, origin_name=None, dest_name=None, max_routes=3):
    """Find multiple routes balancing safety and distance dynamically."""
    if origin_lat is None or origin_lon is None:
        if not origin_name:
            raise ValueError("Must provide either origin coordinates or origin_name")
        print(f"[NaviX] Geocoding origin: {origin_name}")
        origin_lat, origin_lon = ox.geocode(origin_name)
        
    if dest_lat is None or dest_lon is None:
        if not dest_name:
            raise ValueError("Must provide either destination coordinates or destination_name")
        print(f"[NaviX] Geocoding destination: {dest_name}")
        dest_lat, dest_lon = ox.geocode(dest_name)
        
    print(f"[NaviX] Origin Coords: {origin_lat}, {origin_lon}")
    print(f"[NaviX] Destination Coords: {dest_lat}, {dest_lon}")

    import pathlib
    cache_dir = str(pathlib.Path(__file__).resolve().parent.parent.parent / "cache")
    ox.settings.use_cache = True
    ox.settings.cache_folder = cache_dir

    routes = []
    buffers = [0.05, 0.1, 0.2] # ~5km, 11km, 22km
    
    for buffer in buffers:
        try:
            print(f"[NaviX] Attempting routing with buffer {buffer} degrees...")
            north = max(origin_lat, dest_lat) + buffer
            south = min(origin_lat, dest_lat) - buffer
            east = max(origin_lon, dest_lon) + buffer
            west = min(origin_lon, dest_lon) - buffer
            
            print(f"[NaviX] Extracting Bounding Box: N={north}, S={south}, E={east}, W={west}")
            G = ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive')
            
            num_nodes = len(G.nodes)
            print(f"[NaviX] Downloaded graph with {num_nodes} nodes.")
            
            if num_nodes < 10:
                print("[NaviX] Graph too small. Retrying with larger buffer...")
                continue
                
            load_risk_scores_into_graph(G)
            
            orig_node = ox.distance.nearest_nodes(G, origin_lon, origin_lat)
            dest_node = ox.distance.nearest_nodes(G, dest_lon, dest_lat)
            
            print(f"[NaviX] Nearest Nodes -> Origin: {orig_node}, Dest: {dest_node}")
            
            routes_found = False
            for i in range(max_routes):
                risk_weight = i * 0.5
                path = compute_route(G, orig_node, dest_node, risk_weight)
                if not path:
                    raise nx.NetworkXNoPath("No path found between nearest nodes.")
                    
                coords, length, risk, segments = get_route_details(G, path)
                routes.append({
                    'path': coords,
                    'total_distance': length,
                    'total_risk': risk,
                    'segments': segments
                })
                routes_found = True
                
            if routes_found:
                print(f"[NaviX] Successfully generated {len(routes)} road-following routes.")
                break
                
        except nx.NetworkXNoPath:
            print(f"[NaviX] No path found with buffer {buffer}. Retrying...")
            continue
        except Exception as e:
            print(f"[NaviX] Graph extraction failed with buffer {buffer}: {e}. Retrying...")
            continue
            
    if not routes:
        raise RuntimeError("Failed to compute any route. Increase bounding box or check location accessibility.")
        
    return routes
