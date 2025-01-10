import streamlit as st
import cv2
import mediapipe as mp
import sqlite3
import time
from collections import Counter

class GestureAuthSystem:
    def __init__(self, db_path="./gesture_auth.db"):
        """
        제스처 인증 시스템 초기화
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        # 데이터베이스 경로 설정 및 초기화
        self.db_path = db_path
        self.setup_database()
        
        # MediaPipe 제스처 인식을 위한 클래스들 초기화
        self.BaseOptions = mp.tasks.BaseOptions
        self.GestureRecognizer = mp.tasks.vision.GestureRecognizer
        self.GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        
        # 제스처 인식 및 녹화 관련 상태 변수들
        self.current_gesture = None  # 현재 감지된 제스처
        self.gesture_counts = Counter()  # 제스처 빈도수 카운터
        self.start_time = None  # 녹화 시작 시간
        self.is_recording = False  # 녹화 상태
        self.base_timestamp = int(time.time() * 1000)  # 기준 타임스탬프
        
    def setup_database(self):
        """
        SQLite 데이터베이스 설정 및 초기화
        - users 테이블 생성
        - 기존 테이블이 있는 경우 구조 검증 후 필요시 재생성
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # users 테이블 존재 여부 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 기존 테이블의 컬럼 구조 확인
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # id 컬럼이 없으면 테이블 재생성
            if 'id' not in columns:
                cursor.execute("DROP TABLE users")
                table_exists = False
        
        # 테이블이 없는 경우 새로 생성
        if not table_exists:
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,           -- 사용자 고유 ID
                    username TEXT,                 -- 사용자 이름
                    gesture_1 TEXT,                -- 첫 번째 제스처
                    gesture_2 TEXT,                -- 두 번째 제스처
                    gesture_3 TEXT,                -- 세 번째 제스처
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 생성 시간
                )
            ''')
            
        conn.commit()
        conn.close()

    def check_id_availability(self, user_id):
        """
        사용자 ID 중복 확인
        Args:
            user_id (str): 확인할 사용자 ID
        Returns:
            bool: ID 사용 가능 여부 (True: 사용 가능, False: 이미 존재)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is None

    def save_to_database(self, user_id, username, gestures, image_path=None):
        """
        사용자 정보와 제스처를 데이터베이스에 저장
        Args:
            user_id (str): 사용자 ID
            username (str): 사용자 이름
            gestures (list): 3개의 제스처 시퀀스
            image_path (str, optional): 얼굴 이미지 파일 경로
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # UPDATE query로 변경
            cursor.execute("""
                UPDATE users 
                SET gesture_1 = ?, gesture_2 = ?, gesture_3 = ?
                WHERE id = ?
            """, (gestures[0], gestures[1], gestures[2], user_id))
            
            conn.commit()
            conn.close()
            st.success("제스처가 성공적으로 저장되었습니다!")
        except Exception as e:
            st.error(f"데이터베이스 저장 중 오류 발생: {str(e)}")
            raise

    def result_callback(self, result, output_image, timestamp_ms):
        """
        MediaPipe 제스처 인식 결과 콜백 함수
        Args:
            result: MediaPipe 제스처 인식 결과
            output_image: 처리된 이미지
            timestamp_ms: 타임스탬프
        """
        if result.gestures and result.gestures[0]:
            self.current_gesture = result.gestures[0][0].category_name

    def process_video(self, mode, user_id, username=None):
        """
        비디오 스트림 처리 및 제스처 인식 메인 함수
        Args:
            mode (str): 'register' 또는 'verify' 모드
            user_id (str): 사용자 ID
            username (str, optional): 사용자 이름 (등록 모드에서만 필요)
        Returns:
            bool: 제스처 등록/인증 성공 여부
        """
        # 카메라 설정
        cap = cv2.VideoCapture(0)  
                
        frame_placeholder = st.empty()  # 프레임 표시 영역
        status_placeholder = st.empty()  # 상태 메시지 표시 영역
        
        # 카메라 속성 설정
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 60)

        # MediaPipe 제스처 인식기 옵션 설정
        try:
            with open('gesture_recognizer.task', 'rb') as file:
                model_data = file.read()
        except FileNotFoundError:
            st.error("제스처 인식 모델 파일을 찾을 수 없습니다.")
            return False

        options = self.GestureRecognizerOptions(
            base_options=self.BaseOptions(model_asset_buffer=model_data),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            num_hands=1,  # 한 손만 인식
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            result_callback=self.result_callback
        )

        # 상태 변수 초기화
        self.is_recording = False
        is_countdown = False
        all_gestures_complete = False
        self.current_gesture_index = 0
        recorded_gestures = []
        frame_count = 0

        # UI 버튼 생성
        button_container = st.container()
        col1, col2, col3 = button_container.columns([0.2, 0.2, 0.6])
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
                        st.error("카메라에서 프레임을 읽을 수 없습니다.")
                        break

                    frame = cv2.resize(frame, (640, 480))
                    frame_count += 1
                    
                    # 재시작 버튼 처리
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

                    # 시작 버튼 처리
                    if not is_countdown and start_button:
                        self.start_time = time.time()
                        is_countdown = True
                        self.gesture_counts.clear()
                        status_placeholder.warning("준비하세요!")

                    # 카운트다운 및 녹화 처리
                    if is_countdown:
                        current_time = time.time()
                        elapsed_time = current_time - self.start_time

                        # 3초 카운트다운
                        if elapsed_time < 3:
                            countdown_remaining = 3 - int(elapsed_time)
                            status_placeholder.warning(f"제스처 {self.current_gesture_index + 1} 준비: {countdown_remaining}초")
                        
                        # 3초 녹화
                        elif elapsed_time < 6:
                            if not self.is_recording:
                                self.is_recording = True
                                self.gesture_counts.clear()
                            
                            recording_remaining = 6 - int(elapsed_time)
                            status_placeholder.error(f"제스처 {self.current_gesture_index + 1} 녹화중: {recording_remaining}초")
                            
                            # 현재 제스처 카운팅
                            if self.current_gesture:
                                self.gesture_counts[self.current_gesture] += 1
                        
                        # 녹화 완료 처리
                        else:
                            if self.is_recording:
                                # 가장 많이 감지된 제스처 저장
                                if self.gesture_counts:
                                    most_common_gesture = self.gesture_counts.most_common(1)[0][0]
                                    recorded_gestures.append(most_common_gesture)
                                    status_placeholder.success(f"제스처 {self.current_gesture_index + 1}번 완료!")
                                else:
                                    recorded_gestures.append(None)
                                    status_placeholder.warning(f"제스처 {self.current_gesture_index + 1}번 인식 실패!")
                                
                                self.is_recording = False
                                self.current_gesture_index += 1
                                
                                # 다음 제스처 준비 또는 완료 처리
                                if self.current_gesture_index < 3:
                                    self.start_time = current_time
                                    self.gesture_counts.clear()
                                else:
                                    if len(recorded_gestures) == 3 and all(gesture is not None for gesture in recorded_gestures):
                                        all_gestures_complete = True
                                        status_placeholder.success("모든 제스처가 완료되었습니다!")
                                    else:
                                        st.error("일부 제스처가 제대로 인식되지 않았습니다. 다시 시도해주세요.")
                                        return False

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

            except Exception as e:
                st.error(f"비디오 처리 중 오류 발생: {str(e)}")
                return False
            finally:
                cap.release()

            # 모든 제스처 완료 후 처리
            if all_gestures_complete and len(recorded_gestures) == 3:
                if mode == 'register':
                    try:
                        self.save_to_database(user_id, username, recorded_gestures)
                        status_placeholder.success("제스처 등록이 완료되었습니다!")
                        return True
                    except Exception as e:
                        st.error(f"제스처 등록 중 오류 발생: {str(e)}")
                        return False
                elif mode == 'verify':
                    result = self.verify_gestures(user_id, recorded_gestures)
                    status_placeholder.info(result)
                    return "성공" in result

            return False

    def verify_gestures(self, user_id, input_gestures):
        """
        입력된 제스처와 저장된 제스처를 비교하여 인증
        Args:
            user_id (str): 사용자 ID
            input_gestures (list): 입력된 3개의 제스처 시퀀스
        Returns:
            str: 인증 결과 메시지
        """
        try:
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
                # 입력된 제스처와 저장된 제스처 비교
                matches = sum(1 for stored, input_gesture in zip(stored_gestures, input_gestures)
                             if stored == input_gesture)

                if matches == 3:
                    return f"인증 성공! 👋 {username} 님 안녕하세요!"
                else:
                    return "인증 실패: 제스처가 일치하지 않습니다."
            return "인증 실패: 등록되지 않은 사용자입니다."
        except Exception as e:
            return f"인증 오류: {str(e)}"

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