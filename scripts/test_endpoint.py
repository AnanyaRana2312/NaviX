import httpx
import json

def run_test():
    body = {
        "origin_lat": 40.7128,
        "origin_lon": -74.0060,
        "destination_lat": 40.7306,
        "destination_lon": -73.9352,
        "place": "Manhattan, New York City, USA",
        "max_routes": 1
    }
    
    print("Requesting route from backend... (this might take a few seconds)")
    try:
        response = httpx.post("http://127.0.0.1:8000/api/v1/routes", json=body, timeout=120.0)
        data = response.json()
        
        if "routes" in data and len(data["routes"]) > 0:
            route = data["routes"][0]
            segments = route.get("segments", [])
            print(f"\n✅ Success! Received {len(segments)} road segments in the route.")
            
            if segments:
                print("\nHere is the first segment as an example:")
                print(json.dumps(segments[0], indent=2))
                
                print("\nAnd the last segment:")
                print(json.dumps(segments[-1], indent=2))
                
            print(f"\nTotal Route Distance: {route['total_distance']:.2f} meters")
            print(f"Total Route Risk Score: {route['total_risk']:.2f}")
        else:
            print("❌ No routes returned in response.")
            print(data)
    except httpx.ConnectError:
        print("❌ Cannot connect to backend. Make sure uvicorn is running on port 8000.")

if __name__ == "__main__":
    run_test()
