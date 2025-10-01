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
    def handle_special(self, key, x, y):
        pan_step = 1.0
        if key == GLUT_KEY_LEFT:
            self.panX -= pan_step
        elif key == GLUT_KEY_RIGHT:
            self.panX += pan_step
        elif key == GLUT_KEY_UP:
            self.panY += pan_step
        elif key == GLUT_KEY_DOWN:
            self.panY -= pan_step
        glutPostRedisplay()
    def __init__(self):
        self.base_viewport = (-100.0, 100.0, -80.0, 80.0)  # Viewport expandido para as novas distâncias
        self.panX = self.panY = 0.0
        self.zoom_factor = 1.0  # Fator de zoom
        
        self.show_planets = True
        self.tempo_anterior = time.time()
        self.tempo_total = 0.0
        
        # Criar sistema solar real
        self.create_solar_system()
        
        # Estrelas de fundo cobrindo todo o universo
        self.background_stars = BackgroundStars(count=800, seed=42)
        
        # Estrelas móveis com aparição aleatória
        self.moving_stars = []
        self.max_stars = 20
        self.star_spawn_timer = 0.0
        self.star_spawn_interval = random.uniform(0.5, 2.0)
        
        # Criar algumas estrelas iniciais
        for i in range(3):
            self.spawn_new_star()

    def render(self):
        # Usar viewport fixo maior para ver todo o sistema solar
        left, right, bottom, top = self.base_viewport
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(left + self.panX, right + self.panX, 
                   bottom + self.panY, top + self.panY)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.background_stars.render(self.tempo_total)
        
        # Desenhar órbitas dos planetas (linhas sutis)
        self.draw_orbits()
        
        # Desenhar cinturão de asteróides (atrás dos planetas)
        self.asteroid_belt.draw()
        
        # Desenhar sol
        self.sun.draw()
        
        # Desenhar planetas
        if self.show_planets:
            for planet in self.planets:
                planet.draw()
        
        # Desenhar estrelas móveis
        for star in self.moving_stars:
            star.draw()
        
        glDisable(GL_BLEND)
        glFlush()
    
    def update(self):
        tempo_atual = time.time()
        delta_time = tempo_atual - self.tempo_anterior
        self.tempo_anterior = tempo_atual
        self.tempo_total += delta_time
        
        # Atualizar sol
        self.sun.update(delta_time)
        
        # Atualizar cinturão de asteróides
        self.asteroid_belt.update(delta_time)
        
        # Atualizar movimento orbital dos planetas
        for planet in self.planets:
            planet.orbital_angle += planet.orbital_speed * delta_time
            planet.x = planet.orbital_distance * math.cos(planet.orbital_angle)
            planet.y = planet.orbital_distance * math.sin(planet.orbital_angle)
            planet.update(delta_time)
        
        # Sistema de aparição aleatória de estrelas
        self.star_spawn_timer += delta_time
        
        if self.star_spawn_timer >= self.star_spawn_interval and len(self.moving_stars) < self.max_stars:
            self.spawn_new_star()
            self.star_spawn_timer = 0.0
            self.star_spawn_interval = random.uniform(0.5, 2.0)
        
        # Atualizar estrelas móveis em trajetórias retilíneas
        stars_to_remove = []
        for i, star in enumerate(self.moving_stars):
            star.update(delta_time)
            # Remover estrelas que saíram muito longe da tela
            if (star.x > 50 or star.x < -50 or star.y > 40 or star.y < -40):
                stars_to_remove.append(i)
        
        # Remover estrelas que saíram da tela
        for i in reversed(stars_to_remove):
            self.moving_stars.pop(i)
        
        glutPostRedisplay()
    
    def create_solar_system(self):
        from Objects import Planet, COLORS, FireSun, AsteroidBelt
        # Sol realista com efeitos de fogo
        self.sun = FireSun(0, 0, 3.5)
        
        # Configuração dos planetas com distâncias adequadas para visualização
        # (nome, distância_orbital, velocidade_orbital, tamanho_relativo_ao_sol)
        planet_configs = [
            ("Mercury", 10.0, 4.0, 0.25),   # Primeira órbita
            ("Venus", 15.0, 3.5, 0.60),     # Mais espaçamento
            ("Earth", 21.0, 3.0, 0.65),     # Maior separação
            ("Mars", 28.0, 2.4, 0.35),      # Bem separado
            ("Jupiter", 38.0, 1.3, 4.5),    # Gigante gasoso mais distante
            ("Saturn", 50.0, 1.0, 3.8),     # Grande separação
            ("Uranus", 64.0, 0.7, 2.2),     # Muito mais distante
            ("Neptune", 80.0, 0.5, 2.0)     # Na borda do sistema
        ]
        
        self.planets = []
        for name, distance, speed, size in planet_configs:
            color = COLORS.get(name.lower(), (1, 1, 1))
            planet = Planet(name, distance, 0, size, color)
            planet.orbital_distance = distance
            planet.orbital_speed = speed
            planet.orbital_angle = random.uniform(0, 2 * math.pi)
            self.planets.append(planet)
        
        # Cinturão de asteróides entre Marte (28) e Júpiter (38)
        self.asteroid_belt = AsteroidBelt(inner_radius=30, outer_radius=36, count=150)
    
    def draw_orbits(self):
        """Desenha as órbitas dos planetas como círculos sutis"""
        from GraphicsUtils import DrawUtils
        
        # Configurar cor sutil para as órbitas
        orbit_color = (0.3, 0.3, 0.4, 0.3)  # Azul-acinzentado muito sutil
        
        for planet in self.planets:
            # Cor ligeiramente diferente para cada órbita
            distance_factor = planet.orbital_distance / 80.0  # Normalizar baseado na órbita mais distante
            alpha = 0.2 + 0.1 * (1.0 - distance_factor)  # Órbitas internas um pouco mais visíveis
            
            DrawUtils.set_color(0.4, 0.4, 0.5, alpha)
            
            # Desenhar órbita como círculo vazado (apenas contorno)
            DrawUtils.circle(0, 0, planet.orbital_distance, False, 128)
        
        # Desenhar órbitas do cinturão de asteróides
        DrawUtils.set_color(0.5, 0.4, 0.3, 0.15)  # Cor levemente amarronzada
        DrawUtils.circle(0, 0, 30, False, 64)  # Borda interna
        DrawUtils.circle(0, 0, 36, False, 64)  # Borda externa

    def spawn_new_star(self):
        """Cria uma nova estrela em uma posição aleatória fora da tela com trajetória específica"""
        # Escolher lado aleatório para aparecer
        side = random.randint(0, 3)
        
        if side == 0:  # esquerda
            start_x, start_y = -40, random.uniform(-30, 30)
            # Trajetória para a direita com variação
            angle = random.uniform(-math.pi/4, math.pi/4)  # -45° a +45°
        elif side == 1:  # direita
            start_x, start_y = 40, random.uniform(-30, 30)
            # Trajetória para a esquerda com variação
            angle = random.uniform(3*math.pi/4, 5*math.pi/4)  # 135° a 225°
        elif side == 2:  # cima
            start_x, start_y = random.uniform(-35, 35), 35
            # Trajetória para baixo com variação
            angle = random.uniform(5*math.pi/4, 7*math.pi/4)  # 225° a 315°
        else:  # baixo
            start_x, start_y = random.uniform(-35, 35), -35
            # Trajetória para cima com variação
            angle = random.uniform(math.pi/4, 3*math.pi/4)  # 45° a 135°
        
        speed = random.uniform(3.0, 6.0)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        star = create_star(start_x, start_y, vx, vy, random.uniform(0.08, 0.25))
        self.moving_stars.append(star)
    
    def handle_keyboard(self, key, x, y):
        if key == 27:  # ESC
            sys.exit(0)
        
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
    glutSpecialFunc(app.handle_special)
    glutReshapeFunc(app.reshape)
    glutMainLoop()

if __name__ == '__main__':
    main()