# app.py - 실시간 라인+블락 차량 조회 (정확도 강화)
import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

PROXY_URL = "https://vancouver-bus-finder-1.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder", page_icon="🚌")
st.title("🚌 내 버스 찾기")
st.write("라인 + 블락 번호 입력 → 현재 운행 중인 차량 확인")

line_input = st.number_input("라인 번호", min_value=1, step=1, value=3)
block_input = st.number_input("블락 번호", min_value=1, step=1, value=1)

if st.button("🔍 차량 번호 찾기", use_container_width=True):
    # 다양한 포맷 대응
    target_line_full = str(line_input).zfill(3)  # "003"
    target_line_short = str(line_input)          # "3"
    target_block = str(block_input).zfill(3)     # "001"처럼 3자리 포맷까지 체크
    target_block_short = str(block_input)        # "1"

    st.info(f"📡 검색 중: 라인({target_line_full} 또는 {target_line_short}), 블락({target_block} 또는 {target_block_short})")

    try:
        r = requests.get(PROXY_URL, timeout=15)
        if b"html" in r.content.lower():
            st.error("프록시 서버 설정 오류 (HTML 응답)")
        else:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(r.content)

            found_vehicle = None
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip = entity.trip_update.trip
                    # 정확도 높은 매칭: route_id + block_id 확인
                    route_id = trip.route_id if trip.route_id else ""
                    block_id = trip.trip_id.split("_")[-1]  # trip_id 끝부분에 블락 번호 포함된 경우
                    # 라인 번호 매칭
                    if route_id in [target_line_full, target_line_short]:
                        # 블락 번호 매칭
                        if target_block in block_id or target_block_short in block_id:
                            found_vehicle = entity.trip_update.vehicle.id
                            break

            if found_vehicle:
                st.balloons()
                st.success(f"✅ 차량 번호: {found_vehicle}")
                st.markdown(f"🔗 **tcommLive (may require internal access):** [링크](https://tcommlive.translink.ca/vehicle/{found_vehicle})")
            else:
                st.info("💤 현재 운행 중인 차량이 없습니다.")
    except Exception as e:
        st.error(f"에러: {e}")
