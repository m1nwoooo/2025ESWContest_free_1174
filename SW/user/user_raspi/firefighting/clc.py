#!/usr/bin/env python3
"""
Final Production Version: Firefighting Thermal-IR Fusion System
Features: Optimized edge detection, AI person detection, Simple temperature integration.
This version is cleaned for submission, removing all debugging prints and terminal command inputs.
Control is handled exclusively via GPIO buttons and the on-screen UI.
"""

# ===== IMPORTS =====
import cv2
import subprocess
import numpy as np
import time
import threading
from queue import Queue, Empty
import os
import signal
import sys
import select
import termios
import tty
from collections import deque
import serial
import struct

# Coral AI imports
try:
    from pycoral.utils.edgetpu import make_interpreter
    from pycoral.adapters import common, detect
    CORAL_AVAILABLE = True
except ImportError:
    CORAL_AVAILABLE = False

# GPIO imports
try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

# ===== SETTING MENU UI CLASS =====
class SettingMenuUI:
    def __init__(self, parent_system):
        self.parent = parent_system
        self.menu_active = False
        self.current_menu = "main"
        self.selected_index = 0
        self.text_files_dir = "/home/a/Desktop/text_files"
        self.current_text_content = ""
        self.current_text_scroll = 0
        
        # UI colors (raspi-config style)
        self.BLUE_BG = (139, 69, 19)
        self.GRAY_BG = (128, 128, 128)
        self.RED_HIGHLIGHT = (0, 0, 255)
        self.WHITE_TEXT = (255, 255, 255)
        self.BLACK_TEXT = (0, 0, 0)
        
        # Font settings
        self.FONT_SCALE_LARGE = 1.4
        self.FONT_SCALE_MEDIUM = 1.1
        self.FONT_SCALE_SMALL = 0.9
        self.FONT_THICKNESS = 2
        
        # Menu structure
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
        
        self.edge_resolution_options = [
            ("1600x900", 1600, 900, "HIGH PERFORMANCE - Fastest processing"),
            ("1920x1080", 1920, 1080, "BALANCED - Good speed and quality"),
            ("2240x1260", 2240, 1260, "ENHANCED - Better quality, slower"),
            ("2560x1440", 2560, 1440, "HIGH QUALITY - Detailed edges, moderate speed"),
            ("2880x1620", 2880, 1620, "ULTRA QUALITY - Very detailed, slower"),
            ("3200x1800", 3200, 1800, "MAXIMUM QUALITY - Best edges, slowest")
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
        
        self.text_files_list = []
        self.refresh_text_files()

    def refresh_text_files(self):
        """Refresh text file list"""
        try:
            if os.path.exists(self.text_files_dir):
                files = [f for f in os.listdir(self.text_files_dir) if f.endswith('.txt')]
                files_with_time = [(f, os.path.getmtime(os.path.join(self.text_files_dir, f))) for f in files]
                files_sorted = sorted(files_with_time, key=lambda x: x[1], reverse=True)
                self.text_files_list = [f[0] for f in files_sorted]
            else:
                os.makedirs(self.text_files_dir, exist_ok=True)
                self.text_files_list = []
        except Exception:
            self.text_files_list = []

    def load_text_file(self, filename):
        """Load text file"""
        try:
            filepath = os.path.join(self.text_files_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                self.current_text_content = f.read()
            self.current_text_scroll = 0
            return True
        except Exception as e:
            self.current_text_content = f"Error loading file: {e}"
            self.current_text_scroll = 0
            return False

    def toggle_menu(self):
        """Toggle menu"""
        self.menu_active = not self.menu_active
        if self.menu_active:
            self.current_menu = "main"
            self.selected_index = 0

    def navigate_up(self):
        """Move up"""
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
            num_items = len(self.edge_resolution_options) + 1
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
        """Move down"""
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
            num_items = len(self.edge_resolution_options) + 1
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
        """Adjust threshold values"""
        if self.current_menu == "threshold_edit_low":
            self.parent.edge_threshold_low = max(1, min(100, self.parent.edge_threshold_low + direction * 5))
        elif self.current_menu == "threshold_edit_high":
            self.parent.edge_threshold_high = max(10, min(255, self.parent.edge_threshold_high + direction * 5))

    def confirm_selection(self):
        """Confirm selection"""
        if not self.menu_active:
            return

        if self.current_menu == "main":
            quit_index = len(self.main_menu_items)
            if self.selected_index == quit_index:
                self.menu_active = False
                return

            if self.selected_index == 0:  # Text Files
                self.current_menu = "text_files"
                self.selected_index = 0
                self.refresh_text_files()
            elif self.selected_index == 1:  # Color Settings
                self.current_menu = "color_settings"
                self.selected_index = 0
            elif self.selected_index == 2:  # Person Detection
                self.parent.person_detection_enabled = not self.parent.person_detection_enabled
            elif self.selected_index == 3:  # Edge Resolution
                self.current_menu = "edge_resolution"
                self.selected_index = self.parent.current_edge_resolution_index
            elif self.selected_index == 4:  # Edge Threshold
                self.current_menu = "edge_threshold"
                self.selected_index = 0
            elif self.selected_index == 5:  # Temperature
                self.parent.toggle_temperature_mode()
            elif self.selected_index == 6:  # Power Off
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
                self.parent.current_thermal_colormap = (self.parent.current_thermal_colormap + 1) % len(self.parent.thermal_colormaps)
            elif self.selected_index == 4:
                self.current_menu = "main"
                self.selected_index = 0
        
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
                self.parent.edge_threshold_low = 70
                self.parent.edge_threshold_high = 130
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
            finish_index = len(self.edge_resolution_options)
            if self.selected_index == finish_index:
                self.parent.running = False
                return

            if self.selected_index < len(self.edge_resolution_options):
                resolution_name, width, height, description = self.edge_resolution_options[self.selected_index]
                self.parent.current_edge_resolution_index = self.selected_index
                self.parent.EDGE_WIDTH = width
                self.parent.EDGE_HEIGHT = height
                self.current_menu = "main"
                self.selected_index = 3
        
        elif self.current_menu == "power_off":
            finish_index = len(self.power_off_options)
            if self.selected_index == finish_index:
                self.parent.running = False
                return

            if self.selected_index == 0:  # Yes - Power off
                self.parent.running = False
                try:
                    subprocess.run(['sudo', 'poweroff'], check=False)
                except Exception:
                    pass
            elif self.selected_index == 1:  # No - Return to main menu
                self.current_menu = "main"
                self.selected_index = 0
        
        elif self.current_menu.startswith("color_edit_"):
            finish_index = len(self.color_options)
            if self.selected_index == finish_index:
                self.parent.running = False
                return

            mode_index = int(self.current_menu.split("_")[-1])
            color_name, color_bgr = self.color_options[self.selected_index]
            self.parent.MODE_EDGE_COLORS[mode_index] = color_bgr
            self.current_menu = "color_settings"
            self.selected_index = mode_index

    def create_full_screen_menu(self, width, height):
        """Create full screen menu"""
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
            self._draw_raspi_main_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "text_files":
            self._draw_raspi_text_files_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "color_settings":
            self._draw_raspi_color_settings_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "edge_threshold":
            self._draw_raspi_edge_threshold_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu.startswith("threshold_edit_"):
            self._draw_raspi_threshold_edit_menu(frame, margin_x + 50, content_start_y, content_width, height - content_start_y - button_height - 50)
        elif self.current_menu == "text_view":
            self._draw_raspi_text_view(frame, margin_x + 50, content_start_y, content_width, height - content_start_y - button_height - 50)
        elif self.current_menu == "edge_resolution":
            self._draw_raspi_edge_resolution_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu == "power_off":
            self._draw_raspi_power_off_menu(frame, margin_x + 50, content_start_y, content_width)
        elif self.current_menu.startswith("color_edit_"):
            self._draw_raspi_color_edit_menu(frame, margin_x + 50, content_start_y, content_width)
        
        self._draw_title(frame, margin_x + 50, margin_y + 50)
        self._draw_bottom_buttons(frame, button_y + 30, width)
        
        return frame

    def _draw_title(self, frame, x, y):
        """Draw title"""
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

    def _draw_bottom_buttons(self, frame, y, width):
        """Draw bottom buttons"""
        cv2.putText(frame, "<Select>", (100, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_SMALL, self.WHITE_TEXT, self.FONT_THICKNESS)
        
        quit_text = "<Quit>"
        text_size = cv2.getTextSize(quit_text, cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_SMALL, self.FONT_THICKNESS)[0]
        quit_x = width - text_size[0] - 100

        is_quit_selected = False
        if self.current_menu == "main" and self.selected_index == len(self.main_menu_items):
            is_quit_selected = True
        elif self.current_menu == "text_files" and self.selected_index == len(self.text_files_list) + 1:
            is_quit_selected = True
        elif self.current_menu == "color_settings" and self.selected_index == len(self.color_menu_items):
            is_quit_selected = True
        elif self.current_menu == "edge_threshold" and self.selected_index == len(self.edge_threshold_menu_items):
            is_quit_selected = True
        elif self.current_menu == "edge_resolution" and self.selected_index == len(self.edge_resolution_options):
            is_quit_selected = True
        elif self.current_menu == "power_off" and self.selected_index == len(self.power_off_options):
            is_quit_selected = True
        elif self.current_menu.startswith("color_edit_") and self.selected_index == len(self.color_options):
            is_quit_selected = True

        quit_highlight_color = (255, 165, 0)
        if is_quit_selected:
            cv2.rectangle(frame, (quit_x - 20, y - 25), (quit_x + text_size[0] + 20, y + 10), quit_highlight_color, -1)

        cv2.putText(frame, quit_text, (quit_x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_SMALL, self.WHITE_TEXT, self.FONT_THICKNESS)

    def _draw_raspi_main_menu(self, frame, x, y, width):
        """Draw main menu"""
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
                status = "ON" if self.parent.person_detection_enabled else "OFF"
                display_text = f"{item}    [{status}]"
            elif "Edge Resolution" in item:
                current_resolution = self.edge_resolution_options[self.parent.current_edge_resolution_index]
                resolution_name = current_resolution[0]
                display_text = f"{item}    [{resolution_name}]"
            elif "Edge Threshold" in item:
                display_text = f"{item}    [L:{self.parent.edge_threshold_low} H:{self.parent.edge_threshold_high}]"
            elif "Temperature" in item:
                temp_status = "ON" if self.parent.temperature_mode else "OFF"
                display_text = f"{item}    [Mode: {temp_status}]"

            cv2.putText(frame, display_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_LARGE, text_color, self.FONT_THICKNESS)

    def _draw_raspi_text_files_menu(self, frame, x, y, width):
        """Draw text files menu"""
        line_height = 60
        current_y = y
        
        if len(self.text_files_list) == 0:
            cv2.putText(frame, "No text files found in directory:", (x, current_y), 
                        cv2.FONT_HERSHEY_SIMPLEX, self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
            current_y += line_height
            cv2.putText(frame, self.text_files_dir, (x, current_y), 
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

    def _draw_raspi_color_settings_menu(self, frame, x, y, width):
        """Draw color settings menu"""
        line_height = 60
        
        for i, item in enumerate(self.color_menu_items):
            current_y = y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 30), (x + width, current_y + 15), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
            
            if i < 3:
                current_color = self.parent.MODE_EDGE_COLORS.get(i, [255, 255, 255])
                color_name = next((name for name, bgr in self.color_options if bgr == current_color), "Custom")
                display_text = f"{item}    [{color_name}]"
            elif i == 3:
                colormap_name, _ = self.parent.thermal_colormaps[self.parent.current_thermal_colormap]
                display_text = f"{item}    [{colormap_name}]"
            else:
                display_text = item
            
            cv2.putText(frame, display_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_MEDIUM, text_color, self.FONT_THICKNESS)

    def _draw_raspi_edge_threshold_menu(self, frame, x, y, width):
        """Draw edge threshold menu"""
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
            else:
                text_color = self.BLACK_TEXT
            
            display_text = item
            if "Low Threshold" in item:
                display_text = f"{item}    [Current: {self.parent.edge_threshold_low}]"
            elif "High Threshold" in item:
                display_text = f"{item}    [Current: {self.parent.edge_threshold_high}]"
            
            cv2.putText(frame, display_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_LARGE, text_color, self.FONT_THICKNESS)

    def _draw_raspi_threshold_edit_menu(self, frame, x, y, width, height):
        """Draw threshold editing interface"""
        threshold_type = "Low" if "low" in self.current_menu else "High"
        current_value = self.parent.edge_threshold_low if "low" in self.current_menu else self.parent.edge_threshold_high
        
        title_text = f"Adjusting {threshold_type} Threshold"
        cv2.putText(frame, title_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_LARGE, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        value_y = y + 100
        value_text = f"Current Value: {current_value}"
        cv2.putText(frame, value_text, (x, value_y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_LARGE, self.BLACK_TEXT, self.FONT_THICKNESS)

    def _draw_raspi_color_edit_menu(self, frame, x, y, width):
        """Draw color edit menu"""
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

    def _draw_raspi_text_view(self, frame, x, y, width, height):
        """Draw text view"""
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

    def _draw_raspi_power_off_menu(self, frame, x, y, width):
        """Draw power off menu"""
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

    def _draw_raspi_edge_resolution_menu(self, frame, x, y, width):
        """Draw edge resolution menu"""
        header_text = "Select Edge Processing Resolution (Performance vs Quality):"
        cv2.putText(frame, header_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    self.FONT_SCALE_MEDIUM, self.BLACK_TEXT, self.FONT_THICKNESS)
        
        line_height = 80
        start_y = y + 60
        
        for i, (resolution_name, width_val, height_val, description) in enumerate(self.edge_resolution_options):
            current_y = start_y + i * line_height
            
            if i == self.selected_index:
                cv2.rectangle(frame, (x - 20, current_y - 40), (x + width, current_y + 35), self.RED_HIGHLIGHT, -1)
                text_color = self.WHITE_TEXT
            else:
                text_color = self.BLACK_TEXT
            
            current_indicator = " [CURRENT]" if i == self.parent.current_edge_resolution_index else ""
            main_text = f"{i+1} {resolution_name}{current_indicator}"
            cv2.putText(frame, main_text, (x, current_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        self.FONT_SCALE_LARGE, text_color, self.FONT_THICKNESS)

class FirefightingAI:
    def __init__(self):
        self.coral_enabled = False
        self.interpreter = None
        self.person_detected = False
        self.person_boxes = []
        self.person_count = 0
        self.last_check = 0
        self.check_interval = 0.3
        self.confidence_threshold = 0.4
        
        if CORAL_AVAILABLE:
            self.setup_coral()
    
    def setup_coral(self):
        try:
            model_path = "/home/a/Desktop/sobang/coral/models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
            self.interpreter = make_interpreter(model_path)
            self.interpreter.allocate_tensors()
            self.coral_enabled = True
        except Exception:
            self.coral_enabled = False
    
    def get_objects_compatible(self, interpreter, threshold=0.4):
        try:
            return detect.get_objects(interpreter, score_threshold=threshold)
        except TypeError:
            try:
                return detect.get_objects(interpreter, threshold=threshold)
            except TypeError:
                objects = detect.get_objects(interpreter)
                return [obj for obj in objects if obj.score >= threshold]
    
    def check_for_person(self, ir_frame):
        """Check for person with correct coordinate conversion"""
        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return self.person_detected, self.person_boxes, self.person_count
        
        if not self.coral_enabled or ir_frame is None:
            return False, [], 0
        
        try:
            original_height, original_width = ir_frame.shape[:2]
            
            model_input_size = 300
            resized = cv2.resize(ir_frame, (model_input_size, model_input_size))
            if len(resized.shape) == 2:
                resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
            
            input_data = np.expand_dims(resized, axis=0).astype(np.uint8)
            common.set_input(self.interpreter, input_data)
            self.interpreter.invoke()
            
            objects = self.get_objects_compatible(self.interpreter, self.confidence_threshold)
            persons = [obj for obj in objects if obj.id == 0]
            
            person_boxes = []
            for i, person in enumerate(persons):
                bbox = person.bbox
                
                scale_x = original_width / model_input_size
                scale_y = original_height / model_input_size
                
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
        """Create mask for person areas in IR frame coordinates"""
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

    def draw_person_bounding_boxes(self, display_frame, person_boxes, current_mode, scale_settings):
        """Draw bounding boxes for persons with IR scale/offset support"""
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

# ===== MAIN FIREFIGHTING THERMAL SYSTEM CLASS =====
class FirefightingThermalSystem:
    def __init__(self):
        self.gpio_enabled = GPIO_AVAILABLE
        
        # Debouncing variables for GPIO buttons
        self.button_debounce_time = 0.3
        self.last_button_time = {
            'button_3': 0, 'button_2': 0, 'button_14': 0,
            'button_4': 0
        }
        
        if self.gpio_enabled:
            try:
                #HW 연결
                self.mode_button = Button(3) # 주황
                self.edge_toggle_button = Button(4) # 빨강
                self.ui_control_button = Button(2) #노랑
                self.down_button = Button(14) #똥색


                self.mode_button.when_pressed = self.gpio_button_3_handler
                self.edge_toggle_button.when_pressed = self.gpio_button_2_handler
                self.ui_control_button.when_pressed = self.gpio_toggle_settings_handler
                self.down_button.when_pressed = self.gpio_button_4_handler
                
            except Exception:
                self.gpio_enabled = False
        
        # UI display control
        self.ui_visible = True
        
        # Text file notification system
        self.text_files_dir = "/home/a/Desktop/text_files"
        self.last_text_files = set()
        self.notification_active = False
        self.notification_start_time = 0
        self.notification_duration = 10
        self.new_file_name = ""
        self.file_check_interval = 5
        self.last_file_check = 0
        
        self.update_text_files_list()
            
        # Setting menu UI
        self.setting_menu = SettingMenuUI(self)
            
        # AI setup
        self.ai = FirefightingAI()
        self.person_detection_enabled = True
        
        # Screen settings
        self.get_screen_resolution()
        self.fullscreen_enabled = True
        self.window_name = 'Firefighting Thermal System'
        
        # Simple temperature system
        self.temperature_mode = False  # Simple on/off flag
        self.serial_lock = threading.Lock()
        
        # Camera device settings
        self.THERMAL_SERIAL_PORT = None
        self.thermal_serial = None
        self.IR_WIDTH = 1664
        self.IR_HEIGHT = 936
        self.IR_FPS = 9
        
        # Edge detection optimization settings
        self.edge_resolution_options = [
            ("1600x900", 1600, 900, "HIGH PERFORMANCE - Fastest processing"),
            ("1920x1080", 1920, 1080, "BALANCED - Good speed and quality"),
            ("2240x1260", 2240, 1260, "ENHANCED - Better quality, slower"),
            ("2560x1440", 2560, 1440, "HIGH QUALITY - Detailed edges, moderate speed"),
            ("2880x1620", 2880, 1620, "ULTRA QUALITY - Very detailed, slower"),
            ("3200x1800", 3200, 1800, "MAXIMUM QUALITY - Best edges, slowest")
        ]
        self.current_edge_resolution_index = 3
        
        _, self.EDGE_WIDTH, self.EDGE_HEIGHT, _ = self.edge_resolution_options[self.current_edge_resolution_index]
        
        # FPS optimization settings
        self.TARGET_FPS = 9
        self.FRAME_TIME = 1.0 / self.TARGET_FPS
        self.last_process_time = 0
        
        # Display modes
        self.DISPLAY_MODES = {
            0: "SEARCH MODE",
            1: "COLD MODE", 
            2: "EDGE OVERLAY (640x360 optimized)",
            3: "IR ONLY (Fixed 12fps)",
        }
        self.current_mode = 0
        
        # Edge toggle system
        self.EDGE_TOGGLE_MODES = {
            0: "EDGE OFF",
            1: "EDGE ONLY", 
            2: "EDGE + IR OVERLAY"
        }
        self.edge_toggle_mode = 1
        
        # Mode-specific edge colors
        self.MODE_EDGE_COLORS = {
            0: [255, 255, 255],  # SEARCH MODE: White
            1: [255, 255, 255],  # COLD MODE: White
            2: [0, 0, 0],        # EDGE OVERLAY: Black
            3: [255, 255, 255],  # IR ONLY: White
        }
        
        # Camera setup
        self.ir_process = None
        
        # Frame storage
        self.thermal_frame = None
        self.ir_frame = None
        self.frame_lock = threading.Lock()
        
        # Resolution settings
        self.thermal_width = 160
        self.thermal_height = 120
        self.ir_width = self.IR_WIDTH
        self.ir_height = self.IR_HEIGHT
        
        # Basic settings
        self.temp_threshold = 140
        self.overlay_alpha = 0.7
        self.thermal_scale = 1.0
        
        # SEARCH MODE settings
        self.search_hot_percentage = 0.1
        
        # COLD MODE settings
        self.cold_percentage = 0.1
        
        # EDGE OVERLAY MODE settings - removed cache-related variables
        self.edge_threshold_low = 70
        self.edge_threshold_high = 130
        self.edge_blur_kernel = 1
        self.edge_thickness = 0
        self.edge_sharpness_mode = 0
        
        # IR OVERLAY settings
        self.ir_overlay_alpha = 0.3
        
        # Scale and offset settings
        self.thermal_scale_fixed = 1.0
        self.thermal_offset_x_fixed = 0
        self.thermal_offset_y_fixed = 0
        self.ir_scale_fixed = 1.0
        self.ir_offset_x_fixed = 0
        self.ir_offset_y_fixed = 0
        
        # Thermal colormap options
        self.thermal_colormaps = {
            0: ("PLASMA", cv2.COLORMAP_PLASMA),
            1: ("INFERNO", cv2.COLORMAP_INFERNO),
            2: ("HOT", cv2.COLORMAP_HOT),
            3: ("JET", cv2.COLORMAP_JET)
        }
        self.current_thermal_colormap = 0
        
        self.running = False
        self.last_command_time = time.time()

    def update_text_files_list(self):
        """Update current text file list"""
        try:
            if os.path.exists(self.text_files_dir):
                files = set(f for f in os.listdir(self.text_files_dir) if f.endswith('.txt'))
                self.last_text_files = files
            else:
                self.last_text_files = set()
        except Exception:
            self.last_text_files = set()

    def check_new_text_files(self):
        """Check for new text files (every 5 seconds)"""
        current_time = time.time()
        if current_time - self.last_file_check < self.file_check_interval:
            return
        
        self.last_file_check = current_time
        
        try:
            if not os.path.exists(self.text_files_dir):
                return
                
            current_files = set(f for f in os.listdir(self.text_files_dir) if f.endswith('.txt'))
            new_files = current_files - self.last_text_files
            
            if new_files:
                self.new_file_name = list(new_files)[0]
                self.notification_active = True
                self.notification_start_time = current_time
                self.last_text_files = current_files
                
        except Exception:
            pass

    def draw_notification(self, frame):
        """Draw new text file notification"""
        if not self.notification_active:
            return frame
            
        current_time = time.time()
        if current_time - self.notification_start_time > self.notification_duration:
            self.notification_active = False
            return frame
        
        height, width = frame.shape[:2]
        
        notif_width = 280
        notif_height = 60
        notif_x = width - notif_width - 20
        notif_y = 190
        
        overlay = frame.copy()
        
        blink_cycle = int((current_time - self.notification_start_time) * 2) % 2
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
        
        display_name = self.new_file_name if len(self.new_file_name) <= 18 else self.new_file_name[:15] + "..."
        cv2.putText(overlay, display_name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        remaining_time = self.notification_duration - (current_time - self.notification_start_time)
        progress = remaining_time / self.notification_duration
        progress_width = int((notif_width - 20) * progress)
        cv2.rectangle(overlay, (notif_x + 10, notif_y + notif_height - 5), 
                      (notif_x + 10 + progress_width, notif_y + notif_height - 2), (255, 255, 255), -1)
        
        alpha = 0.95
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame

    def get_screen_resolution(self):
        """Auto-detect Raspberry Pi screen resolution"""
        try:
            result = subprocess.run(['xrandr'], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if '*' in line and '+' in line:
                    parts = line.split()
                    for part in parts:
                        if 'x' in part and part.replace('x', '').replace('.', '').isdigit():
                            resolution = part.split('x')
                            if len(resolution) == 2:
                                self.screen_width = int(resolution[0])
                                self.screen_height = int(float(resolution[1]))
                                return
        except Exception:
            pass
        
        self.screen_width, self.screen_height = (1920, 1080)

    def is_button_debounced(self, button_name):
        """Check if enough time has passed since last button press for debouncing"""
        current_time = time.time()
        if current_time - self.last_button_time[button_name] < self.button_debounce_time:
            return False
        self.last_button_time[button_name] = current_time
        return True
        
    def gpio_toggle_settings_handler(self):
        """GPIO 14: Toggles the main settings menu ON/OFF"""
        if not self.is_button_debounced('button_14'):
            return
        self.setting_menu.toggle_menu()
        self.last_command_time = time.time()

    def gpio_button_3_handler(self):
        """GPIO 3: Mode change (Normal) / Confirm (Settings)"""
        if not self.is_button_debounced('button_3'):
            return
        if self.setting_menu.menu_active:
            self.setting_menu.confirm_selection()
        else:
            self.current_mode = (self.current_mode + 1) % len(self.DISPLAY_MODES)
        self.last_command_time = time.time()

    def gpio_button_2_handler(self):
        """GPIO 2: Edge toggle (Normal) / Up (Settings)"""
        if not self.is_button_debounced('button_2'):
            return
        if self.setting_menu.menu_active:
            self.setting_menu.navigate_up()
        else:
            self.edge_toggle_mode = (self.edge_toggle_mode + 1) % len(self.EDGE_TOGGLE_MODES)
        self.last_command_time = time.time()

    def gpio_button_4_handler(self):
        """GPIO 4: UI toggle (Normal) / Down (Settings)"""
        if not self.is_button_debounced('button_4'):
            return
        if self.setting_menu.menu_active:
            self.setting_menu.navigate_down()
        else:
            self.ui_visible = not self.ui_visible
        self.last_command_time = time.time()

    def toggle_temperature_mode(self):
        """Simple temperature mode toggle - sends command to OpenMV"""
        if self.thermal_serial and self.thermal_serial.is_open:
            try:
                with self.serial_lock:
                    self.thermal_serial.write(b"temp")
                    self.thermal_serial.flush()
                    
                    # Wait for status response
                    size_data = self.thermal_serial.read(4)
                    if len(size_data) == 4:
                        msg_size = struct.unpack('<L', size_data)[0]
                        if 5 <= msg_size <= 20:
                            status_bytes = self.thermal_serial.read(msg_size)
                            if len(status_bytes) == msg_size:
                                status = status_bytes.decode('utf-8')
                                
                                if "TEMP_ON" in status:
                                    self.temperature_mode = True
                                elif "TEMP_OFF" in status:
                                    self.temperature_mode = False
                time.sleep(0.5)
            except Exception:
                pass

    def draw_ui_overlay(self, frame):
        """Draw UI overlay (integrated top right panel)"""
        if not self.ui_visible or self.setting_menu.menu_active:
            return frame
        
        # Check for new text files
        self.check_new_text_files()
        
        height, width = frame.shape[:2]
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Integrated panel (top right)
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
        
        # System info
        cv2.putText(overlay, f"Time: {current_time}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        text_y += line_height
        
        # AI status
        if self.ai.coral_enabled:
            ai_status = "ON" if self.person_detection_enabled else "OFF"
            person_text = f"AI Detection: {ai_status} (Persons: {self.ai.person_count if self.person_detection_enabled else 'N/A'})"
            cv2.putText(overlay, person_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(overlay, "AI Detection: DISABLED", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
        text_y += line_height
        
        # Temperature status
        temp_status = "ON" if self.temperature_mode else "OFF"
        temp_color = (0, 255, 255) if self.temperature_mode else (128, 128, 128)
        cv2.putText(overlay, f"Temperature Mode: {temp_status}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, temp_color, 2)
        text_y += line_height
        
        # Remote control
        cv2.putText(overlay, "Remote Control:", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        text_y += line_height
        
        # Icon drawing functions
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
        
        # Icons in one line
        icon_y = text_y - 5
        icon_size = 20
        icon_spacing = 130
        start_x = text_x + 20
        
        # 1. Square (white) - Menu
        draw_small_square(start_x, icon_y, icon_size, (255, 255, 255))
        cv2.putText(overlay, "Menu", (start_x + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 2. Triangle (red) - Edge  
        icon_x2 = start_x + icon_spacing
        draw_small_triangle(icon_x2, icon_y, icon_size, (0, 0, 255))
        cv2.putText(overlay, "Edge", (icon_x2 + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 3. Circle (white) - Mode
        icon_x3 = start_x + icon_spacing * 2
        draw_small_circle(icon_x3, icon_y, icon_size//2, (255, 255, 255))
        cv2.putText(overlay, "Mode", (icon_x3 + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 4. Inverted triangle (red) - UI
        icon_x4 = start_x + icon_spacing * 3
        draw_small_inverted_triangle(icon_x4, icon_y, icon_size, (0, 0, 255))
        ui_status = "UI" if self.ui_visible else "OFF"
        cv2.putText(overlay, ui_status, (icon_x4 + icon_size + 8, icon_y + icon_size - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        alpha = 0.9
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        frame = self.draw_notification(frame)
        
        return frame

    def setup_fullscreen_window(self):
        """Setup fullscreen window"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        if self.fullscreen_enabled:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.resizeWindow(self.window_name, self.screen_width, self.screen_height)
            cv2.moveWindow(self.window_name, 0, 0)

    def resize_frame_to_screen(self, frame):
        """Resize frame to fit screen size"""
        if frame is None:
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        h, w = frame.shape[:2]
        if w != self.screen_width or h != self.screen_height:
            frame = cv2.resize(frame, (self.screen_width, self.screen_height))
        return frame

    def setup_thermal_communication(self):
        """Setup simple serial communication with OpenMV"""
        for port in ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0']:
            try:
                self.thermal_serial = serial.Serial(
                    port=port, 
                    baudrate=115200, 
                    timeout=2,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                
                self.THERMAL_SERIAL_PORT = port
                
                time.sleep(1)
                if self.thermal_serial.is_open:
                    return True
                    
            except Exception:
                continue
                
        return False
    
    def setup_ir_camera(self):
        """Setup IR camera"""
        try:
            cmd = [
                'rpicam-vid', '--width', str(self.ir_width), '--height', str(self.ir_height),
                '--framerate', str(self.IR_FPS), '--timeout', '0', '--output', '-',
                '--codec', 'yuv420', '--nopreview'
            ]
            self.ir_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, 
                                               bufsize=10**7, preexec_fn=os.setsid)
            time.sleep(3)
            
            if self.ir_process.poll() is None:
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def thermal_capture_thread(self):
        """Thermal capture thread"""
        while self.running:
            try:
                if self.thermal_serial and self.thermal_serial.is_open:
                    with self.serial_lock:
                        self.thermal_serial.reset_input_buffer()
                        self.thermal_serial.write(b"snap")
                        self.thermal_serial.flush()
                        
                        size_data = self.thermal_serial.read(4)
                        if len(size_data) != 4: 
                            continue
                        
                        img_size = struct.unpack('<L', size_data)[0]
                        if img_size <= 0 or img_size > 50000: 
                            continue
                        
                        img_data = self.thermal_serial.read(img_size)
                        if len(img_data) != img_size: 
                            continue
                    
                    img_array = np.frombuffer(img_data, dtype=np.uint8)
                    thermal_img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
                    
                    if thermal_img is not None and thermal_img.shape == (120, 160):
                        with self.frame_lock:
                            self.thermal_frame = thermal_img.copy()
                        
                    time.sleep(0.11)
                    
                else:
                    time.sleep(0.1)
                    
            except Exception:
                time.sleep(0.1)
    
    def preprocess_ir_frame(self, ir_frame):
        """Preprocess IR frame: crop and stretch"""
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
        """IR capture thread"""
        frame_size = self.ir_width * self.ir_height * 3 // 2
        while self.running:
            try:
                if self.ir_process and self.ir_process.poll() is None:
                    raw_data = self.ir_process.stdout.read(frame_size)
                    if len(raw_data) == frame_size:
                        yuv = np.frombuffer(raw_data, dtype=np.uint8).reshape((self.ir_height * 3 // 2, self.ir_width))
                        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV420p2BGR)
                        processed_bgr = self.preprocess_ir_frame(bgr)
                        with self.frame_lock:
                            self.ir_frame = processed_bgr.copy()
                    else:
                        time.sleep(0.01)
                else:
                    break
            except Exception:
                time.sleep(0.1)

    def apply_thermal_scale_and_offset(self, thermal_colored):
        """Apply scale and offset to thermal image"""
        if thermal_colored is None:
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        scaled_thermal_width = int(self.thermal_width * self.thermal_scale_fixed)
        scaled_thermal_height = int(self.thermal_height * self.thermal_scale_fixed)
        thermal_scaled = cv2.resize(thermal_colored, (scaled_thermal_width, scaled_thermal_height))
        
        screen_scale_x = self.screen_width / self.thermal_width
        screen_scale_y = self.screen_height / self.thermal_height
        final_thermal_width = int(scaled_thermal_width * screen_scale_x)
        final_thermal_height = int(scaled_thermal_height * screen_scale_y)
        final_offset_x = int(self.thermal_offset_x_fixed * screen_scale_x)
        final_offset_y = int(self.thermal_offset_y_fixed * screen_scale_y)
        
        thermal_final = cv2.resize(thermal_scaled, (final_thermal_width, final_thermal_height))
        
        result = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        start_x = max(0, final_offset_x)
        start_y = max(0, final_offset_y)
        end_x = min(self.screen_width, final_offset_x + final_thermal_width)
        end_y = min(self.screen_height, final_offset_y + final_thermal_height)
        
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
        """Apply scale and offset to IR image"""
        if ir_frame is None:
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        scaled_ir_width = int(self.ir_width * self.ir_scale_fixed)
        scaled_ir_height = int(self.ir_height * self.ir_scale_fixed)
        ir_scaled = cv2.resize(ir_frame, (scaled_ir_width, scaled_ir_height))
        
        screen_scale_x = self.screen_width / self.ir_width
        screen_scale_y = self.screen_height / self.ir_height
        final_ir_width = int(scaled_ir_width * screen_scale_x)
        final_ir_height = int(scaled_ir_height * screen_scale_y)
        final_offset_x = int(self.ir_offset_x_fixed * screen_scale_x)
        final_offset_y = int(self.ir_offset_y_fixed * screen_scale_y)
        
        ir_final = cv2.resize(ir_scaled, (final_ir_width, final_ir_height))
        
        result = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        start_x = max(0, final_offset_x)
        start_y = max(0, final_offset_y)
        end_x = min(self.screen_width, final_offset_x + final_ir_width)
        end_y = min(self.screen_height, final_offset_y + final_ir_height)
        
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
        """Determine if edges should be shown based on edge toggle mode"""
        return self.edge_toggle_mode > 0 and self.current_mode != 3

    def should_show_ir_overlay(self):
        """Determine if IR overlay should be shown based on edge toggle mode"""
        return self.edge_toggle_mode == 2

    def get_current_mode_edge_color(self):
        """Get edge color for current mode"""
        return self.MODE_EDGE_COLORS.get(self.current_mode, [255, 255, 255])

    def process_frame_with_ai(self, result, ir_frame):
        """Helper function to run AI detection and draw boxes if enabled"""
        if self.person_detection_enabled and ir_frame is not None and self.ai.coral_enabled:
            person_detected, person_boxes, person_count = self.ai.check_for_person(ir_frame)
            if person_detected and person_boxes:
                scale_settings = {
                    'ir_scale_fixed': self.ir_scale_fixed, 'ir_offset_x_fixed': self.ir_offset_x_fixed,
                    'ir_offset_y_fixed': self.ir_offset_y_fixed, 'screen_width': self.screen_width,
                    'screen_height': self.screen_height, 'ir_width': self.ir_width, 'ir_height': self.ir_height
                }
                result = self.ai.draw_person_bounding_boxes(result, person_boxes, self.current_mode, scale_settings)
        return result

    def apply_smart_thinning(self, edges):
        """Apply smart thinning to reduce thick edges"""
        _, edges_binary = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        thinned = edges_binary.copy()
        prev_count = cv2.countNonZero(thinned)
        
        for i in range(5):
            eroded = cv2.erode(thinned, kernel, iterations=1)
            opened = cv2.morphologyEx(eroded, cv2.MORPH_OPEN, kernel)
            current_count = cv2.countNonZero(opened)
            if current_count == 0 or current_count == prev_count:
                break
            thinned = opened
            prev_count = current_count
        
        if cv2.countNonZero(thinned) < cv2.countNonZero(edges_binary) * 0.3:
            kernel_cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
            thinned = cv2.erode(edges_binary, kernel_cross, iterations=1)
        
        return thinned

    def apply_sharp_edge_detection_configurable(self, ir_gray):
        """Apply edge detection at configurable resolution with configurable thresholds"""
        ir_gray_small = cv2.resize(ir_gray, (self.EDGE_WIDTH, self.EDGE_HEIGHT))
        
        if self.edge_sharpness_mode == 0:
            blurred = cv2.GaussianBlur(ir_gray_small, (self.edge_blur_kernel, self.edge_blur_kernel), 0) if self.edge_blur_kernel > 0 else ir_gray_small.copy()
        elif self.edge_sharpness_mode == 1:
            blurred = ir_gray_small.copy()
        else:
            gaussian = cv2.GaussianBlur(ir_gray_small, (0, 0), 2.0)
            blurred = cv2.addWeighted(ir_gray_small, 1.5, gaussian, -0.5, 0)
        
        edges_small = cv2.Canny(blurred, self.edge_threshold_low, self.edge_threshold_high)
        
        if self.edge_thickness == 1:
            edges_small = self.apply_smart_thinning(edges_small)
        elif self.edge_thickness == 2:
            kernel = np.ones((2, 2), np.uint8)
            edges_small = cv2.morphologyEx(edges_small, cv2.MORPH_CLOSE, kernel)
            edges_small = cv2.erode(edges_small, kernel, iterations=1)
        elif self.edge_thickness > 2:
            kernel = np.ones((min(self.edge_thickness, 5), min(self.edge_thickness, 5)), np.uint8)
            edges_small = cv2.dilate(edges_small, kernel, iterations=1)
            kernel = np.ones((2, 2), np.uint8)
            edges_small = cv2.morphologyEx(edges_small, cv2.MORPH_CLOSE, kernel)
        
        return edges_small

    def create_search_mode(self, thermal_frame, ir_frame=None):
        """SEARCH MODE"""
        if thermal_frame is None:
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        gray = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2GRAY) if len(thermal_frame.shape) == 3 else thermal_frame.copy()
        gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        hot_threshold = np.percentile(gray_norm, (1.0 - self.search_hot_percentage) * 100)
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
    
    def create_ir_only_mode(self, ir_frame):
        """IR ONLY MODE"""
        if ir_frame is None:
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        result = self.apply_ir_scale_and_offset(ir_frame)
        return self.process_frame_with_ai(result, ir_frame)
    
    def create_cold_mode(self, thermal_frame, ir_frame=None):
        """COLD MODE"""
        if thermal_frame is None:
            return np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        
        gray = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2GRAY) if len(thermal_frame.shape) == 3 else thermal_frame.copy()
        gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        cold_threshold = np.percentile(gray_norm, self.cold_percentage * 100)
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
        """EDGE OVERLAY MODE"""
        if thermal_frame is None:
            result = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        else:
            gray = cv2.cvtColor(thermal_frame, cv2.COLOR_BGR2GRAY) if len(thermal_frame.shape) == 3 else thermal_frame.copy()
            gray_norm = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
            _, colormap_cv2 = self.thermal_colormaps[self.current_thermal_colormap]
            thermal_colored = cv2.applyColorMap(gray_norm, colormap_cv2)
            result = self.apply_thermal_scale_and_offset(thermal_colored)
        
        if ir_frame is not None:
            if self.should_show_ir_overlay():
                result = self.apply_ir_image_overlay(result, ir_frame)
            
            result = self.apply_ai_detection_and_edge_overlay(result, ir_frame)
        
        return result
    
    def apply_ir_image_overlay(self, thermal_background, ir_frame):
        """Apply transparent IR image overlay"""
        if ir_frame is None:
            return thermal_background
        
        ir_positioned = self.apply_ir_scale_and_offset(ir_frame)
        try:
            return cv2.addWeighted(thermal_background, 1.0 - self.ir_overlay_alpha, ir_positioned, self.ir_overlay_alpha, 0)
        except Exception:
            return thermal_background
    
    def apply_ai_detection_and_edge_overlay(self, thermal_background, ir_frame):
        """Apply AI detection + edge overlay - NO CACHE, direct computation every frame"""
        if ir_frame is None:
            return thermal_background
        
        # Always run AI detection for person detection
        person_detected, person_boxes, person_mask = False, [], None
        if self.person_detection_enabled and self.ai.coral_enabled:
            person_detected, person_boxes, _ = self.ai.check_for_person(ir_frame)
            if person_detected:
                person_mask = self.ai.create_person_mask(ir_frame, person_boxes)
        
        # Only process edges if they should be shown
        if self.should_show_edges():
            # Convert IR frame to grayscale and compute edges directly
            ir_gray = cv2.cvtColor(ir_frame, cv2.COLOR_BGR2GRAY)
            edges_configurable = self.apply_sharp_edge_detection_configurable(ir_gray)
            
            # Calculate scaling factors for display
            screen_scale_x = self.screen_width / self.ir_width
            screen_scale_y = self.screen_height / self.ir_height
            final_ir_width = int(self.ir_width * self.ir_scale_fixed * screen_scale_x)
            final_ir_height = int(self.ir_height * self.ir_scale_fixed * screen_scale_y)
            final_offset_x = int(self.ir_offset_x_fixed * screen_scale_x)
            final_offset_y = int(self.ir_offset_y_fixed * screen_scale_y)
            
            # Resize edges to final display size
            edges_final = cv2.resize(edges_configurable, (final_ir_width, final_ir_height))
            person_mask_final = cv2.resize(person_mask, (final_ir_width, final_ir_height)) if person_mask is not None else None
            
            # Apply edge overlay to thermal background
            start_x = max(0, final_offset_x)
            start_y = max(0, final_offset_y)
            end_x = min(self.screen_width, final_offset_x + final_ir_width)
            end_y = min(self.screen_height, final_offset_y + final_ir_height)
            
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
                        
                        # Apply person-specific coloring if detected
                        if person_detected and person_mask_final is not None:
                            person_region = person_mask_final[src_start_y:src_end_y, src_start_x:src_end_x] > 0
                            person_edge_mask = edge_mask & person_region
                            if np.any(person_edge_mask):
                                thermal_region[person_edge_mask] = [0, 255, 0]  # Green for person edges
                            
                            non_person_edge_mask = edge_mask & (~person_region)
                            if np.any(non_person_edge_mask):
                                thermal_region[non_person_edge_mask] = edge_color_bgr  # Normal edge color
                        else:
                            thermal_region[edge_mask] = edge_color_bgr  # Normal edge color for all edges
                        
                        thermal_background[start_y:end_y, start_x:end_x] = thermal_region
                except Exception:
                    pass
        
        # Always apply AI bounding boxes if person detected
        if person_detected and person_boxes:
            scale_settings = {
                'ir_scale_fixed': self.ir_scale_fixed, 'ir_offset_x_fixed': self.ir_offset_x_fixed,
                'ir_offset_y_fixed': self.ir_offset_y_fixed, 'screen_width': self.screen_width,
                'screen_height': self.screen_height, 'ir_width': self.ir_width, 'ir_height': self.ir_height
            }
            thermal_background = self.ai.draw_person_bounding_boxes(thermal_background, person_boxes, self.current_mode, scale_settings)
        
        return thermal_background

    def run_firefighting_system(self):
        """Run the main system loop"""
        print("=== FIREFIGHTING THERMAL SYSTEM - FINAL VERSION ===")
        
        thermal_ok = self.setup_thermal_communication()
        time.sleep(1)
        ir_ok = self.setup_ir_camera()
        
        if not thermal_ok and not ir_ok:
            print("ERROR: All cameras failed to initialize. Exiting.")
            return
        
        self.setup_fullscreen_window()
        self.running = True
        
        threads = []
        if thermal_ok:
            thermal_thread = threading.Thread(target=self.thermal_capture_thread, daemon=True)
            thermal_thread.start()
            threads.append(thermal_thread)
        if ir_ok:
            ir_thread = threading.Thread(target=self.ir_capture_thread, daemon=True)
            ir_thread.start()
            threads.append(ir_thread)
        
        print("\nSYSTEM STARTED SUCCESSFULLY.")
        print("Control via GPIO buttons and on-screen UI.")
        
        try:
            while self.running:
                current_time = time.time()
                if current_time - self.last_process_time < self.FRAME_TIME:
                    time.sleep(self.FRAME_TIME - (current_time - self.last_process_time))
                    continue
                self.last_process_time = time.time()
                
                with self.frame_lock:
                    current_thermal = self.thermal_frame.copy() if self.thermal_frame is not None else None
                    current_ir = self.ir_frame.copy() if self.ir_frame is not None else None
                
                if self.setting_menu.menu_active:
                    display_frame = self.setting_menu.create_full_screen_menu(self.screen_width, self.screen_height)
                else:
                    if self.current_mode == 0:
                        display_frame = self.create_search_mode(current_thermal, current_ir)
                    elif self.current_mode == 1:
                        display_frame = self.create_cold_mode(current_thermal, current_ir)
                    elif self.current_mode == 2:
                        display_frame = self.create_edge_overlay_mode(current_thermal, current_ir)
                    elif self.current_mode == 3:
                        display_frame = self.create_ir_only_mode(current_ir)
                    else:
                        display_frame = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
                    
                    display_frame = self.draw_ui_overlay(display_frame)
                
                display_frame = self.resize_frame_to_screen(display_frame)
                cv2.imshow(self.window_name, display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    self.running = False
                    break
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.running = False
                    break
        
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Safe cleanup"""
        self.running = False
        
        if self.thermal_serial and self.thermal_serial.is_open:
            try:
                self.thermal_serial.close()
            except Exception:
                pass
        
        if self.ir_process:
            try:
                os.killpg(os.getpgid(self.ir_process.pid), signal.SIGTERM)
                self.ir_process.wait(timeout=3)
            except Exception:
                pass
        cv2.destroyAllWindows()
        print("System Shutdown Complete.")

# ===== MAIN FUNCTION =====
def main():
    firefighting_system = FirefightingThermalSystem()
    firefighting_system.run_firefighting_system()

if __name__ == "__main__":
    main()
