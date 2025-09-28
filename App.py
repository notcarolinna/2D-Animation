import math
import time
import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import (Starship, Planet, create_starship, create_planets)

class IntegratedApp:
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
        self.pan_x = 0.0
        self.zoom = 1.0
        
        # Estados da aplicação
        self.paused = False
        self.follow_starship = False
        self.show_starship = True
        self.show_planets = True
        
        # Objetos principais
        self.starship = create_starship()
        self.planets = create_planets()
        
    def update_planets(self, delta_time):
        for planet in self.planets:
            if hasattr(planet, 'orbital_radius') and planet.orbital_radius > 0:
                # Atualiza ângulo orbital
                planet.orbital_angle += planet.orbital_speed * delta_time
                
                # Calcula posição orbital
                planet.x = planet.orbital_radius * math.cos(planet.orbital_angle)
                planet.y = planet.orbital_radius * math.sin(planet.orbital_angle) * 0.3  # órbitas achatadas
            
            # Atualiza rotação própria
            planet.update(delta_time)
    
    def draw_background(self):
        """Fundo limpo - sem estrelas"""
        # Fundo completamente limpo
        pass
    
    def draw_hud(self):
        """HUD simplificado"""
        pass
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(
            self.left / self.zoom + self.pan_x, 
            self.right / self.zoom + self.pan_x,
            self.bottom / self.zoom, 
            self.top / self.zoom
        )
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Habilita blending para transparências
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        if self.show_planets:
            for planet in self.planets:
                planet.draw()

        if self.show_starship:
            self.starship.draw()

        self.draw_hud()
        
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
        
        # Controle de FPS
        if self.soma_dt > 1.0 / self.fps_target:
            self.soma_dt = 0.0
            
            # Atualiza objetos
            if self.show_planets:
                self.update_planets(delta_time)
            
            if self.show_starship:
                self.starship.update(self.tempo_total, delta_time)
                
                # Segue a nave se habilitado
                if self.follow_starship:
                    self.pan_x = -self.starship.pos.x + 2.0
                
                # Reinicia nave se saiu da tela
                if self.starship.should_reset():
                    self.starship.reset()
                    self.tempo_total = 0.0
        
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        """Manipula entrada do teclado"""
        if key == 27:  # ESC
            sys.exit(0)
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('f') or key == ord('F'):
            self.follow_starship = not self.follow_starship
        elif key == ord('s') or key == ord('S'):
            self.show_starship = not self.show_starship
        elif key == ord('1'):
            self.show_planets = not self.show_planets
        elif key == ord('=') or key == ord('+'):
            self.zoom *= 1.1
        elif key == ord('-'):
            self.zoom /= 1.1
        elif key == ord('c') or key == ord('C'):
            self.pan_x = 0.0
            self.zoom = 1.0
        elif key == ord('r') or key == ord('R'):
            self.reset_all()
    
    def handle_special_keys(self, key, x, y):
        """Manipula teclas especiais"""
        if key == GLUT_KEY_LEFT:
            self.pan_x -= 2.0 / self.zoom
        elif key == GLUT_KEY_RIGHT:
            self.pan_x += 2.0 / self.zoom
        elif key == GLUT_KEY_UP:
            self.zoom *= 1.05
        elif key == GLUT_KEY_DOWN:
            self.zoom /= 1.05
    
    def reset_all(self):
        """Reinicia todos os objetos"""
        self.starship.reset()
        self.tempo_total = 0.0
        self.pan_x = 0.0
        self.zoom = 1.0
        
        # Reinicia posições dos planetas
        for planet in self.planets:
            if hasattr(planet, 'orbital_radius'):
                planet.orbital_angle = hash(planet.name) % 100 / 100.0 * 2 * math.pi
                planet.rotation = 0.0
    
    def reshape(self, w, h):
        """Manipula redimensionamento da janela"""
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
    glutCreateWindow(b"App Limpo - Starship + Planetas")
    
    glClearColor(0.0, 0.0, 0.1, 1.0)  # Azul escuro do espaço

    app = IntegratedApp()
    
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutReshapeFunc(reshape)

    glutMainLoop()

if __name__ == '__main__':
    main()