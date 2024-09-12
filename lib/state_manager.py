#state_manager.py

import numpy as np
import cv2 

class StateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.init_state()
        return cls._instance

    def init_state(self):
        self.blank_image = np.zeros((600, 800, 3), dtype=np.uint8)
        self.blank_image2 = np.zeros((225, 300, 3), dtype=np.uint8)
        self.video_path = 0
        
        self.streamConfiguration = {
            "source" : "camera",
            "fps": 60,
            "path": self.video_path
        }
        
        self.status ={
            
        }
        
        self.button_clicked = {
            'elevated': False,
            'image': False,
            'video': False
        }
        
        self.roi_selected = False
        self.roi_points = []
        

    def set_button_clicked(self, button_name):
        self.button_clicked[button_name] = True

    def reset_button_clicked(self, button_name):
        self.button_clicked[button_name] = False
        
    def update_video_source(self, sourceType, path):
        self.video_path = path
        self.streamConfiguration["source"] = sourceType

state = StateManager()
