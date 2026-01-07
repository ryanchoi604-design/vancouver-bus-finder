# app.py - Streamlit + 내장 프록시 포함 (Cloud 배포용)
import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2
from flask import Flask, Response
from threading import Thread

# ================================
# Ryan님의 TransLink API 키
API_KEY = "i95CeGKk3M7wzbteE3cl"
# ================================

# --------------------------
# 1️⃣ Flask 프록시 서버 (내장)
app = Flask(__name__)
GTFS_URL = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"

@app.route("/gtfs")
def gtfs_proxy():
    try:
        r = requests.get(GTFS_URL, timeout=10)
        return Response(r.content, status=r.status_code, content_type="application/octet-stream")
    except Exception as e:
        return Response(str(e), status=500)

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# Flask를 별 스레드에서 실행
Thread(target=run_flask, daemon=True).start()

# --------------------------
# 2️⃣ Streamlit UI
st.set_page_config(
    page_title="🚌 버스 번호 찾기 (Block Finder)",
    page_icon="🚌",
    layout="centered"
)

st.markdown(
    """
    <div style="text-align:center; background-color:#f0f2f6; padding:20px; border-radius:15px;">
        <h1>🚌 내 버스 찾기 (Block Finder)</h1>
        <p>라인 번호 + 블락 번호 → 🚀 현재 운행 중인 차량 번호 확인</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------
# 예시 데이터: 라인 번호와 블락 번호
LINE_BLOCKS = {
    "3": ["1", "2", "10", "12"],
    "4": ["1", "3", "5"],
    "5": ["1", "2", "4"],
    "6": ["1", "2", "7"],
    "7": ["1", "2", "6"],
    "8": ["2", "5", "8"],
    "10": ["1", "2", "5", "10"]
}

# 1️⃣ 라인/블락 선택 UI
col1, col2 = st.columns(2)
with col1:
    line = st.selectbox("라인 번호", options=list(LINE_BLOCKS.keys()))
with col2:
    block = st.selectbox("블락 번호", options=LINE_BLOCKS.get(line, []))

# 2️⃣ 검색 버튼 클릭 시
if st.button("🚀 차량 번호 찾기"):
    st.info(f"📡 라인 {line} / 블락 {block} 검색 중...")

    try:
        PROXY_URL = "http://127.0.0.1:5000/gtfs"
        r = requests.get(PROXY_URL, timeout=10)
        if r.status_code != 200:
            st.error(f"GTFS 데이터 요청 실패! 상태 코드: {r.status_code}")
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
                st.success(f"🚍 차량 번호: {found_vehicle}")
                st.markdown(f"[🔗 T-Comm Live에서 위치 확인](https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle})")
            else:
                st.warning("💤 현재 운행 중인 차량을 찾을 수 없습니다. (차고지에 있거나 아직 출발 안 함)")

    except Exception as e:
        st.error(f"⚠️ 에러 발생: {e}")
        st.info("💡 앱 내부 프록시가 정상 실행 중인지 확인해주세요.")
