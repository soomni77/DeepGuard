import streamlit as st
import cv2
import mediapipe as mp
import sqlite3
import time
from collections import Counter

class GestureAuthSystem:
    def __init__(self, db_path="./gesture_auth.db"):
        """
        시스템 초기화
        Args:
            db_path (str): 데이터베이스 파일 경로
        """
        # 데이터베이스 경로 설정 및 초기화
        self.db_path = db_path
        self.setup_database()
        
        # MediaPipe 제스처 인식 관련 클래스들 초기화
        self.BaseOptions = mp.tasks.BaseOptions
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        
        # 제스처 인식 및 녹화 관련 상태 변수들
        self.current_gesture = None
        self.gesture_counts = Counter()
        self.start_time = None
        self.is_recording = False
        self.base_timestamp = int(time.time() * 1000)
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기존 users 테이블이 있는지 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 기존 테이블의 컬럼 정보 확인
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # id 컬럼이 없으면 테이블 재생성
            if 'id' not in columns:
                # 기존 테이블 삭제
                cursor.execute("DROP TABLE users")
                table_exists = False
        
        # 테이블이 없으면 새로 생성
        if not table_exists:
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

    def result_callback(self, result, output_image, timestamp_ms):
        """
        MediaPipe 제스처 인식 콜백 함수
        """
        if result.gestures and result.gestures[0]:
            self.current_gesture = result.gestures[0][0].category_name

    def process_video(self, mode, user_id, username=None):
        """
        비디오 스트림 처리 및 제스처 인식 메인 함수
        """
        cap = cv2.VideoCapture(1)
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
            result_callback=self.result_callback
        )

        self.is_recording = False
        is_countdown = False
        all_gestures_complete = False
        self.current_gesture_index = 0
        recorded_gestures = []
        frame_count = 0

        button_container = st.container()
        col1, col2, col3 = button_container.columns([0.12, 0.15, 0.73])
        with col1:
            start_button = st.button("시작")
        with col2:
            reset_button_text = "재등록" if mode == 'register' else "재시도"
            restart_button = st.button(reset_button_text)

        with self.GestureRecognizer.create_from_options(options) as recognizer:
            try:
                while cap.isOpened() and not all_gestures_complete:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    frame = cv2.resize(frame, (640, 480))
                    frame_count += 1
                    
                    if restart_button:
                        self.is_recording = False
                        is_countdown = False
                        self.current_gesture_index = 0
                        recorded_gestures = []
                        self.gesture_counts.clear()
                        self.base_timestamp = int(time.time() * 1000)
                        status_text = "재등록" if mode == 'register' else "재시도"
                        status_placeholder.info(f"{status_text}를 하려면 시작 버튼을 눌러주세요.")
                        continue

                    if not is_countdown and start_button:
                        self.start_time = time.time()
                        is_countdown = True
                        self.gesture_counts.clear()
                        status_placeholder.warning("준비하세요!")

                    if is_countdown:
                        current_time = time.time()
                        elapsed_time = current_time - self.start_time

                        if elapsed_time < 3:
                            countdown_remaining = 3 - int(elapsed_time)
                            status_placeholder.warning(f"제스처 {self.current_gesture_index + 1} 준비: {countdown_remaining}초")
                        
                        elif elapsed_time < 6:
                            if not self.is_recording:
                                self.is_recording = True
                                self.gesture_counts.clear()
                            
                            recording_remaining = 6 - int(elapsed_time)
                            status_placeholder.error(f"제스처 {self.current_gesture_index + 1} 녹화중: {recording_remaining}초")
                            
                            if self.current_gesture:
                                self.gesture_counts[self.current_gesture] += 1
                        
                        else:
                            if self.is_recording:
                                if self.gesture_counts:
                                    most_common_gesture = self.gesture_counts.most_common(1)[0][0]
                                    recorded_gestures.append(most_common_gesture)
                                    status_placeholder.success(f"제스처 {self.current_gesture_index + 1}번 완료!")
                                
                                self.is_recording = False
                                self.current_gesture_index += 1
                                
                                if self.current_gesture_index < 3:
                                    self.start_time = current_time
                                    self.gesture_counts.clear()
                                else:
                                    if len(recorded_gestures) == 3:
                                        all_gestures_complete = True
                                        status_placeholder.success("모든 제스처가 완료되었습니다!")
                                    else:
                                        st.error("일부 제스처가 제대로 인식되지 않았습니다. 다시 시도해주세요.")
                                    break

                    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                    current_timestamp = self.base_timestamp + (frame_count * 16)
                    recognizer.recognize_async(mp_image, current_timestamp)

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
        - ILoveYou (ILY)
        """