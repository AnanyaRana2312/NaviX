from fastapi.testclient import TestClient
from backend.main import app
import json

def run_test():
    client = TestClient(app)
    
    body = {
        "origin_lat": 40.7128,
        "origin_lon": -74.0060,
        "destination_lat": 40.7306,
        "destination_lon": -73.9352,
        "place": "Dehradun, Uttarakhand, India",
        "max_routes": 1
    }
    
    print("Testing real route generation with OSMnx graph...")
    response = client.post("/api/v1/routes", json=body)
    
    if response.status_code == 200:
        data = response.json()
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            segments = route.get("segments", [])
            print(f"\nSUCCESS! Received {len(segments)} road segments in the route.")
            
            if segments:
                print("\nHere is the first segment as an example:")
                print(json.dumps(segments[0], indent=2))
                
                print("\nAnd the last segment:")
                print(json.dumps(segments[-1], indent=2))
                
            print(f"\nTotal Route Distance: {route['total_distance']:.2f} meters")
            print(f"Total Route Risk Score: {route['total_risk']:.2f}")
        else:
            print("No routes returned.")
            print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    run_test()
