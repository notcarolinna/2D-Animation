import math
import time
import sys
import random
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import create_planets, create_star, create_entities_for_animation, BackgroundStars
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
        
        self.player_system = PlayerSystem()
        self.animation_system = Animation()
        self.collision_system = CollisionSystem()
        
        total_entities = self.animation_system.total_entities
        self.animated_entities = create_entities_for_animation(total_entities)
        
        self.planets = create_planets()
        self.stars = [create_star(0, 0, 0, 0, 0.20 + i * 0.05) for i in range(4)] 
        self.background_stars = BackgroundStars(count=150, seed=42)
        
        self.animation_system.setup_player_animation(self.player_system)
        self.animation_system.setup_entities_animation(self.animated_entities, 1)

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
        
        self.background_stars.render(self.tempo_total)
        
        if self.show_planets:
            for entity in self.animated_entities:
                if entity in self.animation_system.animated_objects.values():
                    entity.draw()
        
        self.player_system.render(self.tempo_total)
        
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
        
        for entity in self.animated_entities:
            if hasattr(entity, 'update'):
                entity.update(delta_time)
        
        self.player_system.update(delta_time)
        self.animation_system.update(delta_time)
        
        all_objects = self.player_system.get_collision_objects()
        if self.show_planets:
            all_objects.extend(entity for entity in self.animated_entities 
                             if entity in self.animation_system.animated_objects.values())
        
        self.collision_system.update_collisions(all_objects)
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:
            sys.exit(0)
        
        if not self.player_system.handle_keyboard(key):
            pass
        
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