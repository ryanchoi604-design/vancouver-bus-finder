import streamlit as st
import requests
from google.transit import gtfs_realtime_pb2

# 🔹 Render 프록시 서버 주소
PROXY_URL = "https://vancouver-bus-finder.onrender.com/gtfs"

st.set_page_config(page_title="Bus Block Finder")
st.title("🚌 Bus Block Finder")
st.write("Line + Block → 🚀 Find the vehicle currently in service")

line = st.number_input("Line Number", min_value=1, step=1)
block = st.number_input("Block Number", min_value=1, step=1)

if st.button("Find Bus"):
    st.info(f"📡 Searching Line {line} / Block {block}...")

    try:
        r = requests.get(PROXY_URL, timeout=10)

        if r.status_code != 200:
            st.error(f"Proxy error: status {r.status_code}")
            st.stop()

        # 🔹 GTFS Realtime 파싱
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)

        found = False

        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue

            vehicle = entity.vehicle
            trip = vehicle.trip

            route_id = trip.route_id
            block_id = trip.block_id
            vehicle_id = vehicle.vehicle.id

            if route_id == str(line) and block_id == str(block):
                found = True

                st.success("✅ Bus found!")

                st.markdown(f"🚌 **Route:** {route_id}")
                st.markdown(f"📦 **Block:** {block_id}")
                st.markdown(f"🔢 **Vehicle ID:** `{vehicle_id}`")

                # 🔗 tcommLive 링크 (내부망일 수 있음)
                tcomm_link = f"https://tcomm.translink.ca/LiveMap.aspx?vehicle={vehicle_id}"

                st.markdown(
                    f"🔗 **tcommLive (may require internal access):** "
                    f"[Open link]({tcomm_link})"
                )

                break

        if not found:
            st.warning("❌ No matching bus found for this Line / Block.")

    except Exception as e:
        st.error(f"Error: {e}")
