#!/bin/bash

WFB_ID="7669206"
RX_IF="wlan1"
TX_IF="wlan2"

#video
sudo wfb_rx -p 0 -c 127.0.0.1 -u 5602 -K $KEY_FILE -i $WFB_ID $RX_IF &
sudo wfb_tx -f data -p 0 -u 5602 -K $KEY_FILE -B 20 -G long -S 1 -L 1 -M 1 -k 3 -n 6 -i $WFB_ID $TX_IF &

#audio_server_to_node_to_usr
sudo wfb_rx -p 49 -c 127.0.0.1 -u 7003 -K $KEY_FILE -i $WFB_ID $RX_IF &
sudo wfb_tx -f data -p 49 -u 7003 -K $KEY_FILE -k 2 -n 5 -M 1 -i $WFB_ID $TX_IF &

#audio_usr_to_node_to_server
sudo wfb_rx -p 177 -c 127.0.0.1 -u 7002 -K $KEY_FILE -i $WFB_ID $RX_IF &
sudo wfb_tx -f data -p 177 -u 7002 -K /etc/gs.key -k 2 -n 5 -M 1 -i $WFB_ID $TX_IF &

