#!/usr/bin/env python3

import cv2
import time
import threading
from queue import Queue

from config import *
from core.camera_manager import CameraManager
from core.image_processor import ImageProcessor
from core.frame_renderer import FrameRenderer
from ui.menu_system import MenuSystem
from ai.person_detector import PersonDetector
from hardware.gpio_controller import GPIOController
from hardware.serial_comm import SerialComm
from utils.file_monitor import FileMonitor

class FirefightingSystem:
    def __init__(self):
        self.running = False
        self.current_mode = 0
        self.edge_toggle_mode = 1
        self.ui_visible = True
        self.person_detection_enabled = True
        self.temperature_mode = False
        
        self.edge_threshold_low = DEFAULT_EDGE_THRESHOLD_LOW
        self.edge_threshold_high = DEFAULT_EDGE_THRESHOLD_HIGH
        self.current_edge_resolution_index = DEFAULT_EDGE_RESOLUTION_INDEX
        self.current_thermal_colormap = 0
        
        _, self.edge_width, self.edge_height, _ = EDGE_RESOLUTION_OPTIONS[self.current_edge_resolution_index]
        
        self.thermal_frame = None
        self.ir_frame = None
        self.frame_lock = threading.Lock()
        
        self.last_process_time = 0
        self.frame_time = 1.0 / DEFAULT_TARGET_FPS
        
        self.get_screen_resolution()
        self.setup_components()
        
    def get_screen_resolution(self):
        import subprocess
        try:
            result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if '*' in line and '+' in line:
                    for part in line.split():
                        if 'x' in part and part.replace('x', '').replace('.', '').isdigit():
                            resolution = part.split('x')
                            if len(resolution) == 2:
                                self.screen_width = int(resolution[0])
                                self.screen_height = int(float(resolution[1]))
                                return
        except Exception:
            pass
        self.screen_width, self.screen_height = (1920, 1080)
    
    def setup_components(self):
        self.camera_manager = CameraManager(self)
        self.image_processor = ImageProcessor(self)
        self.frame_renderer = FrameRenderer(self)
        self.menu_system = MenuSystem(self)
        self.person_detector = PersonDetector()
        self.gpio_controller = GPIOController(self)
        self.serial_comm = SerialComm()
        self.file_monitor = FileMonitor(TEXT_FILES_DIR)
    
    def setup_display(self):
        cv2.namedWindow('Firefighting System', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Firefighting System', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def toggle_temperature_mode(self):
        if self.serial_comm.is_connected():
            status = self.serial_comm.toggle_temperature()
            if status is not None:
                self.temperature_mode = status
    
    def run(self):
        self.setup_display()
        self.running = True
        
        thermal_ok = self.camera_manager.setup_thermal()
        ir_ok = self.camera_manager.setup_ir()
        
        if not (thermal_ok or ir_ok):
            return
        
        threads = []
        if thermal_ok:
            threads.append(threading.Thread(target=self.camera_manager.thermal_capture_thread, daemon=True))
        if ir_ok:
            threads.append(threading.Thread(target=self.camera_manager.ir_capture_thread, daemon=True))
        
        for thread in threads:
            thread.start()
        
        try:
            while self.running:
                current_time = time.time()
                if current_time - self.last_process_time < self.frame_time:
                    time.sleep(self.frame_time - (current_time - self.last_process_time))
                    continue
                self.last_process_time = current_time
                
                with self.frame_lock:
                    current_thermal = self.thermal_frame.copy() if self.thermal_frame is not None else None
                    current_ir = self.ir_frame.copy() if self.ir_frame is not None else None
                
                if self.menu_system.is_active():
                    display_frame = self.menu_system.render(self.screen_width, self.screen_height)
                else:
                    display_frame = self.image_processor.process_mode(
                        self.current_mode, current_thermal, current_ir
                    )
                    display_frame = self.frame_renderer.add_ui_overlay(display_frame)
                
                display_frame = self.frame_renderer.resize_to_screen(display_frame)
                cv2.imshow('Firefighting System', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or cv2.getWindowProperty('Firefighting System', cv2.WND_PROP_VISIBLE) < 1:
                    break
        
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
    
    def cleanup(self):
        self.running = False
        self.camera_manager.cleanup()
        self.serial_comm.cleanup()
        cv2.destroyAllWindows()

def main():
    system = FirefightingSystem()
    system.run()

if __name__ == "__main__":
    main()
