import streamlit as st
from face import FaceAuthentication, FaceRegister

def main() :
    # Streamlit UI
    st.title("Face Recognition System")
    st.sidebar.title("메뉴 선택")
    option = st.sidebar.radio("기능을 선택하세요", ["얼굴 등록하기", "얼굴 인증하기"])

    if option == "얼굴 등록하기":
        st.header("얼굴 등록하기")
        face_register = FaceRegister()
        face_register.register_face()

    elif option == "얼굴 인증하기":
        st.header("얼굴 인증하기")
        face_auth = FaceAuthentication()
        face_auth.authenticate_face()

if __name__ == "__main__":
    main()


