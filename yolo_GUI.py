# yolov8_GUI.py

import os
import cv2
import pandas as pd
from PIL import Image, ImageTk
from tkinter import ttk, filedialog, messagebox as tkMessageBox
import customtkinter as ctk
from customtkinter import CTkImage
from yolo_hitung import Tracking
import time

class TrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tracking Mice")
        self.root.geometry("1000x700")
        self.average_prob_data = {}
        self.prediction_data = {}

        # StringVar to store selected video path
        self.video_path = ctk.StringVar()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(script_dir, "weights", "epoch_100", "best.pt")
        self.labels_path = os.path.join(script_dir, "utils", "labels.txt")

        try:
            self.tracking = Tracking(model_path=self.model_path, labels_path=self.labels_path)
        except FileNotFoundError as e:
            ctk.CTkMessageBox.showerror("Error", str(e))
            self.root.destroy()
            return
        except OSError as e:
            ctk.CTkMessageBox.showerror("Error", f"Failed to load model: {str(e)}")
            self.root.destroy()
            return

        self.cap = None
        self.start_time = None  # Initialize start_time
        self.setup_gui()
        self.tracking_active = False

    def setup_gui(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(pady=10)

        header_label = ctk.CTkLabel(header_frame, text="T Maze Spontaneous Alternation Test", font=("Inter", 24))
        header_label.pack()

        subheader_label = ctk.CTkLabel(header_frame, text="Rat Tracking and Monitoring for Laboratories", font=("Inter", 16))
        subheader_label.pack()

        content_frame = ctk.CTkFrame(self.root)
        content_frame.pack(pady=10)

        video_frame = ctk.CTkFrame(content_frame)
        video_frame.grid(row=0, column=0, padx=10, pady=10)

        self.video_canvas = ctk.CTkCanvas(video_frame, width=480, height=240)  # Updated dimensions
        self.video_canvas.pack()

        controls_frame = ctk.CTkFrame(content_frame)
        controls_frame.grid(row=1, column=0, padx=10, pady=10)

        # Horizontal arrangement with different colors
        load_video_button = ctk.CTkButton(controls_frame, text="Load Video", command=lambda: self.select_video_source("file"),
                                          width=10, fg_color="#4158D0", hover_color="#C850C0")
        load_video_button.grid(row=0, column=0, padx=5, pady=5)

        self.filepath_label = ctk.CTkEntry(controls_frame, textvariable=self.video_path, width=40)
        self.filepath_label.grid(row=0, column=1, padx=5, pady=5)  # Placeholder for displaying selected video path

        webcam_button = ctk.CTkButton(controls_frame, text="Use Webcam", command=lambda: self.select_video_source("webcam"),
                                      width=10, fg_color="#4158D0", hover_color="#C850C0")
        webcam_button.grid(row=0, column=2, padx=5, pady=5)

        start_button = ctk.CTkButton(controls_frame, text="Start", command=self.start_tracking,
                                     width=10, fg_color="#33FF57", hover_color="#66FF99")
        start_button.grid(row=1, column=0, padx=5, pady=5)

        stop_button = ctk.CTkButton(controls_frame, text="Stop", command=self.stop_tracking,
                                    width=10, fg_color="#FF3333", hover_color="#FF6666")
        stop_button.grid(row=1, column=1, padx=5, pady=5)

        reset_button = ctk.CTkButton(controls_frame, text="Reset", command=self.reset_tracking,
                                     width=10, fg_color="#808080", hover_color="#F0F0F0")
        reset_button.grid(row=1, column=2, padx=5, pady=5)

        img_download = Image.open("icon_new.png")
        download_button = ctk.CTkButton(controls_frame, text="Download", command=self.download_data,
                                        width=10, fg_color="#4158D0", hover_color="#C850C0",
                                        image=CTkImage(dark_image=img_download, light_image=img_download))
        download_button.grid(row=2, column=0, columnspan=3, pady=10)

        prediction_frame = ctk.CTkFrame(content_frame)
        prediction_frame.grid(row=0, column=1, padx=10, pady=10)

        prediction_label = ctk.CTkLabel(prediction_frame, text="Prediction", font=("Inter", 14))
        prediction_label.pack()

        self.prediction_table = ttk.Treeview(prediction_frame, columns=("Class", "Confidence"), show="headings")
        self.prediction_table.heading("Class", text="Class")
        self.prediction_table.heading("Confidence", text="Confidence")
        self.prediction_table.column("Class", anchor="center")
        self.prediction_table.column("Confidence", anchor="center")
        self.prediction_table.pack(padx=10, pady=10)

        self.prediction_table.tag_configure("right", background="#4158D0")
        self.prediction_table.tag_configure("left", background="#C850C0")

        summary_frame = ctk.CTkFrame(content_frame)
        summary_frame.grid(row=1, column=1, padx=10, pady=10)

        summary_label = ctk.CTkLabel(summary_frame, text="Summary", font=("Inter", 14))
        summary_label.pack()

        self.summary_table = ttk.Treeview(summary_frame, columns=("Metric", "Value"), show="headings")
        self.summary_table.heading("Metric", text="Metric")
        self.summary_table.heading("Value", text="Value")
        self.summary_table.column("Metric", anchor="center")
        self.summary_table.column("Value", anchor="center")
        self.summary_table.pack(padx=10, pady=10)

    def start_tracking(self):
        if not self.tracking_active:
            self.tracking.start_tracking()
            self.start_time = time.time()  # Set start_time when tracking starts
            self.tracking_active = True
            self.update_video_feed()

    def clear_summary_table(self):
        self.summary_table.delete(*self.summary_table.get_children())

    def stop_tracking(self):
        self.tracking.stop_tracking()
        self.tracking_active = False
        total_time = time.time() - self.start_time if self.start_time else 0
        summary_details = self.tracking.get_summary_details()
        summary_details["total_time"] = f"{total_time:.2f} seconds"  # Add total time to summary details
        self.update_summary_table(summary_details)
    
    def reset_tracking(self):
        self.tracking.reset_tracking()
        self.clear_summary_table()
        self.prediction_data = {}  # Clear prediction data
        self.average_prob_data = {}  # Clear average probability data
        self.prediction_table.delete(*self.prediction_table.get_children())  # Clear prediction table
        if self.cap:
            self.cap.release()  # Release the video capture if it exists
        self.cap = cv2.VideoCapture(self.video_path.get())  # Reinitialize the video capture
        self.update_video_feed()

    def update_video_feed(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (480, 240))  # Updated dimensions
                prediction_data = self.tracking.update_tracking_data(frame)
                self.prediction_data = prediction_data
                self.average_prob_data = self.tracking.get_tracking_data()

                frame = self.draw_prediction_data(frame)
                self.display_frame(frame)
                self.update_prediction_table(prediction_data)

                if self.tracking_active:
                    self.root.after(10, self.update_video_feed)

    def draw_prediction_data(self, frame):
        for data in self.prediction_data:
            class_name = data["class"]
            conf = data["confidence"]
            bb = data["bounding_box"]
            color = data["color"]

            cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), color, 3)
            cv2.putText(frame, f"{class_name} {round(conf * 100, 2)}%", (int(bb[0]), int(bb[1]) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        return frame

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(image=frame)
        self.video_canvas.create_image(0, 0, anchor="nw", image=frame)
        self.video_canvas.image = frame

    def select_video_source(self, source_type):
        if source_type == "file":
            file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
            if file_path:
                self.video_path.set(file_path)
                self.cap = cv2.VideoCapture(file_path)
        elif source_type == "webcam":
            self.cap = cv2.VideoCapture(0)

    def update_prediction_table(self, prediction_data):
        self.prediction_table.delete(*self.prediction_table.get_children())

        for data in prediction_data:
            class_name = data["class"]
            conf = data["confidence"]
            tag = "left" if "left" in class_name.lower() else "right"
            self.prediction_table.insert("", "end", values=(class_name, f"{round(conf * 100, 2)}%"), tags=(tag,))

    def update_summary_table(self, summary_data):
        for metric, value in summary_data.items():
            self.summary_table.insert("", "end", values=(metric, value))

    def download_data(self):
        download_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if download_path:
            self.save_to_excel(download_path)

    def save_to_excel(self, file_path):
        summary_data = {
            "Metric": [],
            "Value": []
        }

        # Collect summary table data
        for item in self.summary_table.get_children():
            metric = self.summary_table.item(item)["values"][0]
            value = self.summary_table.item(item)["values"][1]
            summary_data["Metric"].append(metric)
            summary_data["Value"].append(value)

        # Convert summary data into a DataFrame
        summary_df = pd.DataFrame(summary_data)

        # Write to Excel
        with pd.ExcelWriter(file_path) as writer:
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        tkMessageBox.showinfo("Success", "Summary data downloaded successfully.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = TrackingApp(root)
    root.mainloop()
