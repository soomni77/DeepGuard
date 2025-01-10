import streamlit as st
import cv2
import mediapipe as mp
import sqlite3
import time
from collections import Counter

class GestureAuthSystem:
    def __init__(self, db_path="./fpwd.db"):
        self.db_path = db_path
        self.setup_database()
        
        self.BaseOptions = mp.tasks.BaseOptions
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        self.base_timestamp = int(time.time() * 1000)  # 기준 타임스탬프
        self.current_gesture = None
        self.gesture_counts = Counter()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fpwd'")
        if not cursor.fetchone():
            cursor.execute('''CREATE TABLE fpwd (
                fname TEXT PRIMARY KEY,
                gesture_1 TEXT,
                gesture_2 TEXT,
                gesture_3 TEXT,
                gesture_4 TEXT)''')
        conn.commit()
        conn.close()

    def result_callback(self, result, output_image, timestamp_ms):
        if result.gestures and result.gestures[0]:
            self.current_gesture = result.gestures[0][0].category_name

    def process_video(self, mode='register', fname=None):
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        status_placeholder = st.empty()

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 30)

        options = self.GestureRecognizerOptions(
            base_options=self.BaseOptions(model_asset_path='gesture_cus_recognizer.task'),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            result_callback=self.result_callback
        )
        frame_count = 0

        if "start_time" not in st.session_state:
            st.session_state.start_time = None

        start_button = st.button("카메라 시작")

        if start_button:
            st.session_state.start_time = time.time()
            st.session_state.gesture_index = 0
            st.session_state.recorded_gestures = []

        if st.session_state.start_time:
            with self.GestureRecognizer.create_from_options(options) as recognizer:
                try:
                    while cap.isOpened() and st.session_state.gesture_index < 4:
                        ret, frame = cap.read()
                        if not ret:
                            break

                        frame = cv2.resize(frame, (620, 480))
                        frame_count += 1
                        current_time = time.time()
                        elapsed_time = current_time - st.session_state.start_time

                        if elapsed_time < 3:
                            status_placeholder.warning(f"제스처 {st.session_state.gesture_index + 1} 준비: {3 - int(elapsed_time)}초")
                        elif elapsed_time < 6:
                            status_placeholder.error(f"제스처 {st.session_state.gesture_index + 1} 녹화 중...")
                            if self.current_gesture:
                                self.gesture_counts[self.current_gesture] += 1
                        else:
                            most_common = self.gesture_counts.most_common(1)
                            if most_common:
                                st.session_state.recorded_gestures.append(most_common[0][0])
                            st.session_state.start_time = current_time
                            st.session_state.gesture_index += 1
                            self.gesture_counts.clear()
                            
                        # 제스처 인식 처리
                        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                        current_timestamp = self.base_timestamp + (frame_count * 16)
                        recognizer.recognize_async(mp_image, current_timestamp)

                        # 감지된 제스처 표시
                        if self.current_gesture:
                            cv2.putText(frame, f"Detected: {self.current_gesture}", 
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        
                        # 프레임 표시
                        frame_placeholder.image(frame, channels="BGR", use_container_width=True)

                        # image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # frame_placeholder.image(image_rgb, channels="RGB")
                finally:
                    cap.release()

            if mode == 'register':
                self.save_to_database(fname, st.session_state.recorded_gestures)
                status_placeholder.success("제스처 등록이 완료되었습니다!")
            elif mode == 'verify':
                self.verify_gestures(fname, st.session_state.recorded_gestures)
                print(st.session_state.recorded_gestures)

    def save_to_database(self, fname, gestures):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""INSERT OR REPLACE INTO fpwd 
            (fname, gesture_1, gesture_2, gesture_3, gesture_4)
            VALUES (?, ?, ?, ?, ?)""", (fname, *gestures))
        conn.commit()
        conn.close()

    def verify_gestures(self, fname, input_gestures):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        print(fname)
        cursor.execute("""SELECT gesture_1, gesture_2, gesture_3, gesture_4 FROM fpwd WHERE fname = ?""", (fname,))
        result = cursor.fetchone()
        conn.close()
        for row in result:
            print(row)

        if result:
            stored_gestures = result
            matches = sum(1 for stored, input_gesture in zip(stored_gestures, input_gestures) if stored == input_gesture)
            
            if matches == 4:
                st.success("인증 성공! 👋")
            else:
                st.error("인증 실패")
        else:
            st.error("등록되지 않은 사용자입니다.")
