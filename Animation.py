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
            x, y, _ = trajectory[0]
            ObjectHandler.set_position(player_obj, x, y)
        
        return 1 if self.add_animated_object(0, player_obj) else 0
    
    def setup_entities_animation(self, entities, start_entity_id=1):
        animated_count = 0
        for i, entity in enumerate(entities):
            entity_id = start_entity_id + i
            if entity_id < self.total_entities:  
                if self.add_animated_object(entity_id, entity):
                    animated_count += 1
            else:
                break 
        return animated_count
    
    def update(self, delta_time):
        # Sincroniza todos pelo frame global (baseado em tempo e FPS)
        if not hasattr(self, 'frame_counter'):
            self.frame_counter = 0
            self.time_accum = 0.0
        self.time_accum += delta_time
        FPS = 30.0
        frame_duration = 1.0 / FPS
        # Descobrir o maior frame final de todas as entidades
        if not hasattr(self, '_max_frame'):
            self._max_frame = 0
            for traj in self.trajectories.values():
                if traj:
                    last_f = traj[-1][2]
                    if last_f > self._max_frame:
                        self._max_frame = last_f
        while self.time_accum >= frame_duration:
            self.time_accum -= frame_duration
            self.frame_counter += 1
            if self.frame_counter > self._max_frame:
                self.frame_counter = 0
        for entity_id in self.animated_objects:
            if entity_id != 0:
                self._update_single_animation_by_frame(entity_id, self.frame_counter)
    
    def _update_single_animation_by_frame(self, entity_id, frame):
        obj = self.animated_objects[entity_id]
        trajectory = self.trajectories[entity_id]
        first_f = trajectory[0][2]
        last_f = trajectory[-1][2]
        # Só desenha/interpola se frame global está entre o primeiro e o último frame da entidade
        if frame < first_f or frame > last_f:
            ObjectHandler.set_position(obj, -9999, -9999)
            return
        # Busca os dois pontos do dataset que englobam o frame atual
        prev = None
        nextp = None
        for pt in trajectory:
            if pt[2] == frame:
                prev = nextp = pt
                break
            if pt[2] < frame:
                prev = pt
            elif pt[2] > frame:
                nextp = pt
                break
        if prev is None:
            prev = nextp = trajectory[0]
        if nextp is None:
            nextp = prev = trajectory[-1]
        # Interpola se possível
        if prev == nextp:
            x, y, _ = prev
        else:
            f0 = prev[2]
            f1 = nextp[2]
            t = (frame - f0) / (f1 - f0) if f1 != f0 else 0.0
            x = prev[0] + (nextp[0] - prev[0]) * t
            y = prev[1] + (nextp[1] - prev[1]) * t
        ObjectHandler.set_position(obj, x, y)
    
    def reset_all(self):
        for entity_id in self.trajectory_indices:
            self.trajectory_indices[entity_id] = 0.0
    
    def set_all_speeds(self, new_speed):
        self.default_speed = new_speed
        for entity_id in self.animation_speeds:
            self.animation_speeds[entity_id] = new_speed