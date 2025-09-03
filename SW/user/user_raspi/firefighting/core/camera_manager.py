import cv2
import subprocess
import numpy as np
import time
import os
import signal
import struct

from config import *

class CameraManager:
    def __init__(self, system):
        self.system = system
        self.thermal_serial = None
        self.ir_process = None
        
    def setup_thermal(self):
        return self.system.serial_comm.connect()
    
    def setup_ir(self):
        try:
            cmd = [
                'rpicam-vid', '--width', str(IR_WIDTH), '--height', str(IR_HEIGHT),
                '--framerate', str(IR_FPS), '--timeout', '0', '--output', '-',
                '--codec', 'yuv420', '--nopreview'
            ]
            self.ir_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, 
                bufsize=10**7, preexec_fn=os.setsid
            )
            time.sleep(3)
            return self.ir_process.poll() is None
        except Exception:
            return False
    
    def thermal_capture_thread(self):
        while self.system.running:
            try:
                if self.system.serial_comm.is_connected():
                    frame = self.system.serial_comm.get_thermal_frame()
                    if frame is not None:
                        with self.system.frame_lock:
                            self.system.thermal_frame = frame
                    time.sleep(0.11)
                else:
                    time.sleep(0.1)
            except Exception:
                time.sleep(0.1)
    
    def preprocess_ir_frame(self, ir_frame):
        if ir_frame is None:
            return None
        try:
            height, width = ir_frame.shape[:2]
            crop_left = int(width * 0.12)
            crop_right = int(width * 0.12)
            cropped_frame = ir_frame[:, crop_left:width-crop_right]
            stretched_frame = cv2.resize(cropped_frame, (width, height))
            return stretched_frame
        except Exception:
            return ir_frame
    
    def ir_capture_thread(self):
        frame_size = IR_WIDTH * IR_HEIGHT * 3 // 2
        while self.system.running:
            try:
                if self.ir_process and self.ir_process.poll() is None:
                    raw_data = self.ir_process.stdout.read(frame_size)
                    if len(raw_data) == frame_size:
                        yuv = np.frombuffer(raw_data, dtype=np.uint8).reshape((IR_HEIGHT * 3 // 2, IR_WIDTH))
                        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV420p2BGR)
                        processed_bgr = self.preprocess_ir_frame(bgr)
                        with self.system.frame_lock:
                            self.system.ir_frame = processed_bgr
                    else:
                        time.sleep(0.01)
                else:
                    break
            except Exception:
                time.sleep(0.1)
    
    def cleanup(self):
        if self.ir_process:
            try:
                os.killpg(os.getpgid(self.ir_process.pid), signal.SIGTERM)
                self.ir_process.wait(timeout=3)
            except Exception:
                pass
