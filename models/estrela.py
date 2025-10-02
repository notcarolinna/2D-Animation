import math
import random
from OpenGL.GL import *
from GraphicsUtils import DrawUtils
from .efeitos import PulseEffect

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

def create_star(x=0, y=0, vx=0, vy=0, size=0.15): 
    return Star(x, y, vx, vy, size)