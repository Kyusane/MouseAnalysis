import cv2
import numpy as np

from state_manager import state

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
        height, width, _ = imageFrame.shape
        
        if len(self.roi) > 0 :
            mask = np.zeros_like(imageFrame)
            cv2.fillPoly(mask, [np.array(self.roi)], (255, 255, 255))
            mask = mask[:, :, 0]
            roi_frame = cv2.bitwise_and(imageFrame, imageFrame, mask=mask)
        else:
            roi_frame = imageFrame
        
        white_lower = np.array([200, 200, 200], np.uint8)
        white_upper = np.array([255, 255, 255], np.uint8)
        white_mask = cv2.inRange(roi_frame, white_lower, white_upper)

        kernel = np.ones((5, 5), "uint8")
        white_mask = cv2.dilate(white_mask, kernel)
        res_white = cv2.bitwise_and(roi_frame, roi_frame, mask=white_mask)

        contours, hierarchy = cv2.findContours(
            white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        detection_count_max = 1
        detection_buffer = 0
        object_detected = False

        for pic, contour in enumerate(contours):
            if detection_buffer < detection_count_max:
                area = cv2.contourArea(contour)
                if area > 300:
                    x, y, w, h = cv2.boundingRect(contour)
                    res_white = cv2.rectangle(
                        res_white, (x, y), (x + w, y + h), (0, 0, 255), 2
                    )
                    cv2.putText(res_white,"Mouse",(x, y - 20),cv2.FONT_HERSHEY_SIMPLEX,1.0, (0, 0, 255),)
                    
                    roi_frame = cv2.rectangle(
                        roi_frame, (x, y), (x + w, y + h), (0, 0, 255), 2
                    )
                    cv2.putText(roi_frame,"Mouse",(x, y),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255),2)
                    cv2.putText(roi_frame, f"({x + (w//2)}, {y + (h//2)})", (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                    self.coordinate = [x + (w//2), y + (h//2)]
                    detection_buffer += 1
                    object_detected = True 

        if not object_detected:
            self.coordinate = [0, 0]
        
        if self.flag_history:
            self.coord_track.append(self.coordinate)
            
        if len(self.roi) > 0 :
            cv2.polylines(roi_frame, [np.array(self.roi)], isClosed=True, color=(0, 255, 0), thickness=2)
            
        roi_frame = cv2.line(roi_frame, (self.line_pos[0], 0), (self.line_pos[0], height), (255, 0, 0), 2)
        cv2.putText(roi_frame,"X1",(self.line_pos[0], 30),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
        roi_frame = cv2.line(roi_frame, (self.line_pos[1], 0), (self.line_pos[1], height), (255, 0, 0), 2)
        cv2.putText(roi_frame,"X2",(self.line_pos[1], 30),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
        
        roi_frame = cv2.line(roi_frame, (0, self.line_pos[2]), (width ,self.line_pos[2]), (255, 0, 0), 2)
        cv2.putText(roi_frame,"Y1",(30, self.line_pos[2]),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
        roi_frame = cv2.line(roi_frame, (0, self.line_pos[3]), (width ,+ self.line_pos[3]), (255, 0, 0), 2)
        cv2.putText(roi_frame,"Y2",(30, self.line_pos[3]),cv2.FONT_HERSHEY_SIMPLEX,1.0, (255, 0, 0),1)
    
        for i in range(len(self.coord_track) - 1):
            cv2.line(res_white, self.coord_track[i], self.coord_track[i+1], (255, 0, 0), 2)
        
        self.image_boundary = cv2.resize(roi_frame,(800,600))
        self.image_result = cv2.resize(res_white,(300,225))
        