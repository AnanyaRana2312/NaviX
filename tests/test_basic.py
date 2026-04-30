from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NaviX backend is running."}

def test_get_routes():
    # Test with valid coordinates for Manhattan
    body = {
        "origin_lat": 40.7128,
        "origin_lon": -74.0060,
        "destination_lat": 40.7306,
        "destination_lon": -73.9352,
        "place": "Manhattan, New York City, USA",
        "max_routes": 3
    }
    response = client.post("/api/v1/routes", json=body)
    assert response.status_code == 200
    data = response.json()
    assert "routes" in data
    assert len(data["routes"]) > 0
    # verify at least one route has path coordinates
    route = data["routes"][0]
    assert "path" in route
    assert "total_distance" in route
    assert "total_risk" in route
