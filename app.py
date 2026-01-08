import streamlit as st
import requests
import pandas as pd
from google.transit import gtfs_realtime_pb2

# 🔹 렌더 프록시 서버 주소
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"

st.title("🚌 Bus Block Finder")

# 1. trips.txt 로드 (app.py와 같은 폴더에 있어야 함)
@st.cache_data
def load_trips():
    return pd.read_csv("trips.txt", dtype=str)

trips_df = load_trips()

line = st.number_input("Line Number", min_value=1, step=1, value=3)
block = st.number_input("Block Number", min_value=1, step=1, value=1)

if st.button("Find Bus"):
    target_line = str(line).zfill(3)
    target_block = str(block)

    # trips.txt에서 먼저 Trip ID를 찾음 (어제의 핵심!)
    matched_trips = trips_df[
        (trips_df['route_id'] == target_line) & 
        (trips_df['block_id'].str.contains(target_block))
    ]['trip_id'].tolist()

    try:
        # 프록시 서버(렌더)에서 외계어 받아오기
        r = requests.get(PROXY_URL, timeout=15)
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)

        found = False
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_id = entity.trip_update.trip.trip_id
                if trip_id in matched_trips:
                    vehicle_id = entity.trip_update.vehicle.id
                    st.success(f"✅ 찾았다! 차번호: {vehicle_id}")
                    found = True
                    break
        
        if not found:
            st.warning("❌ 지금은 운행 중인 차가 없나봐.")
    except Exception as e:
        st.error(f"프록시 서버 연결 실패: {e}")
