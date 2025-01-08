import sqlite3
from collections import Counter
import time
import cv2
import mediapipe as mp
import streamlit as st

class GestureAuthSystem:
    def __init__(self, db_path="./gesture_auth.db"):
        self.db_path = db_path
        self.setup_database()

        self.BaseOptions = mp.tasks.BaseOptions
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode

        self.current_gesture = None
        self.gesture_counts = Counter()
        self.start_time = None
        self.is_recording = False

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    username TEXT,
                    gesture_1 TEXT,
                    gesture_2 TEXT,
                    gesture_3 TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
        conn.close()

    def check_id_availability(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is None

    def save_to_database(self, user_id, username, gestures):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users 
            (id, username, gesture_1, gesture_2, gesture_3)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, gestures[0], gestures[1], gestures[2]))
        conn.commit()
        conn.close()

    def process_video(self, mode, user_id, username=None):
        cap = cv2.VideoCapture(0)
        frame_placeholder = st.empty()
        status_placeholder = st.empty()

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 60)

        options = self.GestureRecognizerOptions(
            base_options=self.BaseOptions(model_asset_path='gesture_recognizer.task'),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            result_callback=self.result_callback)

        self.is_recording = False
        is_countdown = True
        all_gestures_complete = False
        self.current_gesture_index = 0
        recorded_gestures = []

        self.start_time = time.time()
        self.gesture_counts.clear()
        status_placeholder.warning("준비하세요!")

        with self.GestureRecognizer.create_from_options(options) as recognizer:
            try:
                while cap.isOpened() and not all_gestures_complete:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame = cv2.resize(frame, (640, 480))

                    if is_countdown:
                        current_time = time.time()
                        elapsed_time = current_time - self.start_time

                        if elapsed_time < 3:  # 카운트다운
                            countdown_remaining = 3 - int(elapsed_time)
                            status_placeholder.warning(f"제스처 {self.current_gesture_index + 1} 준비: {countdown_remaining}초")

                        elif elapsed_time < 6:  # 녹화
                            if not self.is_recording:
                                self.is_recording = True
                                self.gesture_counts.clear()

                            recording_remaining = 6 - int(elapsed_time)
                            status_placeholder.error(f"제스처 {self.current_gesture_index + 1} 녹화중: {recording_remaining}초")

                            if self.current_gesture:
                                self.gesture_counts[self.current_gesture] += 1

                        else:  # 한 제스처 완료
                            if self.is_recording:
                                if self.gesture_counts:
                                    most_common_gesture = self.gesture_counts.most_common(1)[0][0]
                                    recorded_gestures.append(most_common_gesture)

                                self.is_recording = False
                                self.current_gesture_index += 1

                                if self.current_gesture_index < 3:
                                    self.start_time = current_time
                                    self.gesture_counts.clear()
                                else:
                                    if len(recorded_gestures) == 3:
                                        all_gestures_complete = True
                                    else:
                                        st.error("일부 제스처가 제대로 인식되지 않았습니다. 다시 시도해주세요.")
                                    break

                    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                    recognizer.recognize_async(mp_image, int(time.time() * 1000))

                    if self.current_gesture:
                        cv2.putText(frame, f"Detected: {self.current_gesture}",
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    frame_placeholder.image(frame, channels="BGR", use_container_width=True)

            finally:
                cap.release()

        if all_gestures_complete and len(recorded_gestures) == 3:
            if mode == 'register':
                self.save_to_database(user_id, username, recorded_gestures)
                status_placeholder.success("제스처 등록이 완료되었습니다!")
            elif mode == 'verify':
                result = self.verify_gestures(user_id, recorded_gestures)
                status_placeholder.info(result)

    def result_callback(self, result, output_image, timestamp_ms):
        if result.gestures and result.gestures[0]:
            self.current_gesture = result.gestures[0][0].category_name

    def verify_gestures(self, user_id, input_gestures):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, gesture_1, gesture_2, gesture_3 
            FROM users WHERE id = ?
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            username = result[0]
            stored_gestures = result[1:]
            matches = sum(1 for stored, input_gesture in zip(stored_gestures, input_gestures)
                         if stored == input_gesture)

            if matches == 3:
                return f"인증 성공! 👋 {username} 님 안녕하세요!"
            else:
                return "인증 실패"
        else:
            return "등록되지 않은 사용자입니다."
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT gesture_1, gesture_2, gesture_3 
            FROM users WHERE id = ?
        """, (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_gestures = result
            matches = sum(1 for stored, input_gesture in zip(stored_gestures, input_gestures)
                         if stored == input_gesture)

            if matches == 3:
                return "인증 성공! 👋"
            else:
                return "인증 실패"
        else:
            return "등록되지 않은 사용자입니다."

    @staticmethod
    def get_available_gestures():
        return """
        ### 사용 가능한 제스처 목록
        - None (제스처 없음)
        - Closed_Fist (주먹)
        - Open_Palm (손바닥)
        - Pointing_Up (검지 들기)
        - Thumb_Down (엄지 아래)
        - Thumb_Up (엄지 위)
        - Victory (브이)
        """