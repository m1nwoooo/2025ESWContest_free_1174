# 2025ESWContest_free_sausage



## Team Member
    SW/
    └── user/
    │    ├── user_raspi/                                 # Raspberry Pi 메인 시스템
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
    │       └── main.py                                # OpenMV 카메라 제어 스크립트
    │    
    │    
    │── node/
    │   
    │   
    │── server/

#한수민통신추가
<br>

| 팀원 | 역할 |
|----------|----------|
| 김상만(팀장)  | ㅇ  |
| 조민우   | ㅇ |
| 한수민 | ㅇ |
| 박나영 | ㅇ | 
| 하은지 | ㅇ | 
