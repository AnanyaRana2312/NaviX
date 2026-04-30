from fastapi import APIRouter, HTTPException
from backend.models.schemas import RouteRequest, RouteResponse
from backend.routing.router import find_routes, get_db_connection

router = APIRouter()

@router.get("/progress")
def get_db_progress():
    """Return the progress of the safety score database population."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM risk_scores")
        scored = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM roads")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        percent = round((scored / total) * 100, 1) if total > 0 else 0
        return {"scored": scored, "total": total, "percent": percent}
    except Exception as e:
        return {"scored": 0, "total": 0, "percent": 0, "error": str(e)}

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
            segments = r.get('segments', [])
            # `get_route_details` returns coordinates as [lat, lon]. Keep that order to match schema.
            path = [[coord[0], coord[1]] for coord in r['path']]  # lat, lon
            routes.append({
                'segments': segments,
                'total_distance': r['total_distance'],
                'total_risk': r['total_risk'],
                'path': path
            })
            
        metadata = {
            "graph_source": "OSMnx Disk Cache",
            "safety_source": "PostGIS Database",
            "message": "Graph fetched from local cache. Safety scores attached from DB."
        }

        return RouteResponse(routes=routes, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
