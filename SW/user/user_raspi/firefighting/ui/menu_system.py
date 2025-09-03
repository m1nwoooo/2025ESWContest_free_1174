import cv2
import numpy as np
import os

from config import *

class MenuSystem:
    def __init__(self, system):
        self.system = system
        self.menu_active = False
        self.current_menu = "main"
        self.selected_index = 0
        self.text_files_list = []
        self.current_text_content = ""
        self.current_text_scroll = 0
        
        self.BLUE_BG = (139, 69, 19)
        self.GRAY_BG = (128, 128, 128)
        self.RED_HIGHLIGHT = (0, 0, 255)
        self.WHITE_TEXT = (255, 255, 255)
        self.BLACK_TEXT = (0, 0, 0)
        
        self.FONT_SCALE_LARGE = 1.4
        self.FONT_SCALE_MEDIUM = 1.1
        self.FONT_SCALE_SMALL = 0.9
        self.FONT_THICKNESS = 2
        
        self.main_menu_items = [
            "1 Text Files      Read text files from directory",
            "2 Color Settings    Customize edge and thermal colors", 
            "3 Person Detection  Toggle person detection ON/OFF",
            "4 Edge Resolution   Select edge quality vs performance",
            "5 Edge Threshold    Adjust edge detection sensitivity",
            "6 Temperature       Temperature mode toggle",
            "7 Power Off         Shutdown the system"
        ]
        
        self.color_menu_items = [
            "1 Search Mode Edge    Set edge color for search mode",
            "2 Cold Mode Edge      Set edge color for cold mode",
            "3 Edge Overlay Edge   Set edge color for edge overlay",
            "4 Thermal Colormap    Select thermal color scheme",
            "5 Back to Main        Return to main menu"
        ]
        
        self.edge_threshold_menu_items = [
            "1 Low Threshold     Adjust minimum edge sensitivity",
            "2 High Threshold      Adjust maximum edge sensitivity", 
            "3 Reset to Default    Reset both thresholds to default",
            "4 Back to Main        Return to main menu"
        ]
        
        self.power_off_options = [
            "Yes - Power off the system",
            "No - Return to main menu"
        ]
        
        self.color_options = [
            ("White", [255, 255, 255]),
            ("Black", [0, 0, 0]),
            ("Red", [0, 0, 255]),
            ("Green", [0, 255, 0]),
            ("Blue", [255, 0, 0]),
            ("Yellow", [0, 255, 255]),
            ("Cyan", [255, 255, 0]),
            ("Magenta", [255, 0, 255])
        ]
        
        self.refresh_text_files()
    
    def is_active(self):
        return self.menu_active
    
    def toggle(self):
        self.menu_active = not self.menu_active
        if self.menu_active:
            self.current_menu = "main"
            self.selected_index = 0
    
    def refresh_text_files(self):
        try:
            if os.path.exists(TEXT_FILES_DIR):
                files = [f for f in os.listdir(TEXT_FILES_DIR) if f.endswith('.txt')]
                files_with_time = [(f, os.path.getmtime(os.path.join(TEXT_FILES_DIR, f))) for f in files]
                files_sorted = sorted(files_with_time, key=lambda x: x[1], reverse=True)
                self.text_files_list = [f[0] for f in files_sorted]
            else:
                os.makedirs(TEXT_FILES_DIR, exist_ok=True)
                self.text_files_list = []
        except Exception:
            self.text_files_list = []
    
    def load_text_file(self, filename):
        try:
            filepath = os.path.join(TEXT_FILES_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                self.current_text_content = f.read()
            self.current_text_scroll = 0
            return True
        except Exception as e:
            self.current_text_content = f"Error loading file: {e}"
            self.current_text_scroll = 0
            return False
    
    def navigate_up(self):
        if not self.menu_active:
            return
            
        if self.current_menu == "main":
            num_items = len(self.main_menu_items) + 1
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu == "text_files":
            num_items = len(self.text_files_list) + 2
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu == "color_settings":
            num_items = len(self.color_menu_items) + 1
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu == "edge_threshold":
            num_items = len(self.edge_threshold_menu_items) + 1
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu == "text_view":
            self.current_text_scroll = max(0, self.current_text_scroll - 1)
        elif self.current_menu == "edge_resolution":
            num_items = len(EDGE_RESOLUTION_OPTIONS) + 2
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu == "power_off":
            num_items = len(self.power_off_options) + 1
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu.startswith("color_edit_"):
            num_items = len(self.color_options) + 1
            self.selected_index = (self.selected_index - 1 + num_items) % num_items
        elif self.current_menu.startswith("threshold_edit_"):
            self.adjust_threshold(1)
    
    def navigate_down(self):
        if not self.menu_active:
            return
            
        if self.current_menu == "main":
            num_items = len(self.main_menu_items) + 1
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu == "text_files":
            num_items = len(self.text_files_list) + 2
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu == "color_settings":
            num_items = len(self.color_menu_items) + 1
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu == "edge_threshold":
            num_items = len(self.edge_threshold_menu_items) + 1
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu == "text_view":
            max_scroll = max(0, len(self.current_text_content.split('\n')) - 8)
            self.current_text_scroll = min(max_scroll, self.current_text_scroll + 1)
        elif self.current_menu == "edge_resolution":
            num_items = len(EDGE_RESOLUTION_OPTIONS) + 2
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu == "power_off":
            num_items = len(self.power_off_options) + 1
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu.startswith("color_edit_"):
            num_items = len(self.color_options) + 1
            self.selected_index = (self.selected_index + 1) % num_items
        elif self.current_menu.startswith("threshold_edit_"):
            self.adjust_threshold(-1)
    
    def adjust_threshold(self, direction):
        if self.current_menu == "threshold_edit_low":
            self.system.edge_threshold_low = max(1, min(100, self.system.edge_threshold_low + direction * 5))
        elif self.current_menu == "threshold_edit_high":
            self.system.edge_threshold_high = max(10, min(255, self.system.edge_threshold_high + direction * 5))
    
    def confirm_selection(self):
        if not self.menu_active:
            return

        if self.current_menu == "main":
            quit_index = len(self.main_menu_items)
            if self.selected_index == quit_index:
                self.menu_active = False
                return

            if self.selected_index == 0:
                self.current_menu = "text_files"
                self.selected_index = 0
                self.refresh_text_files()
            elif self.selected_index == 1:
                self.current_menu = "color_settings"
                self.selected_index = 0
            elif self.selected_index == 2:
                self.system.person_detection_enabled = not self.system.person_detection_enabled
            elif self.selected_index == 3:
                self.current_menu = "edge_resolution"
                self.selected_index = self.system.current_edge_resolution_index
            elif self.selected_index == 4:
                self.current_menu = "edge_threshold"
                self.selected_index = 0
            elif self.selected_index == 5:
                self.system.toggle_temperature_mode()
            elif self.selected_index == 6:
                self.current_menu = "power_off"
                self.selected_index = 0
        
        elif self.current_menu == "text_files":
            back_index = len(self.text_files_list)
            quit_index = back_index + 1
            if self.selected_index == quit_index:
                self.menu_active = False
                return

            if self.selected_index < len(self.text_files_list):
                filename = self.text_files_list[self.selected_index]
                if self.load_text_file(filename):
                    self.current_menu = "text_view"
            elif self.selected_index == back_index:
                self.current_menu = "main"
                self.selected_index = 0
        
        elif self.current_menu == "color_settings":
            quit_index = len(self.color_menu_items)
            if self.selected_index == quit_index:
                self.menu_active = False
                return

            if self.selected_index < 3:
                self.current_menu = f"color_edit_{self.selected_index}"
                self.selected_index = 0
            elif self.selected_index == 3:
                self.system.current_thermal_colormap = (self.system.current_thermal_colormap + 1) % len(THERMAL_COLORMAPS)
            elif self.selected_index == 4:
                self.current_menu = "main"
                self.selected_index = 1
        
        elif self.current_menu == "edge_threshold":
            quit_index = len(self.edge_threshold_menu_items)
            if self.selected_index == quit_index:
                self.menu_active = False
                return

            if self.selected_index == 0:
                self.current_menu = "threshold_edit_low"
            elif self.selected_index == 1:
                self.current_menu = "threshold_edit_high"
            elif self.selected_index == 2:
                self.system.edge_threshold_low = DEFAULT_EDGE_THRESHOLD_LOW
                self.system.edge_threshold_high = DEFAULT_EDGE_THRESHOLD_HIGH
            elif self.selected_index == 3:
                self.current_menu = "main"
                self.selected_index = 4
        
        elif self.current_menu.startswith("threshold_edit_"):
            self.current_menu = "edge_threshold"
            if "low" in self.current_menu:
                self.selected_index = 0
            else:
                self.selected_index = 1
        
        elif self.current_menu == "text_view":
            self.current_menu = "text_files"
            self.selected_index = 0
        
        elif self.current_menu == "edge_resolution":
            back_index = len(EDGE_RESOLUTION_OPTIONS)
            quit_index = back_index + 1
            if self.selected_index == quit_index:
                self.menu_active = False
                return

            if self.selected_index < len(EDGE_RESOLUTION_OPTIONS):
                resolution_name, width, height, description = EDGE_RESOLUTION_OPTIONS[self.selected_index]
                self.system.current_edge_resolution_index = self.selected_index
                self.system.edge_width = width
                self.system.edge_height = height
                self.current_menu = "main"
                self.selected_index = 3
            elif self.selected_index == back_index:
                self.current_menu = "main"
                self.selected_index = 3
        
        elif self.current_menu == "power_off":
            finish_index = len(self.power_off_options)
            if self.selected_index == finish_index:
                self.system.running = False
                return

            if self.selected_index == 0:
                self.system.running = False
                try:
                    import subprocess
                    subprocess.run(['sudo', 'poweroff'], check=False)
                except Exception:
                    pass
            elif self.selected_index == 1:
                self.current_menu = "main"
                self.selected_index = 6
        
        elif self.current_menu.startswith("color_edit_"):
            finish_index = len(self.color_options)
            if self.selected_index == finish_index:
                self.system.running = False
                return

            mode_index = int(self.current_menu.split("_")[-1])
            color_name, color_bgr = self.color_options[self.selected_index]
            MODE_EDGE_COLORS[mode_index] = color_bgr
            self.current_menu = "color_settings"
            self.selected_index = mode_index
    
    def render(self, width, height):
        if not self.menu_active:
            return None
        
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:, :] = self.BLUE_BG
        
        margin_y = int(height * 0.1)
        margin_x = int(width * 0.05)
        cv2.rectangle(frame, (margin_x, margin_y), (width - margin_x, height - margin_y), self.GRAY_BG, -1)
        
        title_height = int(height * 0.15)
        cv2.rectangle(frame, (margin_x, margin_y), (width - margin_x, margin_y + title_height), self.BLUE_BG, -1)
        
        button_height = int(height * 0.1)
        button_y = height - margin_y - button_height
        cv2.rectangle(frame, (margin_x, button_y), (width - margin_x, height - margin_y), self.BLUE_BG, -1)
        
        content_start_y = margin_y + title_height + 50
        content_width = width - 2 * margin_x - 100
        
        if self.current_menu == "main":
            self.draw_main_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "text_files":
            self.draw_text_files_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "color_settings":
            self.draw_color_settings_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "edge_threshold":
            self.draw_edge_threshold_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu.startswith("threshold_edit_"):
            self.draw_threshold_edit_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "text_view":
            self.draw_text_view(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "edge_resolution":
            self.draw_edge_resolution_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "power_off":
            self.draw_power_off_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu.startswith("color_edit_"):
            self.draw_color_edit_menu(frame, margin_x + 50, content_start_y, content_width)
        
        self.draw_title(frame, margin_x + 50, margin_y + 50)
        self.draw_bottom_buttons(frame, button_y + 30, width)
        
        return frame
    
    def draw_title(self, frame, x, y):
        titles = {
            "main": "Firefighting Thermal System Configuration Tool",
            "text_files": "Text File Viewer",
            "color_settings": "Color Settings Configuration", 
            "edge_threshold": "Edge Detection Threshold Settings",
            "threshold_edit_low": "Adjust Low Threshold (Edge Sensitivity)",
            "threshold_edit_high": "Adjust High Threshold (Edge Sensitivity)",
            "text_view": "Text File Content",
            "edge_resolution": "Edge Processing Resolution Settings",
            "power_off": "System Power Off Confirmation",
        }
        
        if self.current_menu.startswith("color_edit_"):
            mode_names = ["Search Mode", "Cold Mode", "Edge Overlay"]
            mode_index = int(self.current_menu.split("_")[-1])
            title = f"{mode_names[mode_index]} Edge Color Selection"
        else:
            title = titles.get(self.current_menu, "Settings")
        
        cv2.putText(frame, title, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, self.WHITE_TEXT, self.FONT_THICKNESS)
    
    def draw_bottom_buttons(self, frame, y, width):
        cv2.putText(frame, "<Select>", (100, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_SMALL, self.WHITE_TEXT, self.FONT_THICKNESS)
        
        quit_text = "<Quit>"
        text_size = cv2.getTextSize(quit_text, cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_SMALL, self.FONT_THICKNESS)[0]
        quit_x = width - text_size[0] - 100

        is_quit_selected = self.is_quit_button_selected()

        quit_highlight_color = (255, 165, 0)
        if is_quit_selected:
            cv2.rectangle(frame, (quit_x - 20, y - 25), (quit_x + text_size[0] + 20, y + 10), quit_highlight_color, -1)

        cv2.putText(frame, quit_text, (quit_x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_SMALL, self.WHITE_TEXT, self.FONT_THICKNESS)
    
    def is_quit_button_selected(self):
        if self.current_menu == "main" and self.selected_index == len(self.main_menu_items):
            return True
        elif self.current_menu == "text_files" and self.selected_index == len(self.text_files_list) + 1:
            return True
        elif self.current_menu == "color_settings" and self.selected_index == len(self.color_menu_items):
            return True
        elif self.current_menu == "edge_threshold" and self.selected_index == len(self.edge_threshold_menu_items):
            return True
        elif self.current_menu == "edge_resolution" and self.selected_index == len(EDGE_RESOLUTION_OPTIONS) + 1:
            return True
        elif self.current_menu == "power_off" and self.selected_index == len(self.power_off_options):
            return True
        elif self.current_menu.startswith("color_edit_") and self.selected_index == len(self.color_options):
            return True
        return False
    
    def draw_main_menu(self, frame, x, y, width):
        line_height = 70
        
        for i, item in enumerate(self.main_menu_items):
            current_y = y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 40), (x + width, current_y + 20), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
            
            display_text = item
            if "Person Detection" in item:
                status = "ON" if self.system.person_detection_enabled else "OFF"
                display_text = f"{item}    [{status}]"
            elif "Edge Resolution" in item:
                current_resolution = EDGE_RESOLUTION_OPTIONS[self.system.current_edge_resolution_index]
                resolution_name = current_resolution[0]
                display_text = f"{item}    [{resolution_name}]"
            elif "Edge Threshold" in item:
                display_text = f"{item}    [L:{self.system.edge_threshold_low} H:{self.system.edge_threshold_high}]"
            elif "Temperature" in item:
                temp_status = "ON" if self.system.temperature_mode else "OFF"
                display_text = f"{item}    [Mode: {temp_status}]"

            cv2.putText(frame, display_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_LARGE, text_color, self.FONT_THICKNESS)
    
    def draw_text_files_menu(self, frame, x, y, width):
        line_height = 60
        current_y = y
        
        if len(self.text_files_list) == 0:
            cv2.putText(frame, "No text files found in directory:", (x, current_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
            current_y += line_height
            cv2.putText(frame, TEXT_FILES_DIR, (x, current_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_SMALL, self.BLACK_TEXT, self.FONT_THICKNESS)
        else:
            for i, filename in enumerate(self.text_files_list):
                if i == self.selected_index:
                    cv2.rectangle(frame, (x - 20, current_y - 30), (x + width, current_y + 15), self.RED_HIGHLIGHT, -1)
                    text_color = self.WHITE_TEXT
                else:
                    text_color = self.BLACK_TEXT
                
                display_name = filename if len(filename) <= 40 else filename[:37] + "..."
                menu_text = f"{i+1} {display_name}"
                cv2.putText(frame, menu_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                            self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
                current_y += line_height
        
        back_index = len(self.text_files_list)
        if back_index == self.selected_index:
            cv2.rectangle(frame, (x - 20, current_y - 30), (x + width, current_y + 15), self.RED_HIGHLIGHT, -1)
            text_color = self.WHITE_TEXT
        else:
            text_color = self.BLACK_TEXT
        
        cv2.putText(frame, f"{back_index+1} Back to Main Menu", (x, current_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
    
    def draw_text_view(self, frame, x, y, width):
        lines = self.current_text_content.split('\n')
        visible_lines = 8
        line_height = 50
        
        start_line = self.current_text_scroll
        end_line = min(len(lines), start_line + visible_lines)
        
        for i in range(start_line, end_line):
            line = lines[i]
            if len(line) > 70:
                line = line[:67] + "..."
            
            current_y = y + (i - start_line) * line_height
            cv2.putText(frame, line, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_SMALL, self.BLACK_TEXT, self.FONT_THICKNESS)
    
    def draw_color_settings_menu(self, frame, x, y, width):
        line_height = 60
        
        for i, item in enumerate(self.color_menu_items):
            current_y = y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 30), (x + width, current_y + 15), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
            
            if i < 3:
                current_color = MODE_EDGE_COLORS.get(i, [255, 255, 255])
                color_name = next((name for name, bgr in self.color_options if bgr == current_color), "Custom")
                display_text = f"{item}    [{color_name}]"
            elif i == 3:
                colormap_name, _ = THERMAL_COLORMAPS[self.system.current_thermal_colormap]
                display_text = f"{item}    [{colormap_name}]"
            else:
                display_text = item
            
            cv2.putText(frame, display_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
    
    def draw_edge_threshold_menu(self, frame, x, y, width):
        header_text = "Configure Edge Detection Sensitivity (Canny Algorithm):"
        cv2.putText(frame, header_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        line_height = 80
        start_y = y + 60
        
        for i, item in enumerate(self.edge_threshold_menu_items):
            current_y = start_y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 40), (x + width, current_y + 35), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
                desc_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
                desc_color = self.BLACK_TEXT
            
            display_text = item
            if "Low Threshold" in item:
                display_text = f"{item}    [Current: {self.system.edge_threshold_low}]"
            elif "High Threshold" in item:
                display_text = f"{item}    [Current: {self.system.edge_threshold_high}]"
            
            cv2.putText(frame, display_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_LARGE, text_color, self.FONT_THICKNESS)
            
            descriptions = [
                "Lower values = more sensitive (more edges detected)",
                "Higher values = less sensitive (fewer edges detected)", 
                "Reset Low: 70, High: 130 (recommended defaults)",
                "Return to main configuration menu"
            ]
            if i < len(descriptions):
                description_y = current_y + 30
                cv2.putText(frame, f"    {descriptions[i]}", (x, description_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           self.FONT_SCALE_MEDIUM, desc_color, self.FONT_THICKNESS)
    
    def draw_threshold_edit_menu(self, frame, x, y, width):
        threshold_type = "Low" if "low" in self.current_menu else "High"
        current_value = self.system.edge_threshold_low if "low" in self.current_menu else self.system.edge_threshold_high
        
        title_text = f"Adjusting {threshold_type} Threshold"
        cv2.putText(frame, title_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_LARGE, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        value_y = y + 100
        value_text = f"Current Value: {current_value}"
        cv2.putText(frame, value_text, (x, value_y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_LARGE, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        range_y = value_y + 60
        if "low" in self.current_menu:
            range_text = "Valid Range: 1 - 100 (Lower = more sensitive)"
        else:
            range_text = "Valid Range: 10 - 255 (Higher = less sensitive)"
        cv2.putText(frame, range_text, (x, range_y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        instruction_y = range_y + 80
        instructions = [
            "Use Up/Down buttons to adjust value (±5 per press)",
            "Press Select to return to threshold menu",
            "Changes are applied immediately"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (x, instruction_y + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 
                       self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
    
    def draw_edge_resolution_menu(self, frame, x, y, width):
        header_text = "Select Edge Processing Resolution (Performance vs Quality):"
        cv2.putText(frame, header_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        line_height = 80
        start_y = y + 60
        
        for i, (resolution_name, width_val, height_val, description) in enumerate(EDGE_RESOLUTION_OPTIONS):
            current_y = start_y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 40), (x + width, current_y + 35), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
                desc_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
                desc_color = self.BLACK_TEXT
            
            current_indicator = " [CURRENT]" if i == self.system.current_edge_resolution_index else ""
            main_text = f"{i+1} {resolution_name}{current_indicator}"
            cv2.putText(frame, main_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_LARGE, text_color, self.FONT_THICKNESS)
            
            description_y = current_y + 30
            cv2.putText(frame, f"    {description}", (x, description_y), cv2.FONT_HERSHEY_SIMPLEX, 
                       self.FONT_SCALE_MEDIUM, desc_color, self.FONT_THICKNESS)
        
        # Add Back to Main button
        back_index = len(EDGE_RESOLUTION_OPTIONS)
        back_y = start_y + back_index * line_height
        
        if back_index == self.selected_index:
            cv2.rectangle(frame, (x - 20, back_y - 40), (x + width, back_y + 20), self.RED_HIGHLIGHT, -1)
            text_color = self.WHITE_TEXT
        else:
            text_color = self.BLACK_TEXT
        
        cv2.putText(frame, f"{back_index+1} Back to Main Menu", (x, back_y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
        
        # Add Back to Main button
        back_index = len(EDGE_RESOLUTION_OPTIONS)
        back_y = start_y + back_index * line_height
        
        if back_index == self.selected_index:
            cv2.rectangle(frame, (x - 20, back_y - 40), (x + width, back_y + 20), self.RED_HIGHLIGHT, -1)
            text_color = self.WHITE_TEXT
        else:
            text_color = self.BLACK_TEXT
        
        cv2.putText(frame, f"{back_index+1} Back to Main Menu", (x, back_y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
    
    def draw_power_off_menu(self, frame, x, y, width):
        cv2.putText(frame, "Are you sure you want to power off the system?", (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_LARGE, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        line_height = 80
        start_y = y + 80
        
        for i, option in enumerate(self.power_off_options):
            current_y = start_y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 40), (x + width, current_y + 20), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
            
            cv2.putText(frame, option, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
    
    def draw_color_edit_menu(self, frame, x, y, width):
        line_height = 60
        
        for i, (color_name, color_bgr) in enumerate(self.color_options):
            current_y = y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 30), (x + width, current_y + 15), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
            
            sample_x = x + 300
            sample_y = current_y - 20
            cv2.rectangle(frame, (sample_x, sample_y), (sample_x + 60, sample_y + 30), color_bgr, -1)
            cv2.rectangle(frame, (sample_x, sample_y), (sample_x + 60, sample_y + 30), self.BLACK_TEXT, 2)
            
            menu_text = f"{i+1} {color_name}"
            cv2.putText(frame, menu_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)
