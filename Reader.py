import re
import os

class Reader:
    def __init__(self, paths_file="./resources/Paths_D.txt"):
        self.paths_file = paths_file
        self.scale = None
        self.entities = []
        self.load_data()
    
    def load_data(self):
        
        with open(self.paths_file, 'r') as file:
            lines = file.readlines()
                
        scale_match = re.search(r'\[(\d+)\]', lines[0])
        if scale_match:
            self.scale = int(scale_match.group(1))
        else:
            return
        
        entity_pattern = re.compile(r'(\d+)\s+(.+)')
        point_pattern = re.compile(r'\((\d+),(\d+),(\d+)\)')
        
        for i, line in enumerate(lines[1:], 1): 
            line = line.strip()
            if not line:
                continue
                
            match = entity_pattern.match(line)
            if not match:
                continue
            
            num_points = int(match.group(1))
            coordinates_str = match.group(2)
            
            points = point_pattern.findall(coordinates_str)
            
            trajectory = []
            for x, y, f in points:
                norm_x = int(x) / self.scale
                norm_y = int(y) / self.scale
                frame = int(f)
                trajectory.append([norm_x, norm_y, frame])
            
            self.entities.append(trajectory)
        
    
    def get_entity_trajectory(self, entity_index):        
        if entity_index < len(self.entities):
            trajectory = self.entities[entity_index]
            return trajectory
        else:
            return []
    
    def get_all_entities_count(self):
        return len(self.entities)