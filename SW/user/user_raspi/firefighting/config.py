#!/usr/bin/env python3

import cv2

# Camera settings
THERMAL_SERIAL_PORTS = ['/dev/ttyACM0']
THERMAL_BAUDRATE = 115200
THERMAL_WIDTH = 160
THERMAL_HEIGHT = 120

IR_WIDTH = 1664
IR_HEIGHT = 936
IR_FPS = 9

# GPIO pin configuration
GPIO_MODE_BUTTON = 3        # Orange - Confirm/Mode Change  
GPIO_UP_EDGE_BUTTON = 4     # Red - UP/Edge Toggle
GPIO_MENU_BUTTON = 2        # Yellow - Menu Toggle Only
GPIO_DOWN_UI_BUTTON = 14    # Brown - DOWN/UI Toggle

# Display modes
DISPLAY_MODES = {
    0: "SEARCH MODE",
    1: "COLD MODE", 
    2: "EDGE OVERLAY (640x360 optimized)",
    3: "IR ONLY (Fixed 12fps)",
}

EDGE_TOGGLE_MODES = {
    0: "EDGE OFF",
    1: "EDGE ONLY", 
    2: "EDGE + IR OVERLAY"
}

# Default edge colors for each mode (BGR)
MODE_EDGE_COLORS = {
    0: [255, 255, 255],  # SEARCH MODE: White
    1: [255, 255, 255],  # COLD MODE: White
    2: [0, 0, 0],        # EDGE OVERLAY: Black
    3: [255, 255, 255],  # IR ONLY: White
}

# Edge detection settings
EDGE_RESOLUTION_OPTIONS = [
    ("1024x576", 1024, 576, "HIGH PERFORMANCE - Fastest processing"),
    ("1280x720", 1280, 720, "BALANCED - Good speed and quality"),
    ("1664x936", 1664, 936, "HIGH QUALITY - Detailed edges, moderate speed"),
    ("3200x1800", 2560, 1440, "MAXIMUM QUALITY - Best edges, slowest")
]

DEFAULT_EDGE_RESOLUTION_INDEX = 4

# Thermal colormap options (OpenCV constants)
THERMAL_COLORMAPS = {
    0: ("PLASMA", cv2.COLORMAP_PLASMA),
    1: ("INFERNO", cv2.COLORMAP_INFERNO)
}

# Default values
DEFAULT_EDGE_THRESHOLD_LOW = 45
DEFAULT_EDGE_THRESHOLD_HIGH = 85
DEFAULT_TARGET_FPS = 9
DEFAULT_SEARCH_HOT_PERCENTAGE = 0.07
DEFAULT_COLD_PERCENTAGE = 0.07
DEFAULT_IR_OVERLAY_ALPHA = 0.3
DEFAULT_BUTTON_DEBOUNCE_TIME = 0.3

# File paths
TEXT_FILES_DIR = "text_files"
CORAL_MODEL_PATH = "coral/models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"

# AI settings
AI_CHECK_INTERVAL = 0.3
AI_CONFIDENCE_THRESHOLD = 0.4
AI_MODEL_INPUT_SIZE = 300

# UI settings
NOTIFICATION_DURATION = 10
FILE_CHECK_INTERVAL = 5
