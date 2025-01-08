import streamlit as st
from gesture_auth import GestureAuthSystem

def main():
    """
    메인 애플리케이션 함수
    - Streamlit 웹 인터페이스 구성
    - 페이지 레이아웃 및 스타일 설정
    - 사용자 인터페이스 요소 배치
    - 제스처 인식 시스템 초기화 및 실행
    """
    # 기본 페이지 설정
    # - 페이지 제목, 아이콘, 레이아웃 구성
    st.set_page_config(
        page_title="제스처 인증 시스템",
        page_icon="👋",
        layout="wide",  # 전체 화면 너비 사용
        initial_sidebar_state="expanded"  # 사이드바 초기 상태
    )
    
    # CSS 스타일 정의 및 적용
    # - 웹 페이지의 시각적 요소 스타일링
    st.markdown("""
        <style>
            /* 메인 컨테이너 스타일링 */
            .main > div {
                padding: 2rem 3rem;  # 여백 설정
            }
            
            /* 로고 이미지 스타일링 */
            div[data-testid="stImage"] img {
                display: block;  # 블록 레벨 요소로 설정
                margin: 0 auto;  # 좌우 마진을 auto로 설정하여 중앙 정렬
                padding: 1rem;   # 내부 여백 추가
            }
            
            /* 타이틀 컨테이너 스타일링 */
            .title-container {
                background-color: #f0f2f6;  # 배경색
                padding: 1.5rem;  # 내부 여백
                border-radius: 10px;  # 모서리 둥글게
                margin-bottom: 2rem;  # 하단 여백
                margin-top: -6rem;  # 상단 공백 제거
            }
            
            /* 버튼 스타일링 */
            .stButton > button {
                background-color: #4CAF50;  # 버튼 배경색
                color: white;  # 텍스트 색상
                font-size: 16px;  # 폰트 크기
                border-radius: 8px;  # 모서리 둥글게
                border: none;  # 테두리 제거
                padding: 12px 24px;  # 내부 여백
                transition: all 0.3s ease;  # 애니메이션 효과
            }
            .stButton > button:hover {
                background-color: #45a049;  # 호버 시 배경색
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);  # 그림자 효과
            }
            
            /* 웹캠 영상 컨테이너 스타일링 */
            div[data-testid="stImage"] {
                border-radius: 15px;  # 모서리 둥글게
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);  # 그림자 효과
                margin: 1rem 0;  # 상하 여백
                max-width: 800px;  # 최대 너비
                margin: 0 auto;  # 중앙 정렬
            }
            
            /* 텍스트 입력 필드 스타일링 */
            .stTextInput > div > div > input {
                border-radius: 8px;  # 모서리 둥글게
                font-size: 16px;  # 폰트 크기
                padding: 10px 15px;  # 내부 여백
            }
            
            /* 사이드바 스타일링 */
            .css-1d391kg {
                padding: 2rem 1rem;  # 내부 여백
            }
            
            /* 상태 메시지 스타일링 */
            .stAlert > div {
                border-radius: 8px;  # 모서리 둥글게
                padding: 1rem;  # 내부 여백
            }
            
            /* 사용 방법 카드 스타일링 */
            .usage-guide {
                background-color: #f8f9fa;  # 배경색
                padding: 1.5rem;  # 내부 여백
                border-radius: 10px;  # 모서리 둥글게
                border-left: 5px solid #4CAF50;  # 왼쪽 테두리
                margin-top: -4rem;  # 상단 여백 조정
            }

            /* 헤더 마진 조정 */
            .element-container:has(h1) {
                margin-top: -4rem;  # h1 상단 여백
            }
            .element-container:has(h3) {
                margin-top: -2rem;  # h3 상단 여백
            }

            /* Markdown 컨테이너 스타일링 */
            .element-container {
                margin: 0 !important;  # 여백 제거
                padding: 0 !important;  # 패딩 제거
            }

            /* 기본 메뉴 및 헤더 숨김 처리 */
            #MainMenu {
                visibility: hidden;  # 메인 메뉴 숨김
            }
            header {
                visibility: hidden;  # 헤더 숨김
            }
            
            /* 제스처 목록 스타일링 */
            .gesture-list {
                background-color: #ffffff;  # 배경색
                padding: 1rem;  # 내부 여백
                border-radius: 8px;  # 모서리 둥글게
                margin-top: 1rem;  # 상단 여백
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 로고 이미지 및 타이틀 표시
    # 로고 이미지를 중앙 정렬하여 표시
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("logo1.png", width=200)  # logo.png 파일을 사용하며, 너비는 200픽셀로 설정
    
    # 애플리케이션 타이틀 표시
    st.title("👋 제스처 인증 시스템")
    
    # 사이드바 구성
    # - 메뉴 선택 및 사용 가능한 제스처 목록 표시
    with st.sidebar:
        st.markdown("### 📋 메뉴")
        # 메뉴 선택 드롭다운
        menu = st.selectbox("선택하세요", ["제스처 등록", "사용자 인증"])
        
        st.markdown("---")
        # 사용 가능한 제스처 목록 표시
        st.markdown("### 🤚 사용 가능한 제스처")
        gestures = {
            "주먹 (Closed_Fist)": "✊",
            "손바닥 (Open_Palm)": "✋",
            "검지 들기 (Pointing_Up)": "☝️",
            "엄지 아래 (Thumb_Down)": "👎",
            "엄지 위 (Thumb_Up)": "👍",
            "브이 (Victory)": "✌️",
            "ILY (ILoveYou)": "🤟"
        }
        
        # 각 제스처와 이모지 표시
        for gesture, emoji in gestures.items():
            st.markdown(f"{emoji} {gesture}")
    
    # 제스처 인증 시스템 초기화
    auth_system = GestureAuthSystem()

    # 제스처 등록 모드
    if menu == "제스처 등록":
        st.header("✍️ 제스처 등록")
        # 화면을 두 컬럼으로 분할
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 사용자 이름 입력 필드
            username = st.text_input("👤 사용자 이름을 입력하세요")
            if username:
                # 제스처 등록 프로세스 시작
                auth_system.process_video('register', username)
                
        with col2:
            # 사용 방법 안내
            st.markdown("""
            ### 📝 사용 방법
            1. 👤 사용자 이름 입력
            2. ▶️ 시작 버튼으로 시작
            3. ⏳ 3초 카운트다운
            4. 🤚 각 제스처 3초씩 유지
            """)

    # 사용자 인증 모드
    elif menu == "사용자 인증":
        st.header("🔐 사용자 인증")
        # 화면을 두 컬럼으로 분할
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 사용자 이름 입력 필드
            username = st.text_input("👤 사용자 이름을 입력하세요")
            if username:
                # 사용자 인증 프로세스 시작
                auth_system.process_video('verify', username)
                
        with col2:
            # 사용 방법 안내
            st.markdown("""
            ### 📝 사용 방법
            1. 👤 사용자 이름 입력
            2. ▶️ 시작 버튼으로 시작
            3. ⏳ 3초 카운트다운
            4. 🔄 등록한 순서대로 제스처 인증
            """)

# 메인 함수 실행
if __name__ == "__main__":
    main()