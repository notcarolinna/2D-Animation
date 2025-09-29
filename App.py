import math
import time
import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import (Planet, create_planets, Comet, create_comet)
from Player import PlayerSystem, Ponto, Quadrado
from Animation import Animation 

class App:
    def __init__(self, width=1400, height=1000):
        self.width = width
        self.height = height
        
        # Controle de tempo
        self.tempo_anterior = time.time()
        self.tempo_total = 0.0
        self.soma_dt = 0.0
        self.fps_target = 60.0
        
        # Viewport e câmera
        self.left, self.right = -20.0, 20.0
        self.top, self.bottom = 15.0, -15.0
        self.panX = 0.0
        self.panY = 0.0
        self.zoom = 1.0
        
        # Estados da aplicação
        self.paused = False
        self.show_planets = True
        self.show_player = True
        
        # Objetos principais
        self.planets = create_planets()
        
        # Cometas animados apenas - LIMPO
        self.comets = []
        self.create_comets()
        
        # Sistema de animação
        self.animation_system = Animation()
        
        # Configurar animações
        self.setup_animations()
        
        # Sistema do Player
        self.player_system = PlayerSystem()

    def create_comets(self):
        """
        Cria cometas que serão animados pelas entidades - SEM cometas estáticos
        """
        # Criar apenas cometas que serão animados
        comet_count = 4  # Quantidade de cometas
        
        for i in range(comet_count):
            # Posições iniciais temporárias (serão substituídas pela animação)
            x = 0.0
            y = 0.0
            size = 0.12 + (i * 0.02)  # Tamanhos variados
            
            comet = create_comet(x=x, y=y, size=size)
            # NÃO adicionar cauda estática - será animada
            self.comets.append(comet)

    def setup_animations(self):
        """
        Configura as animações para planetas e cometas
        """
        print("DEBUG: Configurando animações...")
        
        # Primeiro, animar todos os planetas possíveis
        planets_animated = self.animation_system.setup_planets_animation(self.planets)
        
        # Depois, animar os cometas com as entidades restantes
        comets_animated = self.animation_system.setup_comets_animation(self.comets, planets_animated)
        
        total_animated = planets_animated + comets_animated
        print(f"DEBUG: Total de objetos animados: {total_animated}")

    def set_ortho(self, l, r, b, t):
        self.left, self.right, self.bottom, self.top = l, r, b, t
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.left + self.panX, self.right + self.panX, 
                   self.bottom + self.panY, self.top + self.panY)
        glMatrixMode(GL_MODELVIEW)

    def reset_ortho(self):
        self.set_ortho(-20.0, 20.0, -15.0, 15.0)
        
    def update_planets(self, delta_time):
        """
        Atualiza planetas - pula animação orbital se estiver sendo animado pelo sistema
        """
        for planet in self.planets:
            # Verificar se o planeta está sendo animado
            is_animated = planet in self.animation_system.animated_objects.values()
            
            if not is_animated and hasattr(planet, 'orbital_radius') and planet.orbital_radius > 0:
                # Animação orbital normal
                planet.orbital_angle += planet.orbital_speed * delta_time
                planet.x = planet.orbital_radius * math.cos(planet.orbital_angle)
                planet.y = planet.orbital_radius * math.sin(planet.orbital_angle) * 0.3
            
            # Atualizar animações internas (rotação, etc.)
            planet.update(delta_time)
    
    def render(self):
        # Sistema de projeção
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.left + self.panX, self.right + self.panX, 
                   self.bottom + self.panY, self.top + self.panY)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Desenhar planetas
        if self.show_planets:
            for planet in self.planets:
                planet.draw()
        
        # Desenhar quadrados do Player
        if self.show_player:
            for q in self.player_system.quadrados:
                self.player_system.desenhaQuadrado(q.pos.x, q.pos.y, q.w, q.h, q.c)

        # Desenhar APENAS cometas animados
        for comet in self.comets:
            # Só desenhar se estiver sendo animado
            if comet in self.animation_system.animated_objects.values():
                comet.draw()
                
        # overlay: bbox apenas
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
            
            # Atualizar sistema de animação
            self.animation_system.update(delta_time)
        
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:  # ESC
            sys.exit(0)
        
        # Controles do Player - apenas WASD
        elif key == b'w':  # Mover cima
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0, 0.1)
        elif key == b's':  # Mover baixo
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0, 0.1)
        elif key == b'a':  # Mover esquerda
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0.1, 0)
        elif key == b'd':  # Mover direita
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0.1, 0)
    
    def handle_special_keys(self, key, x, y):
        # Manter apenas controles de câmera com setas
        if key == GLUT_KEY_LEFT:  
            self.panX += 0.5
        elif key == GLUT_KEY_RIGHT: 
            self.panX -= 0.5
        elif key == GLUT_KEY_UP:    
            self.panY -= 0.5
        elif key == GLUT_KEY_DOWN:  
            self.panY += 0.5
    
    def reset_all(self):
        # Reset geral
        self.tempo_total = 0.0
        self.panX = 0.0
        self.panY = 0.0
        self.zoom = 1.0
        
        # Reset das animações
        self.animation_system.reset_all()
        
        for planet in self.planets:
            if hasattr(planet, 'orbital_radius'):
                planet.orbital_angle = hash(planet.name) % 100 / 100.0 * 2 * math.pi
                planet.rotation = 0.0
        
        # Reinicia sistema do Player
        self.player_system = PlayerSystem()
        self.reset_ortho()
    
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