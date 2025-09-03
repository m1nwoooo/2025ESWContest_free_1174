import os
import time

from config import *

class FileMonitor:
    def __init__(self, directory):
        self.directory = directory
        self.last_files = set()
        self.notification_active = False
        self.notification_start_time = 0
        self.notification_duration = NOTIFICATION_DURATION
        self.new_file_name = ""
        self.file_check_interval = FILE_CHECK_INTERVAL
        self.last_file_check = 0
        
        self.update_file_list()
    
    def update_file_list(self):
        try:
            if os.path.exists(self.directory):
                files = set(f for f in os.listdir(self.directory) if f.endswith('.txt'))
                self.last_files = files
            else:
                self.last_files = set()
        except Exception:
            self.last_files = set()

    def check_for_new_files(self):
        current_time = time.time()
        if current_time - self.last_file_check < self.file_check_interval:
            return
        
        self.last_file_check = current_time
        
        try:
            if not os.path.exists(self.directory):
                return
                
            current_files = set(f for f in os.listdir(self.directory) if f.endswith('.txt'))
            new_files = current_files - self.last_files
            
            if new_files:
                self.new_file_name = list(new_files)[0]
                self.notification_active = True
                self.notification_start_time = current_time
                self.last_files = current_files
                
        except Exception:
            pass
    
    def has_notification(self):
        return self.notification_active
    
    def clear_notification(self):
        self.notification_active = False
