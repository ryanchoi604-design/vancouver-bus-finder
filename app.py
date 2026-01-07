import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2
import time

# 트랜스링크 V3 키
API_KEY = "i95CeGKk3M7wzbteE3cl"

st.set_page_config(page_title="Route Scanner V58", layout="centered")
st.title("🎯 316번 노선 전수조사 (V58)")
st.write("시스템이 24105호를 뭐라고 부르는지 직접 확인해 봅시다.")

# 입력창: 노선 번호만 받습니다. (블락 번호는 눈으로 찾기 위해 입력 안 함)
target_route = st.text_input("노선 번호 (예: 316)", "316").strip()

if st.button("이 노선의 모든 버스 가져오기 🚀"):
    # V3 실시간 위치 서버
    url = f"https://gtfsapi.translink.ca/v3/gtfsposition?apikey={API_KEY}"
    
    try:
        with st.spinner(f"📡 {target_route}번 버스들을 스캔 중..."):
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                feed = gtfs_realtime_pb2.FeedMessage()
                feed.ParseFromString(response.content)
                
                found_list = []
                
                for entity in feed.entity:
                    if entity.HasField('vehicle'):
                        v = entity.vehicle
                        r_id = v.trip.route_id
                        
                        # [핵심] 사용자가 입력한 노선 번호(316)가 Route ID에 포함되어 있는지 확인
                        # 예: 009, 009_1 등 다양할 수 있어서 포함(in) 조건 사용
                        if target_route in r_id:
                            found_list.append({
                                "차량번호": v.vehicle.id,
                                "내부TripID": v.trip.trip_id,
                                "RouteID": r_id,
                                "위치": f"{v.position.latitude:.4f}, {v.position.longitude:.4f}"
                            })
                
                if found_list:
                    st.success(f"### 🚍 {target_route}번 노선에서 {len(found_list)}대 발견!")
                    
                    # 24105호가 있는지 특별 강조
                    target_bus = next((item for item in found_list if item["차량번호"] == "24105"), None)
                    if target_bus:
                        st.markdown(f"### 🚨 **눈앞의 그 버스(24105) 찾음!**")
                        st.write(f"시스템은 이 버스의 ID를 이렇게 부르고 있습니다: **{target_bus['내부TripID']}**")
                        t_url = f"https://tcomm.bustrainferry.com/mobile/bus/24105"
                        st.markdown(f"[🔗 T-Comm에서 24105 확인하기]({t_url})")
                    else:
                        st.warning("⚠️ 리스트에 24105호가 안 보인다면, 현재 시스템상 노선 정보가 다르게 입력되어 있을 수 있습니다.")

                    # 전체 리스트 출력
                    st.table(found_list)
                else:
                    st.error(f"❌ {target_route}번으로 잡히는 버스가 하나도 없습니다. 노선 번호를 확인해 주세요.")
            else:
                st.error("❌ 서버 응답 실패")
                
    except Exception as e:
        st.error(f"📡 에러: {e}")
