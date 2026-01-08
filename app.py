import streamlit as st
import requests
import pandas as pd
import time

# =========================
# 설정
# =========================
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"
REQUEST_TIMEOUT = 20

st.set_page_config(
    page_title="🚌 Bus Block Finder",
    layout="centered"
)

st.title("🚌 Bus Block Finder")
st.write("Line + Block → 🚀 Find the vehicle currently in service")

# =========================
# 입력 UI
# =========================
line_number = st.text_input("Line Number", "")
block_number = st.text_input("Block Number", "")

# =========================
# 버튼
# =========================
if st.button("Find Bus"):
    if not line_number or not block_number:
        st.warning("Line Number와 Block Number를 모두 입력하세요.")
        st.stop()

    st.info(f"📡 Searching Line {line_number} / Block {block_number}...")
    time.sleep(1)

    try:
        response = requests.get(PROXY_URL, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            st.error(f"프록시 서버 오류 (status {response.status_code})")
            st.stop()

        data = response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Error: {e}")
        st.info("💡 Render 프록시 서버가 깨어있는지 확인하세요.")
        st.stop()

    # =========================
    # 데이터 파싱
    # =========================
    entities = data.get("entity", [])

    results = []

    for entity in entities:
        vehicle = entity.get("vehicle")
        if not vehicle:
            continue

        trip = vehicle.get("trip", {})
        route_id = trip.get("route_id", "")
        block_id = trip.get("block_id", "")

        if route_id == line_number and block_id == block_number:
            position = vehicle.get("position", {})
            results.append({
                "Route": route_id,
                "Block": block_id,
                "Latitude": position.get("latitude"),
                "Longitude": position.get("longitude"),
                "Vehicle ID": vehicle.get("vehicle", {}).get("id")
            })

    # =========================
    # 결과 출력
    # =========================
    if not results:
        st.warning("❌ 해당 Line / Block 조합의 버스를 찾지 못했습니다.")
    else:
        df = pd.DataFrame(results)
        st.success("✅ Bus Found!")
        st.dataframe(df)
