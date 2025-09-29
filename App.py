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
        self.width = width
        self.height = height
        
        self.tempo_anterior = time.time()
        self.tempo_total = 0.0
        self.soma_dt = 0.0
        self.fps_target = 60.0
        
        self.left, self.right = -20.0, 20.0
        self.top, self.bottom = 15.0, -15.0
        self.panX = 0.0
        self.panY = 0.0
        
        self.paused = False
        self.show_planets = True
        self.show_player = True
        
        self.planets = create_planets()
        
        self.stars = []
        self.create_stars()
        
        # Criar estrelas de fundo
        self.background_stars = []
        self.create_background_stars()
        
        self.player_system = PlayerSystem()
        self.animation_system = Animation()
        
        self.setup_animations()

    def create_stars(self):
        star_count = 4
        
        for i in range(star_count):
            x = 0.0
            y = 0.0
            size = 0.12 + (i * 0.02)
            
            star = create_star(x=x, y=y, size=size)
            self.stars.append(star)

    def create_background_stars(self):
        # Criar 150 pequenas estrelas de fundo espalhadas
        random.seed(42)  # Para posições consistentes
        
        for _ in range(150):
            x = random.uniform(-30, 30)  # Área maior que a tela visível
            y = random.uniform(-20, 20)
            brightness = random.uniform(0.3, 1.0)
            size = random.uniform(0.02, 0.05)  # Pequenas
            
            self.background_stars.append({
                'x': x,
                'y': y, 
                'brightness': brightness,
                'size': size,
                'twinkle_speed': random.uniform(0.5, 2.0)
            })

    def draw_background_stars(self):
        glPointSize(1.0)
        glBegin(GL_POINTS)
        
        for star in self.background_stars:
            # Efeito de cintilação sutil
            twinkle = math.sin(self.tempo_total * star['twinkle_speed']) * 0.2 + 0.8
            alpha = star['brightness'] * twinkle
            
            # Cor branca/azulada
            glColor4f(1.0, 1.0, 1.0, alpha)
            glVertex2f(star['x'], star['y'])
            
            # Algumas estrelas com brilho extra
            if star['brightness'] > 0.8:
                glColor4f(0.8, 0.9, 1.0, alpha * 0.5)
                glVertex2f(star['x'] + 0.01, star['y'])
                glVertex2f(star['x'] - 0.01, star['y'])
                glVertex2f(star['x'], star['y'] + 0.01)
                glVertex2f(star['x'], star['y'] - 0.01)
        
        glEnd()

    def setup_animations(self):
        player_animated = self.animation_system.setup_player_animation(self.player_system)
        planets_animated = self.animation_system.setup_planets_animation(self.planets, start_entity_id=1)
        stars_start_id = 1 + planets_animated
        stars_animated = self.animation_system.setup_stars_animation(self.stars, stars_start_id)

    def update_planets(self, delta_time):
        for planet in self.planets:
            is_animated = planet in self.animation_system.animated_objects.values()
            
            if not is_animated and hasattr(planet, 'orbital_radius') and planet.orbital_radius > 0:
                planet.orbital_angle += planet.orbital_speed * delta_time
                planet.x = planet.orbital_radius * math.cos(planet.orbital_angle)
                planet.y = planet.orbital_radius * math.sin(planet.orbital_angle) * 0.3
            
            planet.update(delta_time)
    
    def render(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.left + self.panX, self.right + self.panX, 
                   self.bottom + self.panY, self.top + self.panY)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Fundo escuro do espaço
        glClearColor(0.02, 0.02, 0.08, 1.0)  # Azul muito escuro
        glClear(GL_COLOR_BUFFER_BIT)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Desenhar estrelas de fundo primeiro
        self.draw_background_stars()

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
        if self.paused:
            glutPostRedisplay()
            return
            
        tempo_atual = time.time()
        delta_time = tempo_atual - self.tempo_anterior
        self.tempo_anterior = tempo_atual
        self.soma_dt += delta_time
        self.tempo_total += delta_time
        
        if self.soma_dt > 1.0 / self.fps_target:
            self.soma_dt = 0.0
            
            if self.show_planets:
                self.update_planets(delta_time)
            
            self.animation_system.update(delta_time)
            
            for star in self.stars:
                star.update(delta_time)
        
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:
            sys.exit(0)
        
        if key == b'w':
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0, 0.3)
        elif key == b's':
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0, 0.3)
        elif key == b'a':
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0.3, 0)
        elif key == b'd':
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0.3, 0)
        elif key == b'p':
            self.paused = not self.paused
        elif key == b'1':
            self.show_planets = not self.show_planets
        elif key == b'2':
            self.show_player = not self.show_player
        elif key == b'r' or key == b'R':
            self.reset_all()
    
    def handle_special_keys(self, key, x, y):
        if key == GLUT_KEY_LEFT:  
            self.panX += 0.5
        elif key == GLUT_KEY_RIGHT: 
            self.panX -= 0.5
        elif key == GLUT_KEY_UP:    
            self.panY -= 0.5
        elif key == GLUT_KEY_DOWN:  
            self.panY += 0.5
    
    def reset_all(self):
        self.tempo_total = 0.0
        self.panX = 0.0
        self.panY = 0.0
        
        self.animation_system.reset_all()
        
        for planet in self.planets:
            if hasattr(planet, 'orbital_radius'):
                planet.orbital_angle = hash(planet.name) % 100 / 100.0 * 2 * math.pi
                planet.rotation = 0.0
        
        self.player_system = PlayerSystem()
    
    def reshape(self, w, h):
        self.width, self.height = w, h
        glViewport(0, 0, w, h)
        glutPostRedisplay()

app = None

def display():
    app.render()

def idle():
    app.update()

def keyboard(key, x, y):
    app.handle_keyboard(key, x, y)

def special(key, x, y):
    app.handle_special_keys(key, x, y)

def reshape(w, h):
    app.reshape(w, h)

def main():
    global app
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(1400, 1000)
    glutCreateWindow(b"App Integrado - Starship + Planetas + Player")
    
    app = App()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutReshapeFunc(reshape)

    glutMainLoop()

if __name__ == '__main__':
    main()