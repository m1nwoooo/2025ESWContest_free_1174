import cv2
import numpy as np
import time

class FrameRenderer:
    def __init__(self, system):
        self.system = system
    
    def resize_to_screen(self, frame):
        if frame is None:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        h, w = frame.shape[:2]
        if w != self.system.screen_width or h != self.system.screen_height:
            frame = cv2.resize(frame, (self.system.screen_width, self.system.screen_height))
        return frame
    
    def add_ui_overlay(self, frame):
        if not self.system.ui_visible:
            return frame
        
        self.system.file_monitor.check_for_new_files()
        
        height, width = frame.shape[:2]
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        panel_width = 580
        panel_height = 150
        panel_x = width - panel_width - 20
        panel_y = 20
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), (15, 15, 15), -1)
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), (255, 255, 255), 2)
        
        text_x = panel_x + 15
        text_y = panel_y + 25
        line_height = 25
        
        cv2.putText(overlay, f"Time: {current_time}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        text_y += line_height
        
        if self.system.person_detector.is_available():
            ai_status = "ON" if self.system.person_detection_enabled else "OFF"
            person_count = self.system.person_detector.person_count if self.system.person_detection_enabled else 'N/A'
            person_text = f"AI Detection: {ai_status} (Persons: {person_count})"
            cv2.putText(overlay, person_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(overlay, "AI Detection: DISABLED", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
        text_y += line_height
        
        temp_status = "ON" if self.system.temperature_mode else "OFF"
        temp_color = (0, 255, 255) if self.system.temperature_mode else (128, 128, 128)
        cv2.putText(overlay, f"Temperature Mode: {temp_status}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, temp_color, 2)
        text_y += line_height
        
        cv2.putText(overlay, "Remote Control:", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        text_y += line_height
        
        self.draw_control_icons(overlay, text_x + 20, text_y - 5)
        
        alpha = 0.9
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        frame = self.draw_notification(frame)
        
        return frame
    
    def draw_control_icons(self, overlay, start_x, icon_y):
        icon_size = 20
        icon_spacing = 130
        
        def draw_small_square(x, y, size, color):
            cv2.rectangle(overlay, (x, y), (x + size, y + size), color, -1)
        
        def draw_small_triangle(x, y, size, color):
            pts = np.array([[x + size//2, y], [x, y + size], [x + size, y + size]], np.int32)
            cv2.fillPoly(overlay, [pts], color)
        
        def draw_small_circle(x, y, radius, color):
            cv2.circle(overlay, (x + radius, y + radius), radius, color, -1)
        
        def draw_small_inverted_triangle(x, y, size, color):
            pts = np.array([[x, y], [x + size, y], [x + size//2, y + size]], np.int32)
            cv2.fillPoly(overlay, [pts], color)
        
        draw_small_square(start_x, icon_y, icon_size, (255, 255, 255))
        cv2.putText(overlay, "Menu", (start_x + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        icon_x2 = start_x + icon_spacing
        draw_small_triangle(icon_x2, icon_y, icon_size, (0, 0, 255))
        cv2.putText(overlay, "Edge", (icon_x2 + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        icon_x3 = start_x + icon_spacing * 2
        draw_small_circle(icon_x3, icon_y, icon_size//2, (255, 255, 255))
        cv2.putText(overlay, "Mode", (icon_x3 + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        icon_x4 = start_x + icon_spacing * 3
        draw_small_inverted_triangle(icon_x4, icon_y, icon_size, (0, 0, 255))
        ui_status = "UI" if self.system.ui_visible else "OFF"
        cv2.putText(overlay, ui_status, (icon_x4 + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def draw_notification(self, frame):
        if not self.system.file_monitor.has_notification():
            return frame
            
        current_time = time.time()
        if current_time - self.system.file_monitor.notification_start_time > self.system.file_monitor.notification_duration:
            self.system.file_monitor.clear_notification()
            return frame
        
        height, width = frame.shape[:2]
        
        notif_width = 280
        notif_height = 60
        notif_x = width - notif_width - 20
        notif_y = 190
        
        overlay = frame.copy()
        
        blink_cycle = int((current_time - self.system.file_monitor.notification_start_time) * 2) % 2
        if blink_cycle == 0:
            bg_color = (0, 100, 255)
            border_color = (0, 150, 255)
        else:
            bg_color = (0, 80, 200)
            border_color = (0, 120, 230)
        
        cv2.rectangle(overlay, (notif_x, notif_y), (notif_x + notif_width, notif_y + notif_height), bg_color, -1)
        cv2.rectangle(overlay, (notif_x, notif_y), (notif_x + notif_width, notif_y + notif_height), border_color, 3)
        
        icon_x = notif_x + 15
        icon_y = notif_y + 15
        icon_size = 30
        
        cv2.rectangle(overlay, (icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size), (255, 255, 255), -1)
        cv2.rectangle(overlay, (icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size), (0, 0, 0), 3)
        for i in range(3):
            line_y = icon_y + 8 + i * 6
            cv2.line(overlay, (icon_x + 5, line_y), (icon_x + icon_size - 5, line_y), (0, 0, 0), 2)
        
        text_x = icon_x + icon_size + 15
        text_y = notif_y + notif_height // 2 + 5
        
        display_name = self.system.file_monitor.new_file_name
        if len(display_name) > 18:
            display_name = display_name[:15] + "..."
        cv2.putText(overlay, display_name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        remaining_time = self.system.file_monitor.notification_duration - (current_time - self.system.file_monitor.notification_start_time)
        progress = remaining_time / self.system.file_monitor.notification_duration
        progress_width = int((notif_width - 20) * progress)
        cv2.rectangle(overlay, (notif_x + 10, notif_y + notif_height - 5), 
                      (notif_x + 10 + progress_width, notif_y + notif_height - 2), (255, 255, 255), -1)
        
        alpha = 0.95
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
