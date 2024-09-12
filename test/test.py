import cv2
import numpy as np

class Detection:
    def __init__(self, stream, line_pos):
        self.stream = stream
        self.coordinate = [0, 0]
        self.image_result = None
        self.image_boundary = None
        self.line_pos = line_pos
        self.coord_track = []
        self.flag_history = False
        self.roi_selected = False
        self.roi = None
        self.roi_points = []

    def reset_history(self):
        self.coord_track = []

    def select_roi(self):
        def select_points(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.roi_points.append((x, y))
                if len(self.roi_points) == 4:
                    self.roi_selected = True
                    self.roi = np.array(self.roi_points, dtype=np.int32)

        # Create a window and set mouse callback for ROI selection
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
            if len(self.roi_points) == 4:
                cv2.polylines(temp_frame, [np.array(self.roi_points)], isClosed=True, color=(0, 255, 0), thickness=2)

            cv2.imshow('Select ROI', temp_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyWindow('Select ROI')

    def color_detection(self):
        ret, imageFrame = self.stream.read()
        if not ret:
            return

        if self.roi_selected:
            mask = np.zeros_like(imageFrame[:, :, 0])
            cv2.fillPoly(mask, [self.roi], 255)
            roi_frame = cv2.bitwise_and(imageFrame, imageFrame, mask=mask)
        else:
            roi_frame = imageFrame

        height, width, _ = roi_frame.shape

        white_lower = np.array([110, 110, 110], np.uint8)
        white_upper = np.array([255, 255, 255], np.uint8)
        white_mask = cv2.inRange(roi_frame, white_lower, white_upper)

        kernel = np.ones((5, 5), "uint8")
        white_mask = cv2.dilate(white_mask, kernel)
        res_white = cv2.bitwise_and(roi_frame, roi_frame, mask=white_mask)

        contours, _ = cv2.findContours(white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
                    cv2.putText(res_white, "Mouse", (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

                    imageFrame = cv2.rectangle(
                        imageFrame, (x, y), (x + w, y + h), (0, 0, 255), 2
                    )
                    cv2.putText(imageFrame, "Mouse", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                    cv2.putText(imageFrame, f"({x + (w//2)}, {y + (h//2)})", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                    self.coordinate = [x + (w//2), y + (h//2)]
                    detection_buffer += 1
                    object_detected = True

        if not object_detected:
            self.coordinate = [0, 0]

        if self.flag_history:
            self.coord_track.append(self.coordinate)

        imageFrame = cv2.line(imageFrame, (self.line_pos[0], 0), (self.line_pos[0], height), (255, 0, 0), 2)
        cv2.putText(imageFrame, "X1", (self.line_pos[0], 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 1)
        imageFrame = cv2.line(imageFrame, (self.line_pos[1], 0), (self.line_pos[1], height), (255, 0, 0), 2)
        cv2.putText(imageFrame, "X2", (self.line_pos[1], 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 1)

        imageFrame = cv2.line(imageFrame, (0, self.line_pos[2]), (width, self.line_pos[2]), (255, 0, 0), 2)
        cv2.putText(imageFrame, "Y1", (30, self.line_pos[2]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 1)
        imageFrame = cv2.line(imageFrame, (0, self.line_pos[3]), (width, self.line_pos[3]), (255, 0, 0), 2)
        cv2.putText(imageFrame, "Y2", (30, self.line_pos[3]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 1)

        for i in range(len(self.coord_track) - 1):
            cv2.line(res_white, self.coord_track[i], self.coord_track[i + 1], (255, 0, 0), 2)

        self.image_boundary = cv2.resize(imageFrame, (800, 600))
        self.image_result = cv2.resize(res_white, (300, 225))

def main():
    cap = cv2.VideoCapture('../images/Test.mp4')
    line_pos = [100, 500, 100, 400]
    detection = Detection(cap, line_pos)

    detection.select_roi()  # Select ROI before starting detection

    while cap.isOpened():
        detection.color_detection()

        cv2.imshow('Boundary', detection.image_boundary)
        cv2.imshow('Result', detection.image_result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
