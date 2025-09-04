# 2025ESWContest_free_1174 (팀명 : 소시지)
<br>
작품명: 열화상•적외선 기반 실시간 시야 확보 및 로컬 통신 지원 다기능 모듈형 헬멧


## 🚀Intro
<br>



**"어둠 속 안전을 밝힌다."** ⬛ → 💡 → ✅

저희 팀은 제한된 환경에서 적외선, 열화상 정보를 사용자 친화적으로 제공하여 안전성과 효율성을 증대시키고자 합니다.

## 💡Inspiration
<br>

<img width="839" height="488" alt="image" src="https://github.com/user-attachments/assets/96237be3-6a1a-4168-889c-329cfd3c8144" />


소방관들은 고온, 짙은 연기, 제한된 시야 속에서 구조 활동을 수행해야 합니다. 

그러나 구조 환경과 장비가 열악하여 요구조자의 구조뿐만 아니라 구조대원의 탈출조차 쉽지 않은 실정입니다. 

실제로 화재 현장에서 고립되어 순직하는 사례도 발생하고 있습니다. 
이러한 원인은 시야 확보 장비의 부족에서 비롯되기도 합니다. 

열화상 카메라가 있더라도 일부 대원만 사용할 수 있으며, 사용 시 한 손이 점유되어 구조 활동의 효율이 떨어집니다. 

또한 건물 내부 구조가 복잡해 대원 간 위치 확인이 어렵고, 이로 인해 고립이나 통신 두절 상황이 발생하기도 합니다. 

이에 따라 구조대원의 생존율과 구조 성공률을 높이기 위해 새로운 장비를 개발하였습니다.



## 📝Overview
<br>

## 🔑Main Feature
<br>

<img width="1916" height="1077" alt="image" src="https://github.com/user-attachments/assets/9b6c1c26-691d-4ae6-8a98-e468c8012d45" />




## ⚙️Environment
<br>

## 📂File Architecture
<br>

    SW/
    ├── user/
    │    ├── user_openmv/                       # OpenMV 열화상 카메라
    │    │   └── main.py                        # OpenMV 카메라 제어 스크립트
    │    ├── user_raspi/  
    │    │   ├── text_files/
    │    │   │   └── sample.txt                             
    │    │   └── firefighting/                   # Raspberry Pi 메인 시스템
    │    │       ├── main.py                     # 메인 실행 파일
    │    │       ├── config.py                   # 전역 설정 (상수, 경로 등)
    │    │       ├── core/
    │    │       │   ├── init.py
    │    │       │   ├── camera_manager.py       # 카메라 관리 (thermal, IR)
    │    │       │   ├── image_processor.py      # 영상 처리 모드들
    │    │       │   └── frame_renderer.py       # 화면 출력 관리
    │    │       ├── ui/
    │    │       │   ├── init.py
    │    │       │   └── menu_system.py          # 메뉴 UI 전체
    │    │       ├── ai/
    │    │       │   ├── init.py
    │    │       │   └── person_detector.py      # Coral TPU 사람 감지
    │    │       ├── hardware/
    │    │       │   ├── init.py
    │    │       │   ├── gpio_controller.py      # GPIO 버튼 제어
    │    │       │   └── serial_comm.py          # OpenMV 시리얼 통신
    │    │       └── utils/
    │    │           ├── init.py
    │    │           └── file_monitor.py         # 텍스트 파일 모니터링
    │    └──user_communication/
    │    
    ├── node/
    │   
    │   
    └── server/


        HW/
    ├── 본체/
    │    
    ├── 정면부/
    │   
    │   
    └── 후면부/


        HW/
    ├── 본체/
    │    
    ├── 정면부/
    │   
    │   
    └── 후면부/







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
