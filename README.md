# 2025ESWContest_free_1174 (팀명 : 소시지)
작품명: 열화상•적외선 기반 실시간 시야 확보 및 로컬 통신 지원 다기능 모듈형 헬멧

## 🚀Intro
**"어둠 속 안전을 밝힌다."** ⬛ → 💡 → ✅

저희 팀은 제한된 환경에서 적외선, 열화상 정보를 사용자 친화적으로 제공하여 안전성과 효율성을 증대시키고자 합니다.

## 💡Inspiration

<img width="630" height="366" alt="image" src="https://github.com/user-attachments/assets/96237be3-6a1a-4168-889c-329cfd3c8144" />


소방관들은 고온, 짙은 연기, 제한된 시야 속에서 구조 활동을 수행해야 합니다. 

그러나 구조 환경과 장비가 열악하여 요구조자의 구조뿐만 아니라 구조대원의 탈출조차 쉽지 않은 실정입니다. 

실제로 화재 현장에서 고립되어 순직하는 사례도 발생하고 있습니다. 
이러한 원인은 시야 확보 장비의 부족에서 비롯되기도 합니다. 

열화상 카메라가 있더라도 일부 대원만 사용할 수 있으며, 사용 시 한 손이 점유되어 구조 활동의 효율이 떨어집니다. 

또한 건물 내부 구조가 복잡해 대원 간 위치 확인이 어렵고, 이로 인해 고립이나 통신 두절 상황이 발생하기도 합니다. 

이에 따라 구조대원의 생존율과 구조 성공률을 높이기 위해 새로운 장비를 개발하였습니다.



## 📝Overview

<img width="505" height="209" alt="image" src="https://github.com/user-attachments/assets/9b8b336a-b8d6-4403-a057-52214e9b7299" />
<img width="1218" height="600" alt="image" src="https://github.com/user-attachments/assets/5cd7cd8f-5411-4345-b2f8-92cc5f6ee9f7" />


본 작품은 임베디드 환경에서 사용자에게 실시간 열화상 & 적외선 영상을 제공함과 동시에 edge 검출, 객체 인식, 온도 등의 다양한 정보를 전달합니다. 

또한, 자체적인 서버망을 구축하여 재난 통신망, 군 통신망 등의 특정 통신망에서도 적합하게 사용될 가능성을 제시합니다.

뿐만 아니라, 다양한 기능들을 HW, SW적으로 모듈화하여 사용자 친화적으로 구현하였습니다.



## 🔑Main Feature
### 영상 처리 흐름도(simple)
<img width="703" height="190" alt="image" src="https://github.com/user-attachments/assets/ebb17967-2d18-4036-a694-05d11ed50326" />

<details>
  <summary>영상 처리 흐름도(details)</summary>
<img width="1806" height="798" alt="image" src="https://github.com/user-attachments/assets/3b4638c2-569e-4948-a958-4a8693b51235" />
</details>

### 모드 설정에 따른 열화상 영상 가공

<details>
  <summary>Hot Mode</summary>
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/9f2d82be-13a5-46ea-9576-714268aa1e82" />
</details>

<details>
  <summary>Cold Mode</summary>
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/43f289d9-6695-4ed1-82f4-7a99c456a9d0" />
</details>

<details>
  <summary>Thermal Mode</summary>
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/8d30984a-c78d-4fd2-926e-fb65c0280993" />
</details>





## ⚙️Technology Environment


### Embedded
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-C51A4A?logo=raspberrypi&logoColor=white)
![OpenMV](https://img.shields.io/badge/OpenMV-00979D?logo=arduino&logoColor=white)
![Coral TPU](https://img.shields.io/badge/Coral%20TPU-4285F4?logo=google&logoColor=white)

### Computer Vision & AI
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)
![TensorFlow Lite](https://img.shields.io/badge/TensorFlow%20Lite-FF6F00?logo=tensorflow&logoColor=white)
![PyCoral](https://img.shields.io/badge/PyCoral-4285F4?logo=google&logoColor=white)
![SSD MobileNet](https://img.shields.io/badge/SSD%20MobileNet-FF6F00?logo=tensorflow&logoColor=white)

### Backend/Core
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![Threading](https://img.shields.io/badge/Threading-3776AB?logo=python&logoColor=white)
![PySerial](https://img.shields.io/badge/PySerial-306998?logo=python&logoColor=white)

### Hardware Interface
![GPIOZero](https://img.shields.io/badge/GPIOZero-C51A4A?logo=raspberrypi&logoColor=white)
![rpicam-vid](https://img.shields.io/badge/rpicam--vid-C51A4A?logo=raspberrypi&logoColor=white)
![Serial Communication](https://img.shields.io/badge/Serial%20Comm-00979D?logo=arduino&logoColor=white)
![rtl8812au](https://img.shields.io/badge/rtl8812au-000000?logo=wifi&logoColor=white)
![Wfb-ng](https://img.shields.io/badge/Wfb--ng-000000?logo=linux&logoColor=white)

### System & OS
![Raspberry Pi OS](https://img.shields.io/badge/Raspberry%20Pi%20OS-C51A4A?logo=raspberrypi&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Subprocess](https://img.shields.io/badge/Subprocess-3776AB?logo=python&logoColor=white)

### Image Processing
![Canny Edge](https://img.shields.io/badge/Canny%20Edge-5C3EE8?logo=opencv&logoColor=white)
![YUV420](https://img.shields.io/badge/YUV420-FF6B6B?logo=video&logoColor=white)
![JPEG Decode](https://img.shields.io/badge/JPEG%20Decode-5C3EE8?logo=opencv&logoColor=white)
![Colormap](https://img.shields.io/badge/Colormap-5C3EE8?logo=opencv&logoColor=white)

### UI/Display
![OpenCV GUI](https://img.shields.io/badge/OpenCV%20GUI-5C3EE8?logo=opencv&logoColor=white)

### Development Environment
![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visualstudiocode&logoColor=white)
![OpenMV IDE](https://img.shields.io/badge/OpenMV%20IDE-00979D?logo=arduino&logoColor=white)
![Python 3.9.18](https://img.shields.io/badge/Python%203.9+-3776AB?logo=python&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)



## 📂File Architecture
<details>
  <summary>SW File Architecture </summary>
        SW/
        ├── user/
        │    ├── user_openmv/                       # OpenMV 열화상 카메라
        │    │   └── main.py                        # OpenMV 카메라 제어 스크립트
        │    └── user_raspi/  
        │        ├── text_files/
        │        │   └── sample.txt                             
        │        ├── firefighting/                   # Raspberry Pi 메인 시스템
        │        │   ├── main.py                     # 메인 실행 파일
        │        │   ├── config.py                   # 전역 설정 (상수, 경로 등)
        │        │   ├── core/
        │        │   │   ├── init.py
        │        │   │   ├── camera_manager.py       # 카메라 관리 (thermal, IR)
        │        │   │   ├── image_processor.py      # 영상 처리 모드들
        │        │   │   └── frame_renderer.py       # 화면 출력 관리
        │        │   ├── ui/
        │        │   │   ├── init.py
        │        │   │   └── menu_system.py          # 메뉴 UI 전체
        │        │   ├── ai/
        │        │   │   ├── init.py
        │        │   │   └── person_detector.py      # Coral TPU 사람 감지
        │        │   ├── hardware/
        │        │   │   ├── init.py
        │        │   │   ├── gpio_controller.py      # GPIO 버튼 제어
        │        │   │   └── serial_comm.py          # OpenMV 시리얼 통신
        │        │   └── utils/
        │        │       ├── init.py
        │        │       └── file_monitor.py         # 텍스트 파일 모니터링
        │        │
        │        └──── communication/
        │             ├─── key/                       # 복호화 key파일
        │             │    ├── server.key
        │             │    └── usr.key
        │             │─── setup/
        │             │    │
        │             │    │── setup.sh              #wlan interface 설정
        │             │    └── wifibroadcast.cfg     #ip_tunnel 설정
        │             └─── usr_comm/
        │                  ├── datastream/            #통신 데이터 스트림
        │                  │   ├── audio.sh
        │                  │   ├── heartbeat.sh
        │                  │   └── streaming.sh
        │                  ├── rx_codes.sh          #수신부
        │                  └──tx_codes.sh           #송신부
        │                
        ├── node/
        │  ├── forwarding.sh                        #수신후 재송신
        │  ├── rssi.sh                              #rssi값 산출
        │  └── nodegraph.py                         #통신맵 구성
        │   
        └── server/
            ├── server_comm/
            │  ├── datastream/                       #통신 데이터 스트림
            │  │   ├── audio.sh
            │  │   ├── heartbeat.sh
            │  │   └── videostreaming.sh
            │  ├── rx_codes.sh                     #송신부
            │  └── tx_codes.sh                     #수신부
            ├── ui.py                              #ui 구성
            └── centercon.py                       #중앙 통신망 관제 시스템
</details>

<details>
  <summary>HW File Architecture</summary>

    HW/
    ├── front_part/
    │    ├── main/                       # 본체
    │    │   ├── main_RaspberryPi_top.stl 
    │    │   ├── main_RaspberryPi_bottom.stl
    │    │   ├── main_wifi_top.stl
    │    │   ├── main_wifi_bottom.stl
    │    │   ├── main_coral_top.stl
    │    │   └── main_coral_bottom.stl
    │    ├── cam_binder/              # 캠 바운더
    │    │   ├── cam_top.stl
    │    │   ├── cam_bottom.stl
    │    │   ├── helmet_mount_top.stl
    │    │   └── helmet_mount_bottom.stl
    │    └── remote_control/         # 리모컨
    │          ├── remote_control_top.stl
    │          ├── remote_control_mid.stl
    │          ├── remote_control_bottom.stl
    │          ├── remote_control_cap_circle.stl
    │          ├── remote_control_cap_triangle.stl
    │          └── remote_control_cap_M.stl
    │   
    ├── right_part/
    │    ├── antenna/                   # 안테나
    │    │   └── antenna.stl
    │    └── display/                    # 디스플레이
    │          ├── display_binder_top.stl
    │          ├── display_binder_mid.stl
    │          ├── display_binder_bottom.stl
    │          ├── display_arm_top.stl
    │          └── display_arm_bottom.stl
    │   
    ├── left_part/
    │    ├── light/                       # 라이트
    │    │   ├── light_ir_cover.stl
    │    │   ├── light_rail_top.stl
    │    │   └── light_rail_bottom.stl
    │    └── speaker/                   # 스피커
    │          ├── speaker_left.stl
    │          └── speaker_right.stl
    │   
    └── communication_part/
        └── node/                      # 노드
                ├── node_top.stl
                └── node_bottom.stl
</details>


## 🎥Video

유튜브 링크: https://www.youtube.com/watch?v=UqA-5wN_xS8&feature=youtu.be

## 🧑‍🤝‍🧑Team Member

<br>

<img width="300" height="533" alt="image" src="https://github.com/user-attachments/assets/797abd56-19be-420c-ad6e-0ebeeb477aa8" />

| 팀원 | 역할 |
|----------|----------|
| 김상만(팀장)  | 총괄, 3D 모델링 & 3D 프린팅 |
| 조민우   | 영상 제작, HW 제어, UI 제작 |
| 한수민 | 통신망 구축, 서버 구축 |
| 박나영 | HW 제작, 3D 모델링, 성능 테스트 및 디버깅 | 
| 하은지 | 3D 모델링, 장치 배선, 안전 및 전원 관리리 | 
