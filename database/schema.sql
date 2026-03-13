-- NaviX Database Schema
-- PostgreSQL with PostGIS extension

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table for road segments
CREATE TABLE roads (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT UNIQUE,
    name VARCHAR(255),
    highway VARCHAR(50),
    geom GEOMETRY(LINESTRING, 4326),
    length_m DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for geospatial features (POIs, lighting, etc.)
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    osm_id BIGINT UNIQUE,
    feature_type VARCHAR(50),  -- e.g., 'poi', 'lighting', 'business'
    name VARCHAR(255),
    geom GEOMETRY(POINT, 4326),
    attributes JSONB,  -- flexible for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for risk scores per road segment
CREATE TABLE risk_scores (
    id SERIAL PRIMARY KEY,
    road_id INTEGER REFERENCES roads(id) ON DELETE CASCADE,
    lighting_density DOUBLE PRECISION DEFAULT 0,
    poi_density DOUBLE PRECISION DEFAULT 0,
    isolation_score DOUBLE PRECISION DEFAULT 0,
    human_presence DOUBLE PRECISION DEFAULT 0,
    signal_proxy DOUBLE PRECISION DEFAULT 0,
    composite_risk DOUBLE PRECISION DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial indexes for performance
CREATE INDEX idx_roads_geom ON roads USING GIST (geom);
CREATE INDEX idx_features_geom ON features USING GIST (geom);
