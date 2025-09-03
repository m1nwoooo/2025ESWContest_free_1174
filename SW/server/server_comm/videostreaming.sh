#Note: This code is intended for review purposes only and is not meant to be executed.

gst-launch-1.0 -v udpsrc port=5600 buffer-size=524288 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink sync=false
