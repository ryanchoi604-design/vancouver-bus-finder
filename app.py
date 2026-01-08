# app.py
import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

# 🔹 렌더 프록시 서버 주소 (주소가 다르면 이 부분만 수정하세요)
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder", page_icon="🚌")
st.title("🚌 Bus Block Finder")
st.write("라인과 블락 번호를 입력해 현재 운행 중인 차량 번호를 찾으세요.")

# 🔹 1. trips.txt 데이터 로드
@st.cache_data
def load_trips():
    try:
        # ID가 숫자로 변환되어 '0'이 사라지는 것을 방지합니다.
        return pd.read_csv("trips.txt", dtype=str)
    except FileNotFoundError:
        st.error("❌ 'trips.txt' 파일이 같은 폴더에 있는지 확인해주세요!")
        return None

trips_df = load_trips()

# 🔹 2. 사용자 입력
col1, col2 = st.columns(2)
with col1:
    line_input = st.number_input("Line Number", min_value=1, step=1, value=3)
with col2:
    block_input = st.number_input("Block Number", min_value=1, step=1, value=1)

if st.button("Find Bus", use_container_width=True):
    target_line = str(line_input).zfill(3) # 3 -> 003 포맷팅
    target_block = str(block_input)
    
    st.info(f"📡 {target_line}번 라인 {target_block}번 블락 찾는 중...")

    if trips_df is not None:
        # trips.txt에서 해당 블락의 모든 Trip ID를 찾습니다.
        matched_trips = trips_df[
            (trips_df['route_id'] == target_line) & 
            (trips_df['block_id'].str.contains(target_block))
        ]['trip_id'].tolist()
        
        if not matched_trips:
            st.warning(f"🤔 trips.txt에서 [{target_line}-{target_block}] 정보를 찾을 수 없습니다.")
        else:
            try:
                # 프록시 서버(Render 프로젝트 A) 호출
                r = requests.get(PROXY_URL, timeout=15)
                
                # HTML이 응답되었는지 체크 (에러 방지)
                if b"html" in r.content.lower() or b"<!" in r.content:
                    st.error("❌ 프록시 서버가 데이터 대신 웹페이지를 보냈습니다. Render 설정을 확인하세요.")
                    st.stop()

                # GTFS 데이터 해독
                feed = gtfs_realtime_pb2.FeedMessage()
                feed.ParseFromString(r.content)
                
                found_bus = None
                for entity in feed.entity:
                    if entity.HasField('trip_update'):
                        trip_id = entity.trip_update.trip.trip_id
                        if trip_id in matched_trips:
                            if entity.trip_update.vehicle.id:
                                found_bus = entity.trip_update.vehicle.id
                                break
                
                if found_bus:
                    st.balloons()
                    st.success(f"✅ 차량 번호를 찾았습니다: {found_bus}")
                    st.markdown(f"🔗 [T-Comm Live Map에서 보기](https://tcomm.translink.ca/LiveMap.aspx?vehicle={found_bus})")
                else:
                    st.info("💤 현재 해당 블락으로 운행 중인 차량이 없습니다.")
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
