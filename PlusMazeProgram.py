import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import cv2 

from tkinter import *
from tkinter.messagebox import showinfo
from tkinter import filedialog as fd
from PIL import Image, ImageTk
from lib.chamber_count import *
from lib.object_detection import *
from lib.object_analyze import object_analyze
from utils.settings import *
from lib.state_manager import state


class BoundaryLabel:
    def __init__(self, panel, direction, label_text, row, command_up, command_down):
        style = ttk.Style()
        style.configure("TLabel", background="white")
        self.label = ttk.Label(panel, text=label_text, style="TLabel")
        self.label.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        self.button_down = ttk.Button(panel, text="Left" if direction == 'x' else "Up", command=command_up)
        self.button_down.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        self.button_up = ttk.Button(panel, text="Right" if direction == 'x' else "Down", command=command_down)
        self.button_up.grid(row=row, column=2, padx=5, pady=5, sticky="ew")

        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_columnconfigure(2, weight=1)

class StatisticLabel:
    def __init__(self, panel, row):
        self.panel = panel
        self.row = row
        self.text_time = tk.StringVar()
        self.text_count = tk.StringVar()
        self.label_count = ttk.Label(self.panel, textvariable=self.text_count)
        self.label_count.grid(row=self.row, column=0, padx=5, pady=5, sticky="w")
        self.label_time = ttk.Label(panel, textvariable=self.text_time)
        self.label_time.grid(row=self.row, column=1, padx=5, pady=5, sticky="w")
        

def enumerate_camera_sources(max_cameras=10):
    available_sources = []
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_sources.append(f"Camera {index}")
            cap.release()
    return available_sources

def formatTime(timeInSecond):
    total_seconds = timeInSecond
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{int(hours):02} : {int(minutes):02} : {int(seconds):02}"
    return formatted_time


class MainWindow:
    def __init__(self):
        
        # Inisiasi window GUI
        self.window = tk.Tk()
        self.window.title("Mimofer")
        self.window.configure(bg='white')
        
        # Deteksi camera tersedia
        self.available_source = enumerate_camera_sources()
        
        # Inisiasi Variabel ROI ( Region of Interest)
        self.roi_points = []
        self.roi_selected = False
        
        # Inisiasi Kondisi Tombol
        self.show_chart = False
        self.start_btn_clicked = False
        
        # Inisiasi Menu Window - fungsi ROI
        self.menu = Menu(self.window)
        self.window.config(menu=self.menu)
        self.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="Region Of Interest", menu=self.filemenu)
        self.filemenu.add_command(label="Select" , command=self.select_roi)
        self.filemenu.add_command(label="Clear" , command=self.clear_roi)
        
        # Inisiasi sumber video
        self.stream = cv2.VideoCapture(state.streamConfiguration["path"])
        
        # Inisiasi garis batas (X1, X2, Y1, Y2)
        self.boundary = Boundary_set(10)
        
        # Inisiasi variabel statistik object
        self.text_coordinate = tk.StringVar()
        self.text_time_spend = tk.StringVar()

        # Konfigutasi Layout GRID
        self.window.columnconfigure(0, weight=2)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.panel = tk.Label(self.window)
        self.panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.panel_result = tk.Frame(self.window, bg='white')
        self.panel_result.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.panel_result.grid_rowconfigure(0, weight=1)
        self.panel_result.grid_rowconfigure(10, weight=1)
        self.panel_result.grid_columnconfigure(0, weight=1)
        self.panel_result.grid_columnconfigure(1, weight=1)

        self.panel2 = tk.Label(self.panel_result)
        self.panel2.grid(row=14, column=0, columnspan=2, padx=1, pady=1, sticky="nsew")

        self.panel_settings = tk.Frame(self.panel_result, bg='white')
        self.panel_settings.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.panel_settings.grid_rowconfigure(0, weight=1)
        self.panel_settings.grid_rowconfigure(3, weight=1)
        self.panel_settings.grid_columnconfigure(0, weight=1)
        self.panel_settings.grid_columnconfigure(2, weight=1)

        self.label_coordinate = ttk.Label(self.panel_result, textvariable=self.text_coordinate)
        self.label_coordinate.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Label Statistik hasil Tracking
        self.right = StatisticLabel(self.panel_result, 4)
        self.left = StatisticLabel(self.panel_result, 5)
        self.top = StatisticLabel(self.panel_result, 6)
        self.bottom = StatisticLabel(self.panel_result, 7)
        
        # Label Control Garis Batas
        self.bound_x1 = BoundaryLabel(self.panel_settings, 'x', "X1", 0, self.boundary.set_x1_left, self.boundary.set_x1_right)
        self.bound_x2 = BoundaryLabel(self.panel_settings, 'x', "X2", 1, self.boundary.set_x2_left, self.boundary.set_x2_right)
        self.bound_y1 = BoundaryLabel(self.panel_settings, 'y', "Y1", 2, self.boundary.set_y1_up, self.boundary.set_y1_down)
        self.bound_y2 = BoundaryLabel(self.panel_settings, 'y', "Y2", 3, self.boundary.set_y2_up, self.boundary.set_y2_down)
        
        # Inisiasi class Detection (ROI -> Color Detection), analisis object ( Jarak , Kecepatan) dan counting ( Waktu Lengan dan total masuk ke lengan)
        self.mouse_detection = Detection(self.stream, self.boundary.line_pos)
        self.object_analyze = object_analyze()
        self.object_analyze.object.last_coordinate = self.mouse_detection.coordinate
        self.counter = Elevated_Arm_Counter(self.mouse_detection.coordinate[0],self.mouse_detection.coordinate[1],self.boundary.line_pos)

        self.time_spend = ttk.Label(self.panel_result, textvariable=self.text_time_spend)
        self.time_spend.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        self.select_video_file = ttk.Button(self.panel_result, text="Select File", command=self.select_file, width=20)
        self.select_video_file.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Video Source Selection Button
        self.dd_video_source = ttk.Combobox(self.panel_result,values=self.available_source, state="readonly")
        self.dd_video_source.grid(row=0, column=0 ,padx=5, pady=5, sticky='e')
        self.dd_video_source.set(self.available_source[0])
        self.dd_video_source.bind("<<ComboboxSelected>>", self.switch_video_source)
        

        # CONTROL BUTTONS
        self.button_start_count = ttk.Button(self.panel_result, text="Start", command=self.toggle_button, style="TButton")
        self.button_start_count.grid(row=2, column=0, padx=5, pady=5, columnspan=2, sticky="ew")
        self.button_display_charts = ttk.Button(self.panel_result, text="Summary", command=self.display_bar_charts)
        self.button_display_charts.grid(row=8, column=0, padx=5, pady=5, sticky="ew")
        self.button = ttk.Button(self.panel_result, text="Reset", command=self.resetAll)
        self.button.grid(row=8, column=1, padx=5, pady=5, sticky="ew")
        
      
        self.stop = False
        
        if state.streamConfiguration['path'] != None :
            self.video_loop()
        else:
            self.window_skeleton()
             
        self.window.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()
        
    def select_roi(self):
        def select_points(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and not self.roi_selected:
                self.roi_points.append((x, y))
        
            if len(self.roi_points) > 1:
                distance = np.linalg.norm(np.array(self.roi_points[0]) - np.array(self.roi_points[-1]))
                if distance < 20:
                    self.roi_selected = True
                    self.mouse_detection.roi = self.roi_points

        cv2.namedWindow('Select ROI')
        cv2.setMouseCallback('Select ROI', select_points)

        while not self.roi_selected:
            ret, frame = self.stream.read()
            if not ret:
                break

            temp_frame = frame.copy()
            for point in self.roi_points:
                cv2.circle(temp_frame, point, 5, (0, 0, 255), -1)

            if len(self.roi_points) > 1:
                cv2.polylines(temp_frame, [np.array(self.roi_points)], isClosed=False, color=(0, 255, 0), thickness=2)

            cv2.imshow('Select ROI', temp_frame)
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break

        cv2.destroyWindow('Select ROI')
        
    def clear_roi(self):
        self.roi_selected = False
        self.roi_points = []
        self.mouse_detection.roi=self.roi_points
        
    def select_file(self):
        filetypes = (
        ('Video files', '*.mp4'),
        ('All files', '*.*')
         )

        filepath = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)
        showinfo(title='Selected Files', message=filepath)
        
        if filepath:
            state.video_path = filepath
            self.stream.release()
            self.stream = cv2.VideoCapture(state.video_path)
            if not self.stream.isOpened():
                print(f"Failed to open video file: {state.video_path}")
                return
            self.mouse_detection = Detection(self.stream, self.boundary.line_pos)
        
        
    def switch_video_source(self, event=None):
        selected_source = self.dd_video_source.get()
        camera_number = int(selected_source.split()[-1])
        state.video_path = camera_number
        self.stream.release() 
        self.stream = cv2.VideoCapture(state.video_path) 
        self.mouse_detection = Detection(self.stream, self.boundary.line_pos)
        self.clear_roi()


    def window_skeleton(self):
        self.text_coordinate.set(f"x : 0 m | spd : 0 cm/s")
        self.right.text_count.set(f"R Arm : 00")
        self.left.text_count.set(f"L Arm : 00")
        self.top.text_count.set(f"T Arm : 00")
        self.bottom.text_count.set(f"B Arm : 00")
        
        self.top.text_time.set(f"T Time : 00 : 00 : 00")
        self.bottom.text_time.set(f"B Time : 00 : 00 : 00")
        self.right.text_time.set(f"R Time : 00 : 00 : 00")
        self.left.text_time.set(f"L Time : 00 : 00 : 00")
        
        self.text_time_spend.set(f"00 : 00 : 00")
        
        self.image = Image.fromarray(state.blank_image)
        self.photo = ImageTk.PhotoImage(self.image)
        self.panel.configure(image=self.photo)
        
        self.image2 = Image.fromarray(state.blank_image2)
        self.photo2 = ImageTk.PhotoImage(self.image2)
        self.panel2.configure(image=self.photo2)

    def video_loop(self):
        self.mouse_detection.color_detection()
        
        if self.counter.state.count_start:
            self.object_analyze.object.coordinate = self.mouse_detection.coordinate
            self.object_analyze.calculate_speed()
        self.text_coordinate.set(f"x : {round(self.object_analyze.object.distance*0.00026,1)} m | spd : {round(self.object_analyze.object.speed*0.26)} cm/s")
        self.counter.Count(self.mouse_detection.coordinate[0], self.mouse_detection.coordinate[1])
        
        self.right.text_count.set(f"R Arm : {self.counter.state.right.count:02}")
        self.left.text_count.set(f"L Arm : {self.counter.state.left.count:02}")
        self.top.text_count.set(f"T Arm : {self.counter.state.top.count:02}")
        self.bottom.text_count.set(f"B Arm : {self.counter.state.bottom.count:02}")
        
        self.top.text_time.set(f"T Time : {formatTime(self.counter.state.top.total_time)}")
        self.bottom.text_time.set(f"B Time : {formatTime(self.counter.state.bottom.total_time)}")
        self.right.text_time.set(f"R Time : {formatTime(self.counter.state.right.total_time)}")
        self.left.text_time.set(f"L Time : {formatTime(self.counter.state.left.total_time)}")
        
        self.text_time_spend.set(formatTime(self.counter.state.time_spend))
    
        self.image = Image.fromarray(self.mouse_detection.image_boundary)
        self.photo = ImageTk.PhotoImage(self.image)
        self.panel.configure(image=self.photo)
        
        self.image2 = Image.fromarray(self.mouse_detection.image_result)
        self.photo2 = ImageTk.PhotoImage(self.image2)
        self.panel2.configure(image=self.photo2)
        
        if not self.stop:
            self.window.after(int(1000/state.streamConfiguration["fps"]), self.video_loop)

    def on_close(self):
        self.stop = True
        self.stream.release()
        self.window.destroy()
    
    def toggle_button(self):
          style = ttk.Style()
          
          if self.start_btn_clicked:
               style.configure("TButton", background="SystemButtonFace")
               self.button_start_count.config(text="Start", style="TButton")
          else:
               style.configure("Green.TButton", background="green")
               self.button_start_count.config(text="Stop", style="Green.TButton")

          self.counter.on_start()
          self.mouse_detection.flag_history = self.counter.state.count_start
          self.start_btn_clicked = not self.start_btn_clicked
    
    def resetAll(self):
        if self.start_btn_clicked == True :
            self.toggle_button()
        self.counter.reset()
        self.object_analyze.object.reset()
        self.mouse_detection.reset_history()
        
    def display_bar_charts(self):
        if (self.show_chart == False) :
            self.show_chart = True
            arms = ['Right', 'Left', 'Top', 'Bottom']
            counts = [self.counter.state.right.count,
                    self.counter.state.left.count,
                    self.counter.state.top.count,
                    self.counter.state.bottom.count]
            times = [self.counter.state.right.total_time,
                    self.counter.state.left.total_time,
                    self.counter.state.top.total_time,
                    self.counter.state.bottom.total_time]
            chamber = ['Open', 'Close']
            chamber_counts = [counts[0] + counts[1], counts[2] + counts[3]]
            chamber_times = [times[0] + times[1], times[2] + times[3]]
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 6))
            
            ax1.bar(arms, counts, color='skyblue')
            ax1.set_title('Arm Entries')
            ax1.set_ylabel('Entries')

            ax2.bar(arms, times, color='salmon')
            ax2.set_title('Time In Arm')
            ax2.set_ylabel('Time (s)')
            
            ax3.bar(chamber, chamber_counts, color='skyblue')
            ax3.set_title('Open / Close Entries')
            ax3.set_ylabel('Entries')

            ax4.bar(chamber, chamber_times, color='salmon')
            ax4.set_title('Time In Open/Close')
            ax4.set_ylabel('Time (s)')

            plt.tight_layout()
            plt.show()  
        else : 
            self.show_chart = False
            plt.close("all")   

if __name__ == '__main__':
    MainWindow()
