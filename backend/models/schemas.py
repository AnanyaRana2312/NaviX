from pydantic import BaseModel
from typing import List, Optional

# Request models
class RouteRequest(BaseModel):
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lon: Optional[float] = None
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
    place: Optional[str] = None
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
    metadata: Optional[dict] = None

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
