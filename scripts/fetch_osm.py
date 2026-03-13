#!/usr/bin/env python3
import argparse
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from data_updates.osm_fetcher import fetch_and_store_roads, fetch_and_store_features

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OSM data for a given place and store in database.")
    parser.add_argument('--place', required=True, help="Name of the place, e.g., 'New York City'")
    args = parser.parse_args()

    print(f"Fetching roads for {args.place}...")
    fetch_and_store_roads(args.place)

    print(f"Fetching features for {args.place}...")
    fetch_and_store_features(args.place)

    print("Data fetching complete.")
