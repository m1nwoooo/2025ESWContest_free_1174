import serial
import struct
import time
import threading
import cv2
import numpy as np

from config import *

class SerialComm:
    def __init__(self):
        self.serial = None
        self.port = None
        self.lock = threading.Lock()
        
    def connect(self):
        for port in THERMAL_SERIAL_PORTS:
            try:
                self.serial = serial.Serial(
                    port=port, 
                    baudrate=THERMAL_BAUDRATE, 
                    timeout=2,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                
                self.port = port
                time.sleep(1)
                if self.serial.is_open:
                    return True
                    
            except Exception:
                continue
                
        return False
    
    def is_connected(self):
        return self.serial and self.serial.is_open
    
    def get_thermal_frame(self):
        if not self.is_connected():
            return None
        
        try:
            with self.lock:
                self.serial.reset_input_buffer()
                self.serial.write(b"snap")
                self.serial.flush()
                
                size_data = self.serial.read(4)
                if len(size_data) != 4: 
                    return None
                
                img_size = struct.unpack('<L', size_data)[0]
                if img_size <= 0 or img_size > 50000: 
                    return None
                
                img_data = self.serial.read(img_size)
                if len(img_data) != img_size: 
                    return None
            
            img_array = np.frombuffer(img_data, dtype=np.uint8)
            thermal_img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
            
            if thermal_img is not None and thermal_img.shape == (THERMAL_HEIGHT, THERMAL_WIDTH):
                return thermal_img
            
            return None
                    
        except Exception:
            return None
    
    def toggle_temperature(self):
        if not self.is_connected():
            return None
        
        try:
            with self.lock:
                self.serial.write(b"temp")
                self.serial.flush()
                
                size_data = self.serial.read(4)
                if len(size_data) == 4:
                    msg_size = struct.unpack('<L', size_data)[0]
                    if 5 <= msg_size <= 20:
                        status_bytes = self.serial.read(msg_size)
                        if len(status_bytes) == msg_size:
                            status = status_bytes.decode('utf-8')
                            
                            if "TEMP_ON" in status:
                                return True
                            elif "TEMP_OFF" in status:
                                return False
            
            return None
        except Exception:
            return None
    
    def cleanup(self):
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
            except Exception:
                pass
