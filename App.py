import math
import time
import sys
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from Objects import (Planet, create_planets, Comet, create_comet)
from Player import PlayerSystem, Ponto, Quadrado
from Reader import Reader  # Adicionar import do Reader

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
        self.show_sun_animation = True  # Controle para animação do sol
        
        # Objetos principais
        self.planets = create_planets()
        
        # Encontrar o sol nos planetas
        self.sun = None
        for planet in self.planets:
            # Assumindo que o sol tem orbital_radius == 0 ou nome == 'Sun'
            if hasattr(planet, 'orbital_radius') and planet.orbital_radius == 0:
                self.sun = planet
                break
            elif hasattr(planet, 'name') and planet.name.lower() in ['sun', 'sol']:
                self.sun = planet
                break
        
        # Se não encontrou, usar o primeiro planeta como sol
        if self.sun is None and self.planets:
            self.sun = self.planets[0]
        
        # Inicializar Reader e obter trajetória do sol
        self.reader = Reader()
        self.sun_trajectory = self.reader.get_entity_trajectory(0)  # Primeira entidade
        self.sun_trajectory_index = 0.0
        
        # Debug: Verificar se a trajetória foi carregada corretamente
        print(f"DEBUG: Trajetória carregada com {len(self.sun_trajectory) if self.sun_trajectory else 0} pontos")
        if self.sun_trajectory and len(self.sun_trajectory) > 0:
            print(f"DEBUG: Primeiro ponto da trajetória: {self.sun_trajectory[0]}")
            print(f"DEBUG: Último ponto da trajetória: {self.sun_trajectory[-1]}")
            # Mostrar alguns pontos do meio
            mid_point = len(self.sun_trajectory) // 2
            print(f"DEBUG: Ponto do meio da trajetória: {self.sun_trajectory[mid_point]}")
        
        # Salvar posição original do sol
        if self.sun:
            self.sun_original_x = self.sun.x
            self.sun_original_y = self.sun.y
            print(f"DEBUG: Posição original do sol: ({self.sun_original_x}, {self.sun_original_y})")
        
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
            # Pular atualização orbital do sol se animação estiver ativa
            if planet == self.sun and self.show_sun_animation:
                # Apenas atualizar animações internas (rotação, etc.)
                planet.update(delta_time)
                continue
                
            if hasattr(planet, 'orbital_radius') and planet.orbital_radius > 0:
                planet.orbital_angle += planet.orbital_speed * delta_time
                planet.x = planet.orbital_radius * math.cos(planet.orbital_angle)
                planet.y = planet.orbital_radius * math.sin(planet.orbital_angle) * 0.3
            planet.update(delta_time)
    
    def update_sun_animation(self, delta_time):
        """Atualiza a posição do sol seguindo a trajetória do Reader"""
        if not self.sun_trajectory or not self.show_sun_animation or not self.sun:
            return
            
        # Velocidade da animação (pontos por segundo)
        animation_speed = 30.0
        
        # Calcular quantos pontos avançar baseado no delta_time
        points_to_advance = animation_speed * delta_time
        self.sun_trajectory_index += points_to_advance
        
        # Verificar se chegou ao fim da trajetória (loop)
        if self.sun_trajectory_index >= len(self.sun_trajectory):
            self.sun_trajectory_index = 0.0
            print("DEBUG: Trajetória reiniciou do início")
        
        # Obter posição atual com interpolação
        current_index = int(self.sun_trajectory_index)
        next_index = (current_index + 1) % len(self.sun_trajectory)
        interpolation_factor = self.sun_trajectory_index - current_index
        
        current_point = self.sun_trajectory[current_index]
        next_point = self.sun_trajectory[next_index]
        
        # Interpolação linear entre os pontos
        x = current_point[0] + (next_point[0] - current_point[0]) * interpolation_factor
        y = current_point[1] + (next_point[1] - current_point[1]) * interpolation_factor
        
        # Debug: Mostrar posição atual periodicamente
        if int(self.sun_trajectory_index) % 30 == 0 and interpolation_factor < 0.1:  # A cada 30 pontos
            print(f"DEBUG: Sol no ponto {current_index}: ({x:.2f}, {y:.2f}) | Ponto original: {current_point}")
        
        # Atualizar a posição do sol real do Objects.py
        self.sun.x = x
        self.sun.y = y

    def print_trajectory_info(self):
        """Método para imprimir informações detalhadas da trajetória"""
        print("\n=== INFORMAÇÕES DA TRAJETÓRIA ===")
        print(f"Reader carregado: {self.reader is not None}")
        print(f"Dados carregados: {hasattr(self.reader, 'data') and self.reader.data is not None}")
        
        if hasattr(self.reader, 'data') and self.reader.data:
            entities = self.reader.data.get('entities', [])
            print(f"Número de entidades: {len(entities)}")
            
            if len(entities) > 0:
                first_entity = entities[0]
                print(f"Primeira entidade - ID: {first_entity.get('id', 'N/A')}")
                print(f"Primeira entidade - Nome: {first_entity.get('name', 'N/A')}")
                trajectory = first_entity.get('trajectory', [])
                print(f"Primeira entidade - Pontos na trajetória: {len(trajectory)}")
                
                if len(trajectory) > 0:
                    print(f"Primeiros 5 pontos: {trajectory[:5]}")
                    print(f"Últimos 5 pontos: {trajectory[-5:]}")
        
        print(f"Trajetória do sol carregada: {len(self.sun_trajectory) if self.sun_trajectory else 0} pontos")
        print("================================\n")

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

        # conteúdo: planetas (incluindo sol animado)
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
            
            # Atualizar animação do sol
            self.update_sun_animation(delta_time)
        
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
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0.1, 0)
        elif key == b'd':  # Mover direita
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0.1, 0)
        elif key == b'w':  # Mover cima
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos += Ponto(0, 0.1)
        elif key == b's':  # Mover baixo
            if self.player_system.quadrados:
                self.player_system.quadrados[self.player_system.num_quadrado].pos -= Ponto(0, 0.1)
        elif key == ord('4'):
            self.show_comets = not self.show_comets
            print(f"Cometas: {'ON' if self.show_comets else 'OFF'}")
        elif key == ord('5'):  # Controle da animação do sol
            self.show_sun_animation = not self.show_sun_animation
            if not self.show_sun_animation and self.sun:
                # Restaurar posição original do sol
                self.sun.x = self.sun_original_x
                self.sun.y = self.sun_original_y
                print(f"DEBUG: Sol restaurado para posição original: ({self.sun.x}, {self.sun.y})")
            print(f"Animação do Sol: {'ON' if self.show_sun_animation else 'OFF'}")
        elif key == ord('6'):  # Nova tecla para debug
            self.print_trajectory_info()
        elif key == ord('7'):  # Nova tecla para verificar posição atual do sol
            if self.sun:
                current_pos = (self.sun.x, self.sun.y)
                trajectory_index = int(self.sun_trajectory_index) if self.sun_trajectory else -1
                expected_pos = self.sun_trajectory[trajectory_index] if self.sun_trajectory and trajectory_index < len(self.sun_trajectory) else "N/A"
                print(f"DEBUG: Posição atual do sol: {current_pos}")
                print(f"DEBUG: Índice da trajetória: {trajectory_index}")
                print(f"DEBUG: Posição esperada da trajetória: {expected_pos}")
    
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
        # Reset geral
        self.tempo_total = 0.0
        self.panX = 0.0
        self.panY = 0.0
        self.zoom = 1.0
        
        # Reset da animação do sol
        self.sun_trajectory_index = 0.0
        if self.sun:
            self.sun.x = self.sun_original_x
            self.sun.y = self.sun_original_y
        
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