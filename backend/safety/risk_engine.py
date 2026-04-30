import psycopg2
import psycopg2.extras
import os
from shapely import wkb
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

def compute_lighting_density(cur, road_geom, length_m):
    """Count lighting features within 50m buffer of road."""
    cur.execute("""
        SELECT COUNT(*) FROM features
        WHERE feature_type = 'lighting'
        AND ST_DWithin(geom, ST_GeomFromText(%s, 4326), 0.00045)  -- ~50m in degrees
    """, (road_geom.wkt,))
    count = cur.fetchone()[0]
    return count / length_m if length_m > 0 else 0  # density per meter

def compute_poi_density(cur, road_geom, length_m):
    """Count POI features within 100m buffer."""
    cur.execute("""
        SELECT COUNT(*) FROM features
        WHERE feature_type IN ('amenity', 'shop')
        AND ST_DWithin(geom, ST_GeomFromText(%s, 4326), 0.0009)  -- ~100m
    """, (road_geom.wkt,))
    count = cur.fetchone()[0]
    return count / length_m if length_m > 0 else 0

def compute_isolation_score(cur, road_geom):
    """Inverse of road density: distance to nearest road."""
    cur.execute("""
        SELECT ST_Distance(geom, ST_GeomFromText(%s, 4326)) as dist
        FROM roads
        WHERE id != (SELECT id FROM roads WHERE geom = ST_GeomFromText(%s, 4326) LIMIT 1)
        ORDER BY dist LIMIT 1
    """, (road_geom.wkt, road_geom.wkt))
    dist = cur.fetchone()
    return dist[0] if dist else 1000  # max isolation if no other roads

def compute_human_presence(cur, road_geom, length_m):
    """Proxy: POI density as indicator."""
    return compute_poi_density(cur, road_geom, length_m)

def compute_signal_proxy(cur, road_geom, length_m):
    """Proxy: assume higher in populated areas, use POI density."""
    return compute_poi_density(cur, road_geom, length_m)

def normalize_score(score, min_val, max_val):
    """Simple min-max normalization clamped to [0, 1]."""
    if max_val - min_val == 0:
        return 0.5
    normalized = (score - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))

def compute_composite_risk(lighting, poi, isolation, presence, signal):
    """Weighted sum: higher lighting/poi/presence/signal lower risk, higher isolation higher risk."""
    weights = {'lighting': 0.3, 'poi': 0.2, 'isolation': 0.2, 'presence': 0.15, 'signal': 0.15}
    
    # Lighting and POI densities usually range from 0.0 to 0.1 (per meter)
    lighting_norm = normalize_score(lighting, 0, 0.05)
    poi_norm = normalize_score(poi, 0, 0.02)
    presence_norm = normalize_score(presence, 0, 0.02)
    signal_norm = normalize_score(signal, 0, 0.02)
    
    isolation_norm = normalize_score(isolation, 0, 1000)
    
    risk = ((1.0 - lighting_norm) * weights['lighting'] +
            (1.0 - poi_norm) * weights['poi'] +
            isolation_norm * weights['isolation'] +
            (1.0 - presence_norm) * weights['presence'] +
            (1.0 - signal_norm) * weights['signal'])
            
    return max(0.0, min(1.0, risk))

def process_road_chunk(roads_chunk):
    """Worker function to process a batch of roads in a single thread."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    processed = 0
    for road_id, geom_wkb, length_m in roads_chunk:
        geom = wkb.loads(geom_wkb, hex=True)

        lighting = compute_lighting_density(cur, geom, length_m)
        poi = compute_poi_density(cur, geom, length_m)
        isolation = compute_isolation_score(cur, geom)
        presence = compute_human_presence(cur, geom, length_m)
        signal = compute_signal_proxy(cur, geom, length_m)
        composite = compute_composite_risk(lighting, poi, isolation, presence, signal)

        cur.execute("""
            INSERT INTO risk_scores (road_id, lighting_density, poi_density, isolation_score, human_presence, signal_proxy, composite_risk)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (road_id) DO UPDATE SET
                lighting_density = EXCLUDED.lighting_density,
                poi_density = EXCLUDED.poi_density,
                isolation_score = EXCLUDED.isolation_score,
                human_presence = EXCLUDED.human_presence,
                signal_proxy = EXCLUDED.signal_proxy,
                composite_risk = EXCLUDED.composite_risk,
                updated_at = CURRENT_TIMESTAMP
        """, (road_id, lighting, poi, isolation, presence, signal, composite))
        
        processed += 1
        
    conn.commit()
    cur.close()
    conn.close()
    return processed

def update_risk_scores():
    """Compute and update risk scores for all roads using CPU multithreading."""
    import concurrent.futures
    import multiprocessing
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, geom, length_m FROM roads")
    roads = cur.fetchall()
    cur.close()
    conn.close()

    total_roads = len(roads)
    print(f"Calculating risk scores for {total_roads} roads using Multithreading...")
    
    # Split into chunks of 200 roads per thread
    chunk_size = 200
    chunks = [roads[i:i + chunk_size] for i in range(0, total_roads, chunk_size)]
    
    # Use max CPU threads available (leaving 1 for OS)
    max_workers = max(1, multiprocessing.cpu_count() - 1)
    print(f"Starting ThreadPoolExecutor with {max_workers} workers...")
    
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_road_chunk, chunk): chunk for chunk in chunks}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                processed = future.result()
                completed += processed
                print(f"Processed {completed}/{total_roads} roads...")
            except Exception as exc:
                print(f"A chunk generated an exception: {exc}")

    print("Risk scores update complete.")
