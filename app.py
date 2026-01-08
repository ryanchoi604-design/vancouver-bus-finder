import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

# 🔹 라이언님의 프록시 주소를 여기에 바로 넣었습니다!
# 끝에 /gtfs를 붙여서 데이터 통로를 정확히 지정했습니다.
PROXY_URL = "https://vancouver-bus-finder-1.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder", page_icon="🚌")

st.title("🚌 내 버스 찾기 (Block Finder)")
st.caption("Block Number로 현재 운행 중인 차량 번호(Vehicle ID)를 찾습니다.")

# 1. trips.txt 파일 로드 함수 (캐싱으로 속도 향상)
@st.cache_data
def load_static_data():
    try:
        # 모든 ID를 문자로 읽어야 '003' 같은 형식이 유지됩니다.
        df = pd.read_csv("trips.txt", dtype=str)
        return df
    except FileNotFoundError:
        return None

# 데이터 로드 시도
trips_df = load_static_data()

if trips_df is None:
    st.error("❌ 'trips.txt' 파일이 없습니다! app.py랑 같은 폴더에 파일을 넣어주세요.")
    st.stop()
else:
    st.sidebar.success("✅ trips.txt 로드 완료")

# 2. 사용자 입력 (라인 번호, 블락 번호)
col1, col2 = st.columns(2)
with col1:
    line_input = st.number_input("라인 번호 (Line)", min_value=1, step=1, value=3)
with col2:
    block_input = st.number_input("블락 번호 (Block)", min_value=1, step=1, value=1)

# 3. 검색 버튼 클릭 시 실행
if st.button("🔍 차량 번호 찾기", use_container_width=True):
    target_line = str(line_input).zfill(3) # 3 -> 003 으로 변환
    target_block = str(block_input)
    
    st.write(f"📡 라인: {target_line}, 블락: {target_block} 검색 중...")

    # --- A. trips.txt에서 Trip ID들 찾기 ---
    # TransLink의 block_id 포맷에 대응하기 위해 'contains'를 사용합니다.
    matched_trips = trips_df[
        (trips_df['route_id'] == target_line) & 
        (trips_df['block_id'].str.contains(target_block))
    ]['trip_id'].tolist()
    
    if not matched_trips:
        st.warning(f"🤔 trips.txt에서 [{target_line}번 라인 - {target_block}번 블락] 정보를 못 찾겠어.")
    else:
        # --- B. 실시간 API (프록시 서버) 호출 ---
        try:
            # 설정하신 Render 프록시 주소로 요청을 보냅니다.
            response = requests.get(PROXY_URL, timeout=15)
            
            if response.status_code == 200:
                # 🔹 데이터가 HTML(웹페이지)인지 체크해서 에러 방지
                if b"html" in response.content.lower() or b"<!" in response.content:
                    st.error("❌ 프록시 서버에서 데이터 대신 웹페이지 화면을 보냈습니다. 프록시 서버의 'Start Command'가 'python proxy_server.py'인지 다시 확인해주세요.")
                    st.stop()

                # GTFS 데이터 파싱
                feed = gtfs_realtime_pb2.FeedMessage()
                feed.ParseFromString(response.content)
                
                found_vehicle = None
                
                # 실시간 데이터를 돌며 매칭되는 Trip ID 확인
                for entity in feed.entity:
                    if entity.HasField('trip_update'):
                        current_trip_id = entity.trip_update.trip.trip_id
                        
                        if current_trip_id in matched_trips:
                            if entity.trip_update.vehicle.id:
                                found_vehicle = entity.trip_update.vehicle.id
                                break
                
                # 결과 출력
                if found_vehicle:
                    st.balloons()
                    st.markdown(f"## 🚍 찾았다! 차량 번호: **{found_vehicle}**")
                    st.success(f"오늘 안전운전 해, Ryan! 👋")
                    st.markdown(f"[📡 T-Comm Live Map에서 보기](https://tcomm.translink.ca/LiveMap.aspx?vehicle={found_vehicle})")
                else:
                    st.info("💤 현재 해당 블락으로 운행 중인 차량이 보이지 않아. (차고지에 있거나 아직 출발 전일 수 있어)")
            
            else:
                st.error(f"📡 프록시 서버 접속 실패! (상태 코드: {response.status_code})")
                
        except Exception as e:
            st.error(f"에러 발생: {e}")
