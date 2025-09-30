import math
from ObjectHandler import ObjectHandler

class CollisionSystem:
    def __init__(self):
        self.repulsion_force = 1.2
        self.min_distance_factor = 0.15
        
    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def check_collision(self, obj1, obj2):
        x1, y1 = ObjectHandler.get_pos(obj1)
        x2, y2 = ObjectHandler.get_pos(obj2)
        r1, r2 = ObjectHandler.get_radius(obj1), ObjectHandler.get_radius(obj2)
        
        dist = self.distance(x1, y1, x2, y2)
        return dist < (r1 + r2) * (1 + self.min_distance_factor)
    
    def apply_repulsion(self, obj1, obj2):
        x1, y1 = ObjectHandler.get_pos(obj1)
        x2, y2 = ObjectHandler.get_pos(obj2)
        r1, r2 = ObjectHandler.get_radius(obj1), ObjectHandler.get_radius(obj2)
        
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 0.01:
            dx, dy, dist = 1, 0, 0.01
        
        dx, dy = dx/dist, dy/dist
        min_dist = (r1 + r2) * (1 + self.min_distance_factor)
        overlap = min_dist - dist
        
        if overlap > 0:
            force = overlap * self.repulsion_force * 0.5
            max_move = 0.8
            
            move_x = max(-max_move, min(max_move, force))
            move_y = max(-max_move, min(max_move, force))
            
            ObjectHandler.set_pos(obj1, x1 - dx * move_x, y1 - dy * move_y)
            ObjectHandler.set_pos(obj2, x2 + dx * move_x, y2 + dy * move_y)
    
    def update_collisions(self, objects):
        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                if self.check_collision(objects[i], objects[j]):
                    self.apply_repulsion(objects[i], objects[j])