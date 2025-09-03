#Note: This code is intended for review purposes only and is not meant to be executed.

gst-launch-1.0 -v ximagesrc use-damage=false show-pointer=true ! video/x-raw,framerate=15/1 ! videoscale ! video/x-raw,width=960,height=540 ! videoconvert ! x264enc bitrate=1500 tune=zerolatency ! rtph264pay ! udpsink host=127.0.0.1 port=5602
