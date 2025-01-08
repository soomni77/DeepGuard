import streamlit as st
from gesture_auth import GestureAuthSystem

def main():
    st.set_page_config(
        page_title="제스처 인증 시스템",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("제스처 인증 시스템")

    # 사용 가능한 제스처 목록 표시
    st.sidebar.markdown(GestureAuthSystem.get_available_gestures())

    auth_system = GestureAuthSystem()
    menu = st.sidebar.selectbox("메뉴", ["제스처 등록", "사용자 인증"])

    if menu == "제스처 등록":
        st.header("제스처 등록")
        col1, col2 = st.columns([3, 1])
        with col1:
            user_id = st.text_input("사용자 ID를 입력하세요")
            if user_id:
                if st.button("ID 중복 확인"):
                    if auth_system.check_id_availability(user_id):
                        st.success("사용 가능한 ID입니다.")
                    else:
                        st.error("중복된 ID입니다.")

            username = st.text_input("사용자 이름을 입력하세요")
            if user_id and username:
                if st.button("제스처 등록 시작"):
                    auth_system.process_video('register', user_id, username)

        with col2:
            st.markdown("""
            ### 사용 방법
            1. 사용자 ID와 이름을 입력하세요.
            2. 'ID 중복 확인' 버튼으로 ID를 확인하세요.
            3. '제스처 등록 시작' 버튼으로 등록을 시작하세요.
            4. 3초 카운트다운 후, 각 제스처를 3초씩 유지하며 등록합니다.
            """)

    elif menu == "사용자 인증":
        st.header("사용자 인증")
        col1, col2 = st.columns([3, 1])
        with col1:
            user_id = st.text_input("사용자 ID를 입력하세요")
            if user_id:
                if st.button("인증 시작"):
                    auth_system.process_video('verify', user_id)

        with col2:
            st.markdown("""
            ### 사용 방법
            1. 사용자 ID를 입력하세요.
            2. '인증 시작' 버튼으로 인증을 시작하세요.
            3. 3초 카운트다운 후, 등록된 순서대로 각 제스처를 3초씩 인증합니다.
            """)

if __name__ == "__main__":
    main()
