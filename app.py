# app.py - Streamlit Bus Block Finder (Cloud-ready, proxy required)
import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# ================================
# Set your public proxy server URL here
PROXY_URL = "https://YOUR-PUBLIC-PROXY-SERVER/gtfs"
# ================================

# Page config
st.set_page_config(
    page_title="🚌 Bus Block Finder",
    page_icon="🚌",
    layout="centered"
)

# Header
st.markdown("""
<div style="text-align:center; background-color:#f0f2f6; padding:20px; border-radius:15px;">
    <h1>🚌 Bus Block Finder</h1>
    <p>Enter Line + Block → 🚀 Get Current Vehicle ID</p>
</div>
""", unsafe_allow_html=True)

# Sample Line/Block data
LINE_BLOCKS = {
    "3": ["1", "2", "10", "12"],
    "4": ["1", "3", "5"],
    "5": ["1", "2", "4"],
    "6": ["1", "2", "7"],
    "7": ["1", "2", "6"],
    "8": ["2", "5", "8"],
    "10": ["1", "2", "5", "10"]
}

# --------------------------
# Line / Block selection UI
col1, col2 = st.columns(2)
with col1:
    line = st.selectbox("Line Number", options=list(LINE_BLOCKS.keys()))
with col2:
    block = st.selectbox("Block Number", options=LINE_BLOCKS.get(line, []))

# --------------------------
# Search button
if st.button("🚀 Find Vehicle"):
    st.info(f"📡 Searching Line {line} / Block {block} ...")

    try:
        # GTFS data request via proxy server
        r = requests.get(PROXY_URL, timeout=10)
        if r.status_code != 200:
            st.error(f"Failed to get GTFS data! Status code: {r.status_code}")
        else:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(r.content)

            found_vehicle = None
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    trip_id = entity.trip_update.trip.trip_id
                    if f"_{line}_{block}" in trip_id:
                        if entity.trip_update.vehicle.id:
                            found_vehicle = entity.trip_update.vehicle.id
                            break

            # --------------------------
            # Result display
            if found_vehicle:
                st.success(f"🚍 Vehicle ID: {found_vehicle}")
                st.markdown(f"[🔗 Check Live Location on T-Comm](https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle})")
            else:
                st.warning("💤 Vehicle not currently running (garage or not started yet).")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.info("💡 Make sure the proxy server is running and network is OK.")
