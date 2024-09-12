#object_detection.py

import cv2
import numpy as np

class Detection:
    def __init__(self, stream, line_pos):
        self.stream = stream
        self.coordinate = [0, 0]
        self.image_result = self.stream.read()
        self.image_boundary = self.image_result
        self.line_pos = line_pos
        self.coord_track = []
        self.flag_history = False
        self.roi = []
    
    def reset_history(self):
        self.coord_track = []
        
    def color_detection(self):
        ret , imageFrame = self.stream.read()
        if  not ret:
            imageFrame = np.zeros((600, 800, 3), dtype=np.uint8)
            cv2.putText(imageFrame, "No Frame Available", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        height, width, _ = imageFrame.shape
        rawFrame = imageFrame.copy()
        
        if len(self.roi) > 0 :
            mask = np.zeros_like(imageFrame)
            cv2.fillPoly(mask, [np.array(self.roi)], (255, 255, 255))
            mask = mask[:, :, 0]
        
            gray = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(gray, 150, 200, cv2.THRESH_BINARY)
            masked_binary = cv2.bitwise_and(binary, mask)
            contours, _ = cv2.findContours(masked_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 3)  # Draw bounding box in red
                cv2.putText(imageFrame, 'Tikus', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)  # Label in red
                self.coordinate = [x + (w//2), y + (h//2)]
        

        # if not object_detected:
        #     self.coordinate = [0, 0]
        
        if self.flag_history:
            self.coord_track.append(self.coordinate)
            
        if len(self.roi) > 0 :
            cv2.polylines(imageFrame, [np.array(self.roi)], isClosed=True, color=(0, 255, 0), thickness=4)
        else:
            imageFrame = rawFrame
            
        imageFrame = cv2.line(imageFrame, (self.line_pos[0], 0), (self.line_pos[0], height), (255, 0, 0), 2)
        cv2.putText(imageFrame,"X1",(self.line_pos[0], 30),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
        imageFrame = cv2.line(imageFrame, (self.line_pos[1], 0), (self.line_pos[1], height), (255, 0, 0), 2)
        cv2.putText(imageFrame,"X2",(self.line_pos[1], 30),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
        
        imageFrame = cv2.line(imageFrame, (0, self.line_pos[2]), (width ,self.line_pos[2]), (255, 0, 0), 2)
        cv2.putText(imageFrame,"Y1",(30, self.line_pos[2]),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
        imageFrame = cv2.line(imageFrame, (0, self.line_pos[3]), (width ,+ self.line_pos[3]), (255, 0, 0), 2)
        cv2.putText(imageFrame,"Y2",(30, self.line_pos[3]),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
    
        for i in range(len(self.coord_track) - 1):
            # cv2.circle(rawFrame, self.coord_track[i], 4, (255,0,0), -1)
            cv2.line(rawFrame, self.coord_track[i], self.coord_track[i+1], (255, 0, 0), 3)
        
        self.image_boundary = cv2.resize(imageFrame,(800,600))
        self.image_result = cv2.resize(rawFrame,(300,225))
        