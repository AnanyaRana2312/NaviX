import os
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
geolocator = Nominatim(user_agent="navix_demo")

st.title("NaviX Route Demo")
st.markdown("Safety-aware routing demo. Enter start/end coordinates and place.")

if 'origin_lat' not in st.session_state:
    st.session_state['origin_lat'] = 30.3995
    st.session_state['origin_lon'] = 77.9691
if 'dest_lat' not in st.session_state:
    st.session_state['dest_lat'] = 30.4079
    st.session_state['dest_lon'] = 77.9687
if 'selecting_mode' not in st.session_state:
    st.session_state['selecting_mode'] = 'Origin'

st.markdown("### Set Locations by Address or Click on Map")
col1, col2 = st.columns(2)
with col1:
    origin_address = st.text_input("Origin Address", "", key="origin_addr")
    if st.button("Geocode Origin") and origin_address:
        loc = geolocator.geocode(origin_address)
        if loc:
            st.session_state['origin_lat'] = loc.latitude
            st.session_state['origin_lon'] = loc.longitude
            st.success(f"Found: {loc.address}")
        else:
            st.error("Address not found")
    origin_lat = st.number_input("Origin Latitude", value=st.session_state['origin_lat'], key="olat")
    origin_lon = st.number_input("Origin Longitude", value=st.session_state['origin_lon'], key="olon")
    st.session_state['origin_lat'] = origin_lat
    st.session_state['origin_lon'] = origin_lon

with col2:
    dest_address = st.text_input("Destination Address", "", key="dest_addr")
    if st.button("Geocode Destination") and dest_address:
        loc = geolocator.geocode(dest_address)
        if loc:
            st.session_state['dest_lat'] = loc.latitude
            st.session_state['dest_lon'] = loc.longitude
            st.success(f"Found: {loc.address}")
        else:
            st.error("Address not found")
    dest_lat = st.number_input("Destination Latitude", value=st.session_state['dest_lat'], key="dlat")
    dest_lon = st.number_input("Destination Longitude", value=st.session_state['dest_lon'], key="dlon")
    st.session_state['dest_lat'] = dest_lat
    st.session_state['dest_lon'] = dest_lon

st.session_state['selecting_mode'] = st.radio("Click on map below to select:", ["Origin", "Destination"])

select_m = folium.Map(location=[st.session_state['origin_lat'], st.session_state['origin_lon']], zoom_start=12)
folium.Marker([st.session_state['origin_lat'], st.session_state['origin_lon']], popup="Origin", icon=folium.Icon(color="green")).add_to(select_m)
folium.Marker([st.session_state['dest_lat'], st.session_state['dest_lon']], popup="Destination", icon=folium.Icon(color="red")).add_to(select_m)

map_data = st_folium(select_m, width=700, height=400, key="select_map")
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lng = map_data["last_clicked"]["lng"]
    if st.session_state['selecting_mode'] == 'Origin':
        if st.session_state['origin_lat'] != lat or st.session_state['origin_lon'] != lng:
            st.session_state['origin_lat'] = lat
            st.session_state['origin_lon'] = lng
            st.rerun()
    else:
        if st.session_state['dest_lat'] != lat or st.session_state['dest_lon'] != lng:
            st.session_state['dest_lat'] = lat
            st.session_state['dest_lon'] = lng
            st.rerun()

origin_lat = st.session_state['origin_lat']
origin_lon = st.session_state['origin_lon']
dest_lat = st.session_state['dest_lat']
dest_lon = st.session_state['dest_lon']

@st.fragment(run_every="5s")
def render_sidebar_status():
    st.header("Database Status")
    try:
        prog_resp = requests.get(f'{BACKEND_URL}/api/v1/progress', timeout=2)
        if prog_resp.status_code == 200:
            prog_data = prog_resp.json()
            if 'error' in prog_data:
                st.error("DB Offline")
            else:
                pct = prog_data.get('percent', 0)
                st.progress(int(pct) if pct <= 100 else 100)
                st.write(f"Safety Scores Computed: {prog_data['scored']} / {prog_data['total']} ({pct}%)")
                if pct < 100:
                    st.warning("Routes may use fallback risk scores until 100%. Auto-refreshing...")
                else:
                    st.success("Database fully populated!")
    except Exception:
        st.error("Backend Offline")

with st.sidebar:
    render_sidebar_status()

place = st.text_input("Place Name", value="Dehradun, Uttarakhand, India")
max_routes = st.slider("Number of Routes", min_value=1, max_value=3, value=3)

if st.button("Get Routes"):
    import uuid
    task_id = f"task_demo_{uuid.uuid4().hex[:8]}"
    body = {
        "origin_lat": origin_lat,
        "origin_lon": origin_lon,
        "destination_lat": dest_lat,
        "destination_lon": dest_lon,
        "place": place,
        "max_routes": max_routes,
        "task_id": task_id
    }
    import time
    import threading

    # Create placeholders
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Run request in thread to not block the UI updates
    result_container = {}
    def fetch_data():
        try:
            resp = requests.post(f'{BACKEND_URL}/api/v1/routes', json=body, timeout=150)
            result_container['data'] = resp.json()
        except Exception as e:
            result_container['error'] = str(e)
            
    thread = threading.Thread(target=fetch_data)
    thread.start()
    
    while thread.is_alive():
        time.sleep(0.5)
        try:
            prog_resp = requests.get(f'{BACKEND_URL}/api/v1/routes/progress/{task_id}', timeout=1)
            if prog_resp.status_code == 200:
                prog_data = prog_resp.json()
                pct = prog_data.get('percent', 0)
                msg = prog_data.get('message', 'Fetching routes...')
                progress_bar.progress(int(pct))
                status_text.text(f"{msg} ({pct}%)")
        except:
            pass
        
    thread.join()
    progress_bar.progress(100)
    
    if 'error' in result_container:
        st.session_state['route_data'] = None
        st.session_state['show_map'] = False
        st.error(f"Error: {result_container['error']}")
        status_text.empty()
    else:
        st.session_state['route_data'] = result_container['data']
        st.session_state['show_map'] = True
        status_text.text("Fetch Complete! ✅")
        
        # Display metadata
        metadata = result_container['data'].get('metadata', {})
        if metadata:
            st.info(f"**Data Source:** {metadata.get('message', 'Fetched from cache.')}\n\n"
                    f"🗺️ **Graph Base:** {metadata.get('graph_source', 'OSMnx')}\n\n"
                    f"🛡️ **Safety Scoring:** {metadata.get('safety_source', 'PostGIS')}")

# Show results if present
if st.session_state.get('route_data') and st.session_state.get('show_map'):
    data = st.session_state['route_data']
    st.markdown("### Route Options")
    st.markdown("Hover over the paths to see ETAs. Use the layer control icon in the top right of the map to toggle individual routes!")
    
    m = folium.Map(location=[origin_lat, origin_lon], zoom_start=13)
    colors = ['blue', 'green', 'red']
    
    for idx, route in enumerate(data['routes']):
        # Assume average walking speed of 1.4 meters per second
        eta_mins = route['total_distance'] / 1.4 / 60
        dist_km = route['total_distance'] / 1000
        risk_score = route['total_risk']
        
        tooltip = f"<b>Route {idx+1}</b><br>ETA: {eta_mins:.1f} mins<br>Distance: {dist_km:.2f} km<br>Cumulative Risk: {risk_score:.0f}"
        
        # Create a FeatureGroup for each route so they can be toggled via LayerControl
        fg = folium.FeatureGroup(name=f"Route {idx+1} ({eta_mins:.1f} mins, {dist_km:.2f} km)")
        folium.PolyLine(route['path'], color=colors[idx % len(colors)], weight=5, opacity=0.7, tooltip=tooltip).add_to(fg)
        fg.add_to(m)
        
    # Add layer control so user can toggle overlapping routes
    folium.LayerControl().add_to(m)
    st_folium(m, width=700, height=500)
