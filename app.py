import streamlit as st
import requests

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
        r = requests.get(PROXY_URL, timeout=10)
        if r.status_code == 200:
            st.success("Bus data downloaded successfully!")
            # 여기서 GTFS 데이터 파싱해서 실제 버스 위치 찾는 로직 추가 가능
            st.download_button("Download GTFS data", r.content, file_name="gtfs.pb")
        else:
            st.error(f"Proxy server error: status {r.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Network or proxy error: {e}")
