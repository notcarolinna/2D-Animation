from Reader import Reader

class Animation:
    def __init__(self, paths_file=None):
        if paths_file:
            self.reader = Reader(paths_file)
        else:
            self.reader = Reader()  
            
        self.animated_objects = {}
        self.trajectories = {}
        self.trajectory_indices = {}
        self.animation_speeds = {}
        self.original_positions = {}
        
        self.enabled = True
        self.total_entities = self.reader.get_all_entities_count()
        self.default_speed = 30.0
    
    def add_animated_object(self, entity_id, obj, animation_speed=None):
        if entity_id >= self.total_entities:
            return False
            
        trajectory = self.reader.get_entity_trajectory(entity_id)
        
        if not trajectory:
            return False
        
        if animation_speed is None:
            animation_speed = self.default_speed
        
        # Para player (entidade 0), usar pos.x e pos.y
        if entity_id == 0 and hasattr(obj, 'pos'):
            self.original_positions[entity_id] = (obj.pos.x, obj.pos.y)
        # Para planetas e estrelas, usar x e y
        else:
            self.original_positions[entity_id] = (obj.x, obj.y)
        
        self.animated_objects[entity_id] = obj
        self.trajectories[entity_id] = trajectory
        self.trajectory_indices[entity_id] = 0.0
        self.animation_speeds[entity_id] = animation_speed
        
        return True
    
    def setup_player_animation(self, player_system):
        if len(player_system.quadrados) > 0:
            player_obj = player_system.quadrados[player_system.num_quadrado]
            
            # Posicionar o player na posição inicial da entidade 0
            trajectory = self.reader.get_entity_trajectory(0)
            if trajectory and len(trajectory) > 0:
                initial_pos = trajectory[0]
                player_obj.pos.x = initial_pos[0]
                player_obj.pos.y = initial_pos[1]
            
            success = self.add_animated_object(0, player_obj, self.default_speed)
            return 1 if success else 0
        return 0
    
    def setup_planets_animation(self, planets, start_entity_id=1):
        animated_count = 0
        for i, planet in enumerate(planets):
            entity_id = start_entity_id + i
            if entity_id < self.total_entities:
                success = self.add_animated_object(entity_id, planet, self.default_speed)
                
                if success:
                    animated_count += 1
        
        return animated_count
    
    def setup_stars_animation(self, stars, start_entity_id):
        animated_count = 0
        for i, star in enumerate(stars):
            entity_id = start_entity_id + i
            
            if entity_id < self.total_entities:
                success = self.add_animated_object(entity_id, star, self.default_speed)
                
                if success:
                    animated_count += 1
        
        return animated_count
    
    def update(self, delta_time):
        if not self.enabled:
            return
        
        for entity_id in list(self.animated_objects.keys()):
            self._update_single_animation(entity_id, delta_time)
    
    def _update_single_animation(self, entity_id, delta_time):
        if entity_id not in self.animated_objects:
            return
        
        # Pular atualização da entidade 0 (player) - será controlado manualmente
        if entity_id == 0:
            return
        
        obj = self.animated_objects[entity_id]
        trajectory = self.trajectories[entity_id]
        animation_speed = self.animation_speeds[entity_id]
        
        self.trajectory_indices[entity_id] += animation_speed * delta_time
        
        if self.trajectory_indices[entity_id] >= len(trajectory):
            self.trajectory_indices[entity_id] = 0.0
        
        current_index = int(self.trajectory_indices[entity_id])
        next_index = (current_index + 1) % len(trajectory)
        interpolation_factor = self.trajectory_indices[entity_id] - current_index
        
        current_point = trajectory[current_index]
        next_point = trajectory[next_index]
        
        new_x = current_point[0] + (next_point[0] - current_point[0]) * interpolation_factor
        new_y = current_point[1] + (next_point[1] - current_point[1]) * interpolation_factor
        
        # Para estrelas, usar set_position para criar rastro
        if hasattr(obj, 'set_position'):
            obj.set_position(new_x, new_y)
        # Para planetas, definir posição diretamente
        else:
            obj.x = new_x
            obj.y = new_y
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        
        if not enabled:
            for entity_id, obj in self.animated_objects.items():
                if entity_id in self.original_positions:
                    orig_x, orig_y = self.original_positions[entity_id]
                    # Para player (entidade 0), usar pos
                    if entity_id == 0 and hasattr(obj, 'pos'):
                        obj.pos.x = orig_x
                        obj.pos.y = orig_y
                    # Para estrelas, usar set_position
                    elif hasattr(obj, 'set_position'):
                        obj.set_position(orig_x, orig_y)
                    # Para planetas, definir posição diretamente
                    else:
                        obj.x = orig_x
                        obj.y = orig_y
    
    def reset_all(self):
        for entity_id in self.trajectory_indices:
            self.trajectory_indices[entity_id] = 0.0
        
        if not self.enabled:
            for entity_id, obj in self.animated_objects.items():
                if entity_id in self.original_positions:
                    orig_x, orig_y = self.original_positions[entity_id]
                    if entity_id == 0 and hasattr(obj, 'pos'):
                        obj.pos.x = orig_x
                        obj.pos.y = orig_y
                    elif hasattr(obj, 'set_position'):
                        obj.set_position(orig_x, orig_y)
                    else:
                        obj.x = orig_x
                        obj.y = orig_y
    
    def set_all_speeds(self, new_speed):
        self.default_speed = new_speed
        for entity_id in self.animation_speeds:
            self.animation_speeds[entity_id] = new_speed