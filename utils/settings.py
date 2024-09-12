import cv2

class source_set:
     def __init__(self):
          self.camera_selected = 0
          self.camera_list = self.list_camera_sources()
     
     def list_camera_sources(self):
          camera_sources = []
          for i in range(10):
               cap = cv2.VideoCapture(i)
               if cap.isOpened():
                    camera_name = f"Camera {i}"
                    camera_sources.append(camera_name)
                    cap.release()
          return camera_sources

class Boundary_set :
     def __init__(self, range):
          self.line_pos = [200,300,100,200]
          self.range = range
          self.max_gap = 2
          
     def set_x1_left(self):
          self.line_pos[0] -= self.range
     def set_x1_right(self):
          if self.line_pos[0] < self.line_pos[1] - self.max_gap :
               self.line_pos[0] += self.range
          
     def set_x2_left(self):
          if self.line_pos[1] > self.line_pos[0] + self.max_gap :
               self.line_pos[1] -= self.range
     def set_x2_right(self):
          self.line_pos[1] += self.range
          
     def set_y1_up(self):
          self.line_pos[2] -= self.range
     def set_y1_down(self):
          if self.line_pos[2] < self.line_pos[3] - self.max_gap:
               self.line_pos[2] += self.range
          
     def set_y2_up(self):
          if self.line_pos[3] > self.line_pos[2] + self.max_gap:
               self.line_pos[3] -= self.range
     def set_y2_down(self):
          self.line_pos[3] += self.range
          

               
          