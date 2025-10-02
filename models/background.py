import math
import random
from OpenGL.GL import *
from GraphicsUtils import DrawUtils

class BackgroundStars:
    def __init__(self, count=300, seed=42):
        self.count = count
        self.seed = seed
        self.stars = self._create_stars()
        self.point_size = 3.0  # Pontos maiores para melhor visibilidade
    
    def _create_stars(self):
        import random
        random.seed(self.seed)
        # Expandir para cobrir o novo viewport maior
        return [{'x': random.uniform(-180, 180), 'y': random.uniform(-144, 144),
                'brightness': random.uniform(0.3, 1.0), 
                'twinkle_speed': random.uniform(2.0, 8.0)}
                for _ in range(self.count)]
    
    def render(self, tempo_total):
        from OpenGL.GL import glPointSize, glBegin, glEnd, glColor4f, glVertex2f, GL_POINTS
        import math
        
        glPointSize(self.point_size)
        glBegin(GL_POINTS)
        for star in self.stars:
            alpha = star['brightness'] * (math.sin(tempo_total * star['twinkle_speed']) * 0.9 + 0.8)
            glColor4f(1.0, 1.0, 1.0, alpha)
            glVertex2f(star['x'], star['y'])
        glEnd()
    
    def set_point_size(self, size):
        self.point_size = size

class Nebula:
    def __init__(self, x=0, y=0, width=50, height=30, color_type="blue", seed=42):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color_type = color_type
        self.seed = seed
        self.time = 0.0
        self.dust_particles = []
        self.gas_clouds = []
        self._init_nebula()
    
    def _init_nebula(self):
        import random
        random.seed(self.seed)
        
        # Criar partículas de poeira cósmica
        particle_count = random.randint(150, 300)
        for _ in range(particle_count):
            local_x = random.uniform(-self.width/2, self.width/2)
            local_y = random.uniform(-self.height/2, self.height/2)
            
            self.dust_particles.append({
                'x': local_x,
                'y': local_y,
                'size': random.uniform(0.02, 0.15),
                'intensity': random.uniform(0.1, 0.7),
                'drift_speed': random.uniform(0.1, 0.5),
                'drift_angle': random.uniform(0, 2 * math.pi),
                'twinkle_speed': random.uniform(0.5, 3.0),
                'twinkle_phase': random.uniform(0, 2 * math.pi)
            })
        
        # Criar nuvens de gás (áreas maiores e difusas)
        cloud_count = random.randint(8, 15)
        for _ in range(cloud_count):
            local_x = random.uniform(-self.width/3, self.width/3)
            local_y = random.uniform(-self.height/3, self.height/3)
            
            self.gas_clouds.append({
                'x': local_x,
                'y': local_y,
                'radius': random.uniform(8, 20),
                'intensity': random.uniform(0.05, 0.25),
                'pulse_speed': random.uniform(0.3, 1.5),
                'pulse_phase': random.uniform(0, 2 * math.pi),
                'drift_speed': random.uniform(0.05, 0.2),
                'drift_angle': random.uniform(0, 2 * math.pi)
            })
    
    def update(self, dt):
        self.time += dt
        
        # Atualizar deriva das partículas de poeira
        for particle in self.dust_particles:
            particle['x'] += math.cos(particle['drift_angle']) * particle['drift_speed'] * dt
            particle['y'] += math.sin(particle['drift_angle']) * particle['drift_speed'] * dt
            particle['twinkle_phase'] += particle['twinkle_speed'] * dt
            
            # Manter partículas dentro da nebulosa
            if abs(particle['x']) > self.width/2:
                particle['drift_angle'] = math.pi - particle['drift_angle']
            if abs(particle['y']) > self.height/2:
                particle['drift_angle'] = -particle['drift_angle']
        
        # Atualizar nuvens de gás
        for cloud in self.gas_clouds:
            cloud['x'] += math.cos(cloud['drift_angle']) * cloud['drift_speed'] * dt
            cloud['y'] += math.sin(cloud['drift_angle']) * cloud['drift_speed'] * dt
            cloud['pulse_phase'] += cloud['pulse_speed'] * dt
            
            # Manter nuvens dentro da nebulosa
            if abs(cloud['x']) > self.width/3:
                cloud['drift_angle'] = math.pi - cloud['drift_angle']
            if abs(cloud['y']) > self.height/3:
                cloud['drift_angle'] = -cloud['drift_angle']
    
    def draw(self):
        # Cores baseadas no tipo de nebulosa
        if self.color_type == "blue":
            dust_color = (0.3, 0.6, 1.0)  # Azul
            gas_color = (0.2, 0.4, 0.9)
        elif self.color_type == "red":
            dust_color = (1.0, 0.3, 0.4)  # Vermelho
            gas_color = (0.9, 0.2, 0.3)
        elif self.color_type == "purple":
            dust_color = (0.8, 0.3, 1.0)  # Roxo
            gas_color = (0.7, 0.2, 0.9)
        elif self.color_type == "green":
            dust_color = (0.3, 1.0, 0.5)  # Verde
            gas_color = (0.2, 0.8, 0.4)
        else:  # "mixed"
            dust_color = (0.6, 0.8, 1.0)  # Azul claro
            gas_color = (0.5, 0.7, 0.9)
        
        # Desenhar nuvens de gás (atrás das partículas)
        for cloud in self.gas_clouds:
            world_x = self.x + cloud['x']
            world_y = self.y + cloud['y']
            
            # Pulsação da nuvem
            pulse = 1.0 + 0.3 * math.sin(cloud['pulse_phase'])
            radius = cloud['radius'] * pulse
            alpha = cloud['intensity'] * (0.8 + 0.2 * math.sin(cloud['pulse_phase'] * 0.7))
            
            # Múltiplas camadas para efeito difuso
            for layer in range(3):
                layer_alpha = alpha * (0.3 + 0.4 * (3 - layer) / 3)
                layer_radius = radius * (0.6 + 0.4 * layer / 3)
                
                DrawUtils.set_color(*gas_color, layer_alpha)
                DrawUtils.circle(world_x, world_y, layer_radius, True, 32)
        
        # Desenhar partículas de poeira cósmica
        for particle in self.dust_particles:
            world_x = self.x + particle['x']
            world_y = self.y + particle['y']
            
            # Cintilação da partícula
            twinkle = 0.7 + 0.3 * math.sin(particle['twinkle_phase'])
            alpha = particle['intensity'] * twinkle
            
            # Variação de cor baseada na cintilação
            if self.color_type == "mixed":
                # Nebulosa mista com cores variadas
                color_phase = particle['twinkle_phase'] * 0.3
                r = dust_color[0] * (0.8 + 0.2 * math.sin(color_phase))
                g = dust_color[1] * (0.8 + 0.2 * math.sin(color_phase + 2))
                b = dust_color[2] * (0.8 + 0.2 * math.sin(color_phase + 4))
            else:
                r, g, b = dust_color
            
            DrawUtils.set_color(r, g, b, alpha)
            DrawUtils.circle(world_x, world_y, particle['size'], True, 8)

class CosmicDust:
    def __init__(self, count=500, area_width=200, area_height=160):
        self.count = count
        self.area_width = area_width
        self.area_height = area_height
        self.particles = []
        self.time = 0.0
        self._init_particles()
    
    def _init_particles(self):
        import random
        for _ in range(self.count):
            self.particles.append({
                'x': random.uniform(-self.area_width/2, self.area_width/2),
                'y': random.uniform(-self.area_height/2, self.area_height/2),
                'size': random.uniform(0.01, 0.08),
                'color_type': random.choice(['blue', 'purple', 'pink', 'white']),
                'intensity': random.uniform(0.05, 0.3),
                'drift_speed': random.uniform(0.1, 0.3),
                'drift_angle': random.uniform(0, 2 * math.pi),
                'twinkle_speed': random.uniform(1.0, 4.0),
                'twinkle_phase': random.uniform(0, 2 * math.pi)
            })
    
    def update(self, dt):
        self.time += dt
        for particle in self.particles:
            # Movimento lento da poeira
            particle['x'] += math.cos(particle['drift_angle']) * particle['drift_speed'] * dt
            particle['y'] += math.sin(particle['drift_angle']) * particle['drift_speed'] * dt
            particle['twinkle_phase'] += particle['twinkle_speed'] * dt
            
            # Wrap around nas bordas
            if particle['x'] > self.area_width/2:
                particle['x'] = -self.area_width/2
            elif particle['x'] < -self.area_width/2:
                particle['x'] = self.area_width/2
            if particle['y'] > self.area_height/2:
                particle['y'] = -self.area_height/2
            elif particle['y'] < -self.area_height/2:
                particle['y'] = self.area_height/2
    
    def draw(self):
        for particle in self.particles:
            # Cores baseadas no tipo
            if particle['color_type'] == 'blue':
                base_color = (0.4, 0.7, 1.0)
            elif particle['color_type'] == 'purple':
                base_color = (0.8, 0.4, 1.0)
            elif particle['color_type'] == 'pink':
                base_color = (1.0, 0.5, 0.8)
            else:  # white
                base_color = (0.9, 0.9, 1.0)
            
            # Cintilação
            twinkle = 0.5 + 0.5 * math.sin(particle['twinkle_phase'])
            alpha = particle['intensity'] * twinkle
            
            DrawUtils.set_color(*base_color, alpha)
            DrawUtils.circle(particle['x'], particle['y'], particle['size'], True, 6)