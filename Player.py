import math
from OpenGL.GL import *

class Ponto:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
    def __add__(self, other): return Ponto(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Ponto(self.x - other.x, self.y - other.y)
    def __mul__(self, escalar: float): return Ponto(self.x * escalar, self.y * escalar)

class UFO:
    def __init__(self, radius=0.8, cor=(0.7, 0.7, 0.7)): 
        self.pos = Ponto(0, 0)
        self.radius = radius
        self.w, self.h = radius * 2, radius * 1.2
        self.c = cor

class GLDraw:
    @staticmethod
    def circle(cx, cy, radius, filled=True, segments=32):
        glBegin(GL_TRIANGLE_FAN if filled else GL_LINE_LOOP)
        if filled: glVertex2f(cx, cy)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            glVertex2f(cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        glEnd()

    @staticmethod
    def ellipse(cx, cy, width, height, filled=True, segments=32):
        glBegin(GL_TRIANGLE_FAN if filled else GL_LINE_LOOP)
        if filled: glVertex2f(cx, cy)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            glVertex2f(cx + width * math.cos(angle), cy + height * math.sin(angle))
        glEnd()

    @staticmethod
    def tractor_beam(radius, time_factor):
        beam_start_y = -radius * 0.3
        beam_width = radius * 0.8 * (math.sin(time_factor * 3) * 0.3 + 0.7)
        beam_end_y = beam_start_y - radius * 1.2
        
        layers = [(0.0, 1.0, 0.0, 1.0), (0.2, 1.0, 0.3, 0.85), (0.4, 0.9, 0.6, 0.7), 
                 (0.6, 0.7, 0.9, 0.55), (0.8, 0.5, 1.0, 0.4)]
        
        pulse = (math.sin(time_factor * 3) * 0.3 + 0.7)
        for i, (r, g, b, width_mult) in enumerate(layers):
            glColor4f(r, g, b, (0.6 - i * 0.1) * pulse)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(0, beam_start_y)
            current_width = beam_width * width_mult
            for j in range(21):
                t = (j / 20) * 2 - 1
                glVertex2f(current_width * t, beam_end_y)
            glEnd()

        glColor4f(0.8, 1.0, 0.8, 0.8)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for i in range(8):
            t = i / 8.0
            y = beam_start_y - (radius * 1.2 * t)
            x_offset = math.sin(time_factor * 2 + i) * beam_width * 0.48 * t
            glVertex2f(x_offset, y)
        glEnd()

class PlayerSystem:
    def __init__(self):
        self.quadrados = [UFO(0.8)]
        self.num_quadrado = 0

    def desenhaUFO(self, x, y, radius, cor=(0.7, 0.7, 0.7), time_factor=0):
        glPushMatrix()
        glTranslatef(x, y, 0)
        
        glColor3f(*cor)
        GLDraw.ellipse(0, 0, radius, radius * 0.3, True, 32)
        
        glColor3f(cor[0] * 0.5, cor[1] * 0.5, cor[2] * 0.5)
        glLineWidth(2)
        GLDraw.ellipse(0, 0, radius, radius * 0.3, False, 32)
        
        glColor3f(min(1.0, cor[0] * 1.3), min(1.0, cor[1] * 1.3), min(1.0, cor[2] * 1.3))
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        dome_radius = radius * 0.6
        for i in range(33):
            angle = math.pi * i / 32
            glVertex2f(dome_radius * math.cos(angle), dome_radius * math.sin(angle))
        glEnd()
        
        glColor3f(cor[0] * 0.4, cor[1] * 0.4, cor[2] * 0.4)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for i in range(33):
            angle = math.pi * i / 32
            glVertex2f(dome_radius * math.cos(angle), dome_radius * math.sin(angle))
        glEnd()
        
        GLDraw.tractor_beam(radius, time_factor)
        
        glColor3f(1.0, 1.0, 0.0)
        for i in range(6):
            angle = 2 * math.pi * i / 6
            GLDraw.circle(radius * 0.8 * math.cos(angle), radius * 0.1 * math.sin(angle), 
                         radius * 0.05, True, 8)

        glPopMatrix()