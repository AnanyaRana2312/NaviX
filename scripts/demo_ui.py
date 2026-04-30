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

@st.fragment(run_every="5s")
def render_sidebar_status():
    st.header("Database Status")
    try:
        prog_resp = requests.get('http://127.0.0.1:8000/api/v1/progress', timeout=2)
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

place = st.text_input("Place Name", value="Manhattan, New York City, USA")
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
    import time
    import threading

    # Create placeholders
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Run request in thread to not block the UI updates
    result_container = {}
    def fetch_data():
        try:
            resp = requests.post('http://127.0.0.1:8000/api/v1/routes', json=body, timeout=150)
            result_container['data'] = resp.json()
        except Exception as e:
            result_container['error'] = str(e)
            
    thread = threading.Thread(target=fetch_data)
    thread.start()
    
    # Estimated time is ~5 seconds for cache load + A* 
    eta_seconds = 5
    elapsed = 0
    
    while thread.is_alive():
        time.sleep(0.1)
        elapsed += 0.1
        # Cap visual progress at 95% until thread actually finishes
        progress = min(int((elapsed / eta_seconds) * 100), 95)
        progress_bar.progress(progress)
        status_text.text(f"Fetching routes... (ETA: ~{max(0, int(eta_seconds - elapsed))}s remaining)")
        
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
