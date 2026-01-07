import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

# ========================================
API_KEY = "i95CeGKk3M7wzbteE3cl"
# ========================================

st.set_page_config(page_title="🚌 내 버스 찾기", layout="centered")
st.title("🚌 내 버스 찾기 (라인/블락 변환)")

# ------------------------
# trips.txt 로드
@st.cache_data
def load_trips():
    return pd.read_csv("trips.txt", dtype=str)

trips_df = load_trips()

# ------------------------
# 사용자가 보는 라인/블락 목록
# 실제 route_id, block_id와 숫자형 매핑 예시
# 숫자 입력 → 내부 포맷 변환
route_map = {str(i): f"{i:03d}" for i in range(1, 20)}  # 1→001, 2→002...
# 블락 매핑 예시: 숫자 → 실제 block_id(A-****)
block_map = {}
for r in trips_df["route_id"].unique():
    blocks = sorted(trips_df[trips_df["route_id"]==r]["block_id"].unique())
    # 1,2,3,... 숫자로 선택할 수 있게
    block_map[r] = {str(i+1): b for i,b in enumerate(blocks)}

# ------------------------
# 사용자 입력
col1, col2 = st.columns(2)
with col1:
    user_line = st.number_input("라인 번호", min_value=1, max_value=19, value=3)
with col2:
    user_block = st.number_input("블락 번호", min_value=1, value=1)

# ------------------------
if st.button("🎯 차량 번호 찾기"):

    # 입력 → 내부 ID 변환
    route_id = route_map.get(str(user_line))
    block_id = block_map.get(route_id, {}).get(str(user_block))

    if not route_id or not block_id:
        st.error("❌ 해당 라인/블락 매핑 정보가 없습니다.")
    else:
        st.info(f"검색: 라인 {user_line} → {route_id}, 블락 {user_block} → {block_id}")

        # trips.txt에서 trip_id 찾기
        matched_trips = trips_df[(trips_df["route_id"]==route_id) & (trips_df["block_id"]==block_id)]
        trip_ids = matched_trips["trip_id"].tolist()

        if not trip_ids:
            st.warning("🤔 선택한 블락/라인에 운행 중인 차량이 없거나 trips.txt에 없음")
        else:
            # GTFS-Realtime 호출
            url = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
            headers = {"Accept": "application/x-protobuf", "User-Agent": "Mozilla/5.0"}

            try:
                r = requests.get(url, headers=headers, timeout=15)
                found_vehicle = "운행 중인 차량 없음"
                bus_type = "Unknown"

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

                # 결과 출력
                st.markdown(f"<h1 style='text-align:center; font-size:100px; color:#FF4B4B;'>{found_vehicle}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center;'>🚐 차량 타입: {bus_type}</h3>", unsafe_allow_html=True)

                if found_vehicle not in ["운행 중인 차량 없음", "알 수 없음 (ProtoBuf 파싱 실패)"]:
                    tcomm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle}"
                    st.markdown(f"<div style='text-align:center;'><a href='{tcomm_url}' target='_blank'>🔗 T-Comm Live에서 실시간 위치 확인</a></div>")

            except Exception as e:
                st.error(f"📡 서버 연결 실패: {e}")
                st.info("💡 로컬/핫스팟에서 시도하거나 잠시 후 재접속")
