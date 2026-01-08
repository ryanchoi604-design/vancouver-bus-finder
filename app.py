import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# Render 프록시 서버 주소
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder")
st.title("🚌 Bus Block Finder")
st.write("Line + Block → 🚀 Find the vehicle currently in service")

line = st.number_input("Line Number", min_value=1, step=1)
block = st.number_input("Block Number", min_value=1, step=1)

if st.button("Find Bus"):
    st.info(f"📡 Searching Line {line} / Block {block}...")

    try:
        r = requests.get(PROXY_URL, timeout=15)

        if r.status_code != 200:
            st.error(f"Proxy server error: status {r.status_code}")
            st.stop()

        # 🔹 GTFS Realtime 파싱
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)

        found = False

        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue

            vehicle = entity.vehicle

            if not vehicle.trip:
                continue

            route_id = vehicle.trip.route_id
            block_id = vehicle.trip.block_id
            vehicle_id = vehicle.vehicle.id if vehicle.vehicle.id else "Unknown"

            # 문자열/숫자 혼용 대비
            if str(route_id) == str(line) and str(block_id) == str(block):
                found = True
                st.success("✅ Bus found!")
                st.write(f"🚌 **Bus ID:** `{vehicle_id}`")
                st.write(f"🛣️ Route: {route_id}")
                st.write(f"📦 Block: {block_id}")

                # ⚠️ 추측: 외부에서 열릴 수도, 안 열릴 수도 있음
                tcomm_url = f"https://tcomm.translink.ca/LiveMap?vehicle={vehicle_id}"
                st.markdown(f"🔗 **tcommLive (may require internal access):**  
                [{tcomm_url}]({tcomm_url})")

                break

        if not found:
            st.warning("❌ No active bus found for this Line / Block.")

    except Exception as e:
        st.error(f"Error parsing GTFS data: {e}")
