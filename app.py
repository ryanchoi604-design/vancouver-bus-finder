# app.py
import streamlit as st

# ================================
# Page 설정
st.set_page_config(
    page_title="🚌 Bus Block Finder",
    page_icon="🚌",
    layout="centered"
)

# 배경 + 타이틀
st.markdown("""
<div style="text-align:center; background-color:#f0f2f6; padding:20px; border-radius:15px;">
    <h1>🚌 Bus Block Finder</h1>
    <p>Line + Block → 🚀 Current Vehicle ID (check T-Comm Live for location)</p>
</div>
""", unsafe_allow_html=True)

# 예시 데이터 (버스 번호는 임의)
LINE_BLOCKS = {
    "3": {"1": "V1234", "2": "V1235", "10": "V1240", "12": "V1242"},
    "4": {"1": "V1301", "3": "V1303", "5": "V1305"},
    "5": {"1": "V1401", "2": "V1402", "4": "V1404"},
    "6": {"1": "V3001", "2": "V3002", "7": "V3007"},
    "7": {"1": "V3101", "2": "V3102", "6": "V3106"},
    "8": {"2": "V3202", "5": "V3205", "8": "V3208"},
    "10": {"1": "V2001", "2": "V2002", "5": "V2005", "10": "V2010"}
}

# --------------------------
# Line / Block 선택
col1, col2 = st.columns(2)
with col1:
    line = st.selectbox("Line", options=list(LINE_BLOCKS.keys()))
with col2:
    block = st.selectbox("Block", options=list(LINE_BLOCKS.get(line, {}).keys()))

# --------------------------
# Search 버튼 클릭
if st.button("🚀 Find Vehicle"):
    vehicle_id = LINE_BLOCKS.get(line, {}).get(block)
    if vehicle_id:
        st.success(f"🚍 Vehicle ID: {vehicle_id}")
        st.markdown(f"[🔗 Check location on T-Comm Live](https://tcomm.bustrainferry.com/mobile/bus/{vehicle_id})")
    else:
        st.warning("💤 No vehicle found. Maybe it's still at the depot or not started yet.")
