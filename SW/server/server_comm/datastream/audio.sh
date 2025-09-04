#Note: This code is intended for review purposes only and is not meant to be executed.

#mic input
gst-launch-1.0 pulsesrc ! audioconvert ! opusenc bitrate=96000 ! rtpopuspay ! udpsink host=127.0.0.1 port=7002

#speaker output
gst-launch-1.0 udpsrc port=7003 caps="application/x-rtp, media=(string)audio, clock-rate=(int)48000, encoding-name=(string)OPUS, payload=(int)96" ! rtpopusdepay ! opusdec ! audioconvert ! alsasink device="default"
