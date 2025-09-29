from Reader import Reader

class AnimationSystem:
    def __init__(self, paths_file=None):
        if paths_file:
            self.reader = Reader(paths_file)
        else:
            self.reader = Reader()  
            
        self.sun = None
        self.sun_trajectory = None
        self.sun_trajectory_index = 0.0
        self.sun_animation_speed = 30.0
        self.enabled = True
    
    def set_sun(self, sun_object):
        self.sun = sun_object
        self.sun_trajectory = self.reader.get_entity_trajectory(0)  # Primeira entidade
        
        if self.sun_trajectory:
            # Salvar posição original
            self.sun.original_x = self.sun.x
            self.sun.original_y = self.sun.y
            return True
        return False
    
    def update(self, delta_time):
        if not self.enabled or not self.sun or not self.sun_trajectory:
            return
        
        self.sun_trajectory_index += self.sun_animation_speed * delta_time
        
        if self.sun_trajectory_index >= len(self.sun_trajectory):
            self.sun_trajectory_index = 0.0
        
        current_index = int(self.sun_trajectory_index)
        next_index = (current_index + 1) % len(self.sun_trajectory)
        interpolation_factor = self.sun_trajectory_index - current_index
        
        current_point = self.sun_trajectory[current_index]
        next_point = self.sun_trajectory[next_index]
        
        self.sun.x = current_point[0] + (next_point[0] - current_point[0]) * interpolation_factor
        self.sun.y = current_point[1] + (next_point[1] - current_point[1]) * interpolation_factor
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        
        if not enabled and self.sun:
            self.sun.x = self.sun.original_x
            self.sun.y = self.sun.original_y
    
    def reset_all(self):
        self.sun_trajectory_index = 0.0
        
        if self.sun and not self.enabled:
            self.sun.x = self.sun.original_x
            self.sun.y = self.sun.original_y
    
    def set_sun_speed(self, speed):
        self.sun_animation_speed = speed
    
    def print_status(self):
        self.reader.print_entities_summary()
        
        if self.sun:
            print(f"SOL - Posição atual: ({self.sun.x:.2f}, {self.sun.y:.2f})")
            print(f"SOL - Animação: {'ATIVA' if self.enabled else 'INATIVA'}")
            print(f"SOL - Velocidade: {self.sun_animation_speed}")