import osmnx as ox
import geopandas as gpd
import psycopg2
import psycopg2.extras
from shapely import wkb
from geoalchemy2 import WKTElement
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

def fetch_and_store_roads(place):
    """Fetch road network from OSM and store in DB."""
    G = ox.graph_from_place(place, network_type='drive')
    gdf = ox.graph_to_gdfs(G, nodes=False)[1]  # edges

    conn = get_db_connection()
    cur = conn.cursor()

    for idx, row in gdf.iterrows():
        osm_id = row.get('osmid', None)
        name = row.get('name', None)
        highway = row.get('highway', None)
        geom = row.geometry
        length_m = row.get('length', 0)

        # Convert geom to WKT
        wkt = geom.wkt

        cur.execute("""
            INSERT INTO roads (osm_id, name, highway, geom, length_m)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)
            ON CONFLICT (osm_id) DO NOTHING
        """, (osm_id, name, highway, wkt, length_m))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Stored {len(gdf)} road segments for {place}")

def fetch_and_store_features(place, tags={'amenity': True, 'shop': True, 'highway': 'street_lamp'}):
    """Fetch POIs and features from OSM and store in DB."""
    gdf = ox.geometries_from_place(place, tags=tags)

    conn = get_db_connection()
    cur = conn.cursor()

    for idx, row in gdf.iterrows():
        osm_id = row.get('osmid', None)
        name = row.get('name', None)
        geom = row.geometry
        if geom.geom_type != 'Point':
            continue  # Only points for now

        feature_type = 'poi'  # Default, can refine
        if 'amenity' in row and row['amenity']:
            feature_type = 'amenity'
        elif 'shop' in row and row['shop']:
            feature_type = 'shop'
        elif row.get('highway') == 'street_lamp':
            feature_type = 'lighting'

        attributes = {k: v for k, v in row.items() if k not in ['geometry', 'osmid', 'name']}

        wkt = geom.wkt

        cur.execute("""
            INSERT INTO features (osm_id, feature_type, name, geom, attributes)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)
            ON CONFLICT (osm_id) DO NOTHING
        """, (osm_id, feature_type, name, wkt, psycopg2.extras.Json(attributes)))

    conn.commit()
    cur.close()
    conn.close()
    print(f"Stored {len(gdf)} features for {place}")
