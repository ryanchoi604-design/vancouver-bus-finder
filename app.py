# app.py 수정 버전 (검색 로직 강화)
import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

PROXY_URL = "https://vancouver-bus-finder-1.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder", page_icon="🚌")
st.title("🚌 내 버스 찾기")

@st.cache_data
def load_static_data():
    try:
        # 파일을 읽을 때 모든 데이터를 문자로 읽고 앞뒤 공백을 제거합니다.
        df = pd.read_csv("trips.txt", dtype=str)
        df['route_id'] = df['route_id'].str.strip()
        df['block_id'] = df['block_id'].str.strip()
        return df
    except Exception as e:
        st.error(f"파일 로드 에러: {e}")
        return None

trips_df = load_static_data()

line_input = st.number_input("라인 번호", min_value=1, step=1, value=3)
block_input = st.number_input("블락 번호", min_value=1, step=1, value=1)

if st.button("🔍 차량 번호 찾기", use_container_width=True):
    # 🔹 다양한 포맷 대응 (003 과 3 둘 다 준비)
    target_line_full = str(line_input).zfill(3) # "003"
    target_line_short = str(line_input)         # "3"
    target_block = str(block_input)             # "1"
    
    st.info(f"📡 검색 중: 라인({target_line_full} 또는 {target_line_short}), 블락({target_block})")

    # 🔹 검색 로직: 라인 번호가 003이거나 3인 것 중에서, 블락 번호에 1이 포함된 것을 찾음
    matched_df = trips_df[
        ((trips_df['route_id'] == target_line_full) | (trips_df['route_id'] == target_line_short)) & 
        (trips_df['block_id'].str.contains(target_block, na=False))
    ]
    
    matched_trips = matched_df['trip_id'].tolist()
    
    if not matched_trips:
        st.warning(f"🤔 trips.txt에서 정보를 찾을 수 없습니다.")
        
        # 💡 [디버깅 도우미] 실제로 파일에 어떻게 적혀 있는지 샘플을 보여줍니다.
        st.write("---")
        st.write("📂 **파일 내용 확인 (도움말):**")
        st.write(f"현재 파일의 '{target_line_short}'번 라인 근처 데이터는 이렇게 생겼어요:")
        sample = trips_df[trips_df['route_id'].isin([target_line_full, target_line_short])].head(3)
        if not sample.empty:
            st.table(sample[['route_id', 'block_id', 'trip_id']])
            st.write("위 표의 **block_id** 형식을 확인하고 검색해보세요!")
        else:
            st.write("파일에 이 라인 번호 자체가 없는 것 같아요. trips.txt가 최신 버전인지 확인해주세요.")
    
    else:
        # --- (이후 실시간 API 호출 로직은 동일) ---
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
                        if entity.trip_update.trip.trip_id in matched_trips:
                            found_vehicle = entity.trip_update.vehicle.id
                            break
                
                if found_vehicle:
                    st.balloons()
                    st.success(f"✅ 차량 번호: {found_vehicle}")
                else:
                    st.info("💤 현재 운행 중인 차량이 없습니다.")
        except Exception as e:
            st.error(f"에러: {e}")
