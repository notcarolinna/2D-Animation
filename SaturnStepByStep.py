"""
Demonstração Passo a Passo da Modelagem de Saturno
==================================================

Este arquivo mostra cada etapa da criação de Saturno:

LINHA SUPERIOR - Criação do Planeta:
1. Círculo base
2. Detalhes atmosféricos
3. Anéis com transformação
4. Clipping e profundidade
5. Sombreamento radial

LINHA INFERIOR - Criação dos Anéis:
1. Anel simples
2. Múltiplos anéis
3. Rotação e perspectiva

Todas as etapas são mostradas simultaneamente.
"""

import sys
import time
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from GraphicsUtils import DrawUtils

class SaturnDemo:
    def __init__(self):
        self.viewport = (-12.0, 12.0, -8.0, 8.0)
        self.current_step = 1
        self.max_steps = 5
        self.time_factor = 0.0
        
        # Layout em duas linhas: planeta acima, anéis abaixo
        self.planet_positions = [
            (-8.0, 3.0),   # Etapa 1 - Círculo base
            (-4.0, 3.0),   # Etapa 2 - Atmosfera
            (0.0, 3.0),    # Etapa 3 - Com anéis
            (4.0, 3.0),    # Etapa 4 - Clipping
            (8.0, 3.0),    # Etapa 5 - Sombreamento
        ]
        
        self.rings_positions = [
            (-4.0, -3.0),  # Anel 1 - Anel simples
            (0.0, -3.0),   # Anel 2 - Múltiplos anéis
            (4.0, -3.0),   # Anel 3 - Rotação e perspectiva
        ]
        
        # Parâmetros de Saturno (menores para caber na grade)
        self.saturn_radius = 1.0
        
        # Cores
        self.saturn_color = (0.90, 0.82, 0.70)
        self.ring_color_1 = (0.90, 0.86, 0.78, 0.8)
        self.ring_color_2 = (0.82, 0.78, 0.72, 0.8)
        self.atmospheric_band_color = (0.80, 0.70, 0.50, 0.6)
        
        print("=== DEMONSTRAÇÃO SATURNO PASSO A PASSO ===")
        print("Todas as etapas mostradas simultaneamente")
        print("Teclas:")
        print("ESC: Sair")
        print("SPACE: Alternar animação dos anéis")
    
    def render(self):
        left, right, bottom, top = self.viewport
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(left, right, bottom, top)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Fundo branco
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Desenha todas as etapas lado a lado
        self.draw_all_steps()
        
        glDisable(GL_BLEND)
        glFlush()
    
    def draw_all_steps(self):
        """Desenha todas as etapas lado a lado"""
        # Desenha etapas do planeta (linha superior)
        for i, (x, y) in enumerate(self.planet_positions):
            step_num = i + 1
            
            # Desenha moldura para cada etapa
            self.draw_step_frame(x, y)
            
            # Desenha a etapa específica do planeta
            if step_num == 1:
                self.step_1_base_circle(x, y)
            elif step_num == 2:
                self.step_2_atmospheric_details(x, y)
            elif step_num == 3:
                self.step_4_rings_with_transformation(x, y)
            elif step_num == 4:
                self.step_5_depth_and_clipping(x, y)
            elif step_num == 5:
                self.step_6_radial_shading(x, y)
        
        # Desenha etapas dos anéis (linha inferior)
        for i, (x, y) in enumerate(self.rings_positions):
            step_num = i + 1
            
            # Desenha moldura para cada etapa
            self.draw_step_frame(x, y)
            
            # Desenha a etapa específica dos anéis
            if step_num == 1:
                self.ring_step_1_simple_ring(x, y)
            elif step_num == 2:
                self.ring_step_2_multiple_rings(x, y)
            elif step_num == 3:
                self.ring_step_4_rotation_perspective(x, y)
    
    def draw_step_frame(self, x, y):
        """Desenha moldura ao redor de cada etapa"""
        frame_size = 2.2
        DrawUtils.set_color(0.8, 0.8, 0.8, 1.0)
        glLineWidth(2)
        
        # Desenha retângulo da moldura
        glBegin(GL_LINE_LOOP)
        glVertex2f(x - frame_size, y - frame_size)
        glVertex2f(x + frame_size, y - frame_size)
        glVertex2f(x + frame_size, y + frame_size)
        glVertex2f(x - frame_size, y + frame_size)
        glEnd()
    
    def draw_stars(self):
        """Desenha um fundo com estrelas"""
        import random
        random.seed(42)  # Para estrelas consistentes
        
        glPointSize(2.0)
        glBegin(GL_POINTS)
        DrawUtils.set_color(1.0, 1.0, 1.0, 0.8)
        
        for _ in range(50):
            x = random.uniform(-8.0, 8.0)
            y = random.uniform(-6.0, 6.0)
            glVertex2f(x, y)
        
        glEnd()
    
    def step_1_base_circle(self, saturn_x, saturn_y):
        """ETAPA 1: Círculo Base de Saturno"""
        # Desenha apenas o círculo base
        DrawUtils.set_color(*self.saturn_color)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, True)
        
        # Contorno para definição
        DrawUtils.set_color(0.6, 0.5, 0.4, 1.0)
        glLineWidth(2)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, False)
    
    def step_2_atmospheric_details(self, saturn_x, saturn_y):
        """ETAPA 2: Adiciona Detalhes Atmosféricos"""
        # Círculo base
        DrawUtils.set_color(*self.saturn_color)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, True)
        
        # Banda atmosférica principal
        DrawUtils.set_color(*self.atmospheric_band_color)
        DrawUtils.ellipse(saturn_x, saturn_y + 0.10 * self.saturn_radius, 
                         0.90 * self.saturn_radius, 0.08 * self.saturn_radius, True)
        
        # Bandas adicionais para mais realismo
        DrawUtils.set_color(0.85, 0.75, 0.55, 0.4)
        DrawUtils.ellipse(saturn_x, saturn_y - 0.15 * self.saturn_radius, 
                         0.85 * self.saturn_radius, 0.06 * self.saturn_radius, True)
        
        DrawUtils.set_color(0.88, 0.78, 0.58, 0.3)
        DrawUtils.ellipse(saturn_x, saturn_y + 0.25 * self.saturn_radius, 
                         0.75 * self.saturn_radius, 0.05 * self.saturn_radius, True)
    
    def step_4_rings_with_transformation(self, saturn_x, saturn_y):
        """ETAPA 4: Anéis com Transformação Perspectiva"""
        # Anéis com transformação (atrás do planeta)
        DrawUtils.with_pose(saturn_x, saturn_y, rot_deg=-20, scale=(1.0, 0.40))
        
        # Anéis preenchidos
        DrawUtils.set_color(*self.ring_color_1)
        DrawUtils.ring(0, 0, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius)
        
        DrawUtils.set_color(*self.ring_color_2)
        DrawUtils.ring(0, 0, 1.35 * self.saturn_radius, 1.55 * self.saturn_radius)
        
        DrawUtils.end_pose()
        
        # Planeta
        DrawUtils.set_color(*self.saturn_color)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, True)
        
        # Detalhes atmosféricos
        DrawUtils.set_color(*self.atmospheric_band_color)
        DrawUtils.ellipse(saturn_x, saturn_y + 0.10 * self.saturn_radius, 
                         0.90 * self.saturn_radius, 0.08 * self.saturn_radius, True)
    
    def step_5_depth_and_clipping(self, saturn_x, saturn_y):
        """ETAPA 5: Profundidade e Clipping"""
        # Primeiro: desenha anéis completos
        DrawUtils.with_pose(saturn_x, saturn_y, rot_deg=-20, scale=(1.0, 0.40))
        DrawUtils.set_color(*self.ring_color_1)
        DrawUtils.ring(0, 0, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius)
        DrawUtils.set_color(*self.ring_color_2)
        DrawUtils.ring(0, 0, 1.35 * self.saturn_radius, 1.55 * self.saturn_radius)
        DrawUtils.end_pose()
        
        # Configura clipping circular para o planeta
        DrawUtils.begin_clip_circle(saturn_x, saturn_y, self.saturn_radius)
        
        # Desenha planeta (que vai "mascarar" os anéis)
        DrawUtils.set_color(*self.saturn_color)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, True)
        
        # Detalhes atmosféricos dentro do clipping
        DrawUtils.set_color(*self.atmospheric_band_color)
        DrawUtils.ellipse(saturn_x, saturn_y + 0.10 * self.saturn_radius, 
                         0.90 * self.saturn_radius, 0.08 * self.saturn_radius, True)
        
        DrawUtils.end_clip()
        
        # Desenha contorno do planeta para mostrar o efeito
        DrawUtils.set_color(0.6, 0.5, 0.4, 0.8)
        glLineWidth(2)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, False)
    
    def step_6_radial_shading(self, saturn_x, saturn_y):
        """ETAPA 6: Sombreamento Radial"""
        # Anéis
        DrawUtils.with_pose(saturn_x, saturn_y, rot_deg=-20, scale=(1.0, 0.40))
        DrawUtils.set_color(*self.ring_color_1)
        DrawUtils.ring(0, 0, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius)
        DrawUtils.set_color(*self.ring_color_2)
        DrawUtils.ring(0, 0, 1.35 * self.saturn_radius, 1.55 * self.saturn_radius)
        DrawUtils.end_pose()
        
        # Planeta base
        DrawUtils.set_color(*self.saturn_color)
        DrawUtils.circle(saturn_x, saturn_y, self.saturn_radius, True)
        
        # Detalhes atmosféricos
        DrawUtils.set_color(*self.atmospheric_band_color)
        DrawUtils.ellipse(saturn_x, saturn_y + 0.10 * self.saturn_radius, 
                         0.90 * self.saturn_radius, 0.08 * self.saturn_radius, True)
        
        # Sombreamento radial (simula iluminação)
        DrawUtils.radial_shade(saturn_x, saturn_y, self.saturn_radius, 0.0, 0.20)
    
    # ================== ETAPAS DOS ANÉIS ==================
    
    def ring_step_1_simple_ring(self, center_x, center_y):
        """ANEL ETAPA 1: Anel Simples"""
        # Desenha apenas um anel básico circular
        DrawUtils.set_color(0.90, 0.86, 0.78, 1.0)
        DrawUtils.ring(center_x, center_y, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius)
        
        # Adiciona contorno para visualizar melhor
        DrawUtils.set_color(0.7, 0.7, 0.7, 1.0)
        glLineWidth(2)
        DrawUtils.ring(center_x, center_y, 1.20 * self.saturn_radius, 1.20 * self.saturn_radius + 0.05, 32)
        DrawUtils.ring(center_x, center_y, 1.80 * self.saturn_radius - 0.05, 1.80 * self.saturn_radius, 32)
    
    def ring_step_2_multiple_rings(self, center_x, center_y):
        """ANEL ETAPA 2: Múltiplos Anéis"""
        # Desenha vários anéis com diferentes tamanhos
        DrawUtils.set_color(0.90, 0.86, 0.78, 0.8)
        DrawUtils.ring(center_x, center_y, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius)
        
        DrawUtils.set_color(0.82, 0.78, 0.72, 0.8)
        DrawUtils.ring(center_x, center_y, 1.35 * self.saturn_radius, 1.55 * self.saturn_radius)
    
        
        # Anel mais interno
        DrawUtils.set_color(0.88, 0.84, 0.76, 0.7)
        DrawUtils.ring(center_x, center_y, 1.10 * self.saturn_radius, 1.15 * self.saturn_radius)
    
    def ring_step_4_rotation_perspective(self, center_x, center_y):
        """ANEL ETAPA 4: Rotação e Perspectiva"""
        # Anéis com transformação 3D
        DrawUtils.with_pose(center_x, center_y, rot_deg=-20, scale=(1.0, 0.40))
        
        # Demonstra wireframe primeiro para mostrar a transformação
        DrawUtils.set_color(1.0, 0.8, 0.0, 0.5)  # Amarelo wireframe
        glLineWidth(1)
        DrawUtils.ring(0, 0, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius, 32)
        
        # Anéis preenchidos
        DrawUtils.set_color(0.90, 0.86, 0.78, 0.8)
        DrawUtils.ring(0, 0, 1.20 * self.saturn_radius, 1.80 * self.saturn_radius)
        
        DrawUtils.set_color(0.82, 0.78, 0.72, 0.8)
        DrawUtils.ring(0, 0, 1.35 * self.saturn_radius, 1.55 * self.saturn_radius)
        
        DrawUtils.end_pose()
    
    
    def draw_stars(self):
        """Removido - não precisamos mais de fundo estrelado"""
        pass
    
    def draw_title(self, title, description):
        """Removido - títulos agora são desenhados diferentemente"""
        pass
    
    def draw_step_info(self):
        """Removido - informações agora são mostradas de forma diferente"""
        pass
    
    def update(self):
        self.time_factor += 0.02
        glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        if key == 27:  # ESC
            sys.exit(0)
        elif key == ord(' '):  # SPACE - poderia adicionar alguma animação
            print("Espaço pressionado - funcionalidade futura")
            glutPostRedisplay()
    
    def reshape(self, w, h):
        glViewport(0, 0, w, h)
        glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_STENCIL)
    glutInitWindowSize(1400, 800)
    glutCreateWindow(b"Saturno - Planeta e Aneis Passo a Passo")
    
    # Habilita stencil buffer para clipping
    glEnable(GL_STENCIL_TEST)
    
    demo = SaturnDemo()
    
    glutDisplayFunc(demo.render)
    glutIdleFunc(demo.update)
    glutKeyboardFunc(demo.handle_keyboard)
    glutReshapeFunc(demo.reshape)
    
    print("\n=== LAYOUT DA DEMONSTRAÇÃO ===")
    print("LINHA SUPERIOR - Criação do Planeta:")
    print("1. Círculo Base")
    print("2. Detalhes Atmosféricos")
    print("3. Planeta + Anéis")
    print("4. Profundidade e Clipping")
    print("5. Sombreamento Radial")
    print("")
    print("LINHA INFERIOR - Criação dos Anéis:")
    print("1. Anel Simples")
    print("2. Múltiplos Anéis") 
    print("3. Rotação e Perspectiva")
    
    glutMainLoop()

if __name__ == '__main__':
    main()