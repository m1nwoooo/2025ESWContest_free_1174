import cv2
import numpy as np
import time

from config import *

try:
    from pycoral.utils.edgetpu import make_interpreter
    from pycoral.adapters import common, detect
    CORAL_AVAILABLE = True
except ImportError:
    CORAL_AVAILABLE = False

class PersonDetector:
    def __init__(self):
        self.coral_enabled = False
        self.interpreter = None
        self.person_detected = False
        self.person_boxes = []
        self.person_count = 0
        self.last_check = 0
        
        if CORAL_AVAILABLE:
            self.setup_coral()
    
    def setup_coral(self):
        try:
            self.interpreter = make_interpreter(CORAL_MODEL_PATH)
            self.interpreter.allocate_tensors()
            self.coral_enabled = True
        except Exception:
            self.coral_enabled = False
    
    def is_available(self):
        return self.coral_enabled
    
    def get_objects_compatible(self, interpreter, threshold=AI_CONFIDENCE_THRESHOLD):
        try:
            return detect.get_objects(interpreter, score_threshold=threshold)
        except TypeError:
            try:
                return detect.get_objects(interpreter, threshold=threshold)
            except TypeError:
                objects = detect.get_objects(interpreter)
                return [obj for obj in objects if obj.score >= threshold]
    
    def detect_persons(self, ir_frame):
        current_time = time.time()
        if current_time - self.last_check < AI_CHECK_INTERVAL:
            return self.person_detected, self.person_boxes, self.person_count
        
        if not self.coral_enabled or ir_frame is None:
            return False, [], 0
        
        try:
            original_height, original_width = ir_frame.shape[:2]
            
            resized = cv2.resize(ir_frame, (AI_MODEL_INPUT_SIZE, AI_MODEL_INPUT_SIZE))
            if len(resized.shape) == 2:
                resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
            
            input_data = np.expand_dims(resized, axis=0).astype(np.uint8)
            common.set_input(self.interpreter, input_data)
            self.interpreter.invoke()
            
            objects = self.get_objects_compatible(self.interpreter, AI_CONFIDENCE_THRESHOLD)
            persons = [obj for obj in objects if obj.id == 0]
            
            person_boxes = []
            for i, person in enumerate(persons):
                bbox = person.bbox
                
                scale_x = original_width / AI_MODEL_INPUT_SIZE
                scale_y = original_height / AI_MODEL_INPUT_SIZE
                
                x1 = int(bbox.xmin * scale_x)
                y1 = int(bbox.ymin * scale_y)
                x2 = int(bbox.xmax * scale_x)
                y2 = int(bbox.ymax * scale_y)
                
                x1 = max(0, min(x1, original_width - 1))
                y1 = max(0, min(y1, original_height - 1))
                x2 = max(x1 + 10, min(x2, original_width))
                y2 = max(y1 + 10, min(y2, original_height))
                
                box_width = x2 - x1
                box_height = y2 - y1
                
                if box_width < 5 or box_height < 5:
                    continue
                if box_width > original_width * 0.9 or box_height > original_height * 0.9:
                    continue
                
                person_boxes.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': person.score,
                    'width': box_width,
                    'height': box_height
                })
            
            self.person_detected = len(person_boxes) > 0
            self.person_boxes = person_boxes
            self.person_count = len(person_boxes)
            self.last_check = current_time
            
            return self.person_detected, self.person_boxes, self.person_count
            
        except Exception:
            return False, [], 0

    def create_person_mask(self, ir_frame, person_boxes):
        if not person_boxes or ir_frame is None:
            return None
        
        ir_height, ir_width = ir_frame.shape[:2]
        mask = np.zeros((ir_height, ir_width), dtype=np.uint8)
        
        for person in person_boxes:
            x1, y1, x2, y2 = person['bbox']
            x1 = max(0, min(x1, ir_width - 1))
            y1 = max(0, min(y1, ir_height - 1))
            x2 = max(x1, min(x2, ir_width))
            y2 = max(y1, min(y2, ir_height))
            
            mask[y1:y2, x1:x2] = 255
        
        return mask

    def draw_bounding_boxes(self, display_frame, person_boxes, current_mode, scale_settings):
        if not person_boxes or not self.person_detected:
            return display_frame
        
        try:
            screen_width = scale_settings.get('screen_width', 1920)
            screen_height = scale_settings.get('screen_height', 1080)
            ir_width = scale_settings.get('ir_width', 640)
            ir_height = scale_settings.get('ir_height', 480)
            ir_scale_fixed = scale_settings.get('ir_scale_fixed', 1.0)
            ir_offset_x_fixed = scale_settings.get('ir_offset_x_fixed', 0)
            ir_offset_y_fixed = scale_settings.get('ir_offset_y_fixed', 0)
            
            scaled_ir_width = int(ir_width * ir_scale_fixed)
            scaled_ir_height = int(ir_height * ir_scale_fixed)
            
            screen_scale_x = screen_width / ir_width
            screen_scale_y = screen_height / ir_height
            final_ir_width = int(scaled_ir_width * screen_scale_x)
            final_ir_height = int(scaled_ir_height * screen_scale_y)
            final_offset_x = int(ir_offset_x_fixed * screen_scale_x)
            final_offset_y = int(ir_offset_y_fixed * screen_scale_y)
            
            scale_x = (final_ir_width / ir_width)
            scale_y = (final_ir_height / ir_height)
            
            display_ir_x1 = final_offset_x
            display_ir_y1 = final_offset_y
            display_ir_x2 = final_offset_x + final_ir_width
            display_ir_y2 = final_offset_y + final_ir_height
            
            for i, person in enumerate(person_boxes):
                x1, y1, x2, y2 = person['bbox']
                
                display_x1 = int(x1 * scale_x) + final_offset_x
                display_y1 = int(y1 * scale_y) + final_offset_y
                display_x2 = int(x2 * scale_x) + final_offset_x
                display_y2 = int(y2 * scale_y) + final_offset_y
                
                if (display_x2 < display_ir_x1 or display_x1 > display_ir_x2 or 
                    display_y2 < display_ir_y1 or display_y1 > display_ir_y2):
                    continue
                
                display_x1 = max(0, min(display_x1, screen_width - 1))
                display_y1 = max(0, min(display_y1, screen_height - 1))
                display_x2 = max(display_x1 + 20, min(display_x2, screen_width))
                display_y2 = max(display_y1 + 20, min(display_y2, screen_height))
                
                box_color = (0, 255, 0)
                box_thickness = 6
                cv2.rectangle(display_frame, (display_x1, display_y1), (display_x2, display_y2), 
                              box_color, box_thickness)
                
                corner_length = 30
                corner_thickness = 8
                
                cv2.line(display_frame, (display_x1, display_y1), (display_x1 + corner_length, display_y1), box_color, corner_thickness)
                cv2.line(display_frame, (display_x1, display_y1), (display_x1, display_y1 + corner_length), box_color, corner_thickness)
                cv2.line(display_frame, (display_x2, display_y1), (display_x2 - corner_length, display_y1), box_color, corner_thickness)
                cv2.line(display_frame, (display_x2, display_y1), (display_x2, display_y1 + corner_length), box_color, corner_thickness)
                cv2.line(display_frame, (display_x1, display_y2), (display_x1 + corner_length, display_y2), box_color, corner_thickness)
                cv2.line(display_frame, (display_x1, display_y2), (display_x1, display_y2 - corner_length), box_color, corner_thickness)
                cv2.line(display_frame, (display_x2, display_y2), (display_x2 - corner_length, display_y2), box_color, corner_thickness)
                cv2.line(display_frame, (display_x2, display_y2), (display_x2, display_y2 - corner_length), box_color, corner_thickness)
                
        except Exception:
            pass
        
        return display_frame
