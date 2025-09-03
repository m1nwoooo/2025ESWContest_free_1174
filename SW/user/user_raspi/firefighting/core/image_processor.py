import cv2
import numpy as np

from config import *

class ImageProcessor:
    def __init__(self, system):
        self.system = system
        self.thermal_scale_fixed = 1.0
        self.thermal_offset_x_fixed = 0
        self.thermal_offset_y_fixed = 0
        self.ir_scale_fixed = 1.0
        self.ir_offset_x_fixed = 20
        self.ir_offset_y_fixed = -32
        self.ir_overlay_alpha = DEFAULT_IR_OVERLAY_ALPHA
        
    def process_mode(self, mode, thermal_frame, ir_frame):
        if mode == 0:
            return self.create_search_mode(thermal_frame, ir_frame)
        elif mode == 1:
            return self.create_cold_mode(thermal_frame, ir_frame)
        elif mode == 2:
            return self.create_edge_overlay_mode(thermal_frame, ir_frame)
        elif mode == 3:
            return self.create_ir_only_mode(ir_frame)
        else:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
    
    def create_search_mode(self, thermal_frame, ir_frame=None):
        if thermal_frame is None:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        gray = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2GRAY) if len(thermal_frame.shape) == 3 else thermal_frame.copy()
        gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        hot_threshold = np.percentile(gray_norm, (1.0 - DEFAULT_SEARCH_HOT_PERCENTAGE) * 100)
        search_mask = gray_norm >= hot_threshold
        result_gray = cv2.cvtColor(gray_norm, cv2.COLOR_GRAY2BGR)
        result_gray[search_mask] = [0, 0, 255]
        
        result = self.apply_thermal_scale_and_offset(result_gray)
        
        if self.should_show_ir_overlay() and ir_frame is not None:
            result = self.apply_ir_image_overlay(result, ir_frame)
        if self.should_show_edges() and ir_frame is not None:
            result = self.apply_ai_detection_and_edge_overlay(result, ir_frame)
        else:
            result = self.process_frame_with_ai(result, ir_frame)
        
        return result
    
    def should_show_edges(self):
        return self.system.edge_toggle_mode > 0 and self.system.current_mode != 3
    
    def should_show_ir_overlay(self):
        return self.system.edge_toggle_mode == 2
    
    def get_current_mode_edge_color(self):
        return MODE_EDGE_COLORS.get(self.system.current_mode, [255, 255, 255])
    
    def apply_ir_image_overlay(self, thermal_background, ir_frame):
        if ir_frame is None:
            return thermal_background
        
        ir_positioned = self.apply_ir_scale_and_offset(ir_frame)
        try:
            return cv2.addWeighted(thermal_background, 1.0 - self.ir_overlay_alpha, ir_positioned, self.ir_overlay_alpha, 0)
        except Exception:
            return thermal_background
    
    def process_frame_with_ai(self, result, ir_frame):
        if self.system.person_detection_enabled and ir_frame is not None and self.system.person_detector.is_available():
            person_detected, person_boxes, _ = self.system.person_detector.detect_persons(ir_frame)
            if person_detected and person_boxes:
                scale_settings = {
                    'ir_scale_fixed': self.ir_scale_fixed,
                    'ir_offset_x_fixed': self.ir_offset_x_fixed,
                    'ir_offset_y_fixed': self.ir_offset_y_fixed,
                    'screen_width': self.system.screen_width,
                    'screen_height': self.system.screen_height,
                    'ir_width': IR_WIDTH,
                    'ir_height': IR_HEIGHT
                }
                result = self.system.person_detector.draw_bounding_boxes(result, person_boxes, self.system.current_mode, scale_settings)
        return result
    
    def create_cold_mode(self, thermal_frame, ir_frame=None):
        if thermal_frame is None:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        gray = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2GRAY) if len(thermal_frame.shape) == 3 else thermal_frame.copy()
        gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        cold_threshold = np.percentile(gray_norm, DEFAULT_COLD_PERCENTAGE * 100)
        cold_mask = gray_norm <= cold_threshold
        result_gray = cv2.cvtColor(gray_norm, cv2.COLOR_GRAY2BGR)
        result_gray[cold_mask] = [255, 0, 0]
        
        result = self.apply_thermal_scale_and_offset(result_gray)
        
        if self.should_show_ir_overlay() and ir_frame is not None:
            result = self.apply_ir_image_overlay(result, ir_frame)
        if self.should_show_edges() and ir_frame is not None:
            result = self.apply_ai_detection_and_edge_overlay(result, ir_frame)
        else:
            result = self.process_frame_with_ai(result, ir_frame)
        
        return result
    
    def create_edge_overlay_mode(self, thermal_frame, ir_frame):
        if thermal_frame is None:
            result = np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        else:
            gray = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2GRAY) if len(thermal_frame.shape) == 3 else thermal_frame.copy()
            gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
            _, colormap_cv2 = THERMAL_COLORMAPS[self.system.current_thermal_colormap]
            thermal_colored = cv2.applyColorMap(gray_norm, colormap_cv2)
            result = self.apply_thermal_scale_and_offset(thermal_colored)
        
        if ir_frame is not None:
            if self.should_show_ir_overlay():
                result = self.apply_ir_image_overlay(result, ir_frame)
            result = self.apply_ai_detection_and_edge_overlay(result, ir_frame)
        
        return result
    
    def create_ir_only_mode(self, ir_frame):
        if ir_frame is None:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        result = self.apply_ir_scale_and_offset(ir_frame)
        return self.process_frame_with_ai(result, ir_frame)
    
    def apply_thermal_scale_and_offset(self, thermal_colored):
        if thermal_colored is None:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        scaled_thermal_width = int(THERMAL_WIDTH * self.thermal_scale_fixed)
        scaled_thermal_height = int(THERMAL_HEIGHT * self.thermal_scale_fixed)
        thermal_scaled = cv2.resize(thermal_colored, (scaled_thermal_width, scaled_thermal_height))
        
        screen_scale_x = self.system.screen_width / THERMAL_WIDTH
        screen_scale_y = self.system.screen_height / THERMAL_HEIGHT
        final_thermal_width = int(scaled_thermal_width * screen_scale_x)
        final_thermal_height = int(scaled_thermal_height * screen_scale_y)
        final_offset_x = int(self.thermal_offset_x_fixed * screen_scale_x)
        final_offset_y = int(self.thermal_offset_y_fixed * screen_scale_y)
        
        thermal_final = cv2.resize(thermal_scaled, (final_thermal_width, final_thermal_height))
        result = np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        start_x = max(0, final_offset_x)
        start_y = max(0, final_offset_y)
        end_x = min(self.system.screen_width, final_offset_x + final_thermal_width)
        end_y = min(self.system.screen_height, final_offset_y + final_thermal_height)
        
        src_start_x = max(0, -final_offset_x)
        src_start_y = max(0, -final_offset_y)
        src_end_x = src_start_x + (end_x - start_x)
        src_end_y = src_start_y + (end_y - start_y)
        
        if start_x < end_x and start_y < end_y and src_start_x < final_thermal_width and src_start_y < final_thermal_height:
            try:
                result[start_y:end_y, start_x:end_x] = thermal_final[src_start_y:src_end_y, src_start_x:src_end_x]
            except Exception:
                pass
        
        return result
    
    def apply_ir_scale_and_offset(self, ir_frame):
        if ir_frame is None:
            return np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        scaled_ir_width = int(IR_WIDTH * self.ir_scale_fixed)
        scaled_ir_height = int(IR_HEIGHT * self.ir_scale_fixed)
        ir_scaled = cv2.resize(ir_frame, (scaled_ir_width, scaled_ir_height))
        
        screen_scale_x = self.system.screen_width / IR_WIDTH
        screen_scale_y = self.system.screen_height / IR_HEIGHT
        final_ir_width = int(scaled_ir_width * screen_scale_x)
        final_ir_height = int(scaled_ir_height * screen_scale_y)
        final_offset_x = int(self.ir_offset_x_fixed * screen_scale_x)
        final_offset_y = int(self.ir_offset_y_fixed * screen_scale_y)
        
        ir_final = cv2.resize(ir_scaled, (final_ir_width, final_ir_height))
        result = np.zeros((self.system.screen_height, self.system.screen_width, 3), dtype=np.uint8)
        
        start_x = max(0, final_offset_x)
        start_y = max(0, final_offset_y)
        end_x = min(self.system.screen_width, final_offset_x + final_ir_width)
        end_y = min(self.system.screen_height, final_offset_y + final_ir_height)
        
        src_start_x = max(0, -final_offset_x)
        src_start_y = max(0, -final_offset_y)
        src_end_x = src_start_x + (end_x - start_x)
        src_end_y = src_start_y + (end_y - start_y)
        
        if start_x < end_x and start_y < end_y and src_start_x < final_ir_width and src_start_y < final_ir_height:
            try:
                result[start_y:end_y, start_x:end_x] = ir_final[src_start_y:src_end_y, src_start_x:src_end_x]
            except Exception:
                pass
        
        return result
    
    def should_show_edges(self):
        return self.system.edge_toggle_mode > 0 and self.system.current_mode != 3
    
    def should_show_ir_overlay(self):
        return self.system.edge_toggle_mode == 2
    
    def get_current_mode_edge_color(self):
        return MODE_EDGE_COLORS.get(self.system.current_mode, [255, 255, 255])
    
    def apply_ir_image_overlay(self, thermal_background, ir_frame):
        if ir_frame is None:
            return thermal_background
        
        ir_positioned = self.apply_ir_scale_and_offset(ir_frame)
        try:
            return cv2.addWeighted(thermal_background, 1.0 - self.ir_overlay_alpha, ir_positioned, self.ir_overlay_alpha, 0)
        except Exception:
            return thermal_background
    
    def process_frame_with_ai(self, result, ir_frame):
        if self.system.person_detection_enabled and ir_frame is not None and self.system.person_detector.is_available():
            person_detected, person_boxes, _ = self.system.person_detector.detect_persons(ir_frame)
            if person_detected and person_boxes:
                scale_settings = {
                    'ir_scale_fixed': self.ir_scale_fixed,
                    'ir_offset_x_fixed': self.ir_offset_x_fixed,
                    'ir_offset_y_fixed': self.ir_offset_y_fixed,
                    'screen_width': self.system.screen_width,
                    'screen_height': self.system.screen_height,
                    'ir_width': IR_WIDTH,
                    'ir_height': IR_HEIGHT
                }
                result = self.system.person_detector.draw_bounding_boxes(result, person_boxes, self.system.current_mode, scale_settings)
        return result
    
    def apply_sharp_edge_detection(self, ir_gray):
        ir_gray_small = cv2.resize(ir_gray, (self.system.edge_width, self.system.edge_height))
        edges_small = cv2.Canny(ir_gray_small, self.system.edge_threshold_low, self.system.edge_threshold_high)
        return edges_small
    
    def apply_ai_detection_and_edge_overlay(self, thermal_background, ir_frame):
        if ir_frame is None:
            return thermal_background
        
        person_detected, person_boxes, person_mask = False, [], None
        if self.system.person_detection_enabled and self.system.person_detector.is_available():
            person_detected, person_boxes, _ = self.system.person_detector.detect_persons(ir_frame)
            if person_detected:
                person_mask = self.system.person_detector.create_person_mask(ir_frame, person_boxes)
        
        if self.should_show_edges():
            ir_gray = cv2.cvtColor(ir_frame, cv2.COLOR_BGR2GRAY)
            edges_configurable = self.apply_sharp_edge_detection(ir_gray)
            
            screen_scale_x = self.system.screen_width / IR_WIDTH
            screen_scale_y = self.system.screen_height / IR_HEIGHT
            final_ir_width = int(IR_WIDTH * self.ir_scale_fixed * screen_scale_x)
            final_ir_height = int(IR_HEIGHT * self.ir_scale_fixed * screen_scale_y)
            final_offset_x = int(self.ir_offset_x_fixed * screen_scale_x)
            final_offset_y = int(self.ir_offset_y_fixed * screen_scale_y)
            
            edges_final = cv2.resize(edges_configurable, (final_ir_width, final_ir_height))
            person_mask_final = cv2.resize(person_mask, (final_ir_width, final_ir_height)) if person_mask is not None else None
            
            start_x = max(0, final_offset_x)
            start_y = max(0, final_offset_y)
            end_x = min(self.system.screen_width, final_offset_x + final_ir_width)
            end_y = min(self.system.screen_height, final_offset_y + final_ir_height)
            
            src_start_x = max(0, -final_offset_x)
            src_start_y = max(0, -final_offset_y)
            src_end_x = src_start_x + (end_x - start_x)
            src_end_y = src_start_y + (end_y - start_y)
            
            if start_x < end_x and start_y < end_y and src_start_x < final_ir_width and src_start_y < final_ir_height:
                try:
                    edge_mask = edges_final[src_start_y:src_end_y, src_start_x:src_end_x] > 0
                    if np.any(edge_mask):
                        edge_color_bgr = self.get_current_mode_edge_color()
                        thermal_region = thermal_background[start_y:end_y, start_x:end_x]
                        
                        if person_detected and person_mask_final is not None:
                            person_region = person_mask_final[src_start_y:src_end_y, src_start_x:src_end_x] > 0
                            person_edge_mask = edge_mask & person_region
                            if np.any(person_edge_mask):
                                thermal_region[person_edge_mask] = [0, 255, 0]
                            
                            non_person_edge_mask = edge_mask & (~person_region)
                            if np.any(non_person_edge_mask):
                                thermal_region[non_person_edge_mask] = edge_color_bgr
                        else:
                            thermal_region[edge_mask] = edge_color_bgr
                        
                        thermal_background[start_y:end_y, start_x:end_x] = thermal_region
                except Exception:
                    pass
        
        if person_detected and person_boxes:
            scale_settings = {
                'ir_scale_fixed': self.ir_scale_fixed,
                'ir_offset_x_fixed': self.ir_offset_x_fixed,
                'ir_offset_y_fixed': self.ir_offset_y_fixed,
                'screen_width': self.system.screen_width,
                'screen_height': self.system.screen_height,
                'ir_width': IR_WIDTH,
                'ir_height': IR_HEIGHT
            }
            thermal_background = self.system.person_detector.draw_bounding_boxes(thermal_background, person_boxes, self.system.current_mode, scale_settings)
        
        return thermal_background
