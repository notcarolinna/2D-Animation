import math
import random
from OpenGL.GL import *
from GraphicsUtils import DrawUtils

class Comet:
    def __init__(self, x=0, y=0, vx=0, vy=0, size=1.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.age = 0.0
        self.max_age = random.uniform(8.0, 15.0)
        
        # Cauda simples
        self.tail_particles = []
        self.particle_timer = 0.0
    
    def update(self, dt):
        self.age += dt
        
        # Movimento
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Criar partículas da cauda
        self.particle_timer += dt
        if self.particle_timer > 0.1:
            self._spawn_tail_particle()
            self.particle_timer = 0.0
        
        # Atualizar cauda
        self.tail_particles = [p for p in self.tail_particles 
                              if p['age'] < p['max_age']]
        
        for particle in self.tail_particles:
            particle['age'] += dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
    
    def _spawn_tail_particle(self):
        # Direção oposta ao movimento
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > 0:
            tail_vx = -self.vx * 0.3 + random.uniform(-1, 1)
            tail_vy = -self.vy * 0.3 + random.uniform(-1, 1)
        else:
            tail_vx = random.uniform(-1, 1)
            tail_vy = random.uniform(-1, 1)
        
        particle = {
            'x': self.x + random.uniform(-0.2, 0.2),
            'y': self.y + random.uniform(-0.2, 0.2),
            'vx': tail_vx,
            'vy': tail_vy,
            'age': 0.0,
            'max_age': random.uniform(1.0, 3.0),
            'size': random.uniform(0.05, 0.15),
            'intensity': random.uniform(0.4, 0.8)
        }
        self.tail_particles.append(particle)
    
    def draw(self):
        # Desenhar cauda
        for particle in self.tail_particles:
            age_factor = 1.0 - (particle['age'] / particle['max_age'])
            alpha = particle['intensity'] * age_factor
            
            DrawUtils.set_color(0.8, 0.9, 1.0, alpha)
            DrawUtils.circle(particle['x'], particle['y'], 
                           particle['size'] * age_factor, True, 8)
        
        # Desenhar núcleo
        DrawUtils.set_color(0.4, 0.3, 0.2, 0.9)
        DrawUtils.circle(self.x, self.y, self.size * 0.3, True, 12)
        
        # Brilho central
        DrawUtils.set_color(0.9, 0.95, 1.0, 0.8)
        DrawUtils.circle(self.x, self.y, self.size * 0.2, True, 8)
    
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
        self.max_age = random.uniform(2.0, 5.0)
        
        # Rastro simples
        self.trail = []
        self.trail_timer = 0.0
    
    def update(self, dt):
        self.age += dt
        
        # Movimento
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Criar rastro
        self.trail_timer += dt
        if self.trail_timer > 0.05:
            self._spawn_trail_particle()
            self.trail_timer = 0.0
        
        # Atualizar rastro
        self.trail = [p for p in self.trail if p['age'] < p['max_age']]
        
        for particle in self.trail:
            particle['age'] += dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
    
    def _spawn_trail_particle(self):
        colors = ['orange', 'red', 'yellow']
        particle = {
            'x': self.x + random.uniform(-0.1, 0.1),
            'y': self.y + random.uniform(-0.1, 0.1),
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-0.5, 0.5),
            'age': 0.0,
            'max_age': random.uniform(0.3, 1.0),
            'size': random.uniform(0.06, 0.15),
            'color': random.choice(colors)
        }
        self.trail.append(particle)
    
    def draw(self):
        # Desenhar rastro
        for particle in self.trail:
            age_factor = 1.0 - (particle['age'] / particle['max_age'])
            alpha = 0.8 * age_factor
            
            if particle['color'] == 'orange':
                DrawUtils.set_color(1.0, 0.6, 0.2, alpha)
            elif particle['color'] == 'red':
                DrawUtils.set_color(1.0, 0.3, 0.1, alpha)
            else:  # yellow
                DrawUtils.set_color(1.0, 0.9, 0.3, alpha)
            
            DrawUtils.circle(particle['x'], particle['y'], 
                           particle['size'] * age_factor, True, 6)
        
        # Desenhar núcleo
        DrawUtils.set_color(0.3, 0.2, 0.1, 0.9)
        DrawUtils.circle(self.x, self.y, self.size, True, 10)
        
        # Brilho incandescente
        DrawUtils.set_color(1.0, 0.7, 0.3, 0.6)
        DrawUtils.circle(self.x, self.y, self.size * 0.7, True, 8)
    
    def is_alive(self):
        return self.age < self.max_age

class CometSystem:
    def __init__(self):
        self.comets = []
        self.spawn_timer = 0.0
        self.spawn_interval = random.uniform(10.0, 20.0)
    
    def update(self, dt):
        self.spawn_timer += dt
        
        # Criar novo cometa
        if self.spawn_timer > self.spawn_interval:
            self.spawn_comet()
            self.spawn_timer = 0.0
            self.spawn_interval = random.uniform(10.0, 20.0)
        
        # Atualizar cometas
        self.comets = [c for c in self.comets 
                      if c.is_alive() and self._in_bounds(c)]
        
        for comet in self.comets:
            comet.update(dt)
    
    def spawn_comet(self):
        # Spawnar nas bordas
        side = random.randint(0, 3)
        
        if side == 0:  # esquerda
            start_x, start_y = -120, random.uniform(-80, 80)
            angle = random.uniform(-math.pi/4, math.pi/4)
        elif side == 1:  # direita
            start_x, start_y = 120, random.uniform(-80, 80)
            angle = random.uniform(3*math.pi/4, 5*math.pi/4)
        elif side == 2:  # cima
            start_x, start_y = random.uniform(-100, 100), 100
            angle = random.uniform(math.pi, 2*math.pi)
        else:  # baixo
            start_x, start_y = random.uniform(-100, 100), -100
            angle = random.uniform(0, math.pi)
        
        speed = random.uniform(5.0, 12.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(0.8, 1.5)
        
        comet = Comet(start_x, start_y, vx, vy, size)
        self.comets.append(comet)
    
    def _in_bounds(self, obj):
        return (-130 <= obj.x <= 130 and -110 <= obj.y <= 110)
    
    def draw(self):
        for comet in self.comets:
            comet.draw()

class MeteorShower:
    def __init__(self):
        self.meteors = []
        self.shower_timer = 0.0
        self.shower_interval = random.uniform(15.0, 30.0)
        self.is_active = False
        self.duration = 0.0
        self.max_duration = 4.0
    
    def update(self, dt):
        self.shower_timer += dt
        
        # Iniciar chuva
        if not self.is_active and self.shower_timer > self.shower_interval:
            self.is_active = True
            self.duration = 0.0
            self.max_duration = random.uniform(3.0, 6.0)
            self.shower_timer = 0.0
            self.shower_interval = random.uniform(20.0, 40.0)
        
        # Durante a chuva
        if self.is_active:
            self.duration += dt
            if random.random() < 0.6 * dt:  # Spawnar meteoros
                self.spawn_meteor()
            
            if self.duration > self.max_duration:
                self.is_active = False
        else:
            # Meteoros esporádicos
            if random.random() < 0.05 * dt:
                self.spawn_meteor()
        
        # Atualizar meteoros
        self.meteors = [m for m in self.meteors 
                       if m.is_alive() and self._in_bounds(m)]
        
        for meteor in self.meteors:
            meteor.update(dt)
    
    def spawn_meteor(self):
        if self.is_active:
            # Durante chuva: vêm de cima
            start_x = random.uniform(-120, 120)
            start_y = 100
            angle = random.uniform(math.pi*1.2, math.pi*1.8)
        else:
            # Esporádico: qualquer lado
            side = random.randint(0, 3)
            if side == 0:
                start_x, start_y = -120, random.uniform(-80, 80)
                angle = random.uniform(-math.pi/3, math.pi/3)
            elif side == 1:
                start_x, start_y = 120, random.uniform(-80, 80)
                angle = random.uniform(2*math.pi/3, 4*math.pi/3)
            elif side == 2:
                start_x, start_y = random.uniform(-100, 100), 100
                angle = random.uniform(math.pi, 2*math.pi)
            else:
                start_x, start_y = random.uniform(-100, 100), -100
                angle = random.uniform(0, math.pi)
        
        speed = random.uniform(15.0, 30.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        size = random.uniform(0.15, 0.4)
        
        meteor = Meteor(start_x, start_y, vx, vy, size)
        self.meteors.append(meteor)
    
    def _in_bounds(self, obj):
        return (-130 <= obj.x <= 130 and -110 <= obj.y <= 110)
    
    def draw(self):
        for meteor in self.meteors:
            meteor.draw()

def create_comet(x=0, y=0, vx=0, vy=0, size=0.10):  
    return Comet(x, y, vx, vy, size)