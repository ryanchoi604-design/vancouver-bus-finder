import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# 🔹 Render 프록시 서버 주소 (Ryan님이 만드신 주소)
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder", page_icon="🚌")
st.title("🚌 Bus Block Finder (Proxy)")
st.write("Line + Block → 🚀 Find the vehicle currently in service")

# 입력값 받기
col1, col2 = st.columns(2)
with col1:
    # 003 처럼 문자열로 처리하기 위해 text_input 권장, number_input 쓰려면 후처리 필수
    line_input = st.number_input("Line Number", min_value=1, step=1, value=3)
with col2:
    block_input = st.number_input("Block Number", min_value=1, step=1, value=1)

if st.button("Find Bus", use_container_width=True):
    # 1. 포맷 맞추기 (3 -> "003")
    target_line = str(line_input).zfill(3) 
    target_block = str(block_input) # 블락은 일단 그대로 "1"로 둠

    st.info(f"📡 API에서 라인 [{target_line}], 블락 [{target_block}] 검색 중...")

    try:
        # Proxy 서버 호출
        r = requests.get(PROXY_URL, timeout=15) # 타임아웃 조금 늘림

        if r.status_code != 200:
            st.error(f"Proxy connection failed: {r.status_code}")
            st.stop()

        # GTFS 파싱
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)

        found = False
        
        # 디버깅용: 해당 라인의 버스가 아예 없는지 확인
        bus_count_on_line = 0

        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue
            
            vehicle = entity.vehicle
            trip = vehicle.trip
            
            api_route_id = trip.route_id
            api_block_id = trip.block_id  # 여기가 비어있을 수도 있음!
            api_vehicle_id = vehicle.vehicle.id
            
            # 라인 번호가 같은지 확인
            if api_route_id == target_line:
                bus_count_on_line += 1
                
                # 블락 번호 비교 로직 (유연하게)
                # API가 "003001"을 주고, 우리가 "1"을 찾을 때 -> "1"이 "003001" 끝에 있는지 확인
                if api_block_id and (api_block_id == target_block or api_block_id.endswith(target_block)):
                    found = True
                    
                    st.success("✅ 찾았다! (Bus found!)")
                    st.divider()
                    st.markdown(f"### 🚍 Vehicle ID: **{api_vehicle_id}**")
                    st.markdown(f"- **Route:** {api_route_id}")
                    st.markdown(f"- **Block (API):** {api_block_id}")
                    
                    # tcomm 링크
                    tcomm_link = f"https://tcomm.translink.ca/LiveMap.aspx?vehicle={api_vehicle_id}"
                    st.markdown(f"[📡 T-Comm Live Map 보기]({tcomm_link})")
                    break
        
        if not found:
            st.warning("❌ 해당 블락의 버스를 찾지 못했습니다.")
            if bus_count_on_line > 0:
                st.caption(f"참고: {target_line}번 버스는 현재 {bus_count_on_line}대가 운행 중이지만, 입력하신 블락 번호와 일치하는 차가 없습니다.")
                st.caption("💡 팁: API가 블락 정보를 안 보내주는 시간대일 수도 있습니다.")
            else:
                st.caption(f"참고: 현재 {target_line}번 라인을 운행 중인 버스가 아예 없습니다.")

    except Exception as e:
        st.error(f"Error: {e}")
