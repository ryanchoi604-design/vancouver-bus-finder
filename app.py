# app.py
import streamlit as st
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2

# 🔹 Flask 프록시 URL (Render에서 배포한 프록시 서비스)
PROXY_URL = "https://vancouver-bus-finder-1.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder", page_icon="🚌")
st.title("🚌 내 버스 찾기")
st.write("라인 + 블락 번호 입력 → 현재 운행 중인 차량 확인")

@st.cache_data
def load_static_data():
    try:
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
    target_line_full = str(line_input).zfill(3)
    target_line_short = str(line_input)
    target_block = str(block_input)

    st.info(f"📡 검색 중: 라인({target_line_full} 또는 {target_line_short}), 블락({target_block})")

    matched_df = trips_df[
        ((trips_df['route_id'] == target_line_full) | (trips_df['route_id'] == target_line_short)) &
        (trips_df['block_id'].str.contains(target_block, na=False))
    ]
    
    matched_trips = matched_df['trip_id'].tolist()

    if not matched_trips:
        st.warning("🤔 trips.txt에서 정보를 찾을 수 없습니다.")
        st.write("---")
        st.write("📂 파일 내용 확인 (도움말):")
        sample = trips_df[trips_df['route_id'].isin([target_line_full, target_line_short])].head(3)
        if not sample.empty:
            st.table(sample[['route_id', 'block_id', 'trip_id']])
        else:
            st.write("라인 번호 자체가 파일에 없는 것 같습니다.")
    else:
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
                    st.markdown(f"🔗 **tcommLive 링크 (내부 접속 필요):** [여기 클릭](https://tcomm.translink.ca/vehicle/{found_vehicle})")
                else:
                    st.info("💤 현재 운행 중인 차량이 없습니다.")
        except Exception as e:
            st.error(f"에러: {e}")
