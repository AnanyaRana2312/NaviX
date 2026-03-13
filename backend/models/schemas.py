from pydantic import BaseModel
from typing import List, Optional

# Request models
class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    place: str  # e.g., "New York City"
    max_routes: Optional[int] = 3

# Response models
class RoadSegment(BaseModel):
    id: int
    osm_id: Optional[int]
    name: Optional[str]
    highway: Optional[str]
    length_m: float
    risk_score: float

class Route(BaseModel):
    segments: List[RoadSegment]
    total_distance: float
    total_risk: float
    path: List[List[float]]  # List of [lat, lon] coordinates

class RouteResponse(BaseModel):
    routes: List[Route]

# Feature model for POIs, etc.
class Feature(BaseModel):
    id: int
    osm_id: Optional[int]
    feature_type: str
    name: Optional[str]
    lat: float
    lon: float
    attributes: Optional[dict]

# Risk score model
class RiskScore(BaseModel):
    road_id: int
    lighting_density: float
    poi_density: float
    isolation_score: float
    human_presence: float
    signal_proxy: float
    composite_risk: float
