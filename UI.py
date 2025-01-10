import streamlit as st
from face import FaceAuthentication, FaceRegister
from gesture_auth import GestureAuthSystem
import sqlite3
import os
import base64

# 로고 경로 설정
logo_path = "logo.png"

# 로고 이미지를 Base64로 변환하는 함수
def get_base64_image(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# 로고를 Base64로 변환
logo_base64 = get_base64_image(logo_path)

# 얼굴 등록 디렉토리 설정
REGISTERED_FACES_DIR = 'registered_faces'

# 디렉토리가 존재하지 않으면 생성
if not os.path.exists(REGISTERED_FACES_DIR):
    os.makedirs(REGISTERED_FACES_DIR)

if 'page' not in st.session_state:
    st.session_state['page'] = 'main'
if 'id_checked' not in st.session_state:
    st.session_state['id_checked'] = False

# SQLite 연결 함수
def get_db_connection():
    try:
        db_path = os.path.abspath("./gesture_auth.db")
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류 발생: {str(e)}")
        return None

def navigate_to(page):
    st.session_state['page'] = page
    st.query_params['page']=page

def check_user_exists(user_id):
    """데이터베이스에서 사용자 ID 존재 여부 확인"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        st.error(f"데이터베이스 확인 중 오류 발생: {str(e)}")
        return False

# CSS 스타일 추가
def add_custom_css():
    st.markdown(
        """
        <style>
        .header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .header-container img {
            width: 250px;
            height: auto;
        }
        .tab-container {
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #031227;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 8px;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #183b56;
        }
        .main-text {
            font-size: 28px;
            font-weight: bold;
            margin-top: 20px;
            text-align: center;
        }
        .deepguard-title {
            padding: 20px 150px;
            border-radius: 10px;
            display: inline-block;
            text-align: center;
            margin: 0 auto;
        }
        .description-text {
            font-weight: bold;
            font-size: 15px;
            text-align: center;
            line-height: 1.6;
            margin-top: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# 메인 페이지
def main_page():
    st.markdown(
        f"""
        <div class="main-text">
            <h1 class="deepguard-title">DeepGuard</h1>
            🔒DeepGuard - 2단계 생체인증 시스템🔒
        </div>
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo">
        </div>
        <div class="description-text">
            - DeepGuard는 얼굴 인식과 제스처 인식을 결합한 2단계 생체인증 시스템입니다.<br>
            - 기존의 패스워드 기반 인증 시스템의 한계를 극복하고, 더욱 안전하고 편리한 인증 방식을 제공합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

# 로그인 및 회원가입 페이지
def login_signup_page():
    st.title('로그인 및 회원가입')

    # 사용자 입력
    user_id = st.text_input("사용자 ID", key="login_user_id")

    # 로그인 버튼
    if st.button("로그인"):
        if not user_id:
            st.error("사용자 ID를 입력해주세요.")
        elif not check_user_exists(user_id):
            st.error("존재하지 않는 사용자 ID입니다.")
        else:
            st.session_state['user_id'] = user_id
            navigate_to('face_auth')

    # 회원가입 버튼
    if st.button("회원가입"):
        st.session_state['page'] = 'signup'
        st.query_params['page']='signup'

# 회원가입 페이지
def signup_page():
    st.title('회원가입')
    user_id = st.text_input("사용자 ID", key="signup_user_id")
    username = st.text_input("사용자 이름", key="signup_username")

    # ID 중복 확인
    if st.button("ID 중복 확인"):
        if user_id and username:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                conn.close()
                if result:
                    st.error("중복된 ID입니다.")
                    st.session_state['id_checked'] = False
                else:
                    st.success("사용 가능한 ID입니다.")
                    st.session_state['id_checked'] = True
            except Exception as e:
                st.error(f"ID 중복 확인 중 오류 발생: {str(e)}")
        else:
            st.error("사용자 ID와 이름을 모두 입력해주세요.")

    # 다음 버튼
    if st.button("다음"):
        if st.session_state.get('id_checked') and user_id and username:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (user_id, username))
                conn.commit()
                conn.close()
                st.success("사용자 정보가 저장되었습니다.")
                st.session_state['user_id'] = user_id
                st.session_state['username'] = username
                st.session_state['page'] = 'face_registration'
                st.query_params['page'] = 'face_registration'
            except Exception as e:
                st.error(f"사용자 정보 저장 중 오류 발생: {str(e)}")
        else:
            st.error("모든 정보를 입력하고 ID 중복 확인을 진행해주세요.")

# 얼굴 등록 페이지
def face_registration_page():
    st.header("얼굴 등록")
    face_register = FaceRegister()


    stframe = st.empty()
    if st.button("얼굴 등록 시작"):
        with st.spinner("얼굴을 등록 중입니다..."):
            user_id = st.session_state['user_id']

            # 데이터베이스 상태 확인
            conn = sqlite3.connect("./gesture_auth.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
            conn.close()

            result = face_register.register_face(user_id, stframe)
            if result:
                st.success("얼굴이 성공적으로 등록되었습니다!")

                # 등록 후 데이터베이스 상태 재확인
                conn = sqlite3.connect("./gesture_auth.db")
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                updated_user_data = cursor.fetchone()
                conn.close()
            else:
                st.error("얼굴 등록에 실패했습니다.")

    if st.button("다음"):
        if os.path.exists(os.path.join(REGISTERED_FACES_DIR, f"{st.session_state['user_id']}.jpg")):
            navigate_to('gesture_registration')
        else:
            st.error("얼굴 등록을 먼저 완료해주세요.")


# 제스처 등록 페이지
def gesture_registration_page():
    st.header("제스처 등록")
    gesture_auth_system = GestureAuthSystem()

    # 제스처 목록 표시
    st.markdown(GestureAuthSystem.get_available_gestures())
    st.info("세 가지 제스처를 순서대로 등록합니다.")

    if 'is_recording' not in st.session_state:
        st.session_state['is_recording'] = False

    if st.button("제스처 등록 시작"):
        st.session_state['is_recording'] = True

    if st.session_state['is_recording']:
        with st.spinner("제스처 등록 중입니다..."):
            user_id = st.session_state['user_id']
            result = gesture_auth_system.process_video('register', user_id)
            if result:
                st.success("제스처 등록이 완료되었습니다!")
                st.session_state['gesture_registered'] = True
            else:
                st.error("제스처 등록에 실패했습니다.")
            st.session_state['is_recording'] = False

       # 제스처 등록이 성공적으로 완료된 경우에만 회원가입 완료 버튼 활성화
    if st.button("회원가입 완료"):
        if st.session_state.get('gesture_registered', False):
            navigate_to('main')
        else:
            st.warning("제스처 등록을 먼저 완료해주세요.")

# 얼굴 인증 페이지
def face_auth_page():
    st.header("얼굴 인증")
    if 'user_id' not in st.session_state:
        st.error("사용자 ID가 없습니다. 다시 로그인해주세요.")
        navigate_to('main')
        return

    # 얼굴 인증 상태를 session_state에 저장
    if 'face_auth_started' not in st.session_state:
        st.session_state['face_auth_started'] = False

    face_auth = FaceAuthentication()
    stframe = st.empty()

    if not st.session_state['face_auth_started']:
        if st.button("얼굴 인증 시작"):
            st.session_state['face_auth_started'] = True
            st.rerun()

    if st.session_state['face_auth_started']:
        with st.spinner("얼굴을 인증 중입니다..."):
            result = face_auth.authenticate_face(st.session_state['user_id'], stframe)
            if result:
                st.success("얼굴 인증 성공!")
                st.session_state['face_auth_success'] = True
            else:
                st.error("얼굴 인증 실패!")
                st.session_state['face_auth_success'] = False
            st.session_state['face_auth_started'] = False  # 리셋

    if st.button("다음"):
        if st.session_state.get('face_auth_success', False):
            navigate_to('gesture_auth')
        else:
            st.warning("얼굴 인증을 먼저 완료해주세요.")

# 제스처 인증 페이지
def gesture_auth_page():
    st.header("제스처 인증")
    if 'user_id' not in st.session_state:
        st.error("사용자 ID가 없습니다. 다시 로그인해주세요.")
        navigate_to('main')
        return

    # 제스처 인증 상태를 session_state에 저장
    if 'gesture_auth_started' not in st.session_state:
        st.session_state['gesture_auth_started'] = False

    gesture_auth_system = GestureAuthSystem()
    st.markdown(gesture_auth_system.get_available_gestures())

    if not st.session_state['gesture_auth_started']:
        if st.button("제스처 인증 시작"):
            st.session_state['gesture_auth_started'] = True
            st.rerun()

    if st.session_state['gesture_auth_started']:
        try:
            with st.spinner("제스처 인증 중입니다..."):
                auth_success = gesture_auth_system.process_video('verify', st.session_state['user_id'])
                if auth_success:
                    st.success("제스처 인증 성공!")
                    st.session_state['gesture_auth_success'] = True
                else:
                    st.error("제스처 인증 실패!")
                    st.session_state['gesture_auth_success'] = False
                st.session_state['gesture_auth_started'] = False  # 리셋
        except Exception as e:
            st.error(f"제스처 인증 중 오류 발생: {str(e)}")
            st.session_state['gesture_auth_success'] = False
            st.session_state['gesture_auth_started'] = False  # 리셋

    if st.button("인증 완료"):
        if st.session_state.get('gesture_auth_success', False):
            st.success("모든 인증이 완료되었습니다!")
            st.session_state.clear()  # 모든 인증 상태 초기화

            if st.button("돌아가기"):
                navigate_to('main')
        else:
            st.warning("제스처 인증을 먼저 완료해주세요.")


# CSS 추가 호출
add_custom_css()

# 탭으로 네비게이션
tabs = st.tabs(["메인", "로그인 및 회원가입"])

with tabs[0]:
    main_page()

with tabs[1]:
    # 상태에 따라 페이지 로드
    current_page = st.session_state.get('page', 'main')

    if current_page == 'main':
        login_signup_page()
    elif current_page == 'signup':
        signup_page()
    elif current_page == 'face_auth':
        face_auth_page()
    elif current_page == 'face_registration':
        face_registration_page()
    elif current_page == 'gesture_registration':
        gesture_registration_page()
    elif current_page == 'gesture_auth':
        gesture_auth_page()
