import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

# ========================
API_KEY = "i95CeGKk3M7wzbteE3cl"
# ========================

st.set_page_config(page_title="🚌 내 버스 찾기", page_icon="🚌", layout="centered")

# 🎨 배경 + 스타일
st.markdown("""
<style>
body {
    background-image: url('https://images.unsplash.com/photo-1556761175-5973dc0f32e7?auto=format&fit=crop&w=1050&q=80');
    background-size: cover;
}
.big-bus { font-size: 80px; font-weight: bold; color: #FF4B4B; text-align: center; }
.medium { font-size: 25px; text-align: center; }
.st-button {
    font-size: 18px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🚌 내 버스 찾기")
st.caption("라인 번호 + 블락 번호 → 🚀 지금 운행 중인 차량 번호")

# ========================
# 정적 trips 데이터
@st.cache_data
def load_trips():
    return pd.read_csv("trips.txt", dtype=str)

trips_df = load_trips()

# ========================
# 즐겨찾기 관리
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

# ========================
# UI: 노선 선택
routes = sorted(trips_df["route_id"].unique())
route = st.selectbox("🚏 노선 선택", routes)

# 즐겨찾기 추가
if route not in st.session_state["favorites"]:
    if st.button(f"➕ '{route}' 즐겨찾기 추가", key="fav_add"):
        st.session_state["favorites"].append(route)

# 즐겨찾기 바로가기
if st.session_state["favorites"]:
    fav_route = st.selectbox("🔥 즐겨찾기 노선 바로가기",
                             st.session_state["favorites"],
                             key="fav_select")
    if fav_route != route:
        route = fav_route

# ========================
# 블락 선택 (운행 중인 것만)
route_trips = trips_df[trips_df["route_id"] == route]
active_blocks = sorted(route_trips["block_id"].unique())
block = st.selectbox("🧱 블락 선택", active_blocks)

# ========================
# 검색 버튼
if st.button("🎯 차량 번호 찾기", key="search"):

    matched_trips = route_trips[
        route_trips["block_id"].str.lstrip('0') == block.lstrip('0')
    ]
    trip_ids = matched_trips["trip_id"].tolist()

    if not trip_ids:
        st.warning("😅 해당 블락 정보가 trips.txt에 없거나 운행 중이지 않을 수 있음")
    else:
        # GTFS 실시간 호출
        url = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
        headers = {"Accept": "application/x-protobuf", "User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=15)
            found_vehicle = "운행 중인 차량 없음"
            if r.status_code == 200 and r.content:
                feed = gtfs_realtime_pb2.FeedMessage()
                try:
                    feed.ParseFromString(r.content)
                    for e in feed.entity:
                        if e.HasField("vehicle") and e.vehicle.trip.trip_id in trip_ids:
                            found_vehicle = e.vehicle.id
                            bus_type = e.vehicle.label or "Unknown"
                            break
                except Exception:
                    found_vehicle = "알 수 없음 (ProtoBuf 파싱 실패)"
            else:
                found_vehicle = f"서버 문제 (응답 코드: {r.status_code})"

            # ========================
            # 결과 출력
            st.markdown(f"<div class='big-bus'>{found_vehicle}</div>", unsafe_allow_html=True)
            if found_vehicle not in ["운행 중인 차량 없음", "알 수 없음 (ProtoBuf 파싱 실패)"] \
               and "서버 문제" not in found_vehicle:
                st.markdown(f"<div class='medium'>🚐 차량 타입: {bus_type}</div>", unsafe_allow_html=True)
                tcomm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle}"
                st.markdown(f"### 🔗 [T-Comm Live에서 실시간 위치 보기]({tcomm_url})")
                st.balloons()
            else:
                st.info("💡 차량 번호만 확인 가능, 실시간 위치는 T-Comm Live에서 확인하세요.")

        except Exception as e:
            st.error(f"📡 서버 연결 실패: {e}")
            st.info("💡 로컬/핫스팟에서 시도하거나 잠시 후 재접속")
