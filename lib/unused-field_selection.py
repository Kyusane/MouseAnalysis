import cv2
import numpy as np

video_path = "C:/Users/ACER/Downloads/VID_20240220155651.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Gagal membuka video. Periksa path file atau perangkat webcam.")
else:
    while True:
        ret, frame = cap.read()

        # Break the loop if there are no more frames
        if not ret:
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian Blur
        blurred = cv2.GaussianBlur(gray, (11,11), 0)

        # Apply Adaptive Thresholding
        adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Detect edges using Canny
        edges = cv2.Canny(adaptive_thresh, 50, 100)

        # Apply morphological operations to refine edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.erode(edges, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour
            max_contour = max(contours, key=cv2.contourArea)

            # Draw the largest contour
            contour_image = frame.copy()
            cv2.drawContours(contour_image, [max_contour], -1, (0, 0, 255), 2)

            # Create a mask with the largest contour
            mask = np.zeros_like(gray)
            cv2.drawContours(mask, [max_contour], -1, 255, thickness=cv2.FILLED)

            # Apply the mask to the original image
            masked_image = cv2.bitwise_and(frame, frame, mask=mask)

            # Invert the mask to get the area outside the contour
            inverted_mask = cv2.bitwise_not(mask)

            # Fill the area outside the contour with black
            frame[inverted_mask == 255] = 0

            # Calculate the bounding box and center of the largest contour
            x, y, w, h = cv2.boundingRect(max_contour)
            center_x, center_y = x + w // 2, y + h // 2

            # Print the center coordinates
            print(f"Center coordinates: ({center_x}, {center_y})")

            # Display the results
            cv2.imshow('Contours', contour_image)
            # cv2.imshow('Masked Image', frame)
            # cv2.imshow('Gray', blurred)
            # cv2.imshow('Edges', edges)

        # Add a delay (in milliseconds)
        delay = 3  # Adjust this value to change the delay (30 ms ~ 33 FPS)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break

    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()
