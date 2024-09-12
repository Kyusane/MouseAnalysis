import cv2

def enumerate_camera_sources(max_cameras=10):
    available_sources = []
    for index in range(max_cameras):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_sources.append(index)
            cap.release()
    return available_sources

# # Example usage
# if __name__ == '__main__':
#     sources = enumerate_camera_sources()
#     print("Available camera sources:", sources)
    

