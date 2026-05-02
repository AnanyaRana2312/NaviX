import psycopg2
import os
from dotenv import load_dotenv
from backend.data_updates.osm_fetcher import fetch_and_store_roads, fetch_and_store_features, fetch_and_store_roads_bbox, fetch_and_store_features_bbox
from backend.safety.risk_engine import update_risk_scores

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

def clear_all_data():
    """Wipe all routing and safety data from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    print("[NaviX] Wiping existing data from DB...")
    cur.execute("TRUNCATE TABLE risk_scores, features, roads RESTART IDENTITY CASCADE;")
    conn.commit()
    cur.close()
    conn.close()

def repopulate_database(place, task_id=None, progress_callback=None):
    """
    Full pipeline: Clear DB -> Fetch OSM -> Compute Scores.
    """
    def notify(msg, pct):
        if progress_callback:
            progress_callback(task_id, msg, pct)
        print(f"[NaviX] {msg} ({pct}%)")

    notify(f"Clearing old data for new location: {place}", 0)
    clear_all_data()

    notify(f"Fetching road network for {place}...", 10)
    fetch_and_store_roads(place)

    notify(f"Fetching POIs and lighting for {place}...", 30)
    fetch_and_store_features(place)

def repopulate_database_bbox(north, south, east, west, task_id=None, progress_callback=None):
    """
    Full pipeline by BBOX: Clear DB -> Fetch OSM -> Compute Scores.
    """
    def notify(msg, pct):
        if progress_callback:
            progress_callback(task_id, msg, pct)
        print(f"[NaviX] {msg} ({pct}%)")

    notify(f"Clearing old data for new coordinate area", 0)
    clear_all_data()

    notify(f"Fetching road network for area...", 10)
    fetch_and_store_roads_bbox(north, south, east, west)

    notify(f"Fetching POIs and lighting for area...", 30)
    fetch_and_store_features_bbox(north, south, east, west)

    notify(f"Calculating Safety Risk Scores...", 50)
    update_risk_scores()

    notify(f"Database population for coordinate area complete!", 100)

    notify(f"Calculating Safety Risk Scores (this takes a moment)...", 50)
    update_risk_scores()

    notify(f"Database population for {place} complete!", 100)
