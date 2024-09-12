import cv2
import numpy as np

# Global variable to store the points and tolerance
points = []
tolerance = 15  # Set the tolerance value (in pixels)
polygon_selected = False

# Mouse callback function
def select_points(event, x, y, flags, param):
    global points, polygon_selected
    
    if event == cv2.EVENT_LBUTTONDOWN and not polygon_selected:
        # Store the point when the left mouse button is clicked
        points.append((x, y))
        
        # Check if the first point and the last point are within tolerance
        if len(points) > 1:
            distance = np.linalg.norm(np.array(points[0]) - np.array(points[-1]))
            if distance < tolerance:
                polygon_selected = True

# Create a window
cv2.namedWindow('Select Points')
cv2.setMouseCallback('Select Points', select_points)

# Open video file
cap = cv2.VideoCapture('../images/Test.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Make a copy of the frame to draw on
    temp_frame = frame.copy()

    # Draw the points and connect them
    for i, point in enumerate(points):
        cv2.circle(temp_frame, point, 5, (0, 0, 255), -1)  # Draw points in red
        if i > 0:
            cv2.line(temp_frame, points[i - 1], point, (255, 0, 0), 2)  # Connect points with blue lines

    if polygon_selected:
        cv2.polylines(temp_frame, [np.array(points)], isClosed=True, color=(0, 255, 0), thickness=2)  # Draw polygon
        cv2.putText(temp_frame, 'Area Selected!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Create a mask for the selected area
        mask = np.zeros_like(frame)
        cv2.fillPoly(mask, [np.array(points)], (255, 255, 255))
        mask = mask[:, :, 0]  # Convert mask to single channel

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Threshold the grayscale image to get binary image for white object detection
        _, binary = cv2.threshold(gray, 150, 200, cv2.THRESH_BINARY)

        # Apply the mask to the binary image
        masked_binary = cv2.bitwise_and(binary, mask)

        # Find contours of the white objects within the selected area
        contours, _ = cv2.findContours(masked_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(temp_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Draw bounding box in red
            cv2.putText(temp_frame, 'Tikus', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Label in red

    # Display the frame
    cv2.imshow('Select Points', temp_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
