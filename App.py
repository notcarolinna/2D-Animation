import math
import time
import sys
import random
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import create_planets, create_star
from Player import PlayerSystem, Ponto
from Animation import Animation 
from CollisionSystem import CollisionSystem

class App:
    def __init__(self):
        self.viewport = (-20.0, 20.0, -15.0, 15.0)
        self.panX = self.panY = 0.0
        
        self.paused = False
        self.show_planets = True
        self.show_player = True
        self.tempo_anterior = time.time()
        self.tempo_total = 0.0
        
        self.planets = create_planets()
        self.stars = [create_star(0, 0, 0, 0, 0.12 + i * 0.02) for i in range(4)]
        self.background_stars = self._create_background_stars()
        
        self.player_system = PlayerSystem()
        self.animation_system = Animation()
        self.collision_system = CollisionSystem()
        
        self.animation_system.setup_player_animation(self.player_system)
        planets_count = self.animation_system.setup_planets_animation(self.planets, 1)
        self.animation_system.setup_stars_animation(self.stars, 1 + planets_count)

    def _create_background_stars(self):
        random.seed(42)
        return [{'x': random.uniform(-30, 30), 'y': random.uniform(-20, 20),
                'brightness': random.uniform(0.3, 1.0), 'twinkle_speed': random.uniform(0.5, 2.0)}
                for _ in range(150)]

    def render(self):
        left, right, bottom, top = self.viewport
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(left + self.panX, right + self.panX, bottom + self.panY, top + self.panY)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Background stars
        glPointSize(1.0)
        glBegin(GL_POINTS)
        for star in self.background_stars:
            alpha = star['brightness'] * (math.sin(self.tempo_total * star['twinkle_speed']) * 0.2 + 0.8)
            glColor4f(1.0, 1.0, 1.0, alpha)
            glVertex2f(star['x'], star['y'])
        glEnd()
        
        # Objects
        if self.show_planets:
            for planet in self.planets:
                planet.draw()
        
        if self.show_player:
            for q in self.player_system.quadrados:
                self.player_system.desenhaUFO(q.pos.x, q.pos.y, q.radius, q.c, self.tempo_total)

        for star in self.stars:
            if star in self.animation_system.animated_objects.values():
                star.draw()
        
        glDisable(GL_BLEND)
        glFlush()
    
    def update(self):
        if self.paused:
            glutPostRedisplay()
            return
            
        tempo_atual = time.time()
        delta_time = tempo_atual - self.tempo_anterior
        self.tempo_anterior = tempo_atual
        self.tempo_total += delta_time
        
        for planet in self.planets:
            planet.update(delta_time)
        
        self.animation_system.update(delta_time)
        
        for star in self.stars:
            star.update(delta_time)
        
        # Collisions
        all_objects = []
        if self.show_player and self.player_system.quadrados:
            all_objects.append(self.player_system.quadrados[self.player_system.num_quadrado])
        if self.show_planets:
            all_objects.extend(self.planets)
        all_objects.extend(star for star in self.stars 
                          if star in self.animation_system.animated_objects.values())
        
        self.collision_system.update_collisions(all_objects)
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:
            sys.exit(0)
        
        moves = {b'w': (0, 0.3), b's': (0, -0.3), b'a': (-0.3, 0), b'd': (0.3, 0)}
        
        if key in moves and self.player_system.quadrados:
            dx, dy = moves[key]
            self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(dx, dy)
        
    def reshape(self, w, h):
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