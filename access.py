import streamlit as st
from importlib import import_module


# 스트림릿 페이지 설정
st.set_page_config(page_title="파일 사진 예제", layout="wide")

st.title("🖼️ 파일 사진 및 이름 표시 예제")


# 파일 사진 및 이름을 위한 데이터
file_data = [
    {"image": "kmg_design_folder.png", "name": "그냥문서.txt"}, 
    {"image": "kmg_design_folder.png", "name": "평범파일.pdf"},
    {"image": "kmg_design_folder.png", "name": "Folder_One"},
    {"image": "kmg_design_folder.png", "name": "Folder_Two"},
    {"image": "kmg_design_folder.png", "name": "발표자료.pptx"},
    {"image": "kmg_design_folder.png", "name": "일반문서.xlsx"},
]

# 컬럼을 활용하여 파일 사진과 이름 배치
cols = st.columns(len(file_data))  # 파일 개수에 맞게 열 생성
for i, data in enumerate(file_data):
    with cols[i]:
        try:
            # 이미지 표시
            st.image(data["image"], width=100)  # 이미지 크기 조정
            if st.button(f'{data["name"]}', key=data["name"]) :
                module = import_module('one_p')  # 동적 로딩
                module.gg(data["name"])  # 함수 실행

            # 이미지 중앙 정렬 및 파일명 중앙 정렬
            st.markdown(
                f"""
                <style>
                    .stApp{{
                        background-color : pink;
                    }}
                    .stButton:active > button:active {{
                        background-color: pink;
                    }}
                    .stButton:hover > button:hover {{
                        color: gray;
                    }}
                    
                    .stButton > button {{
                        background-color: transparent;
                        color: gray;
                        font-size: 16px;
                        border: none;
                        cursor: pointer;
                    }}
                    img:hover {{
                        transform: scale(1.1);  /* 확대 효과 */
                        transition: transform 0.2s ease-in-out;
                    }}
                    img:active{{
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"이미지를 로드하는 중 오류가 발생했습니다: {e}")
