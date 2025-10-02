import math
import random
from GraphicsUtils import DrawUtils

class BackgroundStars:
    def __init__(self, count=300, seed=42):
        self.count = count
        self.seed = seed
        self.stars = self._create_stars()
        self.point_size = 4.0
    
    def _create_stars(self):
        random.seed(self.seed)
        stars = []
        
        for _ in range(self.count):
            star_type = random.choice(['small', 'medium', 'bright', 'giant'])
            
            if star_type == 'small':
                brightness = random.uniform(0.3, 0.6)
                size_mult = 0.8
                twinkle_speed = random.uniform(3.0, 6.0)
            elif star_type == 'medium':
                brightness = random.uniform(0.6, 0.8)
                size_mult = 1.0
                twinkle_speed = random.uniform(2.0, 4.0)
            elif star_type == 'bright':
                brightness = random.uniform(0.8, 1.0)
                size_mult = 1.3
                twinkle_speed = random.uniform(1.5, 3.0)
            else:
                brightness = random.uniform(0.9, 1.0)
                size_mult = 1.8
                twinkle_speed = random.uniform(0.8, 2.0)
            
            stars.append({
                'x': random.uniform(-180, 180), 
                'y': random.uniform(-144, 144),
                'brightness': brightness,
                'size_mult': size_mult,
                'twinkle_speed': twinkle_speed,
                'color_temp': random.choice(['blue', 'white', 'yellow', 'orange'])
            })
        
        return stars
    
    def render(self, tempo_total):
        for star in self.stars:
            twinkle = math.sin(tempo_total * star['twinkle_speed']) * 0.3 + 0.7
            alpha = star['brightness'] * twinkle
            radius = (self.point_size * star['size_mult']) * 0.1
            
            if star['color_temp'] == 'blue':
                color = (0.7, 0.8, 1.0)
            elif star['color_temp'] == 'white':
                color = (1.0, 1.0, 1.0)
            elif star['color_temp'] == 'yellow':
                color = (1.0, 1.0, 0.8)
            else:
                color = (1.0, 0.8, 0.6)
            
            DrawUtils.set_color(*color, alpha)
            DrawUtils.circle(star['x'], star['y'], radius, True, 8)
    
    def set_point_size(self, size):
        self.point_size = size

class Nebula:
    def __init__(self, x=0, y=0, width=50, height=30, seed=42):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.seed = seed
        self.time = 0.0
        self.gas_clouds = []
        self._init_nebula()
    
    def _init_nebula(self):
        random.seed(self.seed)
        
        cloud_count = random.randint(2, 4)
        for _ in range(cloud_count):
            local_x = random.uniform(-self.width/2, self.width/2)
            local_y = random.uniform(-self.height/2, self.height/2)
            
            self.gas_clouds.append({
                'x': local_x,
                'y': local_y,
                'radius': random.uniform(15, 25),
                'intensity': random.uniform(0.02, 0.08),
                'pulse_speed': random.uniform(0.1, 0.5),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'drift_speed': random.uniform(0.01, 0.03),
                'drift_angle': random.uniform(0, 2 * math.pi)
            })
    
    def update(self, dt):
        self.time += dt
        
        for cloud in self.gas_clouds:
            cloud['x'] += math.cos(cloud['drift_angle']) * cloud['drift_speed'] * dt
            cloud['y'] += math.sin(cloud['drift_angle']) * cloud['drift_speed'] * dt
            cloud['pulse_phase'] += cloud['pulse_speed'] * dt
            
            if abs(cloud['x']) > self.width/3:
                cloud['drift_angle'] = math.pi - cloud['drift_angle']
            if abs(cloud['y']) > self.height/3:
                cloud['drift_angle'] = -cloud['drift_angle']
    
    def draw(self):
        gas_color = (0.08, 0.12, 0.25)
        
        for cloud in self.gas_clouds:
            world_x = self.x + cloud['x']
            world_y = self.y + cloud['y']
            
            pulse = 1.0 + 0.1 * math.sin(cloud['pulse_phase'])
            radius = cloud['radius'] * pulse
            alpha = cloud['intensity'] * (0.4 + 0.1 * math.sin(cloud['pulse_phase'] * 0.3))
            
            DrawUtils.set_color(*gas_color, alpha)
            DrawUtils.circle(world_x, world_y, radius, True, 32)

class CosmicBackground:
    def __init__(self):
        self.background_stars = BackgroundStars(count=300, seed=42)
        self.background_stars.set_point_size(4.0)
        
        self.nebulae = [
            Nebula(-80, 50, width=40, height=25, seed=200)
        ]
    
    def update(self, dt):
        for nebula in self.nebulae:
            nebula.update(dt)
    
    def draw(self, tempo_total):
        for nebula in self.nebulae:
            nebula.draw()
        
        self.background_stars.render(tempo_total)