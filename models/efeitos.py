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