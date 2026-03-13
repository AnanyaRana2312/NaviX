from fastapi import APIRouter, HTTPException
from backend.models.schemas import RouteRequest, RouteResponse
from backend.routing.router import find_routes

router = APIRouter()

@router.post("/routes", response_model=RouteResponse)
def get_routes(request: RouteRequest):
    """Get multiple safety-aware routes."""
    try:
        raw_routes = find_routes(
            request.origin_lat, request.origin_lon,
            request.destination_lat, request.destination_lon,
            request.place, request.max_routes
        )
        routes = []
        for r in raw_routes:
            # Placeholder: segment-level details are not yet implemented.
            segments = []
            # `get_route_details` returns coordinates as [lat, lon]. Keep that order to match schema.
            path = [[coord[0], coord[1]] for coord in r['path']]  # lat, lon
            routes.append({
                'segments': segments,
                'total_distance': r['total_distance'],
                'total_risk': r['total_risk'],
                'path': path
            })
        return RouteResponse(routes=routes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
