import tkinter as tk
import matplotlib.pyplot as plt
import cv2 
from PIL import Image, ImageTk
from lib.chamber_count import *
from lib.object_detection import *
from lib.object_analyze import object_analyze
from utils.settings import *

class boundary_label:
    def __init__(self, panel, direction, label_text,row, command_up,command_down):
        self.label = tk.Label(panel, text=label_text,width=7).grid(row=row, column=0,padx=2, pady=2)
        self.button_down = tk.Button(panel, text="Left" if direction =='x' else "Up", command=command_up, width=15)
        self.button_down.grid(row=row, column=1, padx=2, pady=2)
        self.button_up = tk.Button(panel, text="Right" if direction == 'x' else "Down", command=command_down ,width=15)
        self.button_up.grid(row=row, column=2, padx=2, pady=2)
    
class statistic_label:
    def __init__(self, panel, row):
        self.panel = panel
        self.row = row
        self.text_time = tk.StringVar()
        self.text_count = tk.StringVar()
        self.label_count = tk.Label(self.panel, textvariable=self.text_count, width=20)
        self.label_count.grid(row=self.row,column=0, padx=5, pady=5)
        self.label_time = tk.Label(panel, textvariable=self.text_time, width=20)
        self.label_time.grid(row=self.row,column=1,padx=5, pady=5)

class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Mimofer")
        self.window['bg'] = 'white'
        self.streamConf = {
            "fps" : 30,
            "path" : "../Ball.mp4"
            # "path" : 0
        }
        self.stream = cv2.VideoCapture(self.streamConf["path"])
        self.boundary = Boundary_set(10)
        self.show_chart = False
        
        self.start_btn_clicked = False 
        self.text_coordinate = tk.StringVar()
        self.text_time_spend = tk.StringVar()
        
        self.panel = tk.Label(self.window)
        self.panel.grid(row=0, column=0, padx=5, pady=5)
        
        self.panel_result = tk.Frame(self.window, width=320, height=600, bg='white')
        self.panel_result.grid(row=0, column=1, padx=5, pady=5)
        self.panel_result.grid_propagate(0)
        
        self.panel2 = tk.Label(self.panel_result)
        self.panel2.grid(row=14, column=0, columnspan=2, padx=1, pady=1)
        
        self.panel_settings = tk.Frame(self.panel_result, width=300, height=150, bg='white')
        self.panel_settings.grid(row=13, column=0,columnspan=2,padx=5, pady=5)
        self.panel_settings.grid_propagate(0)
        
        self.label_coordinate = tk.Label(self.panel_result, textvariable=self.text_coordinate, width=20)
        self.label_coordinate.grid(row=0,column=0, padx=5, pady=5)
       
        self.right = statistic_label(self.panel_result,1)
        self.left = statistic_label(self.panel_result,2)
        self.top = statistic_label(self.panel_result,3)
        self.bottom = statistic_label(self.panel_result,4)
        
        self.bound_x1 = boundary_label(self.panel_settings,'x',"X1",0,self.boundary.set_x1_left, self.boundary.set_x1_right)
        self.bound_x2 = boundary_label(self.panel_settings,'x',"X2",1,self.boundary.set_x2_left, self.boundary.set_x2_right)
        self.bound_y1 = boundary_label(self.panel_settings,'y',"Y1",2,self.boundary.set_y1_up, self.boundary.set_y1_down)
        self.bound_y2 = boundary_label(self.panel_settings,'y',"Y2",3,self.boundary.set_y2_up, self.boundary.set_y2_down)
        
        self.mouse_detection = Detection(self.stream,self.boundary.line_pos)
        self.object_analyze = object_analyze()
        self.object_analyze.object.last_coordinate = self.mouse_detection.coordinate
        self.counter = Elevated_Arm_Counter(self.mouse_detection.coordinate[0],
                                            self.mouse_detection.coordinate[1], 
                                            self.boundary.line_pos)
        
        self.time_spend = tk.Label(self.panel_result, textvariable=self.text_time_spend, width=20)
        self.time_spend.grid(row=0, column=1, padx=5, pady=5)
        
        # CONTROL BUTTON
        self.button = tk.Button(self.panel_result, text="Reset", command=self.resetAll, width=20)
        self.button.grid(row=10, column=1, padx=5, pady=5)
        
        self.button_display_charts = tk.Button(self.panel_result, text="Display Charts", command=self.display_bar_charts, width=20)
        self.button_display_charts.grid(row=10, column=0, padx=5, pady=5)
        
        self.button_start_count = tk.Button(self.panel_result, text="Start", command=self.toggle_button, width=43)
        self.button_start_count.grid(row=11, column=0, padx=1 ,pady=1 , columnspan=2)

        self.stop = False
        
        self.video_loop()
        self.window.wm_protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.mainloop()

    def video_loop(self):
        self.mouse_detection.color_detection()
        if self.counter.state.count_start:
            self.object_analyze.object.coordinate = self.mouse_detection.coordinate
            self.object_analyze.calculate_speed()
        self.text_coordinate.set(f"x : {round(self.object_analyze.object.distance*0.00026,1)} m | spd : {round(self.object_analyze.object.speed*0.26)} cm/s")
        self.counter.Count(self.mouse_detection.coordinate[0], self.mouse_detection.coordinate[1])
        
        self.right.text_count.set(f"R Arm : {self.counter.state.right.count}")
        self.left.text_count.set(f"L Arm : {self.counter.state.left.count}")
        self.top.text_count.set(f"T Arm : {self.counter.state.top.count}")
        self.bottom.text_count.set(f"B Arm : {self.counter.state.bottom.count}")
        
        self.top.text_time.set(f"T Time : {round(self.counter.state.top.total_time,2)} s")
        self.bottom.text_time.set(f"B Time : {round(self.counter.state.bottom.total_time,2)} s")
        self.right.text_time.set(f"R Time : {round(self.counter.state.right.total_time,2)} s")
        self.left.text_time.set(f"L Time : {round(self.counter.state.left.total_time,2)} s")
        
        self.text_time_spend.set(f"{round(self.counter.state.time_spend,2)} s")
        
        self.image = Image.fromarray(self.mouse_detection.image_boundary)
        self.photo = ImageTk.PhotoImage(self.image)
        self.panel.configure(image=self.photo)
        
        self.image2 = Image.fromarray(self.mouse_detection.image_result)
        self.photo2 = ImageTk.PhotoImage(self.image2)
        self.panel2.configure(image=self.photo2)
        
        if not self.stop:
            self.window.after(int(1000/self.streamConf["fps"]), self.video_loop)

    def on_close(self):
        self.stop = True
        self.stream.release()
        self.window.destroy()
    
    def toggle_button(self):
        if self.start_btn_clicked:
            self.button_start_count.config(bg="SystemButtonFace")
        else:
            self.button_start_count.config(bg="green") 
        self.counter.on_start()
        self.mouse_detection.flag_history = self.counter.state.count_start
        self.start_btn_clicked = not self.start_btn_clicked
    
    def resetAll(self):
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
