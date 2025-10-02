import math
import random
from OpenGL.GL import *
from GraphicsUtils import DrawUtils
from .estrela import Star

class Comet:
    def __init__(self, x=0, y=0, vx=0, vy=0, size=1.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.age = 0.0
        self.max_age = random.uniform(15.0, 25.0)
        self.nucleus_size = size * 0.3
        
        # Cauda do cometa (rastro de partículas)
        self.tail_particles = []
        self.tail_length = 60
        self.particle_spawn_timer = 0.0
        self.particle_spawn_interval = 0.05
        
        # Sublimação de gelo (efeito de vapor)
        self.sublimation_particles = []
        self.sublimation_timer = 0.0
        
        # Poeira cósmica ao redor
        self.dust_particles = []
        self._init_dust_cloud()
    
    def _init_dust_cloud(self):
        """Inicializa partículas de poeira ao redor do cometa"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.size * 1.5, self.size * 3.0)
            
            self.dust_particles.append({
                'x': self.x + math.cos(angle) * distance,
                'y': self.y + math.sin(angle) * distance,
                'local_x': math.cos(angle) * distance,
                'local_y': math.sin(angle) * distance,
                'size': random.uniform(0.02, 0.08),
                'intensity': random.uniform(0.1, 0.4),
                'orbit_speed': random.uniform(0.5, 2.0),
                'orbit_radius': distance,
                'angle': angle,
                'twinkle_speed': random.uniform(2.0, 5.0),
                'twinkle_phase': random.uniform(0, 2 * math.pi)
            })
    
    def update(self, dt):
        self.age += dt
        
        # Movimento do cometa
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Criar partículas da cauda
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer >= self.particle_spawn_interval:
            self.spawn_tail_particle()
            self.particle_spawn_timer = 0.0
        
        # Atualizar partículas da cauda
        particles_to_remove = []
        for i, particle in enumerate(self.tail_particles):
            particle['age'] += dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            
            # Remover partículas antigas
            if particle['age'] > particle['max_age']:
                particles_to_remove.append(i)
        
        for i in reversed(particles_to_remove):
            self.tail_particles.pop(i)
        
        # Sublimação (vapor saindo do núcleo)
        self.sublimation_timer += dt
        if self.sublimation_timer > 0.1:
            self.spawn_sublimation_particle()
            self.sublimation_timer = 0.0
        
        # Atualizar partículas de sublimação
        sublimation_to_remove = []
        for i, particle in enumerate(self.sublimation_particles):
            particle['age'] += dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['size'] += particle['expansion'] * dt
            
            if particle['age'] > particle['max_age']:
                sublimation_to_remove.append(i)
        
        for i in reversed(sublimation_to_remove):
            self.sublimation_particles.pop(i)
        
        # Atualizar poeira cósmica ao redor do cometa
        for dust in self.dust_particles:
            dust['angle'] += dust['orbit_speed'] * dt
            dust['x'] = self.x + math.cos(dust['angle']) * dust['orbit_radius']
            dust['y'] = self.y + math.sin(dust['angle']) * dust['orbit_radius']
            dust['twinkle_phase'] += dust['twinkle_speed'] * dt
    
    def spawn_tail_particle(self):
        """Cria uma partícula na cauda do cometa"""
        # Direção oposta ao movimento
        tail_direction_x = -self.vx
        tail_direction_y = -self.vy
        
        # Normalizar direção
        length = math.sqrt(tail_direction_x**2 + tail_direction_y**2)
        if length > 0:
            tail_direction_x /= length
            tail_direction_y /= length
        
        # Adicionar dispersão
        spread_angle = random.uniform(-0.3, 0.3)
        cos_spread = math.cos(spread_angle)
        sin_spread = math.sin(spread_angle)
        
        new_dir_x = tail_direction_x * cos_spread - tail_direction_y * sin_spread
        new_dir_y = tail_direction_x * sin_spread + tail_direction_y * cos_spread
        
        # Posição inicial próxima ao núcleo
        start_offset = random.uniform(0.3, 0.8)
        start_x = self.x + new_dir_x * start_offset
        start_y = self.y + new_dir_y * start_offset
        
        particle = {
            'x': start_x,
            'y': start_y,
            'vx': new_dir_x * random.uniform(1.0, 3.0),
            'vy': new_dir_y * random.uniform(1.0, 3.0),
            'size': random.uniform(0.05, 0.15),
            'age': 0.0,
            'max_age': random.uniform(2.0, 5.0),
            'intensity': random.uniform(0.3, 0.8)
        }
        
        self.tail_particles.append(particle)
    
    def spawn_sublimation_particle(self):
        """Cria partículas de vapor sublimando do núcleo"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.0)
        
        particle = {
            'x': self.x,
            'y': self.y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': random.uniform(0.03, 0.08),
            'age': 0.0,
            'max_age': random.uniform(1.0, 3.0),
            'expansion': random.uniform(0.05, 0.15),
            'intensity': random.uniform(0.2, 0.5)
        }
        
        self.sublimation_particles.append(particle)
    
    def draw(self):
        # Desenhar poeira cósmica ao redor (mais sutil)
        for dust in self.dust_particles:
            twinkle = 0.5 + 0.5 * math.sin(dust['twinkle_phase'])
            alpha = dust['intensity'] * twinkle * 0.6
            
            DrawUtils.set_color(0.7, 0.8, 1.0, alpha)
            DrawUtils.circle(dust['x'], dust['y'], dust['size'], True, 6)
        
        # Desenhar cauda (partículas mais antigas primeiro)
        for particle in self.tail_particles:
            age_factor = 1.0 - (particle['age'] / particle['max_age'])
            alpha = particle['intensity'] * age_factor
            
            # Cor azul-branca para gelo sublimando
            DrawUtils.set_color(0.8, 0.9, 1.0, alpha)
            DrawUtils.circle(particle['x'], particle['y'], particle['size'] * age_factor, True, 8)
        
        # Desenhar partículas de sublimação
        for particle in self.sublimation_particles:
            age_factor = 1.0 - (particle['age'] / particle['max_age'])
            alpha = particle['intensity'] * age_factor
            
            DrawUtils.set_color(0.9, 0.95, 1.0, alpha)
            DrawUtils.circle(particle['x'], particle['y'], particle['size'], True, 6)
        
        # Desenhar núcleo rochoso
        DrawUtils.set_color(0.4, 0.3, 0.2, 0.9)  # Marrom escuro
        DrawUtils.circle(self.x, self.y, self.nucleus_size, True, 16)
        
        # Brilho central
        DrawUtils.set_color(0.9, 0.95, 1.0, 0.8)
        DrawUtils.circle(self.x, self.y, self.nucleus_size * 0.6, True, 12)
    
    def is_alive(self):
        return self.age < self.max_age

class Meteor:
    def __init__(self, x=0, y=0, vx=0, vy=0, size=0.3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.age = 0.0
        self.max_age = random.uniform(3.0, 8.0)
        
        # Rastro de fogo
        self.trail_particles = []
        self.trail_spawn_timer = 0.0
        
        # Faíscas
        self.sparks = []
        self.spark_timer = 0.0
        
        # Fragmentação
        self.fragments = []
        self.has_fragmented = False
        self.fragmentation_chance = 0.3  # 30% chance de fragmentar
        
        # Poeira sutil ao redor
        self.dust_trail = []
        self.dust_timer = 0.0
    
    def update(self, dt):
        self.age += dt
        
        # Movimento
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Criar rastro de fogo
        self.trail_spawn_timer += dt
        if self.trail_spawn_timer > 0.02:
            self.spawn_trail_particle()
            self.trail_spawn_timer = 0.0
        
        # Criar faíscas ocasionalmente
        self.spark_timer += dt
        if self.spark_timer > 0.1 and random.random() < 0.7:
            self.spawn_spark()
            self.spark_timer = 0.0
        
        # Criar poeira sutil
        self.dust_timer += dt
        if self.dust_timer > 0.05:
            self.spawn_dust_particle()
            self.dust_timer = 0.0
        
        # Fragmentação aleatória
        if not self.has_fragmented and self.age > 1.0 and random.random() < self.fragmentation_chance * dt:
            self.fragment()
        
        # Atualizar rastro
        trail_to_remove = []
        for i, particle in enumerate(self.trail_particles):
            particle['age'] += dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            if particle['age'] > particle['max_age']:
                trail_to_remove.append(i)
        
        for i in reversed(trail_to_remove):
            self.trail_particles.pop(i)
        
        # Atualizar faíscas
        sparks_to_remove = []
        for i, spark in enumerate(self.sparks):
            spark['age'] += dt
            spark['x'] += spark['vx'] * dt
            spark['y'] += spark['vy'] * dt
            if spark['age'] > spark['max_age']:
                sparks_to_remove.append(i)
        
        for i in reversed(sparks_to_remove):
            self.sparks.pop(i)
        
        # Atualizar poeira
        dust_to_remove = []
        for i, dust in enumerate(self.dust_trail):
            dust['age'] += dt
            dust['x'] += dust['vx'] * dt
            dust['y'] += dust['vy'] * dt
            if dust['age'] > dust['max_age']:
                dust_to_remove.append(i)
        
        for i in reversed(dust_to_remove):
            self.dust_trail.pop(i)
        
        # Atualizar fragmentos
        for fragment in self.fragments:
            fragment.update(dt)
    
    def spawn_trail_particle(self):
        """Cria partícula no rastro de fogo"""
        # Posição ligeiramente atrás do meteoro
        trail_x = self.x - self.vx * 0.1 + random.uniform(-0.2, 0.2)
        trail_y = self.y - self.vy * 0.1 + random.uniform(-0.2, 0.2)
        
        particle = {
            'x': trail_x,
            'y': trail_y,
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(-1, 1),
            'size': random.uniform(0.08, 0.2),
            'age': 0.0,
            'max_age': random.uniform(0.5, 1.5),
            'intensity': random.uniform(0.5, 1.0),
            'color_type': random.choice(['orange', 'red', 'yellow'])
        }
        
        self.trail_particles.append(particle)
    
    def spawn_spark(self):
        """Cria faísca"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        
        spark = {
            'x': self.x,
            'y': self.y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': random.uniform(0.03, 0.08),
            'age': 0.0,
            'max_age': random.uniform(0.3, 0.8),
            'intensity': random.uniform(0.7, 1.0)
        }
        
        self.sparks.append(spark)
    
    def spawn_dust_particle(self):
        """Cria partícula de poeira sutil"""
        dust_x = self.x + random.uniform(-0.5, 0.5)
        dust_y = self.y + random.uniform(-0.5, 0.5)
        
        dust = {
            'x': dust_x,
            'y': dust_y,
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-0.5, 0.5),
            'size': random.uniform(0.01, 0.04),
            'age': 0.0,
            'max_age': random.uniform(2.0, 4.0),
            'intensity': random.uniform(0.1, 0.3)
        }
        
        self.dust_trail.append(dust)
    
    def fragment(self):
        """Fragmenta o meteoro em pedaços menores"""
        self.has_fragmented = True
        fragment_count = random.randint(2, 4)
        
        for _ in range(fragment_count):
            # Velocidade dos fragmentos
            angle = random.uniform(0, 2 * math.pi)
            speed_variation = random.uniform(0.5, 1.5)
            
            frag_vx = self.vx + math.cos(angle) * speed_variation
            frag_vy = self.vy + math.sin(angle) * speed_variation
            
            fragment = Meteor(
                self.x + random.uniform(-0.2, 0.2),
                self.y + random.uniform(-0.2, 0.2),
                frag_vx, frag_vy,
                self.size * random.uniform(0.3, 0.7)
            )
            fragment.max_age = random.uniform(1.0, 3.0)  # Fragmentos duram menos
            self.fragments.append(fragment)
    
    def draw(self):
        # Desenhar poeira sutil
        for dust in self.dust_trail:
            age_factor = 1.0 - (dust['age'] / dust['max_age'])
            alpha = dust['intensity'] * age_factor
            
            DrawUtils.set_color(0.6, 0.5, 0.4, alpha)
            DrawUtils.circle(dust['x'], dust['y'], dust['size'], True, 6)
        
        # Desenhar rastro de fogo
        for particle in self.trail_particles:
            age_factor = 1.0 - (particle['age'] / particle['max_age'])
            alpha = particle['intensity'] * age_factor
            
            if particle['color_type'] == 'orange':
                DrawUtils.set_color(1.0, 0.6, 0.2, alpha)
            elif particle['color_type'] == 'red':
                DrawUtils.set_color(1.0, 0.3, 0.1, alpha)
            else:  # yellow
                DrawUtils.set_color(1.0, 0.9, 0.3, alpha)
            
            DrawUtils.circle(particle['x'], particle['y'], particle['size'] * age_factor, True, 8)
        
        # Desenhar faíscas
        for spark in self.sparks:
            age_factor = 1.0 - (spark['age'] / spark['max_age'])
            alpha = spark['intensity'] * age_factor
            
            DrawUtils.set_color(1.0, 1.0, 0.8, alpha)
            DrawUtils.circle(spark['x'], spark['y'], spark['size'], True, 6)
        
        # Desenhar núcleo do meteoro
        DrawUtils.set_color(0.3, 0.2, 0.1, 0.9)  # Marrom escuro rochoso
        DrawUtils.circle(self.x, self.y, self.size, True, 12)
        
        # Brilho incandescente
        DrawUtils.set_color(1.0, 0.7, 0.3, 0.6)
        DrawUtils.circle(self.x, self.y, self.size * 0.7, True, 10)
        
        # Desenhar fragmentos
        for fragment in self.fragments:
            fragment.draw()
    
    def is_alive(self):
        return self.age < self.max_age

class CometSystem:
    def __init__(self):
        self.comets = []
        self.spawn_timer = 0.0
        self.spawn_interval = random.uniform(8.0, 15.0)
    
    def update(self, dt):
        self.spawn_timer += dt
        
        # Criar novo cometa periodicamente
        if self.spawn_timer > self.spawn_interval:
            self.spawn_comet()
            self.spawn_timer = 0.0
            self.spawn_interval = random.uniform(8.0, 15.0)
        
        # Atualizar cometas existentes
        comets_to_remove = []
        for i, comet in enumerate(self.comets):
            comet.update(dt)
            if not comet.is_alive() or self.is_out_of_bounds(comet):
                comets_to_remove.append(i)
        
        for i in reversed(comets_to_remove):
            self.comets.pop(i)
    
    def spawn_comet(self):
        """Cria um novo cometa vindo do espaço distante"""
        # Spawnar na borda do sistema
        side = random.randint(0, 3)
        
        if side == 0:  # esquerda
            start_x, start_y = -130, random.uniform(-100, 100)
            target_x, target_y = random.uniform(-20, 20), random.uniform(-20, 20)
        elif side == 1:  # direita
            start_x, start_y = 130, random.uniform(-100, 100)
            target_x, target_y = random.uniform(-20, 20), random.uniform(-20, 20)
        elif side == 2:  # cima
            start_x, start_y = random.uniform(-120, 120), 110
            target_x, target_y = random.uniform(-20, 20), random.uniform(-20, 20)
        else:  # baixo
            start_x, start_y = random.uniform(-120, 120), -110
            target_x, target_y = random.uniform(-20, 20), random.uniform(-20, 20)
        
        # Calcular velocidade em direção ao centro do sistema
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        speed = random.uniform(8.0, 15.0)
        vx = (dx / distance) * speed
        vy = (dy / distance) * speed
        
        size = random.uniform(0.8, 2.0)
        comet = Comet(start_x, start_y, vx, vy, size)
        self.comets.append(comet)
    
    def is_out_of_bounds(self, comet):
        return (comet.x < -150 or comet.x > 150 or 
                comet.y < -120 or comet.y > 120)
    
    def draw(self):
        for comet in self.comets:
            comet.draw()

class MeteorShower:
    def __init__(self):
        self.meteors = []
        self.shower_timer = 0.0
        self.shower_interval = random.uniform(5.0, 12.0)
        self.is_shower_active = False
        self.shower_duration = 0.0
        self.max_shower_duration = 3.0
    
    def update(self, dt):
        self.shower_timer += dt
        
        # Iniciar chuva de meteoros
        if not self.is_shower_active and self.shower_timer > self.shower_interval:
            self.start_shower()
        
        # Durante a chuva, spawnar meteoros rapidamente
        if self.is_shower_active:
            self.shower_duration += dt
            if random.random() < 0.8 * dt:  # Alta frequência durante a chuva
                self.spawn_meteor()
            
            if self.shower_duration > self.max_shower_duration:
                self.end_shower()
        else:
            # Meteoros esporádicos
            if random.random() < 0.1 * dt:
                self.spawn_meteor()
        
        # Atualizar meteoros
        meteors_to_remove = []
        for i, meteor in enumerate(self.meteors):
            meteor.update(dt)
            if not meteor.is_alive() or self.is_out_of_bounds(meteor):
                meteors_to_remove.append(i)
        
        for i in reversed(meteors_to_remove):
            self.meteors.pop(i)
    
    def start_shower(self):
        self.is_shower_active = True
        self.shower_duration = 0.0
        self.max_shower_duration = random.uniform(2.0, 5.0)
    
    def end_shower(self):
        self.is_shower_active = False
        self.shower_timer = 0.0
        self.shower_interval = random.uniform(10.0, 20.0)
    
    def spawn_meteor(self):
        """Cria um novo meteoro"""
        # Meteoros geralmente vêm de uma direção similar durante chuvas
        if self.is_shower_active:
            # Durante chuva: direção mais uniforme
            start_x = random.uniform(-130, 130)
            start_y = 110
            angle = random.uniform(math.pi*1.2, math.pi*1.8)  # Direção para baixo
        else:
            # Meteoros esporádicos: qualquer direção
            side = random.randint(0, 3)
            if side == 0:  # esquerda
                start_x, start_y = -130, random.uniform(-100, 100)
                angle = random.uniform(-math.pi/3, math.pi/3)
            elif side == 1:  # direita
                start_x, start_y = 130, random.uniform(-100, 100)
                angle = random.uniform(2*math.pi/3, 4*math.pi/3)
            elif side == 2:  # cima
                start_x, start_y = random.uniform(-120, 120), 110
                angle = random.uniform(math.pi, 2*math.pi)
            else:  # baixo
                start_x, start_y = random.uniform(-120, 120), -110
                angle = random.uniform(0, math.pi)
        
        speed = random.uniform(20.0, 40.0)  # Meteoros são muito rápidos
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        size = random.uniform(0.2, 0.6)
        meteor = Meteor(start_x, start_y, vx, vy, size)
        self.meteors.append(meteor)
    
    def is_out_of_bounds(self, meteor):
        return (meteor.x < -150 or meteor.x > 150 or 
                meteor.y < -120 or meteor.y > 120)
    
    def draw(self):
        for meteor in self.meteors:
            meteor.draw()

def create_comet(x=0, y=0, vx=0, vy=0, size=0.10):  
    return Comet(x, y, vx, vy, size)