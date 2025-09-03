#!/bin/bash

echo ">> start heartbeat tx codes..."

#Making heartbeat data
(while true; do echo "heartbeat"; sleep 1; done | socat -u - UDP-SENDTO:127.0.0.1:6010) &

# save pid for killling process
SOCAT_PID=$!
echo "   -> socat process ID: $SOCAT_PID"

# run wfb_tx and use udp port 6010 and steam
echo ">> start wfb_tx (wfb-ng stream 10)"
sudo wfb_tx -f data -p 10 -u 6010 -K /etc/drone.key -k 2 -n 4 -M 1 -i 7669206 wlan1

trap "echo '>> kill socat process($SOCAT_PID)'; kill $SOCAT_PID" EXIT

echo ">> stop heartbeat tx process..."
