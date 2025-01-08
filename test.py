import streamlit as st
from face import FaceRegister, FaceAuthentication
from gesture_auth import GestureAuthSystem

def main():
    st.title("얼굴 & 제스처 등록 테스트")
    
    # 사이드바 생성
    st.sidebar.title("메뉴")
    menu = st.sidebar.radio("선택하세요:", ["얼굴 등록", "제스처 등록"])
    
    if menu == "얼굴 등록":
        st.header("얼굴 등록")
        face_register = FaceRegister()
        
        if st.button("얼굴 등록 시작"):
            with st.spinner("얼굴을 등록중입니다..."):
                result = face_register.register_face()
                if result:
                    st.success("얼굴이 성공적으로 등록되었습니다!")
                else:
                    st.error("얼굴 등록에 실패했습니다. 다시 시도해주세요.")
    
    elif menu == "제스처 등록":
        st.header("제스처 등록")
        gesture_system = GestureAuthSystem()
        
        # 사용 가능한 제스처 목록 표시
        st.markdown(gesture_system.get_available_gestures())
        
        st.info("세 가지 제스처를 순서대로 등록합니다. 시작 버튼을 누르면 등록이 시작됩니다.")
        # 테스트용 임시 ID와 username 사용
        gesture_system.process_video('register', 'test_user', 'test_name')

if __name__ == "__main__":
    main()