from Reader import Reader
from ObjectHandler import ObjectHandler

class Animation:
    def __init__(self, paths_file=None):
        self.reader = Reader(paths_file) if paths_file else Reader()
        self.animated_objects = {}
        self.trajectories = {}
        self.trajectory_indices = {}
        self.animation_speeds = {}
        self.total_entities = self.reader.get_all_entities_count()
        self.default_speed = 30.0
    
    def add_animated_object(self, entity_id, obj, animation_speed=None):
        if entity_id >= self.total_entities:
            return False
            
        trajectory = self.reader.get_entity_trajectory(entity_id)
        if not trajectory:
            return False
        
        self.animated_objects[entity_id] = obj
        self.trajectories[entity_id] = trajectory
        self.trajectory_indices[entity_id] = 0.0
        self.animation_speeds[entity_id] = animation_speed or self.default_speed
        
        return True
    
    def setup_player_animation(self, player_system):
        if not player_system.quadrados:
            return 0
            
        player_obj = player_system.quadrados[player_system.num_quadrado]
        trajectory = self.reader.get_entity_trajectory(0)
        
        if trajectory:
            ObjectHandler.set_position(player_obj, *trajectory[0])
        
        return 1 if self.add_animated_object(0, player_obj) else 0
    
    def setup_entities_animation(self, entities, start_entity_id=1):
        animated_count = 0
        for i, entity in enumerate(entities):
            entity_id = start_entity_id + i
            if entity_id < self.total_entities:  # Só anima se houver trajetória
                if self.add_animated_object(entity_id, entity):
                    animated_count += 1
            else:
                break  # Para de tentar animar se não há mais trajetórias
        return animated_count
    
    def update(self, delta_time):
        for entity_id in self.animated_objects:
            if entity_id != 0:  # Skip player
                self._update_single_animation(entity_id, delta_time)
    
    def _update_single_animation(self, entity_id, delta_time):
        obj = self.animated_objects[entity_id]
        trajectory = self.trajectories[entity_id]
        
        self.trajectory_indices[entity_id] += self.animation_speeds[entity_id] * delta_time
        
        if self.trajectory_indices[entity_id] >= len(trajectory):
            self.trajectory_indices[entity_id] = 0.0
        
        current_index = int(self.trajectory_indices[entity_id])
        next_index = (current_index + 1) % len(trajectory)
        t = self.trajectory_indices[entity_id] - current_index
        
        current_point = trajectory[current_index]
        next_point = trajectory[next_index]
        
        new_x = current_point[0] + (next_point[0] - current_point[0]) * t
        new_y = current_point[1] + (next_point[1] - current_point[1]) * t
        
        ObjectHandler.set_position(obj, new_x, new_y)
    
    def reset_all(self):
        for entity_id in self.trajectory_indices:
            self.trajectory_indices[entity_id] = 0.0
    
    def set_all_speeds(self, new_speed):
        self.default_speed = new_speed
        for entity_id in self.animation_speeds:
            self.animation_speeds[entity_id] = new_speed