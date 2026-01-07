import streamlit as st
import requests

# 트랜스링크 API 키
API_KEY = "i95CeGKk3M7wzbteE3cl"

st.set_page_config(page_title="Ryan's One-Shot Sniper", layout="centered")

# 화면 구성은 최대한 심플하게
st.title("🎯 버스 번호 저격기 (Final)")
st.write("노선과 블락만 넣으세요. 자동차 번호만 딱 찾아드립니다.")

# 입력창
in_route = st.text_input("1. 노선 번호 (Route)", "25").strip()
in_block = st.text_input("2. 블락 번호 (Block)", "42").strip()

if st.button("지금 버스 번호 찾기 🚀"):
    # 온라인 서버에서는 이 주소가 가장 정확하고 빠릅니다.
    url = f"https://api.translink.ca/rttiapi/v1/buses?apikey={API_KEY}&routeNo={in_route}"
    headers = {'Accept': 'application/json'}
    
    try:
        with st.spinner("📡 실시간 데이터 조회 중..."):
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                buses = response.json()
                found_vid = None
                
                # 배차표 블락(BlockNo)과 실시간 데이터 매칭
                for bus in buses:
                    if str(bus['BlockNo']).lstrip('0') == in_block.lstrip('0'):
                        found_vid = bus['VehicleNo']
                        break
                
                if found_vid:
                    st.success(f"### 찾았습니다! {in_route}번-{in_block}블락")
                    # 버스 번호를 제일 크게!
                    st.markdown(f"<h1 style='text-align: center; color: #FF4B4B; font-size: 100px;'>{found_vid}</h1>", unsafe_allow_html=True)
                    
                    # T-Comm Live 직행 링크
                    t_comm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{found_vid}"
                    st.markdown(f"### [🔗 {found_vid}호 T-Comm 위치 확인하기]({t_comm_url})")
                else:
                    st.warning(f"⚠️ {in_route}번 {in_block}블락은 지금 신호가 없습니다.")
            else:
                st.error("❌ 트랜스링크 서버에 문제가 있네요. 노선 번호를 확인해 주세요.")
                
    except Exception as e:
        # 온라인에서는 아까 같은 DNS 에러가 거의 안 날 겁니다.
        st.error(f"📡 연결 실패! 서버 상태를 확인해 주세요. ({e})")
