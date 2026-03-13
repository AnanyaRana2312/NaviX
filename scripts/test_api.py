import requests
import json

body = {
    "origin_lat": 40.7128,
    "origin_lon": -74.0060,
    "destination_lat": 40.7306,
    "destination_lon": -73.9352,
    "place": "New York City",
    "max_routes": 3
}

resp = requests.post('http://127.0.0.1:8000/api/v1/routes', json=body, timeout=10)
print('Status:', resp.status_code)
print(resp.text)

