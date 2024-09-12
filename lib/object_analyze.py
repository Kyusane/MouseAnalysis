#object_analyze.py

import math

class obj_state:
    def __init__(self):
        self.speed = 0
        self.distance = 0
        self.coordinate = [0,0]
        self.last_coordinate = [0,0]
        
    def reset(self):
        self.speed = 0
        self.distance = 0
        self.coordinate = [0,0]
        self.last_coordinate = [0,0]

class object_analyze:
    def __init__(self):
        self.object = obj_state()
        
    def manhattan_distance(self, coordinate, last_coordinate):
        return abs(coordinate[0] - last_coordinate[0]) + abs(coordinate[1] - last_coordinate[1])
   
    def euclidean_distance(self, a, b):
        return  math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    
    def calculate_speed(self):
        distance = self.euclidean_distance(self.object.coordinate, self.object.last_coordinate)
     #    distance = self.manhattan_distance(self.object.coordinate, self.object.last_coordinate)
        self.object.speed = distance
        self.object.last_coordinate = self.object.coordinate
        self.object.distance += distance