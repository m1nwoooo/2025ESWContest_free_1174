#Note: This code is intended for review purposes only and is not meant to be executed.
#video tx udp port: 5602, video stream_id: 0
#audio tx udp port: 7003, video stream_id: 49_uplink

#video tx code
sudo wfb_tx -f data -p 0 -u 5602 -K /etc/usr.key -B 20 -G long -S 1 -L 1 -M 1 -k 3 -n 6 -i 7669206 wlan1

#audio tx code
sudo wfb_tx -f data -p 49 -u 7003 -K /etc/usr.key -k 2 -n 5 -M 1 -i 7669206 wlan1
