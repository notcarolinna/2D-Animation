import math
import random
from OpenGL.GL import *
from GraphicsUtils import DrawUtils

class FireSun:
    def __init__(self, x=0, y=0, size=3.5):
        self.x = x
        self.y = y
        self.size = size
        self.time = 0.0
        self.magma_bubbles = []
        self._init_magma_bubbles()
        
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
    
    def update(self, dt):
        self.time += dt
        
        # Atualizar bolhas de magma
        for bubble in self.magma_bubbles:
            bubble['angle'] += bubble['bubble_speed'] * dt * 0.3
            bubble['growth_phase'] += dt * 3.0
            size_mult = 1.0 + 0.4 * math.sin(bubble['growth_phase'])
            bubble['current_size'] = bubble['size'] * size_mult
            
    def draw(self):
        # 1. Núcleo solar principal (múltiplas camadas)
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
        
        # 2. Bolhas de magma na superfície
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
    def __init__(self, inner_radius=30, outer_radius=36, count=200, belt_name="Main Belt"):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.count = count
        self.belt_name = belt_name
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
            
            # Características do asteróide - tamanhos maiores e mais variados
            size = random.uniform(0.05, 0.20)  # Aumentei o tamanho
            brightness = random.uniform(0.5, 1.0)  # Maior brilho
            
            # Tipos de asteroides com cores diferentes
            asteroid_type = random.choice(['rocky', 'metallic', 'carbonaceous', 'icy'])
            
            asteroid = {
                'angle': angle,
                'distance': distance,
                'orbital_speed': orbital_speed,
                'size': size,
                'brightness': brightness,
                'rotation': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-2, 2),
                'type': asteroid_type,
                'twinkle_phase': random.uniform(0, 2 * math.pi),
                'twinkle_speed': random.uniform(1.0, 3.0)
            }
            self.asteroids.append(asteroid)
    
    def update(self, dt):
        self.time += dt
        for asteroid in self.asteroids:
            # Movimento orbital
            asteroid['angle'] += asteroid['orbital_speed'] * dt
            # Rotação individual
            asteroid['rotation'] += asteroid['rotation_speed'] * dt
            # Cintilação
            asteroid['twinkle_phase'] += asteroid['twinkle_speed'] * dt
    
    def draw(self):
        for asteroid in self.asteroids:
            # Calcular posição
            x = asteroid['distance'] * math.cos(asteroid['angle'])
            y = asteroid['distance'] * math.sin(asteroid['angle'])
            
            # Cores baseadas no tipo de asteroide
            brightness = asteroid['brightness']
            twinkle = 0.8 + 0.2 * math.sin(asteroid['twinkle_phase'])
            
            if asteroid['type'] == 'rocky':
                r, g, b = 0.7 * brightness, 0.5 * brightness, 0.3 * brightness
            elif asteroid['type'] == 'metallic':
                r, g, b = 0.8 * brightness, 0.8 * brightness, 0.7 * brightness
            elif asteroid['type'] == 'carbonaceous':
                r, g, b = 0.4 * brightness, 0.3 * brightness, 0.2 * brightness
            else:  # icy
                r, g, b = 0.9 * brightness, 0.9 * brightness, 1.0 * brightness
            
            # Variação sutil de brilho
            flicker = 1.0 + 0.15 * math.sin(self.time * 3 + asteroid['angle'] * 10)
            alpha = brightness * flicker * twinkle * 0.9
            
            DrawUtils.set_color(r, g, b, alpha)
            
            # Desenhar asteróide - todos com forma ligeiramente irregular
            if asteroid['size'] > 0.08:
                # Asteróide maior - forma mais irregular
                for i in range(8):
                    angle_offset = asteroid['rotation'] + i * math.pi / 4
                    radius_var = asteroid['size'] * (0.7 + 0.5 * math.sin(angle_offset * 3))
                    px = x + radius_var * 0.8 * math.cos(angle_offset)
                    py = y + radius_var * 0.8 * math.sin(angle_offset)
                    DrawUtils.circle(px, py, asteroid['size'] * 0.4, True, 8)
                
                # Núcleo central mais brilhante
                DrawUtils.set_color(r * 1.2, g * 1.2, b * 1.2, alpha * 1.3)
                DrawUtils.circle(x, y, asteroid['size'] * 0.6, True, 12)
            else:
                # Asteróide pequeno - ponto mais brilhante
                DrawUtils.circle(x, y, asteroid['size'] * 1.5, True, 8)

class MultipleAsteroidBelts:
    def __init__(self):
        self.belts = []
        self._create_multiple_belts()
    
    def _create_multiple_belts(self):
        # Cinturão Principal (entre Marte e Júpiter)
        main_belt = AsteroidBelt(inner_radius=28, outer_radius=38, count=300, belt_name="Main Belt")
        self.belts.append(main_belt)
        
        # Cinturão de Kuiper (além de Netuno)
        kuiper_belt = AsteroidBelt(inner_radius=75, outer_radius=95, count=200, belt_name="Kuiper Belt")
        self.belts.append(kuiper_belt)
        
        # Cinturão Interior (entre Vênus e Terra)
        inner_belt = AsteroidBelt(inner_radius=12, outer_radius=18, count=80, belt_name="Inner Belt")
        self.belts.append(inner_belt)
        
        # Cinturão Exterior (entre Saturno e Urano)
        outer_belt = AsteroidBelt(inner_radius=55, outer_radius=65, count=150, belt_name="Outer Belt")
        self.belts.append(outer_belt)
        
        # Cinturão Distante (muito além do sistema solar)
        distant_belt = AsteroidBelt(inner_radius=100, outer_radius=120, count=120, belt_name="Distant Belt")
        self.belts.append(distant_belt)
    
    def update(self, dt):
        for belt in self.belts:
            belt.update(dt)
    
    def draw(self):
        for belt in self.belts:
            belt.draw()
    
    def draw_belt_boundaries(self):
        """Desenha as bordas dos cinturões para melhor visualização"""
        from GraphicsUtils import DrawUtils
        
        belt_colors = [
            (0.7, 0.5, 0.3, 0.2),  # Main Belt - marrom
            (0.3, 0.5, 0.8, 0.15), # Kuiper Belt - azul
            (0.8, 0.6, 0.4, 0.25), # Inner Belt - dourado
            (0.5, 0.7, 0.5, 0.2),  # Outer Belt - verde
            (0.6, 0.4, 0.8, 0.15)  # Distant Belt - roxo
        ]
        
        for i, belt in enumerate(self.belts):
            color = belt_colors[i % len(belt_colors)]
            DrawUtils.set_color(*color)
            
            # Desenhar bordas do cinturão
            DrawUtils.circle(0, 0, belt.inner_radius, False, 64)
            DrawUtils.circle(0, 0, belt.outer_radius, False, 64)