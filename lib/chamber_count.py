#chamber_count.py

import time
import math


class chamber_state:
    def __init__(self):
        self.inside = False
        self.count = 0
        self.entry_time = None
        self.total_time = 0
        self.last_time = 0
    
    def reset(self):
        self.inside = False
        self.count = 0
        self.entry_time = None
        self.total_time = 0
        self.last_time = 0

class Analyze_State:
    def __init__(self):
        self.count_start = False
        self.time_spend = 0
        self.time_spend_start = 0
        self.right = chamber_state()
        self.left = chamber_state()
        self.top = chamber_state()
        self.bottom = chamber_state()

class Elevated_Arm_Counter:
    def __init__(self, x, y, line_pos):
        self.line_pos = line_pos
        self.x = x
        self.y = y
        self.state = Analyze_State()
        
    def Count(self, new_x, new_y):
        if self.state.count_start :
            #RIGHT_CHAMBER
            if self.x <= self.line_pos[1] and self.x >= self.line_pos[0]:
                if new_x > self.line_pos[1] :
                    if not self.state.right.inside:
                        self.state.right.count +=1
                        self.state.right.inside = True
                else :
                    self.state.right.inside = False
                    
            if self.state.right.inside :
                if not self.state.right.entry_time:
                    self.state.right.entry_time = time.time()
                self.state.right.total_time = (time.time() - self.state.right.entry_time ) + self.state.right.last_time
            else :
                self.state.right.entry_time = None
                self.state.right.last_time = self.state.right.total_time
                    
            
            #LEFT_CHAMBER
            if self.x <= self.line_pos[1] and self.x >= self.line_pos[0] :
                if new_x < self.line_pos[0] :
                    if not self.state.left.inside:
                        self.state.left.count +=1
                        self.state.left.inside = True
                else :
                    self.state.left.inside = False
                    
            if self.state.left.inside :
                if not self.state.left.entry_time:
                    self.state.left.entry_time = time.time()
                self.state.left.total_time = (time.time() - self.state.left.entry_time ) + self.state.left.last_time
            else :
                self.state.left.entry_time = None
                self.state.left.last_time = self.state.left.total_time
                    
            #TOP_CHAMBER
            if self.y >= self.line_pos[2] and self.y <= self.line_pos[3]:
                if new_y < self.line_pos[2] :
                    if not self.state.top.inside:
                        self.state.top.count +=1
                        self.state.top.inside = True
                else :
                    self.state.top.inside = False
            
            if self.state.top.inside :
                if not self.state.top.entry_time:
                    self.state.top.entry_time = time.time()
                self.state.top.total_time = (time.time() - self.state.top.entry_time ) + self.state.top.last_time
            else :
                self.state.top.entry_time = None
                self.state.top.last_time = self.state.top.total_time
        
            #BOTTOM_CHAMBER
            if self.y >= self.line_pos[2] and self.y <= self.line_pos[3]:
                if new_y > self.line_pos[3] :
                    if not self.state.bottom.inside:
                        self.state.bottom.count +=1
                        self.state.bottom.inside = True
                else :
                    self.state.bottom.inside = False
            
            if self.state.bottom.inside :
                if not self.state.bottom.entry_time:
                    self.state.bottom.entry_time = time.time()
                self.state.bottom.total_time = (time.time() - self.state.bottom.entry_time ) + self.state.bottom.last_time
            else :
                self.state.bottom.entry_time = None
                self.state.bottom.last_time = self.state.bottom.total_time
                    
            self.state.time_spend = time.time() - self.state.time_spend_start   
            self.x = new_x
            self.y = new_y
        
    def on_start(self):
        if self.state.count_start :
            self.state.count_start = False
            self.state.time_spend_start = 0
        else :
            self.state.count_start = True
            self.state.time_spend_start = time.time()
    
    def reset(self):
        self.state.count_start = False
        self.state.time_spend = 0
        self.state.time_spend_start = 0
        self.state.right.reset()
        self.state.left.reset()
        self.state.top.reset()
        self.state.bottom.reset()

        
    