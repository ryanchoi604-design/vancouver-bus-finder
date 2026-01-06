import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

# 트랜스링크 API 키
API_KEY = "i95CeGKk3M7wzbteE3cl"

st.set_page_config(page_title="Juho's Bus Tracker", layout="wide")
st.title("🎯 실시간 블락 저격기 (V30)")

# 1. 파일 로드 함수
@st.cache_resource
def load_data():
    try:
        # 깃허브에 올린 파일들을 읽어옵니다.
        trips = pd.read_csv("trips.txt", dtype=str)
        routes = pd.read_csv("routes.txt", dtype=str)
        # 공백 제거 등 데이터 정리
        trips['trip_id'] = trips['trip_id'].str.strip()
        trips['block_id'] = trips['block_id'].str.strip()
        routes['route_short_name'] = routes['route_short_name'].str.strip()
        routes['route_id'] = routes['route_id'].str.strip()
        return trips, routes
    except Exception as e:
        st.error(f"❌ 파일을 찾을 수 없습니다: {e}")
        return None, None

trips_db, routes_db = load_data()

# 2. 사이드바 입력창
with st.sidebar:
    st.header("🔍 검색 설정")
    in_route = st.text_input("노선 번호 (예: 301, 25)", "301").strip()
    in_block = st.text_input("블락 번호 (예: 4, 17)", "4").strip()

# 3. 찾기 버튼
if st.button("내 버스 실시간 확인 🚀"):
    if trips_db is not None:
        with st.spinner("📡 데이터를 분석 중입니다..."):
            # 노선 ID 확인
            route_match = routes_db[routes_db['route_short_name'] == in_route]
            if route_match.empty:
                # 0을 붙여서 재시도 (예: 25 -> 025)
                route_match = routes_db[routes_db['route_short_name'] == in_route.zfill(3)]
            
            if route_match.empty:
                st.error(f"❌ '{in_route}' 노선을 찾을 수 없습니다.")
            else:
                r_id = route_match.iloc[0]['route_id']
                
                # 실시간 API 호출
                tu_url = f"https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey={API_KEY}"
                pos_url = f"https://gtfsapi.translink.ca/v3/gtfsposition?apikey={API_KEY}"
                
                tu_resp = requests.get(tu_url)
                pos_resp = requests.get(pos_url)
                
                tu_feed = gtfs_realtime_pb2.FeedMessage()
                tu_feed.ParseFromString(tu_resp.content)
                pos_feed = gtfs_realtime_pb2.FeedMessage()
                pos_feed.ParseFromString(pos_resp.content)

                found_bus = None
                # 기계식 블락 ID 매칭 로직
                for entity in tu_feed.entity:
                    if entity.HasField('trip_update'):
                        tu = entity.trip_update
                        if tu.trip.route_id == r_id:
                            match = trips_db[trips_db['trip_id'] == tu.trip.trip_id]
                            if not match.empty:
                                b_id = match.iloc[0]['block_id']
                                # 입력한 블락 번호가 시스템 ID에 포함되는지 확인
                                if in_block in b_id:
                                    found_bus = {"vid": tu.vehicle.id, "b_id": b_id}
                                    break

                if found_bus:
                    # 위치 정보 표시
                    for entity in pos_feed.entity:
                        if entity.HasField('vehicle') and entity.vehicle.vehicle.id == found_bus['vid']:
                            st.success(f"✅ 블락 {in_block}번 차량(차번: {found_bus['vid']})을 찾았습니다!")
                            map_df = pd.DataFrame([{"lat": entity.vehicle.position.latitude, "lon": entity.vehicle.position.longitude}])
                            st.map(map_df, zoom=14)
                            st.info(f"시스템 블락 ID: {found_bus['b_id']}")
                            st.markdown(f"### [👉 T-Comm에서 확인](https://tcomm.bustrainferry.com/mobile/bus/{found_bus['vid']})")
                            break
                else:
                    st.error(f"❌ 현재 {in_route}번의 {in_block} 블락은 운행 중이 아닙니다.")
