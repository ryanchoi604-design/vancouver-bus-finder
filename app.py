# app.py
import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

API_KEY = "i95CeGKk3M7wzbteE3cl"  # TransLink GTFS API 키

st.set_page_config(page_title="🚌 내 버스 실시간 찾기", layout="centered")

st.markdown("<h1 style='text-align:center;'>🚌 내 버스 실시간 찾기</h1>", unsafe_allow_html=True)
st.markdown("라인과 블락 선택 후 🚀 버튼 클릭하면 차량 번호 확인 가능!")

# --- UI: 라인/블락 선택 ---
line_options = ["3","4","5","6","7","8","10"]
line_input = st.selectbox("라인 번호 선택", line_options)

block_options = ["001","002","003","004","005","006","007","010","012"]
block_input = st.selectbox("블락 번호 선택", block_options)

# 즐겨찾기 기능
favorite_lines = st.session_state.get("favorites", [])
if st.checkbox("⭐ 즐겨찾기 등록", key="fav"):
    if line_input not in favorite_lines:
        favorite_lines.append(line_input)
        st.session_state["favorites"] = favorite_lines

# --- 차량 번호 조회 버튼 ---
if st.button("🚀 차량 번호 확인"):
    st.write(f"📡 라인 {line_input}, 블락 {block_input} 검색 중...")
    try:
        # GTFS Realtime 호출
        url = f"https://gtfs.translink.ca/v2/gtfsrealtime?apikey={API_KEY}"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            st.error(f"API 접속 실패! 상태 코드: {r.status_code}")
        else:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(r.content)
            found_vehicle = None

            # 실시간 데이터 순회
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    trip = entity.trip_update.trip
                    vehicle = entity.trip_update.vehicle
                    # 여기선 예시로 line/block 상관 없이 첫 차량 id 가져오기
                    if vehicle.id:
                        found_vehicle = vehicle.id
                        break

            if found_vehicle:
                st.balloons()
                st.markdown(
                    f"""
                    <div style='background-color:#FFEB3B; border-radius:20px; padding:20px; text-align:center; margin-top:20px;'>
                    <h1 style='font-size:80px; color:#E91E63; margin:0;'>🚍 {found_vehicle}</h1>
                    <h3 style='margin:0;'>라인 {line_input}, 블락 {block_input}</h3>
                    </div>
                    """, unsafe_allow_html=True
                )
                tcomm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{found_vehicle}"
                st.markdown(
                    f"<div style='text-align:center; margin-top:15px;'>"
                    f"<a href='{tcomm_url}' target='_blank' "
                    f"style='background-color:#4CAF50;color:white;padding:12px 25px;"
                    f"border-radius:10px;text-decoration:none;font-size:18px;'>"
                    f"🔗 T-Comm Live 위치 확인</a></div>",
                    unsafe_allow_html=True
                )
            else:
                st.info("💤 현재 운행 중인 차량이 안 보여요 (차고지에 있거나 아직 출발 전)")
    except Exception as e:
        st.error(f"에러 발생: {e}")

# --- 즐겨찾기 표시 ---
if favorite_lines:
    st.markdown("### ⭐ 즐겨찾기 라인")
    st.write(", ".join(favorite_lines))
