import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# ===========================
API_KEY = "i95CeGKk3M7wzbteE3cl"
st.set_page_config(page_title="🚌 내 버스 실시간 찾기 V2", layout="centered")

st.markdown("<h1 style='text-align:center;'>🚌 내 버스 실시간 찾기</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>라인 선택 → 블락 선택 → 🚀 차량 번호 확인 → T-Comm 링크</p>", unsafe_allow_html=True)

# ------------------------
# 라인 번호 리스트 (예시, 실제 사용시 전체 라인/블락 데이터로 확장 가능)
line_options = ["3","4","5","6","7","8","10"]
line_input = st.selectbox("라인 번호 선택", line_options)

# ------------------------
# 블락 번호를 자동 드롭다운으로
# GTFS-Realtime 호출 후, 해당 라인 운행중인 블락 번호 추출
def fetch_blocks(line):
    url = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
    blocks = set()
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return [], f"API 응답 실패: {r.status_code}"
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)
        for entity in feed.entity:
            if entity.HasField("trip_update"):
                trip = entity.trip_update.trip
                # 여기서 Trip ID에 블락 정보가 포함되어 있다고 가정
                if line == trip.route_id:
                    blocks.add(trip.trip_id)  # 실제로는 Trip ID → Block ID 매핑 필요
        return sorted(list(blocks)), None
    except Exception as e:
        return [], f"에러 발생: {e}"

blocks_list, err = fetch_blocks(line_input)
if err:
    st.warning(err)
if not blocks_list:
    blocks_list = ["001","002","010"]  # 예시 블락
block_input = st.selectbox("블락 번호 선택", blocks_list)

# ------------------------
def get_vehicle(line, block):
    url = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return None, f"API 응답 실패: {r.status_code}"
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)
        for entity in feed.entity:
            if entity.HasField("trip_update"):
                trip = entity.trip_update.trip
                vehicle = entity.trip_update.vehicle
                # 여기서 Trip ID에 블락 정보가 포함돼 있다고 가정
                if line == trip.route_id and block in trip.trip_id:
                    return vehicle.id, None
        return None, "현재 운행 중인 차량 없음"
    except Exception as e:
        return None, f"에러 발생: {e}"

# ------------------------
if st.button("🚀 차량 번호 확인"):
    st.write(f"📡 라인 {line_input}, 블락 {block_input} 검색 중...")
    vehicle_id, error = get_vehicle(line_input, block_input)

    if vehicle_id:
        st.markdown(
            f"""
            <div style='background-color:#FFEB3B; border-radius:20px; padding:20px; text-align:center; margin-top:20px;'>
            <h1 style='font-size:80px; color:#E91E63; margin:0;'>🚍 {vehicle_id}</h1>
            <h3 style='margin:0;'>라인 {line_input}, 블락 {block_input}</h3>
            </div>
            """, unsafe_allow_html=True
        )
        tcomm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{vehicle_id}"
        st.markdown(
            f"<div style='text-align:center; margin-top:15px;'>"
            f"<a href='{tcomm_url}' target='_blank' "
            f"style='background-color:#4CAF50;color:white;padding:12px 25px;"
            f"border-radius:10px;text-decoration:none;font-size:18px;'>"
            f"🔗 T-Comm Live 위치 확인</a></div>",
            unsafe_allow_html=True
        )
    else:
        st.warning(error)
