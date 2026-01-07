import streamlit as st
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

# 트랜스링크 공식 API 키
API_KEY = "i95CeGKk3M7wzbteE3cl"

st.set_page_config(page_title="Pro Vehicle Sniper", layout="centered")
st.title("🎯 Pro 버전: 차량 번호 저격기 (V56)")

# 입력
in_route = st.text_input("1. 노선 번호 (예: 25)", "25").strip()
in_block = st.text_input("2. 블락 번호 (예: 42)", "42").strip()

if st.button("지금 이 버스 번호 저격 🚀"):

    url = f"https://api.translink.ca/rttiapi/v1/buses?apikey={API_KEY}&routeNo={in_route}"
    headers = {"Accept": "application/json"}

    try:
        with st.spinner("📡 트랜스링크 서버에서 실시간 데이터 조회 중..."):
            response = requests.get(url, headers=headers, timeout=10)

        # --- 서버 응답은 왔는데 에러인 경우 ---
        if response.status_code != 200:
            st.error(f"❌ 트랜스링크 서버 오류 (HTTP {response.status_code})")
            st.info("💡 서버가 일시적으로 응답하지 않을 수 있습니다. 잠시 후 다시 시도해 보세요.")
            st.stop()

        buses = response.json()
        found_vid = None

        for bus in buses:
            if str(bus.get("BlockNo", "")).lstrip("0") == in_block.lstrip("0"):
                found_vid = bus.get("VehicleNo")
                break

        if found_vid:
            st.success(f"### 찾았습니다! {in_route}번 {in_block}블락")
            st.markdown(
                f"<h1 style='text-align:center;color:#FF4B4B;font-size:100px;'>{found_vid}</h1>",
                unsafe_allow_html=True
            )

            t_comm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{found_vid}"
            st.markdown(f"### [🔗 {found_vid}호 T-Comm Live 보기]({t_comm_url})")

        else:
            st.warning(f"⚠️ {in_route}번 {in_block}블락은 현재 운행 중이 아닙니다.")

    # --- 네트워크 예외들 ---
    except Timeout:
        st.error("⏱️ 서버 응답 시간이 초과되었습니다.")
        st.info("💡 트랜스링크 서버가 느리거나 네트워크 상태가 불안정합니다.")

    except ConnectionError:
        st.error("📡 서버에 연결할 수 없습니다.")
        st.info("💡 VPN, 회사 와이파이, 방화벽을 확인해 주세요. 휴대폰 핫스팟 테스트가 가장 빠릅니다.")

    except RequestException as e:
        st.error("❌ 알 수 없는 네트워크 오류 발생")
        st.code(str(e))

    except Exception as e:
        st.error("❌ 예상치 못한 오류 발생")
        st.code(str(e))
