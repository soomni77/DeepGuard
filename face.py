import streamlit as st
import face_recognition
import cv2
import os
import numpy as np
from datetime import datetime
from PIL import Image
import mediapipe as mp
import time

# Mediapipe 초기화
mp_face_detection = mp.solutions.face_detection

# 등록된 얼굴 디렉토리
REGISTERED_FACES_DIR = 'registered_faces'
if not os.path.exists(REGISTERED_FACES_DIR):
    os.makedirs(REGISTERED_FACES_DIR)


class FaceRegister:
    def __init__(self, save_dir=REGISTERED_FACES_DIR):
        self.save_dir = save_dir

    def register_face(self):
        st.info("웹캠을 통해 얼굴을 등록합니다.")
        video_capture = cv2.VideoCapture(0)
        stframe = st.empty()
        captured_frame = None
        face_detected_time = None

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.8) as face_detection:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    st.error("웹캠에 접근할 수 없습니다.")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_frame)

                if results.detections:
                    if face_detected_time is None:
                        face_detected_time = time.time()
                        st.info("얼굴이 감지되었습니다. 2초 후에 캡처됩니다.")
                    elif time.time() - face_detected_time > 2:
                        captured_frame = frame.copy()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_path = os.path.join(self.save_dir, f"face_{timestamp}.jpg")
                        
                        # 얼굴 인코딩 확인
                        face_encodings = face_recognition.face_encodings(cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB))
                        if not face_encodings:
                            st.warning("얼굴이 감지되지 않았습니다. 다시 시도하세요.")
                            break
                        
                        cv2.imwrite(file_path, captured_frame)
                        st.success("얼굴이 성공적으로 등록되었습니다!")
                        break
                else:
                    face_detected_time = None

                stframe.image(frame, channels="BGR", use_container_width=True)

            video_capture.release()
            cv2.destroyAllWindows()
            stframe.empty()


class FaceAuthentication:
    def __init__(self, faces_dir=REGISTERED_FACES_DIR):
        self.faces_dir = faces_dir
        self.known_face_encodings, self.known_face_names = self.load_registered_faces()

    def load_registered_faces(self):
        known_face_encodings = []
        known_face_names = []

        for filename in os.listdir(self.faces_dir):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                image_path = os.path.join(self.faces_dir, filename)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(os.path.splitext(filename)[0])
                else:
                    st.warning(f"{filename}에서 얼굴을 감지하지 못했습니다. 해당 파일을 건너뜁니다.")

        return known_face_encodings, known_face_names

    def authenticate_face(self):
        st.info("웹캠을 통해 얼굴을 인증합니다.")
        video_capture = cv2.VideoCapture(0)
        stframe = st.empty()
        authenticated = False
        authentication_failed = False

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.8) as face_detection:
            face_detected_time = None

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    st.warning("웹캠에 접근할 수 없습니다.")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_frame)

                if results.detections:
                    if face_detected_time is None:
                        face_detected_time = time.time()

                    if time.time() - face_detected_time > 2:
                        face_locations = face_recognition.face_locations(rgb_frame)
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                        if not face_encodings:
                            st.warning("얼굴이 감지되지 않았습니다. 다시 시도하세요.")
                            if st.button("재인증"):
                                authentication_failed = False
                                face_detected_time = None
                            break

                        for face_encoding in face_encodings:
                            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.4)
                            name = "Unknown"

                            if True in matches:
                                first_match_index = matches.index(True)
                                name = self.known_face_names[first_match_index]
                                st.success(f"인증 성공! 얼굴: {name}")
                                authenticated = True
                                break
                            else:
                                authentication_failed = True
                                break
                else:
                    face_detected_time = None

                stframe.image(frame, channels="BGR", use_container_width=True)

                if authenticated:
                    break

                if authentication_failed:
                    st.error("인증 실패! 등록된 얼굴이 없습니다.")
                    if st.button("재인증"):
                        authentication_failed = False
                        face_detected_time = None
                    break

            video_capture.release()
            cv2.destroyAllWindows()
            stframe.empty()


