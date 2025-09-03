#Note: This code is intended for review purposes only and is not meant to be executed.
#audio rx udp port: 7002, video stream_id: 177_downlink

sudo wfb_rx -p 177 -c 127.0.0.1 -u 7002 -K /etc/drone.key -i 7669206 wlan1
