import psycopg2
import psycopg2.extras
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

def compute_lighting_density(road_geom):
    """Count lighting features within 50m buffer of road."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM features
        WHERE feature_type = 'lighting'
        AND ST_DWithin(geom, ST_GeomFromText(%s, 4326), 0.00045)  -- ~50m in degrees
    """, (road_geom.wkt,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count / road_geom.length if road_geom.length > 0 else 0  # density per meter

def compute_poi_density(road_geom):
    """Count POI features within 100m buffer."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM features
        WHERE feature_type IN ('amenity', 'shop')
        AND ST_DWithin(geom, ST_GeomFromText(%s, 4326), 0.0009)  -- ~100m
    """, (road_geom.wkt,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count / road_geom.length if road_geom.length > 0 else 0

def compute_isolation_score(road_geom):
    """Inverse of road density: distance to nearest road."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ST_Distance(geom, ST_GeomFromText(%s, 4326)) as dist
        FROM roads
        WHERE id != (SELECT id FROM roads WHERE geom = ST_GeomFromText(%s, 4326) LIMIT 1)
        ORDER BY dist LIMIT 1
    """, (road_geom.wkt, road_geom.wkt))
    dist = cur.fetchone()
    cur.close()
    conn.close()
    return dist[0] if dist else 1000  # max isolation if no other roads

def compute_human_presence(road_geom):
    """Proxy: POI density as indicator."""
    return compute_poi_density(road_geom)

def compute_signal_proxy(road_geom):
    """Proxy: assume higher in populated areas, use POI density."""
    return compute_poi_density(road_geom)

def normalize_score(score, min_val, max_val):
    """Simple min-max normalization."""
    if max_val - min_val == 0:
        return 0.5
    return (score - min_val) / (max_val - min_val)

def compute_composite_risk(lighting, poi, isolation, presence, signal):
    """Weighted sum: higher lighting/poi/presence/signal lower risk, higher isolation higher risk."""
    weights = {'lighting': 0.3, 'poi': 0.2, 'isolation': 0.2, 'presence': 0.15, 'signal': 0.15}
    # Normalize each (assuming ranges, but for simplicity, assume 0-1 already or scale)
    # For now, assume densities are 0-1, isolation 0-1000, normalize isolation to 0-1 (higher worse)
    isolation_norm = normalize_score(isolation, 0, 1000)
    risk = (1 - lighting) * weights['lighting'] + (1 - poi) * weights['poi'] + isolation_norm * weights['isolation'] + (1 - presence) * weights['presence'] + (1 - signal) * weights['signal']
    return risk

def update_risk_scores():
    """Compute and update risk scores for all roads."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, geom FROM roads")
    roads = cur.fetchall()

    for road_id, geom_wkb in roads:
        geom = psycopg2.extras.wkb.loads(geom_wkb, hex=False)  # Assuming binary

        lighting = compute_lighting_density(geom)
        poi = compute_poi_density(geom)
        isolation = compute_isolation_score(geom)
        presence = compute_human_presence(geom)
        signal = compute_signal_proxy(geom)
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

    conn.commit()
    cur.close()
    conn.close()
    print("Risk scores updated.")
