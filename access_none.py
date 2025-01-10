import streamlit as st
from gesture_access import GestureAuthSystem

# 스트림릿 페이지 설정
st.set_page_config(page_title="제스처 기반 파일 액세스 시스템", layout="centered")

st.title("🖼️ 제스처 기반 파일 액세스 시스템")

# 제스처 인증 시스템 초기화
auth_system = GestureAuthSystem()

# 파일 데이터 설정
file_data = [
    {"image": "Freepik_folderlock.png", "name": "기밀문서.docx"}, 
]

# 세션 상태 초기화
if "active_process" not in st.session_state:
    st.session_state.active_process = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False

cols = st.columns(len(file_data))  # 파일 개수에 맞게 열 생성

for i, data in enumerate(file_data):
    with cols[i]:
        try:
            # 이미지 표시
            st.image(data["image"], width=120)
            
            # 버튼 클릭 시 제스처 인증 시작
            if st.button(f'{data["name"]}', key=data["name"]):
                st.session_state.active_process = data["name"]
                st.session_state.is_running = True
        
        except Exception as e:
            st.error(f"이미지를 로드하는 중 오류가 발생했습니다: {e}")

# 인증 프로세스 시작
if st.session_state.active_process and st.session_state.is_running:
    st.write(f"선택된 파일: {st.session_state.active_process}")
    auth_system.process_video('verify', st.session_state.active_process)
