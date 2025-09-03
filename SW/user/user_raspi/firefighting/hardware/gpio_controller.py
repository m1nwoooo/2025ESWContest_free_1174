import time

from config import *

try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

class GPIOController:
    def __init__(self, system):
        self.system = system
        self.gpio_enabled = GPIO_AVAILABLE
        
        self.button_debounce_time = DEFAULT_BUTTON_DEBOUNCE_TIME
        self.last_button_time = {
            'button_3': 0,    # Mode/Confirm
            'button_4': 0,    # UP/Edge
            'button_2': 0,    # Menu Toggle
            'button_14': 0    # DOWN/UI
        }
        
        if self.gpio_enabled:
            try:
                # Hardware connections with clear mapping
                self.mode_button = Button(GPIO_MODE_BUTTON)         # GPIO 3 (orange) - Confirm/Mode Change
                self.up_edge_button = Button(GPIO_UP_EDGE_BUTTON)   # GPIO 4 (red) - UP/Edge Toggle  
                self.menu_button = Button(GPIO_MENU_BUTTON)         # GPIO 2 (yellow) - Menu Toggle Only
                self.down_ui_button = Button(GPIO_DOWN_UI_BUTTON)   # GPIO 14 (brown) - DOWN/UI Toggle

                # Handler mapping
                self.mode_button.when_pressed = self.handle_mode_confirm_button      # GPIO 3
                self.up_edge_button.when_pressed = self.handle_up_edge_button        # GPIO 4
                self.menu_button.when_pressed = self.handle_menu_toggle_button       # GPIO 2  
                self.down_ui_button.when_pressed = self.handle_down_ui_button        # GPIO 14
                
            except Exception:
                self.gpio_enabled = False
    
    def is_button_debounced(self, button_name):
        current_time = time.time()
        if current_time - self.last_button_time[button_name] < self.button_debounce_time:
            return False
        self.last_button_time[button_name] = current_time
        return True
        
    def handle_mode_confirm_button(self):
        """GPIO 3 (Orange): Confirm/Mode Change"""
        if not self.is_button_debounced('button_3'):
            return
        
        if self.system.menu_system.is_active():
            # In menu: Confirm selection
            self.system.menu_system.confirm_selection()
        else:
            # In normal view: Mode change
            self.system.current_mode = (self.system.current_mode + 1) % len(DISPLAY_MODES)
    
    def handle_up_edge_button(self):
        """GPIO 4 (Red): UP/Edge Toggle"""
        if not self.is_button_debounced('button_4'):
            return
        
        if self.system.menu_system.is_active():
            # In menu: Navigate up
            self.system.menu_system.navigate_up()
        else:
            # In normal view: Edge toggle
            self.system.edge_toggle_mode = (self.system.edge_toggle_mode + 1) % len(EDGE_TOGGLE_MODES)
    
    def handle_menu_toggle_button(self):
        """GPIO 2 (Yellow): Menu Toggle Only"""
        if not self.is_button_debounced('button_2'):
            return
        
        # Always toggle menu (works in all states)
        self.system.menu_system.toggle()
    
    def handle_down_ui_button(self):
        """GPIO 14 (Brown): DOWN/UI Toggle"""
        if not self.is_button_debounced('button_14'):
            return
        
        if self.system.menu_system.is_active():
            # In menu: Navigate down
            self.system.menu_system.navigate_down()
        else:
            # In normal view: UI toggle (top-right panel)
            self.system.ui_visible = not self.system.ui_visible
