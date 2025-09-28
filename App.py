import math
import time
import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import (Planet, create_planets, Comet, create_comet)
from Player import PlayerSystem, Ponto, Quadrado

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
        self.follow_starship = False
        self.show_planets = True
        self.show_player = True
        
        # Objetos principais
        self.planets = create_planets()
        
        # Sistema do Player - importado
        self.player_system = PlayerSystem()
        
        # Adicionar um cometa estático ao lado dos planetas
        self.comets = []
        self.show_comets = True  # habilitado por padrão para mostrar o cometa
        
        # Criar um cometa estático posicionado entre os planetas
        static_comet = create_comet(x=7.5, y=2.0, size=0.15)  # Entre Mars e Jupiter
        # Adicionar algumas posições à cauda para parecer que está se movendo
        static_comet.tail_positions = [
            (6.8, 2.3), (7.0, 2.2), (7.2, 2.1), (7.4, 2.05), (7.5, 2.0)
        ]
        self.comets.append(static_comet)

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
        for planet in self.planets:
            if hasattr(planet, 'orbital_radius') and planet.orbital_radius > 0:
                planet.orbital_angle += planet.orbital_speed * delta_time
                planet.x = planet.orbital_radius * math.cos(planet.orbital_angle)
                planet.y = planet.orbital_radius * math.sin(planet.orbital_angle) * 0.3
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

        # conteúdo: planetas e nave
        if self.show_planets:
            for planet in self.planets:
                planet.draw()
        
        # conteúdo: quadrados do Player
        if self.show_player:
            for q in self.player_system.quadrados:
                self.player_system.desenhaQuadrado(q.pos.x, q.pos.y, q.w, q.h, q.c)

        # Desenhar cometas (antes dos planetas para ficarem atrás)
        if self.show_comets:
            for comet in self.comets:
                comet.draw()
                
        # overlay: bbox apenas (removido grid e eixos)
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
        
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:  # ESC
            sys.exit(0)
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('f') or key == ord('F'):
            if self.show_player:
                bounds = self.player_system.fit_to_squares()
                self.set_ortho(*bounds)
        elif key == ord('1'):
            self.show_planets = not self.show_planets
        elif key == ord('2'):
            self.show_player = not self.show_player
        elif key == ord('r') or key == ord('R'):
            self.reset_all()
        
        # Controles do Player
        elif key == ord(' '):  # novo quadrado
            self.player_system.quadrados.append(Quadrado(0.5, 0.5))  # Quadrado maior
            self.player_system.num_quadrado = len(self.player_system.quadrados) - 1
        elif key == b'a':  # Mover esquerda
            self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0.1, 0)  # Movimento mais rápido
        elif key == b'd':  # Mover direita
            self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0.1, 0)
        elif key == b'w':  # Mover cima
            self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0, 0.1)
        elif key == b's':  # Mover baixo
            self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0, 0.1)
        elif key == ord('4'):
            self.show_comets = not self.show_comets
            print(f"Cometas: {'ON' if self.show_comets else 'OFF'}")
    
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
        # REMOVIDO: self.starship.reset() - não existe mais
        self.tempo_total = 0.0
        self.panX = 0.0
        self.panY = 0.0
        self.zoom = 1.0
        
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