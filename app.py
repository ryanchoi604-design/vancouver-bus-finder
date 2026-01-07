# app.py - Streamlit 최종 완성본 (프록시 서버 연동)
import streamlit as st
import pandas as pd
import requests

# ================================
# Ryan님의 API 키 (프록시 서버 필요)
PROXY_URL = "http://127.0.0.1:5000/gtfs"
# ================================

# 페이지 설정
st.set_page_config(
    page_title="🚌 버스 번호 찾기 (Block Finder)",
    page_icon="🚌",
    layout="centered"
)

# 배경 이미지 + 타이틀
st.markdown(
    """
    <div style="text-align:center; background-color:#f0f2f6; padding:20px; border-radius:15px;">
        <h1>🚌 내 버스 찾기 (Block Finder)</h1>
        <p>라인 번호 + 블락 번호 → 🚀 지금 운행 중인 차량 번호 확인</p>
    </div>
    """,
    unsafe_allow_html=True
)

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

# --------------------------
# 1️⃣ 라인/블락 선택 UI
col1, col2 = st.columns(2)

with col1:
    line = st.selectbox("라인 번호", options=list(LINE_BLOCKS.keys()))

with col2:
    block = st.selectbox("블락 번호", options=LINE_BLOCKS.get(line, []))

# --------------------------
# 2️⃣ 검색 버튼 클릭 시
if st.button("🚀 차량 번호 찾기"):
    st.info(f"📡 라인 {line} / 블락 {block} 검색 중...")

    try:
        # GTFS 데이터 요청 (프록시 서버 사용)
        r = requests.get(PROXY_URL, timeout=10)
        if r.status_code != 200:
            st.error(f"GTFS 데이터 요청 실패! 상태 코드: {r.status_code}")
        else:
            # GTFS 파싱 (간단하게 Vehicle ID만 추출)
            from google.transit import gtfs_realtime_pb2
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(r.content)

            found_vehicle = None
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    trip_id = entity.trip_update.trip.trip_id
                    # 단순히 line + block 조합을 trip_id로 추정 (실제 T-Comm 기반)
                    if f"_{line}_{block}" in trip_id:
                        if entity.trip_update.vehicle.id:
                            found_vehicle = entity.trip_update.vehicle.id
                            break

            # --------------------------
            # 3️⃣ 결과 출력
            if found_vehicle:
                st.success(f"🚍 차량 번호: {found_vehicle}")
                st.markdown(f"[🔗 T-Comm Live에서 위치 확인](https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle})")
            else:
                st.warning("💤 현재 운행 중인 차량을 찾을 수 없습니다. (차고지에 있거나 아직 출발 안 함)")

    except Exception as e:
        st.error(f"⚠️ 에러 발생: {e}")
        st.info("💡 프록시 서버가 켜져 있는지, 네트워크가 정상인지 확인해주세요.")
