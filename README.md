# 🔒DeepGuard - 2단계 생체인증 시스템
(사진)

---

## 📋 프로젝트 소개
- DeepGuard는 얼굴 인식과 제스처 인식을 결합한 2단계 생체인증 시스템입니다. 
- 기존의 패스워드 기반 인증 시스템의 한계를 극복하고, 더욱 안전하고 편리한 인증 방식을 제공합니다.
---

## ✨ 주요 기능
1. **얼굴인식**
   - MediaPipe와 face_recognition 라이브러리를 활용한 고성능 얼굴 감지 및 인식
   - 실시간 웹캠 스트리밍을 통한 자연스러운 인증 프로세스
   - 2초 간의 얼굴 감지 시간을 통한 정확한 인증

2. **제스처 인식**
   - MediaPipe의 Gesture Recognizer를 활용한 7가지 기본 제스처 지원
   - 3단계 연속 제스처 인증으로 보안성 강화
   - 실시간 제스처 피드백 제공
3. **사용자 인터페이스**
   - Streamlit을 활용한 직관적이고 반응형 웹 인터페이스
   - 단계별 가이드와 실시간 피드백
   - 간편한 사용자 등록 및 인증 프로세스
---
## 🚀 지원하는 제스처
   - ✊ Closed_Fist (주먹)
   - ✋ Open_Palm (손바닥)
   - ☝️ Pointing_Up (검지 들기)
   - 👎 Thumb_Down (엄지 아래)
   - 👍 Thumb_Up (엄지 위)
   - ✌️ Victory (브이)
   - 🤟 ILoveYou (ILY)
---
## 📁 프로젝트 구조
```
DeepGuard/
├── README.md
├── requirements.txt
├── gesture_recognizer.task    # MediaPipe 제스처 인식 모델
├── gesture_auth.db            # SQLite 데이터베이스
├── UI.py                      # Streamlit 메인 UI
├── face.py                    # 얼굴 인식 모듈
├── gesture_auth.py            # 제스처 인식 모듈
│
└── registered_faces/          # 등록된 얼굴 이미지 저장소
    └── *.jpg                  # 등록된 얼굴 이미지들
```
---
## 🛠️ 설치 방법
1. **저장소 클론**

```bash
git clone https://github.com/soomni77/DeepGuard.git
cd DeepGuard
```

2. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```
3. **MediaPipe 모델 다운로드**
```
# gesture_recognizer.task 파일이 프로젝트 루트 디렉토리에 위치해야 합니다
``` 
## 📦 필요 라이브러리
- streamlit
- opencv-python
- mediapipe
- face_recognition
- numpy
- Pillow

requirement.txt
```
streamlit
opencv-python
mediapipe
face-recognition
numpy
Pillow
```
---
## 💻 실행방법
```bash
streamlit run UI.py
```
