# 2025ESWContest_free_1174 (팀명 : 소시지)
<br>

## 🚀Intro
<br>

#### ⬛ → 💡 → ✅

### ⬛ → 💡 → ✅

## ⬛ → 💡 → ✅



**"어둠 속 안전을 밝힌다."**

저희 팀은 열화상·적외선 영상을 Raspberry Pi로 융합하고 실시간으로 HMD에 표시하여 암시야 환경에서도 시야를 확보하는 시스템을 구현하였습니다.    
이에 더해, 서버와 무선 통신으로 위험 요소 탐지와 관제 연동이 가능하며, 모듈형 구조로 산업 현장, 군사 작전 등 다양한 환경에 확장할 수 있습니다.


## 💡Inspiration
<br>

## 📝Overview
<br>

## ⚙️Environment
<br>

## 📂File Architecture
<br>

    SW/
    ├── user/
    │    ├── user_raspi/                                # Raspberry Pi 메인 시스템
    │    │   └── firefighting/
    │    │       ├── main.py                            # 메인 실행 파일
    │    │       ├── config.py                          # 전역 설정 (상수, 경로 등)
    │    │       ├── core/
    │    │       │   ├── init.py
    │    │       │   ├── camera_manager.py              # 카메라 관리 (thermal, IR)
    │    │       │   ├── image_processor.py             # 영상 처리 모드들
    │    │       │   └── frame_renderer.py              # 화면 출력 관리
    │    │       ├── ui/
    │    │       │   ├── init.py
    │    │       │   └── menu_system.py                 # 메뉴 UI 전체
    │    │       ├── ai/
    │    │       │   ├── init.py
    │    │       │   └── person_detector.py             # Coral TPU 사람 감지
    │    │       ├── hardware/
    │    │       │   ├── init.py
    │    │       │   ├── gpio_controller.py             # GPIO 버튼 제어
    │    │       │   └── serial_comm.py                 # OpenMV 시리얼 통신
    │    │       └── utils/
    │    │           ├── init.py
    │    │           └── file_monitor.py                # 텍스트 파일 모니터링
    │    └── user_openmv/                               # OpenMV 열화상 카메라
    │        └── main.py                                # OpenMV 카메라 제어 스크립트
    │    
    │── node/
    │   
    └── server/
    
    HW/
    ├── 본체/
    │    
    ├── 정면부/
    │   
    └── 후면부/
    

# 📡한수민통신추가



## 🎥Video
<br>

## 🧑‍🤝‍🧑Team Member

<br>

| 팀원 | 역할 |
|----------|----------|
| 김상만(팀장)  | ㅇ  |
| 조민우   | ㅇ |
| 한수민 | ㅇ |
| 박나영 | ㅇ | 
| 하은지 | ㅇ | 
