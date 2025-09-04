#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import time
import os
import signal
from datetime import datetime
import queue
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gst, GstVideo, GLib

class WFBGroundStationUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WFB-NG Ground Station Control")
        self.root.attributes('-fullscreen', True)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.fullscreen = True
        Gst.init(None)
        self.processes = {}
        self.voice_enabled = False
        self.video_running = False
        self.video_pipeline = None
        self.nodes = {
            'usr1': False,
            'usr2': False,
            'node': False
        }
        self.log_queue = queue.Queue()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.setup_ui()
        self.monitor_processes()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        
    def setup_ui(self):
        left_width = int(self.screen_width * 0.65)
        right_width = self.screen_width - left_width - 40
        video_height = int(self.screen_height * 0.7)
        log_height = self.screen_height - video_height - 60
        left_frame = tk.Frame(self.root, bg='black')
        left_frame.place(x=20, y=20, width=left_width, height=self.screen_height-40)
        self.video_frame = tk.Frame(left_frame, bg='#2a2a2a', highlightbackground='white', highlightthickness=2)
        self.video_frame.place(x=0, y=0, width=left_width, height=video_height)
        self.video_widget = tk.Frame(self.video_frame, bg='black')
        self.video_widget.place(x=2, y=2, width=left_width-4, height=video_height-4)
        self.video_label = tk.Label(self.video_widget, text="영상\n→ 영상 시작 버튼을 클릭하세요", 
                                    bg='black', fg='white', font=('Arial', 16))
        self.video_label.pack(expand=True)
        video_btn_frame = tk.Frame(self.video_frame, bg='#2a2a2a')
        video_btn_frame.place(x=10, y=10)
        self.video_start_btn = tk.Button(video_btn_frame, text="▶ 비디오 시작", 
                                         command=self.start_video, bg='#4CAF50', fg='white',
                                         font=('Arial', 11, 'bold'))
        self.video_start_btn.pack(side='left', padx=2)
        self.video_stop_btn = tk.Button(video_btn_frame, text="■ 비디오 정지", 
                                        command=self.stop_video, bg='#f44336', fg='white',
                                        font=('Arial', 11, 'bold'), state='disabled')
        self.video_stop_btn.pack(side='left', padx=2)
        self.log_frame = tk.Frame(left_frame, bg='#d3d3d3', highlightbackground='white', highlightthickness=2)
        self.log_frame.place(x=0, y=video_height+20, width=left_width, height=log_height-20)
        log_title = tk.Label(self.log_frame, text="LOG:", bg='#d3d3d3', fg='black', 
                            font=('Arial', 12, 'bold'))
        log_title.pack(anchor='w', padx=10, pady=(5, 0))
        self.log_text = scrolledtext.ScrolledText(self.log_frame, bg='#d3d3d3', fg='black',
                                                  font=('Consolas', 10),
                                                  highlightthickness=0, bd=0)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.log_text.config(state='disabled')
        right_frame = tk.Frame(self.root, bg='black')
        right_frame.place(x=left_width+40, y=20, width=right_width, height=self.screen_height-40)
        self.status_frame = tk.Frame(right_frame, bg='#d3d3d3', highlightbackground='white', 
                                     highlightthickness=2, height=140)
        self.status_frame.pack(fill='x', pady=(0, 20))
        status_title = tk.Label(self.status_frame, text="연결상태", bg='#d3d3d3', fg='black',
                               font=('Arial', 12, 'bold'))
        status_title.pack(pady=(15, 10))
        nodes_frame = tk.Frame(self.status_frame, bg='#d3d3d3')
        nodes_frame.pack()
        self.node_indicators = {}
        for i, (node_name, status) in enumerate(self.nodes.items()):
            node_container = tk.Frame(nodes_frame, bg='#d3d3d3')
            node_container.pack(side='left', padx=25)
            canvas = tk.Canvas(node_container, width=35, height=35, bg='#d3d3d3', highlightthickness=0)
            canvas.pack()
            indicator = canvas.create_oval(5, 5, 30, 30, fill='#505050', outline='black', width=2)
            self.node_indicators[node_name] = (canvas, indicator)
            tk.Label(node_container, text=node_name, bg='#d3d3d3', fg='black',
                    font=('Arial', 11)).pack()
        self.voice_frame = tk.Frame(right_frame, bg='#d3d3d3', highlightbackground='white',
                                    highlightthickness=2, height=120)
        self.voice_frame.pack(fill='x', pady=(0, 20))
        voice_container = tk.Frame(self.voice_frame, bg='#d3d3d3')
        voice_container.pack(pady=35)
        tk.Label(voice_container, text="VOICE_TALK", bg='#d3d3d3', fg='black',
                font=('Arial', 13, 'bold')).pack(side='left', padx=(0, 25))
        self.switch_frame = tk.Frame(voice_container, bg='#d3d3d3')
        self.switch_frame.pack(side='left')
        self.create_toggle_switch()
        self.command_frame = tk.Frame(right_frame, bg='#d3d3d3', highlightbackground='white',
                                      highlightthickness=2)
        self.command_frame.pack(fill='both', expand=True)
        command_title = tk.Label(self.command_frame, text="------*** COMMAND ***------",
                                bg='#d3d3d3', fg='black', font=('Arial', 11))
        command_title.pack(anchor='w', padx=15, pady=15)
        title_container = tk.Frame(self.command_frame, bg='#d3d3d3')
        title_container.pack(fill='x', padx=15, pady=(0, 10))
        tk.Label(title_container, text="Title:", bg='#d3d3d3', fg='black',
                font=('Arial', 11, 'bold')).pack(side='left', padx=(0, 10))
        self.title_entry = tk.Entry(title_container, bg='white', fg='black', font=('Arial', 11))
        self.title_entry.pack(side='left', fill='x', expand=True)
        self.title_entry.insert(0, "→ 배경 현황")
        text_container = tk.Frame(self.command_frame, bg='#d3d3d3')
        text_container.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        tk.Label(text_container, text="TEXT:", bg='#d3d3d3', fg='black',
                font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        self.text_input = tk.Text(text_container, bg='white', fg='black', font=('Arial', 11),
                                 wrap='word')
        self.text_input.pack(fill='both', expand=True)
        self.text_input.insert('1.0', "→ 배경현황")
        send_container = tk.Frame(self.command_frame, bg='#d3d3d3')
        send_container.pack(fill='x', padx=15, pady=15)
        self.send_btn = tk.Button(send_container, text="SEND", bg='#ff0000', fg='white',
                                 font=('Arial', 12, 'bold'), command=self.send_text,
                                 activebackground='#cc0000', cursor='hand2', padx=20, pady=5)
        self.send_btn.pack(side='right')
        bottom_text = tk.Label(send_container, text="",
                              bg='#d3d3d3', fg='#ff0000', font=('Arial', 10))
        bottom_text.pack(side='right', padx=(0, 20))
        exit_btn = tk.Button(self.root, text="✕ 종료", bg='#ff0000', fg='white',
                           font=('Arial', 10, 'bold'), command=self.on_closing)
        exit_btn.place(x=self.screen_width-80, y=10)
        
    def create_toggle_switch(self):
        self.switch_canvas = tk.Canvas(self.switch_frame, width=110, height=45,
                                       bg='#d3d3d3', highlightthickness=0)
        self.switch_canvas.pack()
        self.switch_bg = self.switch_canvas.create_rounded_rectangle(5, 10, 105, 35, 18,
                                                                      fill='#cccccc', outline='')
        self.switch_circle = self.switch_canvas.create_oval(8, 13, 33, 32, fill='white', outline='')
        self.switch_text = self.switch_canvas.create_text(55, 22, text='OFF', fill='#666666',
                                                          font=('Arial', 11, 'bold'))
        self.switch_canvas.bind('<Button-1>', self.toggle_voice)
        
    def toggle_voice(self, event=None):
        if not self.voice_enabled:
            self.voice_enabled = True
            self.switch_canvas.itemconfig(self.switch_bg, fill='#4CAF50')
            self.switch_canvas.coords(self.switch_circle, 77, 13, 102, 32)
            self.switch_canvas.itemconfig(self.switch_text, text='ON', fill='white')
            self.switch_canvas.coords(self.switch_text, 45, 22)
            threading.Thread(target=self.start_voice, daemon=True).start()
        else:
            self.voice_enabled = False
            self.switch_canvas.itemconfig(self.switch_bg, fill='#cccccc')
            self.switch_canvas.coords(self.switch_circle, 8, 13, 33, 32)
            self.switch_canvas.itemconfig(self.switch_text, text='OFF', fill='#666666')
            self.switch_canvas.coords(self.switch_text, 55, 22)
            self.stop_voice()
    
    def start_video(self):
        try:
            wfb_cmd = "sudo wfb_rx -p 0 -c 127.0.0.1 -u 5600 -K /etc/drone.key -i 7669206 wlxfc221c30076b"
            self.processes['video_wfb'] = subprocess.Popen(wfb_cmd, shell=True, 
                                                          stdout=subprocess.PIPE, 
                                                          stderr=subprocess.PIPE)
            time.sleep(2)
            self.video_label.pack_forget()
            self.video_widget.update()
            window_id = self.video_widget.winfo_id()
            pipeline_str = """
                udpsrc port=5600 buffer-size=524288 ! 
                application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! 
                rtph264depay ! h264parse ! avdec_h264 ! 
                videoconvert ! videoscale ! 
                ximagesink sync=false
            """
            self.video_pipeline = Gst.parse_launch(pipeline_str)
            bus = self.video_pipeline.get_bus()
            bus.add_signal_watch()
            bus.enable_sync_message_emission()
            bus.connect("sync-message::element", self.on_sync_message, window_id)
            self.video_pipeline.set_state(Gst.State.PLAYING)
            self.video_running = True
            self.video_start_btn.config(state='disabled')
            self.video_stop_btn.config(state='normal')
            self.add_log("Video stream started and embedded successfully")
        except Exception as e:
            self.add_log(f"Error starting video: {str(e)}")
            messagebox.showerror("Error", f"Failed to start video stream: {str(e)}")
    
    def on_sync_message(self, bus, message, window_id):
        if message.get_structure() is None:
            return
        message_name = message.get_structure().get_name()
        if message_name == "prepare-window-handle":
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(window_id)
    
    def stop_video(self):
        try:
            if self.video_pipeline:
                self.video_pipeline.set_state(Gst.State.NULL)
                self.video_pipeline = None
            if 'video_wfb' in self.processes:
                self.processes['video_wfb'].terminate()
                del self.processes['video_wfb']
            self.video_label.pack(expand=True)
            self.video_running = False
            self.video_start_btn.config(state='normal')
            self.video_stop_btn.config(state='disabled')
            self.add_log("Video stream stopped")
        except Exception as e:
            self.add_log(f"Error stopping video: {str(e)}")
    
    def start_voice(self):
        try:
            tx_cmd = "sudo wfb_tx -f data -p 177 -u 7002 -K /etc/gs.key -k 2 -n 5 -M 1 -i 7669206 wlxfc221c30076b"
            self.processes['voice_tx'] = subprocess.Popen(tx_cmd, shell=True,
                                                         stdout=subprocess.PIPE,
                                                         stderr=subprocess.PIPE)
            self.add_log("Voice TX started")
            time.sleep(1)
            rx_cmd = "sudo wfb_rx -p 49 -c 127.0.0.1 -u 7003 -K /etc/gs.key -i 7669206 wlxfc221c30076b"
            self.processes['voice_rx'] = subprocess.Popen(rx_cmd, shell=True,
                                                         stdout=subprocess.PIPE,
                                                         stderr=subprocess.PIPE)
            self.add_log("Voice RX started")
            time.sleep(1)
            actual_user = os.environ.get('SUDO_USER', os.environ.get('USER', 'user'))
            mic_cmd = f"sudo -u {actual_user} gst-launch-1.0 pulsesrc ! audioconvert ! opusenc bitrate=96000 ! rtpopuspay ! udpsink host=127.0.0.1 port=7002"
            self.processes['voice_mic'] = subprocess.Popen(mic_cmd, shell=True,
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE)
            self.add_log("Microphone input started")
            time.sleep(0.5)
            spk_cmd = f'sudo -u {actual_user} gst-launch-1.0 udpsrc port=7003 caps="application/x-rtp, media=(string)audio, clock-rate=(int)48000, encoding-name=(string)OPUS, payload=(int)96" ! rtpopusdepay ! opusdec ! audioconvert ! alsasink device="default"'
            self.processes['voice_spk'] = subprocess.Popen(spk_cmd, shell=True,
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE)
            self.add_log("Speaker output started")
            self.add_log("Voice communication ON - All components running")
            self.check_voice_processes()
        except Exception as e:
            self.add_log(f"Error starting voice: {str(e)}")
            self.voice_enabled = False
            self.root.after(0, self.reset_voice_switch)
    
    def check_voice_processes(self):
        if self.voice_enabled:
            for name in ['voice_tx', 'voice_rx', 'voice_mic', 'voice_spk']:
                if name in self.processes:
                    if self.processes[name].poll() is not None:
                        returncode = self.processes[name].poll()
                        stderr = self.processes[name].stderr.read().decode() if self.processes[name].stderr else ""
                        self.add_log(f"Warning: {name} terminated with code {returncode}")
                        if stderr:
                            self.add_log(f"Error details: {stderr[:200]}")
            if self.voice_enabled:
                self.root.after(5000, self.check_voice_processes)
    
    def reset_voice_switch(self):
        self.switch_canvas.itemconfig(self.switch_bg, fill='#cccccc')
        self.switch_canvas.coords(self.switch_circle, 8, 13, 33, 32)
        self.switch_canvas.itemconfig(self.switch_text, text='OFF', fill='#666666')
        self.switch_canvas.coords(self.switch_text, 55, 22)
    
    def stop_voice(self):
        try:
            self.voice_enabled = False
            for key in ['voice_mic', 'voice_spk', 'voice_tx', 'voice_rx']:
                if key in self.processes:
                    try:
                        self.processes[key].terminate()
                        time.sleep(0.1)
                        if self.processes[key].poll() is None:
                            self.processes[key].kill()
                    except:
                        pass
                    del self.processes[key]
            self.add_log("Voice communication OFF")
        except Exception as e:
            self.add_log(f"Error stopping voice: {str(e)}")
    
    def send_text(self):
        title = self.title_entry.get()
        text = self.text_input.get('1.0', 'end-1c')
        if not title or not text:
            messagebox.showwarning("Warning", "Title and Text are required")
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.add_log(f"Text sent - Title: {title} at {timestamp}")
        self.title_entry.delete(0, 'end')
        self.text_input.delete('1.0', 'end')
    
    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_queue.put(log_message)
        self.root.after(0, self._update_log_display)
    
    def _update_log_display(self):
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert('end', message + '\n')
                self.log_text.see('end')
                self.log_text.config(state='disabled')
        except:
            pass
    
    def update_node_status(self, node_name, connected):
        if node_name in self.node_indicators:
            canvas, indicator = self.node_indicators[node_name]
            color = '#FFD700' if connected else '#505050'
            canvas.itemconfig(indicator, fill=color)
            if connected:
                self.add_log(f"Connected with {node_name}!")
            else:
                self.add_log(f"Disconnected from {node_name}")
    
    def monitor_processes(self):
        for name, process in list(self.processes.items()):
            if process.poll() is not None:
                if name not in ['voice_mic', 'voice_spk'] or not self.voice_enabled:
                    self.add_log(f"Process {name} terminated")
                del self.processes[name]
        self.root.after(1000, self.monitor_processes)
    
    def on_closing(self):
        result = messagebox.askyesno("종료 확인", "프로그램을 종료하시겠습니까?")
        if not result:
            return
        if self.video_pipeline:
            self.video_pipeline.set_state(Gst.State.NULL)
        for name, process in list(self.processes.items()):
            try:
                process.terminate()
                self.add_log(f"Terminating {name}")
            except:
                pass
        time.sleep(0.5)
        for name, process in list(self.processes.items()):
            try:
                process.kill()
            except:
                pass
        self.root.destroy()
    
    def run(self):
        self.add_log("WFB-NG Ground Station initialized")
        self.add_log("Ready for connections...")
        self.add_log("Press ESC to toggle fullscreen")
        self.root.mainloop()

def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
    points = []
    for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                 (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                 (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                 (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
        points.extend([x, y])
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rectangle = _create_rounded_rectangle

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("이 프로그램은 sudo 권한이 필요합니다.")
        print("다음과 같이 실행하세요: sudo python3 wfb_gs_ui.py")
        print("\n필요한 패키지 설치:")
        print("sudo apt install python3-tk python3-gi python3-gi-cairo gir1.2-gtk-3.0 gstreamer1.0-tools")
        exit(1)
    
    app = WFBGroundStationUI()
    app.run()
