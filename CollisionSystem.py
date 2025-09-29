import math

class ObjectHandler:
    def get_pos(obj):
        return (obj.pos.x, obj.pos.y) if hasattr(obj, 'pos') else (obj.x, obj.y)
    
    def set_pos(obj, x, y):
        if hasattr(obj, 'pos'):
            obj.pos.x, obj.pos.y = x, y
        else:
            obj.x, obj.y = x, y
    
    def get_radius(obj):
        if hasattr(obj, 'size'):
            return obj.size * 3.0
        if hasattr(obj, 'radius'):
            multipliers = {
                'sun': 1.3, 'saturn': 2.0, 'jupiter': 1.2, 'earth': 1.1
            }
            name = getattr(obj, 'name', '').lower()
            return obj.radius * multipliers.get(name, 1.05)
        if hasattr(obj, 'w'):
            return max(obj.w, obj.h) / 2 * 1.1
        return 0.5
    
    def get_mass(obj):
        if hasattr(obj, 'name'):
            masses = {
                'sun': 15.0, 'jupiter': 8.0, 'saturn': 6.0, 'neptune': 4.0,
                'uranus': 4.0, 'earth': 2.5, 'venus': 2.4, 'mars': 1.5, 'mercury': 1.0
            }
            return masses.get(obj.name.lower(), 2.0)
        if hasattr(obj, 'size'):
            return obj.size * 0.8
        return 1.8

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
        m1, m2 = ObjectHandler.get_mass(obj1), ObjectHandler.get_mass(obj2)
        
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 0.01:
            dx, dy, dist = 1, 0, 0.01
        
        dx, dy = dx/dist, dy/dist
        min_dist = (r1 + r2) * (1 + self.min_distance_factor)
        overlap = min_dist - dist
        
        if overlap > 0:
            total_mass = m1 + m2
            force1 = overlap * self.repulsion_force * (m2 / total_mass) * 0.8
            force2 = overlap * self.repulsion_force * (m1 / total_mass) * 0.8
            
            max_move1, max_move2 = 0.8 / math.sqrt(m1), 0.8 / math.sqrt(m2)
            
            move1_x = max(-max_move1, min(max_move1, -dx * force1))
            move1_y = max(-max_move1, min(max_move1, -dy * force1))
            move2_x = max(-max_move2, min(max_move2, dx * force2))
            move2_y = max(-max_move2, min(max_move2, dy * force2))
            
            ObjectHandler.set_pos(obj1, x1 + move1_x, y1 + move1_y)
            ObjectHandler.set_pos(obj2, x2 + move2_x, y2 + move2_y)
    
    def update_collisions(self, objects):
        for i in range(len(objects)):
            for j in range(i + 1, len(objects)):
                if self.check_collision(objects[i], objects[j]):
                    self.apply_repulsion(objects[i], objects[j])