import streamlit as st
import pandas as pd
import requests
import datetime
from google.transit import gtfs_realtime_pb2

# ==================================
API_KEY = "i95CeGKk3M7wzbteE3cl"
# ==================================

st.set_page_config(
    page_title="🚌 내 버스 찾기",
    page_icon="🚌",
    layout="centered"
)

# 🎨 스타일
st.markdown("""
<style>
body {
    background-image: url('https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1050&q=80');
    background-size: cover;
}
.big-bus { font-size: 80px; font-weight: bold; color: #FF4B4B; text-align: center; }
.medium { font-size: 25px; text-align: center; }
.button-big { font-size: 20px !important; height: 3em; }
</style>
""", unsafe_allow_html=True)

# 🔄 15초 자동 갱신
st.autorefresh(interval=15000, key="refresh")

st.title("🚌 내 버스 찾기 (Block Finder)")
st.caption("라인 번호 + 블락 번호 → 🚀 지금 운행 중인 차량 번호")

# ======================
# 정적 데이터 로드
@st.cache_data
def load_static():
    trips = pd.read_csv("trips.txt", dtype=str)
    stops = pd.read_csv("stops.txt", dtype=str)
    return trips, stops

trips_df, stops_df = load_static()

# ======================
# 실시간 GTFS 로드
@st.cache_data(ttl=15)
def load_feed():
    feed = gtfs_realtime_pb2.FeedMessage()
    url = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
    r = requests.get(url, timeout=15)
    feed.ParseFromString(r.content)
    return feed

feed = load_feed()

# ======================
# 차량 정보 & trip_update 정리
vehicles = {}
trip_updates = {}
for e in feed.entity:
    if e.HasField("vehicle"):
        v = e.vehicle
        if v.trip.trip_id and v.vehicle.id:
            vehicles[v.trip.trip_id] = {
                "id": v.vehicle.id,
                "type": v.vehicle.label or "Unknown"
            }
    if e.HasField("trip_update"):
        trip_updates[e.trip_update.trip.trip_id] = e.trip_update

# ======================
# 즐겨찾기
st.sidebar.header("⭐ 즐겨찾기")
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = []

# ======================
# 노선 선택
routes = sorted(trips_df["route_id"].unique())
route = st.selectbox("🚏 노선 선택", routes)

# 즐겨찾기 추가 버튼
if route not in st.session_state['favorites']:
    if st.sidebar.button(f"➕ '{route}' 즐겨찾기 추가"):
        st.session_state['favorites'].append(route)

# 즐겨찾기 바로가기
if st.session_state['favorites']:
    fav_route = st.sidebar.selectbox("🔥 즐겨찾기 노선 바로가기",
                                     st.session_state['favorites'],
                                     key="fav_select")
    if fav_route != route:
        route = fav_route

# ======================
# 블락 선택 (운행 중만)
route_trips = trips_df[trips_df["route_id"] == route]
active_blocks = sorted(route_trips[
    route_trips["trip_id"].isin(vehicles.keys())
]["block_id"].unique())

if not active_blocks:
    st.warning("😴 지금 운행 중인 블락이 없어")
    st.stop()

block = st.selectbox("🧱 블락 선택 (운행 중만)", active_blocks)

# ======================
# 검색 버튼
if st.button("🎯 버스 번호 찾기", use_container_width=True):

    matched = route_trips[
        (route_trips["block_id"] == block) &
        (route_trips["trip_id"].isin(vehicles.keys()))
    ]

    if matched.empty:
        st.warning("😅 버스가 현재 운행 중이지 않아")
    else:
        trip_id = matched.iloc[0]["trip_id"]
        bus = vehicles[trip_id]

        # 🎉 결과 출력
        st.markdown(f"<div class='big-bus'>{bus['id']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='medium'>🚐 차량 타입: {bus['type']}</div>", unsafe_allow_html=True)
        st.balloons()

        # 📍 다음 정류장 ETA
        tu = trip_updates.get(trip_id)
        if tu and tu.stop_time_update:
            next_stop = tu.stop_time_update[0]
            stop_id = next_stop.stop_id

            stop_name = stops_df[stops_df["stop_id"] == stop_id]["stop_name"].values

            if next_stop.arrival.time:
                arrival = datetime.datetime.fromtimestamp(next_stop.arrival.time)
                mins = int((arrival - datetime.datetime.now()).total_seconds() / 60)
                st.success(f"📍 다음 정류장: **{stop_name[0] if len(stop_name) else stop_id}** · 약 **{mins}분** 남음")

        # 🔗 T-Comm Live 링크
        tcomm = f"https://tcomm.bustrainferry.com/mobile/bus/{bus['id']}"
        st.markdown(f"### 🔗 [T-Comm Live에서 실시간 위치 보기]({tcomm})")

        st.caption("🔄 15초마다 자동 업데이트 중")
