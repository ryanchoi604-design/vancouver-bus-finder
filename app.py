import streamlit as st
from PIL import Image, ImageEnhance
import os

# ===========================
st.set_page_config(page_title="🚌 내 버스 찾기 (Fun V3)", layout="centered")
st.markdown(
    "<h1 style='text-align:center;'>🚌 내 버스 찾기 (모바일 최적화!)</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;'>라인 선택 → 블락 선택 → 차량 번호 확인 → T-Comm Live 클릭!</p>",
    unsafe_allow_html=True
)

# ------------------------
# 배경 이미지 흐림 처리
if os.path.exists("bus_bg.jpg"):
    bg = Image.open("bus_bg.jpg")
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.6)  # 조금 어둡게
    st.image(bg, use_column_width=True)

# ------------------------
# 차량 번호 데이터
vehicle_map = {
    "3": {"1": "V1234", "2": "V1235", "10": "V1240"},
    "10": {"1": "V2001", "2": "V2002", "5": "V2005"},
    "6": {"1": "V3001", "7": "V3007"}
}

# ------------------------
# 즐겨찾기
st.sidebar.header("⭐ 즐겨찾기 노선")
if "favorites" not in st.session_state:
    st.session_state.favorites = []

new_fav = st.sidebar.selectbox("즐겨찾기 라인 추가", options=list(vehicle_map.keys()))
if st.sidebar.button("➕ 즐겨찾기 추가") and new_fav:
    if new_fav not in st.session_state.favorites:
        st.session_state.favorites.append(new_fav)
        st.sidebar.success(f"라인 {new_fav} 추가됨!")
    else:
        st.sidebar.info("이미 즐겨찾기 등록됨")

if st.session_state.favorites:
    st.sidebar.write("현재 즐겨찾기:", ", ".join(st.session_state.favorites))

# ------------------------
# 라인/블락 드롭다운
line_input = st.selectbox("라인 번호 선택", options=list(vehicle_map.keys()))
block_input = st.selectbox("블락 번호 선택", options=list(vehicle_map[line_input].keys()))

# ------------------------
if st.button("🎯 차량 번호 찾기"):

    vehicle = vehicle_map.get(line_input, {}).get(block_input)

    if vehicle:
        # 초대형 차량 번호 + 컬러풀 카드 스타일
        st.markdown(
            f"""
            <div style='background-color:#FFEB3B; border-radius:20px; padding:30px; text-align:center; margin-top:20px;'>
            <h1 style='font-size:80px; color:#E91E63; margin:0;'>🚍 {vehicle}</h1>
            <h3 style='margin:0;'>라인 {line_input}, 블락 {block_input}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # T-Comm 버튼
        tcomm_url = f"https://tcomm.bustrainferry.com/mobile/bus/{vehicle}"
        st.markdown(
            f"""
            <div style='text-align:center; margin-top:20px;'>
            <a href='{tcomm_url}' target='_blank' 
            style='background-color:#4CAF50;color:white;padding:15px 30px;border-radius:10px;text-decoration:none;font-size:18px;'>
            🔗 T-Comm Live에서 실시간 위치 확인
            </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning(f"⚠️ 라인 {line_input}, 블락 {block_input}의 차량 번호를 찾을 수 없음")
        st.caption("💡 아직 데이터가 업데이트되지 않았을 수 있음. 관리자에게 문의하세요.")
