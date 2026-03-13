import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.title("NaviX Route Demo")
st.markdown("Safety-aware routing demo. Enter start/end coordinates and place.")

col1, col2 = st.columns(2)
with col1:
    origin_lat = st.number_input("Origin Latitude", value=40.7128)
    origin_lon = st.number_input("Origin Longitude", value=-74.0060)
with col2:
    dest_lat = st.number_input("Destination Latitude", value=40.7306)
    dest_lon = st.number_input("Destination Longitude", value=-73.9352)

place = st.text_input("Place Name", value="New York City")
max_routes = st.slider("Number of Routes", min_value=1, max_value=3, value=3)

if st.button("Get Routes"):
    body = {
        "origin_lat": origin_lat,
        "origin_lon": origin_lon,
        "destination_lat": dest_lat,
        "destination_lon": dest_lon,
        "place": place,
        "max_routes": max_routes
    }
    try:
        resp = requests.post('http://127.0.0.1:8000/api/v1/routes', json=body, timeout=10)
        data = resp.json()
        st.session_state['route_data'] = data
        st.session_state['show_map'] = True
        st.success("Routes fetched!")
    except Exception as e:
        st.session_state['route_data'] = None
        st.session_state['show_map'] = False
        st.error(f"Error: {e}")

# Show results if present
if st.session_state.get('route_data') and st.session_state.get('show_map'):
    data = st.session_state['route_data']
    st.json(data)
    m = folium.Map(location=[origin_lat, origin_lon], zoom_start=13)
    colors = ['blue', 'green', 'red']
    for idx, route in enumerate(data['routes']):
        folium.PolyLine(route['path'], color=colors[idx % len(colors)], weight=5, opacity=0.7).add_to(m)
    st_folium(m, width=700, height=500)
