import streamlit as st
import time
from face import FaceAuthentication, FaceRegister
from gesture_auth import GestureAuthSystem
# Streamlit 세션 상태에서 현재 페이지를 추적하기 위한 초기 설정
if 'page' not in st.session_state:
    st.session_state['page'] = 'main'


users = {}
# 다른 페이지로 이동하는 함수
def navigate_to(page):
    st.session_state['page'] = page
    st.rerun()

# 메인 페이지 내용 정의
def main_page():
    st.title('DeepGuard')
    username = st.text_input("사용자 이름")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        navigate_to('face_auth')
        #if username in users and users[username] == password:
         #   st.success("로그인 성공!")
            # 로그인 성공 후 처리할 내용
        #else:
         #   st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
    if st.button('회원가입'):
        navigate_to('signup')

# 서브 페이지 내용 정의
def signup_page():
    st.title('회원가입')
    new_username = st.text_input("새로운 사용자 이름")
    new_password = st.text_input("새로운 비밀번호", type="password")
    if st.button("다음"):
        if new_username not in users:
            users[new_username] = new_password
            navigate_to('face_registration')
        else:
            st.error("이미 존재하는 아이디입니다.")
    if st.button('메인 페이지로 돌아가기'):
        navigate_to('main')

def face_registration_page() :
    st.header("얼굴 등록")
    face_register = FaceRegister()
        
    if st.button("얼굴 등록 시작"):
        with st.spinner("얼굴을 등록중입니다..."):
            result = face_register.register_face()
            if result:
                st.success("얼굴이 성공적으로 등록되었습니다!")
    if st.button("다음"):
        navigate_to('gesture_registration')
            #else:
             #   st.error("얼굴 등록에 실패했습니다. 다시 시도해주세요.")

def gesture_registration_page() :
    st.header("제스처 등록")
    gesture_system = GestureAuthSystem()
        
    # 사용 가능한 제스처 목록 표시
    st.markdown(gesture_system.get_available_gestures())
        
    st.info("세 가지 제스처를 순서대로 등록합니다. 시작 버튼을 누르면 등록이 시작됩니다.")
    # 테스트용 임시 ID와 username 사용
    gesture_system.process_video('register', 'test_user', 'test_name')

    if st.button("회원가입"):
        navigate_to('main')


def face_auth_page() :
    st.header("얼굴 인증")
    face_authen = FaceAuthentication()
        
    if st.button("얼굴 인증 시작"):
        with st.spinner("얼굴을 인식중입니다..."):
            result = face_authen.authenticate_face()
          
    if st.button("다음"):
        navigate_to('gesture_auth')
            #else:
             #   st.error("얼굴 등록에 실패했습니다. 다시 시도해주세요.")

def gesture_auth_page() :
    st.header("제스처 등록")
    gesture_system = GestureAuthSystem()
    
    # 사용 가능한 제스처 목록 표시
    st.markdown(gesture_system.get_available_gestures())
        
    st.info("세 가지 제스처를 순서대로 등록합니다. 시작 버튼을 누르면 등록이 시작됩니다.")
    # 테스트용 임시 ID와 username 사용
    gesture_system.process_video('register', 'test_user', 'test_name')
    
    if st.button("인증"):

        navigate_to('main')


# 페이지 네비게이션 로직
if st.session_state['page'] == 'main':
    main_page()
elif st.session_state['page'] == 'signup':
    signup_page()
elif st.session_state['page'] == 'face_registration':
    face_registration_page()
elif st.session_state['page'] == 'gesture_registration':
    gesture_registration_page()
elif st.session_state['page'] == 'face_auth':
    face_auth_page()
elif st.session_state['page'] == 'gesture_auth':
    gesture_auth_page()
