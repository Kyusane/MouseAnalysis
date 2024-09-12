#hitung.py

import os
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import time as t

class Tracking:
    def __init__(self, model_path, labels_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO(model_path)  # Load the model
        self.model.to(self.device)  # Move the model to the correct device
        self.labels = self.load_labels(labels_path)
        self.active = False  # Initialize active attribute
        self.tracking_data = []
        self.previous_positions = []
        self.total_distance = 0
        self.start_time = None
        self.num_left = 0
        self.num_right = 0
        self.arm_left_time = 0
        self.arm_right_time = 0
        self.prob_left_arm = 0
        self.prob_right_arm = 0
        self.pixel_to_meter_scale = 0.35  # Misalnya, 1 unit video = 35 cm = 0.35 meter

    def load_labels(self, labels_path):
        if not os.path.exists(labels_path):
            raise FileNotFoundError(f"Labels file not found: {labels_path}")
        with open(labels_path, 'r') as file:
            labels = file.read().strip().split('\n')
        return labels

    def start_tracking(self):
        self.tracking_data = []
        self.start_time = t.time()
        self.num_left = 0
        self.num_right = 0
        self.arm_left_time = 0
        self.arm_right_time = 0
        self.prob_left_arm = 0
        self.prob_right_arm = 0

    def stop_tracking(self):
        self.start_time = None

    def reset_tracking(self):
        self.tracking_data = []
        self.previous_positions = []
        self.total_distance = 0
        self.start_time = None
        self.num_left = 0
        self.num_right = 0
        self.arm_left_time = 0
        self.arm_right_time = 0
        self.prob_left_arm = 0
        self.prob_right_arm = 0

    def update_tracking_data(self, frame):
        results = self.model(frame)
        frame_wid = 480
        frame_hyt = 240

        # Define boundaries for left and right arms of the T
        top_left = (int(frame_wid * 0.3), int(frame_hyt * 0.4))
        top_right = (int(frame_wid * 0.7), int(frame_hyt * 0.4))
        bottom_center = (int(frame_wid * 0.5), int(frame_hyt * 0.4))

        # Draw boundaries on the frame
        cv2.rectangle(frame, (0, 0), (top_left[0], top_left[1]), (255, 0, 0), 2)  # Left arm
        cv2.rectangle(frame, (top_right[0], 0), (frame_wid, top_right[1]), (0, 0, 255), 2)  # Right arm
        cv2.line(frame, (0, bottom_center[1]), (frame_wid, bottom_center[1]), (0, 255, 0), 2)  # Horizontal line in the center

        if isinstance(results, list):
            results = results[0]

        predictions = results.boxes
        current_positions = []
        tracking_data = []
        for prediction in predictions:
            x1, y1, x2, y2 = prediction.xyxy[0].tolist()
            conf = prediction.conf[0].item()
            cls = prediction.cls[0].item()

            if conf < 0.6:
                continue

            centroid_x = (x1 + x2) / 2
            centroid_y = (y1 + y2) / 2

            if centroid_y > bottom_center[1]:
                continue

            class_name = self.labels[int(cls)]
            tracking_data.append({
                "class": class_name,
                "confidence": conf,
                "bounding_box": [x1, y1, x2, y2],
                "color": (0, 255, 0) if class_name == "right" else (255, 0, 0)
            })

            current_positions.append((centroid_x, centroid_y))

        # Update previous positions and total distance only if there is a change in position
        if len(self.previous_positions) > 0 and len(current_positions) == len(self.previous_positions):
            for i in range(len(current_positions)):
                distance = np.linalg.norm(np.array(current_positions[i]) - np.array(self.previous_positions[i]))
                # Check if the distance exceeds a threshold to consider it as movement
                if distance > 5:  # Adjust this threshold based on your specific scenario
                    self.total_distance += distance * self.pixel_to_meter_scale

        self.previous_positions = current_positions
        self.tracking_data.extend(tracking_data)

        for prev_data in self.tracking_data:
            prev_center_x = prev_data["bounding_box"][0] + (prev_data["bounding_box"][2] - prev_data["bounding_box"][0]) / 2
            prev_center_y = prev_data["bounding_box"][1] + (prev_data["bounding_box"][3] - prev_data["bounding_box"][1]) / 2
            prev_cls = prev_data["class"]
            prev_prob = prev_data["confidence"]

            for curr_data in self.tracking_data:
                curr_center_x = curr_data["bounding_box"][0] + (curr_data["bounding_box"][2] - curr_data["bounding_box"][0]) / 2
                curr_center_y = curr_data["bounding_box"][1] + (curr_data["bounding_box"][3] - curr_data["bounding_box"][1]) / 2
                curr_cls = curr_data["class"]

                if prev_cls == curr_cls:
                    if prev_center_y > bottom_center[1] and curr_center_y <= top_left[1]:
                        if curr_center_x < frame_wid / 2:
                            self.num_left += 1
                            self.arm_left_time += t.time() - self.start_time
                            self.prob_left_arm += prev_prob
                        elif curr_center_x > frame_wid / 2:
                            self.num_right += 1
                            self.arm_right_time += t.time() - self.start_time
                            self.prob_right_arm += prev_prob

        return tracking_data

    def calculate_distance(self, pos1, pos2):
        return np.linalg.norm(np.array(pos1) - np.array(pos2)) * self.pixel_to_meter_scale

    def calculate_speed(self, distance, time_elapsed):
        return distance / time_elapsed if time_elapsed > 0 else 0

    def get_tracking_data(self):
        left_confidences = [data["confidence"] for data in self.tracking_data if data["class"] == "left"]
        right_confidences = [data["confidence"] for data in self.tracking_data if data["class"] == "right"]

        left_mean = np.mean(left_confidences) if left_confidences else 0
        right_mean = np.mean(right_confidences) if right_confidences else 0

        return {
            "left": left_mean,
            "right": right_mean,
        }

    def get_summary_details(self):
        total_time = t.time() - self.start_time if self.start_time else 0
        total_time = round(total_time, 2)

        avg_speed = self.total_distance / total_time if total_time > 0 else 0

        arm_left_time = self.arm_left_time
        arm_right_time = self.arm_right_time

        arm_left_time_seconds = round(arm_left_time, 2)
        arm_right_time_seconds = round(arm_right_time, 2)
        
        left_confidences = [data["confidence"] for data in self.tracking_data if data["class"] == "left"]
        right_confidences = [data["confidence"] for data in self.tracking_data if data["class"] == "right"]

        avg_confidence_left = np.mean(left_confidences) * 100 if left_confidences else 0
        avg_confidence_right = np.mean(right_confidences) * 100 if right_confidences else 0
        avg_speed = self.total_distance / total_time if total_time > 0 else 0

        return {
            "total_time": f"{total_time:.2f} seconds",
            "num_left_entries": self.num_left,
            "num_right_entries": self.num_right,
            "avg_confidence_left": f"{avg_confidence_left:.2f}%",
            "avg_confidence_right": f"{avg_confidence_right:.2f}%",
            #"arm_left_time": f"{arm_left_time_seconds:.2f} seconds",
            #"arm_right_time": f"{arm_right_time_seconds:.2f} seconds",
            "avg_speed": f"{avg_speed:.2f} m/s",
            "total_distance": f"{self.total_distance:.2f} meters"
        }

def convert_frames_to_video(frame_list, output_file_path, frame_width, frame_height, frame_rate):
    out = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (frame_width, frame_height))
    for frame in frame_list:
        out.write(frame)
    out.release()

def process_video(input_video_path, model_path, labels_path, output_video_path):
    tracker = Tracking(model_path, labels_path)
    cap = cv2.VideoCapture(input_video_path)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    frame_list = []
    tracker.start_tracking()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (480, 240))
        tracker.update_tracking_data(frame)
        frame_list.append(frame)
    tracker.stop_tracking()

    convert_frames_to_video(frame_list, output_video_path, 480, 240, frame_rate)
    summary_details = tracker.get_summary_details()
    print("Summary Details:")
    for key, value in summary_details.items():
        print(f"{key}: {value}")

    cap.release()
    return summary_details

if __name__ == "__main__":
    input_video_path = "sample_video.mp4"
    model_path = "best.pt"
    labels_path = "labels.txt"
    output_video_path = "output_video.mp4"

    summary_details = process_video(input_video_path, model_path, labels_path, output_video_path)
    print(summary_details)
