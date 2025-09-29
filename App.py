import math
import time
import sys
import random
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import (Planet, create_planets, Star, create_star)
from Player import PlayerSystem, Ponto
from Animation import Animation 

class App:
    def __init__(self, width=1400, height=1000):
        self.width, self.height = width, height
        self.tempo_anterior = time.time()
        self.tempo_total = 0.0
        self.soma_dt = 0.0
        self.fps_target = 120.0
        
        self.left, self.right, self.bottom, self.top = -20.0, 20.0, -15.0, 15.0
        self.panX = self.panY = 0.0
        
        self.show_planets = self.show_player = True
        
        self.planets = create_planets()
        self.stars = [create_star(0, 0, 0, 0, 0.12 + i * 0.02) for i in range(4)]
        self.background_stars = self._create_background_stars()
        
        self.player_system = PlayerSystem()
        self.animation_system = Animation()
        self._setup_animations()

    def _create_background_stars(self):
        random.seed(42)
        return [{
            'x': random.uniform(-30, 30),
            'y': random.uniform(-20, 20),
            'brightness': random.uniform(0.3, 1.0),
            'twinkle_speed': random.uniform(0.5, 2.0)
        } for _ in range(150)]

    def _setup_animations(self):
        player_animated = self.animation_system.setup_player_animation(self.player_system)
        planets_animated = self.animation_system.setup_planets_animation(self.planets, 1)
        self.animation_system.setup_stars_animation(self.stars, 1 + planets_animated)

    def _draw_background_stars(self):
        glPointSize(1.0)
        glBegin(GL_POINTS)
        for star in self.background_stars:
            alpha = star['brightness'] * (math.sin(self.tempo_total * star['twinkle_speed']) * 0.2 + 0.8)
            glColor4f(1.0, 1.0, 1.0, alpha)
            glVertex2f(star['x'], star['y'])
        glEnd()

    def render(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.left + self.panX, self.right + self.panX, 
                   self.bottom + self.panY, self.top + self.panY)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._draw_background_stars()
        
        if self.show_planets:
            for planet in self.planets:
                planet.draw()
        
        if self.show_player:
            for q in self.player_system.quadrados:
                self.player_system.desenhaQuadrado(q.pos.x, q.pos.y, q.w, q.h, q.c)

        for star in self.stars:
            if star in self.animation_system.animated_objects.values():
                star.draw()
                
        self.player_system.desenhaBBox()
        
        glDisable(GL_BLEND)
        glFlush()
    
    def update(self):
        tempo_atual = time.time()
        delta_time = tempo_atual - self.tempo_anterior
        self.tempo_anterior = tempo_atual
        self.soma_dt += delta_time
        self.tempo_total += delta_time
        
        if self.soma_dt > 1.0 / self.fps_target:
            self.soma_dt = 0.0
            
            # Atualizar tudo
            for planet in self.planets:
                planet.update(delta_time)
            
            self.animation_system.update(delta_time)
            
            for star in self.stars:
                star.update(delta_time)
        
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:  # ESC
            sys.exit(0)
        
        move_map = {
            b'w': (0, 0.3), b's': (0, -0.3), 
            b'a': (-0.3, 0), b'd': (0.3, 0)
        }
        
        if key in move_map and self.player_system.quadrados:
            dx, dy = move_map[key]
            self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(dx, dy)
        

    def reshape(self, w, h):
        self.width, self.height = w, h
        glViewport(0, 0, w, h)
        glutPostRedisplay()


def main():
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(1400, 1000)
    glutCreateWindow(b"Space Animation")
    
    app = App()
    
    glutDisplayFunc(app.render)
    glutIdleFunc(app.update)
    glutKeyboardFunc(app.handle_keyboard)
    glutReshapeFunc(app.reshape)

    glutMainLoop()

if __name__ == '__main__':
    main()