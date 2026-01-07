# app.py
import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# ================================
# YOUR TRANS_LINK API KEY
API_KEY = "YOUR_TRANS_LINK_API_KEY"
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
# ================================

st.set_page_config(
    page_title="🚌 Vancouver Bus Finder",
    page_icon="🚌",
    layout="centered"
)

st.markdown(
    """
    <div style="text-align:center; background-color:#f0f2f6; padding:20px; border-radius:15px;">
        <h1>🚌 Vancouver Bus Finder</h1>
        <p>Line + Block → Current Vehicle ID</p>
    </div>
    """,
    unsafe_allow_html=True
)

LINE_BLOCKS = {
    "3": ["1", "2", "10", "12"],
    "4": ["1", "3", "5"],
    "5": ["1", "2", "4"],
    "6": ["1", "2", "7"],
    "7": ["1", "2", "6"],
    "8": ["2", "5", "8"],
    "10": ["1", "2", "5", "10"]
}

col1, col2 = st.columns(2)
with col1:
    line = st.selectbox("Line", list(LINE_BLOCKS.keys()))
with col2:
    block = st.selectbox("Block", LINE_BLOCKS[line])

if st.button("🚀 Find Vehicle"):
    st.info(f"Searching Line {line} / Block {block} ...")
    try:
        r = requests.get(GTFS_URL, timeout=10)
        if r.status_code != 200:
            st.error(f"GTFS request failed! Status code: {r.status_code}")
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

            if found_vehicle:
                st.success(f"🚍 Vehicle ID: {found_vehicle}")
                st.markdown(f"[🔗 View live location](https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle})")
            else:
                st.warning("💤 No vehicle currently running for this Line/Block.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        st.info("Check your network or API key.")
