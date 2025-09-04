#Note: This code is intended for review purposes only and is not meant to be executed.

#chose your own mic and speaker device
MIC_DEVICE="plughw:4,0"
SPEAKER_DEVICE="plughw:0,0"


#mic input
gst-launch-1.0 alsasrc device="${MIC_DEVICE}" ! audioconvert ! opusenc bitrate=96000 ! rtpopuspay ! udpsink host=127.0.0.1 port=7003

#speaker output
gst-launch-1.0 udpsrc port=7002 caps="application/x-rtp, media=(string)audio, clock-rate=(int)48000, encoding-name=(string)OPUS, payload=(int)96" ! rtpopusdepay ! opusdec ! audioconvert ! alsasink device="${SPEAKER_DEVICE}"

