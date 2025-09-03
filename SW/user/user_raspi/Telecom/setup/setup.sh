#!/bin/bash

#check your rlt8812au device interface
#configure WLAN,tx_power, wifi_freq

WLAN="ur_interface"
tx_power=""
wifi_freq=""

sudo ip link set ${WLAN} down
sudo iw dev ${WLAN} set type monitor
sleep 2
sudo ip link set ${WLAN} txpower ${tx_power}
sudo iw dev ${WLAN} set channel ${wifi_freq}
sudo systemctl daemon-reload
