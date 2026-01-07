# app.py - Streamlit Bus Finder with Render Proxy

import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# ================================
# Render proxy server URL
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"
# ================================

# Page setup
st.set_page_config(
    page_title="🚌 Bus Block Finder",
    page_icon="🚌",
    layout="centered"
)

# Header
st.markdown(
    """
    <div style="text-align:center; background-color:#f0f2f6; padding:20px; border-radius:15px;">
        <h1>🚌 Bus Block Finder</h1>
        <p>Line + Block → 🚀 Find the vehicle currently in service</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Example line/block data
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
# 1️⃣ Select Line / Block
col1, col2 = st.columns(2)

with col1:
    line = st.selectbox("Line Number", options=list(LINE_BLOCKS.keys()))

with col2:
    block = st.selectbox("Block Number", options=LINE_BLOCKS.get(line, []))

# --------------------------
# 2️⃣ Search button
if st.button("🚀 Find Vehicle"):
    st.info(f"📡 Searching Line {line} / Block {block}...")

    try:
        # Request GTFS data from Render proxy
        r = requests.get(PROXY_URL, timeout=10)
        if r.status_code != 200:
            st.error(f"GTFS request failed! Status code: {r.status_code}")
        else:
            # Parse GTFS Realtime feed
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(r.content)

            found_vehicle = None
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    trip_id = entity.trip_update.trip.trip_id
                    # Match line + block in trip_id (T-Comm style)
                    if f"_{line}_{block}" in trip_id:
                        if entity.trip_update.vehicle.id:
                            found_vehicle = entity.trip_update.vehicle.id
                            break

            # --------------------------
            # 3️⃣ Display result
            if found_vehicle:
                st.success(f"🚍 Vehicle ID: {found_vehicle}")
                st.markdown(
                    f"[🔗 View live location on T-Comm](https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle})"
                )
            else:
                st.warning(
                    "💤 No vehicle found currently in service. (It may be at the depot or not yet started)"
                )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.info("💡 Make sure the Render proxy server is up and network is working.")
