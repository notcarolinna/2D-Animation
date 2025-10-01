import math
from OpenGL.GL import *
from GraphicsUtils import DrawUtils

class PulseEffect:
    def __init__(self, frequency=2.0, amplitude=0.2, offset=0.8):
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
    
    def get_value(self, time):
        return math.sin(time * self.frequency) * self.amplitude + self.offset

class GlowEffect:
    def __init__(self, color, intensity=0.5, layers=4, max_size=2.0, pulse=None):
        self.color = color
        self.intensity = intensity
        self.layers = layers
        self.max_size = max_size
        self.pulse = pulse or PulseEffect()
    
    def draw(self, cx, cy, base_radius, time):
        pulse_value = self.pulse.get_value(time)
        current_intensity = self.intensity * pulse_value
        
        for i in range(self.layers, 0, -1):
            size_mult = (i / self.layers) * self.max_size + 1.0
            alpha = (current_intensity / i) * 0.35
            
            r, g, b = self.color[0], self.color[1], self.color[2]
            if i == self.layers:
                DrawUtils.set_color(r * 0.8, g * 0.8, b * 0.8, alpha * 0.5)
            elif i == self.layers - 1:
                DrawUtils.set_color(r, g, b, alpha * 0.7)
            else:
                DrawUtils.set_color(min(1.0, r * 1.2), min(1.0, g * 1.2), min(1.0, b * 1.2), alpha)
            
            size_pulse = 1.0 + (pulse_value - 0.8) * 0.3
            DrawUtils.circle(cx, cy, base_radius * size_mult * size_pulse, True, 64)

class Star:
    def __init__(self, x=0, y=0, vx=0, vy=0, size=0.15):  
        self.x, self.y, self.vx, self.vy, self.size = x, y, vx, vy, size
        self.tail_positions = [(x, y)]
        self.life_time = 0.0
        self.core_size = size * 0.9
        self.tail_length = 35
        self.pulse = PulseEffect(6.0, 0.2, 0.8)
        
    def update(self, dt):
        self.life_time += dt
        # Atualizar posição com velocidade
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Atualizar rastro
        self.set_position(self.x, self.y)
        
    def set_position(self, x, y):
        self.x, self.y = x, y
        if not self.tail_positions or (abs(self.tail_positions[-1][0] - x) > 0.005 or 
                                     abs(self.tail_positions[-1][1] - y) > 0.005):
            self.tail_positions.append((x, y))
            if len(self.tail_positions) > self.tail_length:
                self.tail_positions.pop(0)
        
    def draw(self):
        brightness = self.pulse.get_value(self.life_time) * 0.9 + 0.1
        self._draw_tail(brightness)
        self._draw_glow(brightness)
        self._draw_core(brightness)
    
    def _draw_tail(self, brightness):
        if len(self.tail_positions) < 2: return
        for i in range(len(self.tail_positions) - 1):
            t = i / max(1, len(self.tail_positions) - 1)
            alpha = (t ** 1.5) * 0.7 * brightness
            width = max(0.3, self.size * 20 * (t ** 0.7))
            
            # Rastro branco puro
            r, g, b = 1.0, 1.0, 1.0
            
            DrawUtils.set_color(r, g, b, alpha)
            DrawUtils.line(*self.tail_positions[i], *self.tail_positions[i + 1], width)
    
    def _draw_glow(self, brightness):
        colors = [(0.6, 0.8, 1.0), (0.8, 0.9, 1.0), (1.0, 0.95, 0.9), (1.0, 0.9, 0.7)]
        for layer in range(4, 0, -1):
            alpha = (0.15 / layer) * brightness
            DrawUtils.set_color(*colors[layer-1], alpha)
            DrawUtils.circle(self.x, self.y, self.size * layer * 1.8, True, 64)
    
    def _draw_core(self, brightness):
        # Núcleo branco brilhante
        core_layers = [(1.0, 1.0, 1.0, brightness), 
                      (1.0, 1.0, 1.0, brightness * 1.2), 
                      (1.0, 1.0, 1.0, brightness * 1.5)]
        sizes = [self.core_size, self.core_size * 0.6, self.core_size * 0.3]
        segs = [32, 16, 12]
        
        for (r, g, b, a), size, seg in zip(core_layers, sizes, segs):
            DrawUtils.set_color(r, g, b, a)
            DrawUtils.circle(self.x, self.y, size, True, seg)

class BackgroundStars:
    def __init__(self, count=300, seed=42):
        self.count = count
        self.seed = seed
        self.stars = self._create_stars()
        self.point_size = 3.0  # Pontos maiores para melhor visibilidade
    
    def _create_stars(self):
        import random
        random.seed(self.seed)
        # Expandir para cobrir uma área muito maior que o viewport
        return [{'x': random.uniform(-150, 150), 'y': random.uniform(-120, 120),
                'brightness': random.uniform(0.3, 1.0), 
                'twinkle_speed': random.uniform(0.5, 2.0)}
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

class Planet:
    def __init__(self, name, x=0, y=0, radius=1.0, color=(1,1,1)):
        self.name, self.x, self.y, self.radius, self.color = name, x, y, radius, color
        self.life_time = 0.0
        self.solar_flares = []
        
        config = PLANET_CONFIGS.get(name.lower(), PLANET_CONFIGS["earth"])
        planet_color = COLORS.get(name.lower(), color[:3])
        pulse = PulseEffect(config["frequency"], 0.2, 0.8)
        self.glow = GlowEffect(planet_color, config["intensity"], config["layers"], config["max_size"], pulse)
        
        if name.lower() == "sun":
            self._init_solar_effects()

    def _init_solar_effects(self):
        import random
        for _ in range(16):
            self.solar_flares.append({
                'angle': random.uniform(0, 2 * math.pi),
                'length': random.uniform(0.2, 1.0),
                'width': random.uniform(0.015, 0.08),
                'speed': random.uniform(1.5, 5.0),
                'life': random.uniform(0, 2 * math.pi),
                'intensity': random.uniform(0.4, 1.0)
            })

    def update(self, dt):
        self.life_time += dt
        if self.name.lower() == "sun":
            self._update_solar_effects(dt)

    def _update_solar_effects(self, dt):
        for flare in self.solar_flares:
            flare['life'] += flare['speed'] * dt
            base_length = 0.3 + 0.5 * math.sin(flare['life'])
            flare['length'] = base_length * flare['intensity']
            flare['angle'] += math.sin(flare['life'] * 0.5) * 0.02 * dt

    def draw(self):
        DrawUtils.with_pose(self.x, self.y, scale=(self.radius, self.radius))
        self.glow.draw(0, 0, 1.0, self.life_time)
        
        if self.name.lower() == "sun":
            self._draw_solar_effects()
        
        drawer = PLANET_DRAWERS.get(self.name.lower())
        if drawer:
            if self.name.lower() == "sun":
                drawer(0, 0, 1.0, self.life_time)
            else:
                drawer(0, 0, 1.0)
        else:
            DrawUtils.set_color(*self.color)
            DrawUtils.circle(0, 0, 1.0, True)
        DrawUtils.end_pose()

    def _draw_solar_effects(self):
        for flare in self.solar_flares:
            self._draw_solar_flare(flare)
    
    def _draw_solar_flare(self, flare):
        angle, length, width, intensity = flare['angle'], flare['length'], flare['width'], flare['intensity']
        base_x, base_y = math.cos(angle), math.sin(angle)
        tip_x, tip_y = base_x * (1.0 + length), base_y * (1.0 + length)
        
        colors = [(1.0, 1.0, 0.9), (1.0, 0.8, 0.4), (1.0, 0.5, 0.2)]
        for i, color in enumerate(colors):
            alpha = (3 - i) * 0.25 * intensity
            w = width * (3 - i) * 0.8
            DrawUtils.set_color(*color, alpha)
            DrawUtils.line(base_x, base_y, tip_x, tip_y, w * 25)

COLORS = {
    "sun": (1.00, 0.65, 0.15), "mercury": (0.70, 0.50, 0.30), "venus": (1.00, 0.95, 0.20),
    "earth": (0.25, 0.66, 0.96), "earthLand": (0.42, 0.82, 0.42), "mars": (0.90, 0.20, 0.10),
    "jupiter": (0.74, 0.53, 0.33), "saturn": (0.90, 0.82, 0.70), 
    "uranus": (0.43, 0.86, 0.79), "neptune": (0.29, 0.39, 0.85)
}

PLANET_CONFIGS = {
    "sun": {"intensity": 1.0, "layers": 6, "max_size": 2.5, "frequency": 3.0},
    "mercury": {"intensity": 0.3, "layers": 3, "max_size": 1.8, "frequency": 4.5},
    "venus": {"intensity": 0.6, "layers": 4, "max_size": 2.0, "frequency": 2.8},
    "earth": {"intensity": 0.5, "layers": 4, "max_size": 1.9, "frequency": 2.2},
    "mars": {"intensity": 0.4, "layers": 3, "max_size": 1.7, "frequency": 3.5},
    "jupiter": {"intensity": 0.7, "layers": 5, "max_size": 2.2, "frequency": 1.8},
    "saturn": {"intensity": 0.6, "layers": 4, "max_size": 2.1, "frequency": 2.0},
    "uranus": {"intensity": 0.5, "layers": 4, "max_size": 1.9, "frequency": 2.5},
    "neptune": {"intensity": 0.6, "layers": 4, "max_size": 2.0, "frequency": 2.3}
}


def edge_ring(cx, cy, r, k=0.985, rgba=(1,1,1,0.20)):
    DrawUtils.set_color(*rgba)
    DrawUtils.ring(cx, cy, r*k, r, seg=140)

def draw_sun(cx, cy, r, time=0.0):
    pulse = math.sin(time * 3.0) * 0.1 + 1.0
    glow_pulse = math.sin(time * 5.0) * 0.15 + 0.85
    
    for layer in range(5, 0, -1):
        size_mult = layer * 0.3 + 1.2
        alpha = (0.08 / layer) * glow_pulse
        if layer >= 4: color = (1.0, 0.9, 0.6)
        elif layer >= 3: color = (1.0, 0.7, 0.3)
        else: color = (1.0, 0.5, 0.2)
        DrawUtils.set_color(*color, alpha)
        DrawUtils.circle(cx, cy, r * size_mult * pulse, True, 96)
    
    DrawUtils.set_color(*COLORS["sun"])
    DrawUtils.circle(cx, cy, r * pulse, True, 128)
    
    DrawUtils.begin_clip_circle(cx, cy, r * pulse)
    spot_time, flare_time = time * 2.0, time * 4.0
    
    DrawUtils.set_color(1.00, 0.50, 0.15, 0.6)
    DrawUtils.ellipse(cx + 0.10*r*math.sin(spot_time), cy + 0.25*r, 0.70*r, 0.18*r, True)
    DrawUtils.set_color(1.00, 0.45, 0.05, 0.4)
    DrawUtils.ellipse(cx + 0.15*r + 0.05*r*math.cos(spot_time*1.5), cy - 0.30*r, 0.55*r, 0.15*r, True)
    
    DrawUtils.set_color(1.00, 0.80, 0.30, 0.7 * (math.sin(flare_time) * 0.3 + 0.7))
    DrawUtils.ellipse(cx - 0.20*r, cy + 0.15*r*math.sin(flare_time), 0.40*r, 0.12*r, True)
    DrawUtils.set_color(1.00, 0.75, 0.25, 0.5 * (math.cos(flare_time*0.7) * 0.3 + 0.7))
    DrawUtils.ellipse(cx + 0.25*r, cy - 0.20*r*math.cos(flare_time*1.2), 0.35*r, 0.10*r, True)
    DrawUtils.end_clip()
    
    center_pulse = math.sin(time * 7.0) * 0.2 + 0.8
    DrawUtils.set_color(1.00, 0.95, 0.60, 0.6 * center_pulse)
    DrawUtils.circle(cx, cy, 0.75*r*pulse, True, 96)
    DrawUtils.set_color(1.00, 1.00, 0.85, 0.4 * center_pulse)
    DrawUtils.circle(cx, cy, 0.5*r*pulse, True, 64)
    DrawUtils.radial_shade(cx, cy, r*pulse, 0.0, 0.35 * glow_pulse)

def draw_mercury(cx, cy, r):
    DrawUtils.set_color(*COLORS["mercury"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(0.46, 0.33, 0.23, 1.0)
    DrawUtils.circle(cx-0.26*r, cy+0.16*r, 0.26*r, True)
    DrawUtils.set_color(0.38, 0.27, 0.20, 1.0)
    DrawUtils.circle(cx+0.22*r, cy-0.14*r, 0.18*r, True)
    DrawUtils.set_color(0.54, 0.40, 0.29, 1.0)
    DrawUtils.circle(cx-0.06*r, cy-0.28*r, 0.12*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_venus(cx, cy, r):
    DrawUtils.set_color(*COLORS["venus"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(1.00, 0.84, 0.45, 1.0)
    DrawUtils.ellipse(cx, cy+0.26*r, 0.95*r, 0.12*r, True)
    DrawUtils.set_color(1.00, 0.90, 0.68, 1.0)
    DrawUtils.ellipse(cx, cy-0.02*r, 0.99*r, 0.11*r, True)
    DrawUtils.set_color(0.98, 0.78, 0.42, 1.0)
    DrawUtils.ellipse(cx, cy-0.30*r, 0.93*r, 0.12*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_earth(cx, cy, r):
    DrawUtils.set_color(*COLORS["earth"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(*COLORS["earthLand"])
    DrawUtils.circle(cx-0.30*r, cy+0.10*r, 0.42*r, True)
    DrawUtils.circle(cx+0.32*r, cy-0.02*r, 0.30*r, True)
    DrawUtils.circle(cx+0.12*r, cy-0.36*r, 0.18*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r, rgba=(1,1,1,0.35))

def draw_mars(cx, cy, r):
    DrawUtils.set_color(*COLORS["mars"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(0.70, 0.18, 0.12, 1.0)
    DrawUtils.ellipse(cx-0.12*r, cy+0.16*r, 0.34*r, 0.14*r, True)
    DrawUtils.set_color(0.62, 0.16, 0.10, 1.0)
    DrawUtils.ellipse(cx+0.22*r, cy-0.12*r, 0.26*r, 0.12*r, True)
    DrawUtils.set_color(0.55, 0.10, 0.10, 1.0)
    DrawUtils.circle(cx+0.10*r, cy-0.08*r, 0.16*r, True)
    DrawUtils.set_color(0.58, 0.14, 0.12, 1.0)
    DrawUtils.circle(cx-0.26*r, cy+0.02*r, 0.12*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_jupiter(cx, cy, r):
    DrawUtils.set_color(*COLORS["jupiter"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(0.80, 0.70, 0.60, 0.8)
    DrawUtils.ellipse(cx, cy+0.40*r, 0.90*r, 0.10*r, True)
    DrawUtils.ellipse(cx, cy+0.10*r, 0.95*r, 0.12*r, True)
    DrawUtils.ellipse(cx, cy-0.20*r, 0.90*r, 0.10*r, True)
    DrawUtils.ellipse(cx, cy-0.50*r, 0.85*r, 0.08*r, True)
    DrawUtils.set_color(0.80, 0.30, 0.20, 0.9)
    DrawUtils.ellipse(cx+0.40*r, cy-0.10*r, 0.25*r, 0.15*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.18)

def draw_saturn(cx, cy, r):
    DrawUtils.with_pose(cx, cy, rot_deg=-20, scale=(1.0, 0.40))
    DrawUtils.set_color(0.90, 0.86, 0.78, 0.8)
    DrawUtils.ring(0, 0, 1.20*r, 1.80*r)
    DrawUtils.set_color(0.82, 0.78, 0.72, 0.8)
    DrawUtils.ring(0, 0, 1.35*r, 1.55*r)
    DrawUtils.end_pose()
    DrawUtils.set_color(*COLORS["saturn"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.set_color(0.80, 0.70, 0.50, 0.6)
    DrawUtils.ellipse(cx, cy+0.10*r, 0.90*r, 0.08*r, True)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.20)

def draw_uranus(cx, cy, r):
    DrawUtils.set_color(*COLORS["uranus"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.with_pose(cx, cy, rot_deg=85, scale=(1.0, 0.20))
    DrawUtils.set_color(0.80, 0.90, 1.00, 0.6)
    DrawUtils.ring(0, 0, 1.10*r, 1.30*r)
    DrawUtils.end_pose()
    DrawUtils.set_color(0.40, 0.60, 0.80, 0.4)
    DrawUtils.ellipse(cx, cy, 0.90*r, 0.10*r, True)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.18)

def draw_neptune(cx, cy, r):
    DrawUtils.set_color(*COLORS["neptune"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.set_color(0.20, 0.40, 0.80, 0.7)
    DrawUtils.line(cx-0.8*r, cy+0.1*r, cx+0.8*r, cy-0.1*r, 5.0)
    DrawUtils.set_color(0.10, 0.20, 0.50, 0.8)
    DrawUtils.ellipse(cx+0.30*r, cy-0.25*r, 0.15*r, 0.12*r, True)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.20)

PLANET_DRAWERS = {
    "sun": draw_sun, "mercury": draw_mercury, "venus": draw_venus, "earth": draw_earth,
    "mars": draw_mars, "jupiter": draw_jupiter, "saturn": draw_saturn,
    "uranus": draw_uranus, "neptune": draw_neptune
}

def create_planets():
    cfg = [
        ("Sun", 0.0, 0.0, 1.2), ("Mercury", 2.0, 0.0, 0.3), ("Venus", 3.0, 0.0, 0.4),
        ("Earth", 4.5, 0.0, 0.5), ("Mars", 6.0, 0.0, 0.4), ("Jupiter", 9.0, 0.0, 1.0),
        ("Saturn", 12.0, 0.0, 0.8), ("Uranus", 15.0, 0.0, 0.6), ("Neptune", 18.0, 0.0, 0.6)
    ]
    return [Planet(name, x, y, size, COLORS.get(name.lower(), (1,1,1))) for name, x, y, size in cfg]

def create_entities_for_animation(total_entities):
    entities = []
    
    solar_system_config = [
        ("Sun", 0.0, 0.0, 1.2), ("Mercury", 2.0, 0.0, 0.3), ("Venus", 3.0, 0.0, 0.4),
        ("Earth", 4.5, 0.0, 0.5), ("Mars", 6.0, 0.0, 0.4), ("Jupiter", 9.0, 0.0, 1.0),
        ("Saturn", 12.0, 0.0, 0.8), ("Uranus", 15.0, 0.0, 0.6), ("Neptune", 18.0, 0.0, 0.6)
    ]
    
    for i in range(1, total_entities):
        if i - 1 < len(solar_system_config):  # i-1 porque pulamos o player
            name, x, y, size = solar_system_config[i - 1]
            planet = Planet(name, x, y, size, COLORS.get(name.lower(), (1,1,1)))
            entities.append(planet)
        else:
            size = 0.12  
            star = Star(0, 0, 0, 0, size)
            entities.append(star)
    
    return entities

def create_star(x=0, y=0, vx=0, vy=0, size=0.15): 
    return Star(x, y, vx, vy, size)

def create_comet(x=0, y=0, vx=0, vy=0, size=0.10):  
    return create_star(x, y, vx, vy, size)

class FireSun:
    def __init__(self, x=0, y=0, size=3.5):
        self.x = x
        self.y = y
        self.size = size
        self.time = 0.0
        self.flame_particles = []
        self.magma_bubbles = []
        self.corona_streams = []
        self.surface_waves = []
        self._init_flame_particles()
        self._init_magma_bubbles()
        self._init_corona_streams()
        self._init_surface_waves()
        
    def _init_flame_particles(self):
        import random
        # Partículas de fogo externas - mais numerosas
        for _ in range(80):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(1.0, 1.8) * self.size
            self.flame_particles.append({
                'angle': angle,
                'base_distance': distance,
                'distance': distance,
                'speed': random.uniform(0.8, 3.0),
                'intensity': random.uniform(0.4, 1.0),
                'size': random.uniform(0.08, 0.4),
                'flicker_speed': random.uniform(2.0, 8.0),
                'wave_offset': random.uniform(0, 2 * math.pi)
            })
    
    def _init_magma_bubbles(self):
        import random
        # Bolhas de magma na superfície
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.3, 0.9) * self.size
            size = random.uniform(0.05, 0.2)
            self.magma_bubbles.append({
                'angle': angle,
                'distance': distance,
                'size': size,
                'current_size': size,  # Inicializar current_size
                'intensity': random.uniform(0.6, 1.0),
                'bubble_speed': random.uniform(0.2, 1.0),
                'growth_phase': random.uniform(0, 2 * math.pi)
            })
    
    def _init_corona_streams(self):
        import random
        # Fluxos de corona solar
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            self.corona_streams.append({
                'angle': angle,
                'length': random.uniform(2.0, 4.0) * self.size,
                'width': random.uniform(0.1, 0.3),
                'intensity': random.uniform(0.3, 0.8),
                'flow_speed': random.uniform(0.5, 2.0),
                'segments': random.randint(8, 15)
            })
    
    def _init_surface_waves(self):
        import random
        # Ondas na superfície solar
        for _ in range(40):
            self.surface_waves.append({
                'angle': random.uniform(0, 2 * math.pi),
                'amplitude': random.uniform(0.1, 0.3),
                'frequency': random.uniform(1.0, 4.0),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.5, 2.0)
            })
    
    def update(self, dt):
        self.time += dt
        
        # Atualizar partículas de fogo
        for particle in self.flame_particles:
            particle['angle'] += particle['speed'] * dt
            wave = math.sin(self.time * particle['flicker_speed'] + particle['wave_offset'])
            particle['distance'] = particle['base_distance'] * (1.0 + 0.3 * wave)
            particle['intensity'] = max(0.2, particle['intensity'] + 0.1 * wave)
            
        # Atualizar bolhas de magma
        for bubble in self.magma_bubbles:
            bubble['angle'] += bubble['bubble_speed'] * dt * 0.3
            bubble['growth_phase'] += dt * 3.0
            size_mult = 1.0 + 0.4 * math.sin(bubble['growth_phase'])
            bubble['current_size'] = bubble['size'] * size_mult
            
        # Atualizar fluxos de corona
        for stream in self.corona_streams:
            stream['angle'] += stream['flow_speed'] * dt * 0.1
            
        # Atualizar ondas da superfície
        for wave in self.surface_waves:
            wave['phase'] += wave['speed'] * dt
            
    def draw(self):
        # 1. Fluxos de corona (mantidos mas reduzidos)
        for stream in self.corona_streams:
            segments = stream['segments']
            for seg in range(segments):
                t = seg / segments
                distance = self.size * 1.1 + t * stream['length'] * 0.5  # Reduzido
                x = self.x + distance * math.cos(stream['angle'])
                y = self.y + distance * math.sin(stream['angle'])
                
                alpha = stream['intensity'] * (1.0 - t) * 0.2  # Reduzido
                width = stream['width'] * (1.0 - t * 0.7)
                
                DrawUtils.set_color(1.0, 0.9, 0.6, alpha)
                DrawUtils.circle(x, y, width, True, 8)
        
        # 3. Partículas de fogo externas
        for particle in self.flame_particles:
            x = self.x + particle['distance'] * math.cos(particle['angle'])
            y = self.y + particle['distance'] * math.sin(particle['angle'])
            
            # Cor baseada na intensidade e distância
            intensity = particle['intensity']
            dist_factor = particle['distance'] / (self.size * 1.5)
            
            if intensity > 0.8:
                r, g, b = 1.0, 1.0, 0.3  # Branco-amarelo quente
            elif intensity > 0.6:
                r, g, b = 1.0, 0.8, 0.1  # Amarelo-laranja
            elif intensity > 0.4:
                r, g, b = 1.0, 0.5, 0.0  # Laranja
            else:
                r, g, b = 1.0, 0.2, 0.0  # Vermelho
                
            alpha = intensity * (1.0 - dist_factor * 0.5) * 0.8
            DrawUtils.set_color(r, g, b, alpha)
            DrawUtils.circle(x, y, particle['size'], True, 12)
        
        # 4. Superfície solar com ondas (textura de magma)
        base_segments = 64
        for wave in self.surface_waves:
            for i in range(base_segments):
                angle = (i / base_segments) * 2 * math.pi
                wave_effect = wave['amplitude'] * math.sin(angle * wave['frequency'] + wave['phase'])
                radius = self.size * (0.95 + wave_effect)
                
                x = self.x + radius * math.cos(angle)
                y = self.y + radius * math.sin(angle)
                
                # Cor variável da superfície
                heat = 0.8 + 0.2 * math.sin(self.time * 2 + angle * 3)
                r = 1.0
                g = 0.3 + 0.4 * heat
                b = 0.0 + 0.2 * heat
                
                DrawUtils.set_color(r, g, b, 0.9)
                DrawUtils.circle(x, y, 0.1, True, 6)
        
        # 5. Núcleo solar principal (múltiplas camadas)
        # Camada externa - laranja escuro
        DrawUtils.set_color(1.0, 0.4, 0.1, 1.0)
        DrawUtils.circle(self.x, self.y, self.size * 0.9, True, 64)
        
        # Camada intermediária - laranja brilhante
        pulse1 = 1.0 + 0.08 * math.sin(self.time * 4)
        DrawUtils.set_color(1.0, 0.6, 0.1, 0.95)
        DrawUtils.circle(self.x, self.y, self.size * 0.75 * pulse1, True, 64)
        
        # Núcleo interno - amarelo quente
        pulse2 = 1.0 + 0.05 * math.sin(self.time * 6 + 1)
        DrawUtils.set_color(1.0, 0.9, 0.3, 0.9)
        DrawUtils.circle(self.x, self.y, self.size * 0.6 * pulse2, True, 64)
        
        # Centro - branco quente
        pulse3 = 1.0 + 0.03 * math.sin(self.time * 8 + 2)
        DrawUtils.set_color(1.0, 1.0, 0.8, 0.8)
        DrawUtils.circle(self.x, self.y, self.size * 0.4 * pulse3, True, 32)
        
        # 6. Bolhas de magma na superfície
        for bubble in self.magma_bubbles:
            x = self.x + bubble['distance'] * math.cos(bubble['angle'])
            y = self.y + bubble['distance'] * math.sin(bubble['angle'])
            
            # Cor da bolha baseada na intensidade
            intensity = bubble['intensity']
            bubble_heat = 0.7 + 0.3 * math.sin(self.time * 5 + bubble['angle'])
            
            r = 1.0
            g = 0.2 + 0.3 * bubble_heat
            b = 0.0
            alpha = intensity * 0.8
            
            DrawUtils.set_color(r, g, b, alpha)
            DrawUtils.circle(x, y, bubble['current_size'], True, 8)

class AsteroidBelt:
    def __init__(self, inner_radius=30, outer_radius=36, count=200):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.count = count
        self.asteroids = []
        self.time = 0.0
        self._create_asteroids()
    
    def _create_asteroids(self):
        import random
        for i in range(self.count):
            # Posição orbital aleatória
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(self.inner_radius, self.outer_radius)
            
            # Velocidade orbital (mais lenta que planetas)
            orbital_speed = random.uniform(0.1, 0.3) / distance  # Mais distante = mais lento
            
            # Características do asteróide
            size = random.uniform(0.03, 0.12)
            brightness = random.uniform(0.4, 0.8)
            
            asteroid = {
                'angle': angle,
                'distance': distance,
                'orbital_speed': orbital_speed,
                'size': size,
                'brightness': brightness,
                'rotation': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-2, 2)
            }
            self.asteroids.append(asteroid)
    
    def update(self, dt):
        self.time += dt
        for asteroid in self.asteroids:
            # Movimento orbital
            asteroid['angle'] += asteroid['orbital_speed'] * dt
            # Rotação individual
            asteroid['rotation'] += asteroid['rotation_speed'] * dt
    
    def draw(self):
        for asteroid in self.asteroids:
            # Calcular posição
            x = asteroid['distance'] * math.cos(asteroid['angle'])
            y = asteroid['distance'] * math.sin(asteroid['angle'])
            
            # Cor acinzentada dos asteróides
            brightness = asteroid['brightness']
            r = 0.6 * brightness
            g = 0.5 * brightness  
            b = 0.4 * brightness
            
            # Variação sutil de brilho
            flicker = 1.0 + 0.1 * math.sin(self.time * 3 + asteroid['angle'] * 10)
            alpha = brightness * flicker * 0.9
            
            DrawUtils.set_color(r, g, b, alpha)
            
            # Desenhar asteróide como pequeno círculo irregular
            # Alguns asteróides maiores aparecem como formas ligeiramente irregulares
            if asteroid['size'] > 0.08:
                # Asteróide maior - forma ligeiramente irregular
                for i in range(8):
                    angle_offset = asteroid['rotation'] + i * math.pi / 4
                    radius_var = asteroid['size'] * (0.8 + 0.4 * math.sin(angle_offset * 3))
                    px = x + radius_var * math.cos(angle_offset)
                    py = y + radius_var * math.sin(angle_offset)
                    DrawUtils.circle(px, py, asteroid['size'] * 0.3, True, 8)
            else:
                # Asteróide pequeno - ponto simples
                DrawUtils.circle(x, y, asteroid['size'], True, 6)