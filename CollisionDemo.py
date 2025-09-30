import sys
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from GraphicsUtils import DrawUtils
from Objects import Planet

class CollisionDemo:
    def __init__(self):
        self.viewport = (-10.0, 10.0, -7.5, 7.5)
        
        # Propriedades dos planetas
        self.saturn = {
            'pos': [3.0, 0.0],
            'radius': 1.5,
            'color': (0.9, 0.8, 0.5),
            'name': 'Saturno'
        }
        
        self.jupiter = {
            'pos': [-3.0, 0.0],
            'radius': 2.0,
            'color': (0.43, 0.86, 0.79),
            'name': 'Urano'
        }
        
        # Criar objetos Planet para renderização
        self.saturn_obj = Planet("Saturn", self.saturn['pos'][0], self.saturn['pos'][1], self.saturn['radius'])
        self.uranus_obj = Planet("Uranus", self.jupiter['pos'][0], self.jupiter['pos'][1], self.jupiter['radius'])
        
        # Estado da demonstração
        self.mouse_pos = [0.0, 0.0]
        self.dragging = False
        self.show_debug = True
        self.show_vectors = True
        self.collision_detected = False
        
        # Display movimentável
        self.display_pos = [0.0, -6.5]  # Posição inicial do display
        self.dragging_display = False
        self.display_size = 0.8  # Raio da área clicável do display
        
        # Cálculos de colisão
        self.distance = 0.0
        self.collision_threshold = 0.0
        self.overlap = 0.0
        self.direction_vector = [0.0, 0.0]
        self.normalized_vector = [0.0, 0.0]
        
        # Cálculos matemáticos adicionais
        self.angle_degrees = 0.0
        self.angle_radians = 0.0
        self.velocity_saturn = [0.0, 0.0]
        self.velocity_uranus = [0.0, 0.0]
        self.relative_velocity = [0.0, 0.0]
        self.approach_speed = 0.0
        self.contact_force = 0.0
        
        # Zona segura de 15%
        self.safe_zone_breach = False
        self.safe_distance = 0.0
        
        print("=== DEMONSTRAÇÃO DE COLISÃO ===")
        print("Mouse: Clique e arraste Saturno")
        print("Mouse: Clique e arraste o display de status")
        print("SPACE: Resetar posições")
        print("V: Toggle vetores")
        print("ESC: Sair")
    
    def world_to_screen(self, world_x, world_y):
        """Converte coordenadas do mundo para coordenadas de tela"""
        left, right, bottom, top = self.viewport
        screen_x = (world_x - left) / (right - left)
        screen_y = (world_y - bottom) / (top - bottom)
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x, screen_y):
        """Converte coordenadas de tela para coordenadas do mundo"""
        left, right, bottom, top = self.viewport
        world_x = left + (screen_x / glutGet(GLUT_WINDOW_WIDTH)) * (right - left)
        world_y = bottom + ((glutGet(GLUT_WINDOW_HEIGHT) - screen_y) / glutGet(GLUT_WINDOW_HEIGHT)) * (top - bottom)
        return world_x, world_y
    
    def update_collision_calculations(self):
        """Atualiza todos os cálculos de colisão em tempo real"""
        # 1. CÁLCULO DA DISTÂNCIA ENTRE CENTROS
        dx = self.jupiter['pos'][0] - self.saturn['pos'][0]
        dy = self.jupiter['pos'][1] - self.saturn['pos'][1]
        self.distance = math.sqrt(dx*dx + dy*dy)
        
        # 2. LIMIAR DE COLISÃO (soma dos raios)
        self.collision_threshold = self.saturn['radius'] + self.jupiter['radius']
        
        # 3. DETECÇÃO DE COLISÃO
        self.collision_detected = self.distance < self.collision_threshold
        
        # 4. CÁLCULO DO OVERLAP (sobreposição)
        self.overlap = max(0, self.collision_threshold - self.distance)
        
        # 5. VETOR DE DIREÇÃO (não normalizado)
        self.direction_vector = [dx, dy]
        
        # 6. VETOR NORMALIZADO (direção unitária)
        if self.distance > 0.001:  # Evita divisão por zero
            self.normalized_vector = [dx / self.distance, dy / self.distance]
        else:
            self.normalized_vector = [1.0, 0.0]  # Padrão se muito próximos
            
        # 7. CÁLCULOS ANGULARES
        self.angle_radians = math.atan2(dy, dx)
        self.angle_degrees = math.degrees(self.angle_radians)
        if self.angle_degrees < 0:
            self.angle_degrees += 360  # Converter para 0-360°
            
        # 8. VELOCIDADES SIMULADAS (baseadas na posição do mouse)
        # Para fins de demonstração, simular velocidades baseadas no movimento
        center_x = (self.saturn['pos'][0] + self.jupiter['pos'][0]) / 2
        center_y = (self.saturn['pos'][1] + self.jupiter['pos'][1]) / 2
        
        # Velocidade simulada do Saturno (em direção ao centro)
        self.velocity_saturn = [
            (center_x - self.saturn['pos'][0]) * 0.1,
            (center_y - self.saturn['pos'][1]) * 0.1
        ]
        
        # Velocidade simulada do Urano (em direção oposta)
        self.velocity_uranus = [
            (self.jupiter['pos'][0] - center_x) * 0.1,
            (self.jupiter['pos'][1] - center_y) * 0.1
        ]
        
        # 9. VELOCIDADE RELATIVA
        self.relative_velocity = [
            self.velocity_uranus[0] - self.velocity_saturn[0],
            self.velocity_uranus[1] - self.velocity_saturn[1]
        ]
        
        # 10. VELOCIDADE DE APROXIMAÇÃO
        self.approach_speed = (self.relative_velocity[0] * self.normalized_vector[0] + 
                              self.relative_velocity[1] * self.normalized_vector[1])
        
        # 11. FORÇA DE CONTATO (baseada na zona segura e colisão)
        spring_constant = 100.0  # Constante da mola
        
        if self.collision_detected:
            # Força máxima durante colisão física
            self.contact_force = self.overlap * spring_constant
        elif self.safe_zone_breach:
            # Força proporcional à invasão da zona segura
            safety_invasion = self.safe_distance - self.distance
            safety_zone_thickness = self.safe_distance - self.collision_threshold
            invasion_ratio = safety_invasion / safety_zone_thickness
            self.contact_force = invasion_ratio * spring_constant * 0.5  # 50% da força máxima
        else:
            self.contact_force = 0.0
        
        # 12. ZONA SEGURA DE 15%
        saturn_safe_radius = self.saturn['radius'] * 1.15
        uranus_safe_radius = self.jupiter['radius'] * 1.15
        self.safe_distance = saturn_safe_radius + uranus_safe_radius
        self.safe_zone_breach = self.distance <= self.safe_distance
    
    def render(self):
        # Configuração da projeção
        left, right, bottom, top = self.viewport
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(left, right, bottom, top)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Limpar tela com fundo branco
        glClearColor(1.0, 1.0, 1.0, 1.0)  # Fundo branco
        glClear(GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)  # Limpar stencil também
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Atualizar cálculos
        self.update_collision_calculations()
        
        # Desenhar elementos
        self.draw_background_grid()
        self.draw_collision_zones()
        self.draw_planets()
        self.draw_connection_line()
        
        if self.show_vectors:
            self.draw_vectors()
        
        self.draw_collision_status()
        
        glDisable(GL_BLEND)
        glFlush()
    
    def draw_background_grid(self):
        """Fundo limpo sem grade"""
        pass  # Removido grid e cruz para visual mais limpo
    
    def draw_collision_zones(self):
        """Desenha zonas seguras de 15% ao redor dos planetas"""
        # Zona segura do Saturno (15% maior que o raio)
        saturn_safe_radius = self.saturn['radius'] * 1.15
        DrawUtils.set_color(0.9, 0.8, 0.5, 0.12)  # Amarelo transparente
        DrawUtils.circle(self.saturn['pos'][0], self.saturn['pos'][1], 
                        saturn_safe_radius, True, 64)
        
        # Contorno da zona segura do Saturno
        DrawUtils.set_color(0.9, 0.8, 0.5, 0.6)  # Amarelo mais visível
        glLineWidth(2)
        DrawUtils.circle(self.saturn['pos'][0], self.saturn['pos'][1], 
                        saturn_safe_radius, False, 64)
        
        # Zona segura do Urano (15% maior que o raio)
        uranus_safe_radius = self.jupiter['radius'] * 1.15
        DrawUtils.set_color(0.43, 0.86, 0.79, 0.12)  # Azul-turquesa transparente
        DrawUtils.circle(self.jupiter['pos'][0], self.jupiter['pos'][1], 
                        uranus_safe_radius, True, 64)
        
        # Contorno da zona segura do Urano
        DrawUtils.set_color(0.43, 0.86, 0.79, 0.6)  # Azul-turquesa mais visível
        glLineWidth(2)
        DrawUtils.circle(self.jupiter['pos'][0], self.jupiter['pos'][1], 
                        uranus_safe_radius, False, 64)
        
        # Linha pontilhada conectando as bordas das zonas seguras (opcional)
        self.draw_safe_zone_connection()
    
    def draw_safe_zone_connection(self):
        """Desenha linha pontilhada entre as zonas seguras"""
        saturn_safe_radius = self.saturn['radius'] * 1.15
        uranus_safe_radius = self.jupiter['radius'] * 1.15
        
        # Distância entre zonas seguras
        safe_distance = saturn_safe_radius + uranus_safe_radius
        
        # Cor da linha baseada na proximidade das zonas
        if self.distance <= safe_distance:
            # Dentro da zona de risco - linha vermelha
            DrawUtils.set_color(1.0, 0.4, 0.4, 0.8)
            line_width = 3
        else:
            # Fora da zona de risco - linha verde
            DrawUtils.set_color(0.4, 1.0, 0.4, 0.6)
            line_width = 2
        
        # Desenhar linha pontilhada
        saturn_x, saturn_y = self.saturn['pos']
        uranus_x, uranus_y = self.jupiter['pos']
        
        # Calcular pontos nas bordas das zonas seguras
        if self.distance > 0.001:
            # Ponto na borda da zona segura do Saturno
            saturn_edge_x = saturn_x + self.normalized_vector[0] * saturn_safe_radius
            saturn_edge_y = saturn_y + self.normalized_vector[1] * saturn_safe_radius
            
            # Ponto na borda da zona segura do Urano
            uranus_edge_x = uranus_x - self.normalized_vector[0] * uranus_safe_radius
            uranus_edge_y = uranus_y - self.normalized_vector[1] * uranus_safe_radius
            
            # Linha pontilhada entre as bordas
            self.draw_dashed_line(saturn_edge_x, saturn_edge_y, 
                                uranus_edge_x, uranus_edge_y, line_width)
    
    def draw_dashed_line(self, x1, y1, x2, y2, width):
        """Desenha uma linha pontilhada"""
        glLineWidth(width)
        
        # Calcular número de segmentos para a linha pontilhada
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        num_segments = int(distance * 8)  # 8 segmentos por unidade
        
        if num_segments < 2:
            return
        
        for i in range(0, num_segments, 2):  # Desenhar apenas segmentos pares (pontilhado)
            t1 = i / num_segments
            t2 = min((i + 1) / num_segments, 1.0)
            
            seg_x1 = x1 + (x2 - x1) * t1
            seg_y1 = y1 + (y2 - y1) * t1
            seg_x2 = x1 + (x2 - x1) * t2
            seg_y2 = y1 + (y2 - y1) * t2
            
            DrawUtils.line(seg_x1, seg_y1, seg_x2, seg_y2, width)
    
    def draw_planets(self):
        """Desenha os planetas usando a classe Planet do Objects.py"""
        # Atualizar posições dos objetos Planet
        self.saturn_obj.x = self.saturn['pos'][0]
        self.saturn_obj.y = self.saturn['pos'][1]
        self.uranus_obj.x = self.jupiter['pos'][0]
        self.uranus_obj.y = self.jupiter['pos'][1]
        
        # Atualizar life_time para animações
        import time
        current_time = time.time()
        self.saturn_obj.life_time = current_time
        self.uranus_obj.life_time = current_time
        
        # Desenhar os planetas
        self.saturn_obj.draw()
        self.uranus_obj.draw()
    
    def draw_saturn_advanced(self):
        """Desenha Saturno com clipping funcional e gradientes"""
        saturn_x, saturn_y = self.saturn['pos']
        saturn_r = self.saturn['radius'] * 0.7
        
        # 1. ANÉIS DE SATURNO (ATRÁS DO PLANETA)
        DrawUtils.with_pose(saturn_x, saturn_y, rot_deg=-15, scale=(1.0, 0.35))
        
        # Anel externo principal
        DrawUtils.set_color(0.88, 0.82, 0.70, 0.8)
        DrawUtils.ring(0, 0, saturn_r * 1.6, saturn_r * 2.0)
        
        # Anel médio
        DrawUtils.set_color(0.92, 0.87, 0.75, 0.85)
        DrawUtils.ring(0, 0, saturn_r * 1.2, saturn_r * 1.55)
        
        # Anel interno (mais opaco)
        DrawUtils.set_color(0.85, 0.80, 0.68, 0.9)
        DrawUtils.ring(0, 0, saturn_r * 1.05, saturn_r * 1.15)
        
        # Divisão de Cassini (gap escuro entre anéis)
        DrawUtils.set_color(0.3, 0.3, 0.3, 0.6)
        DrawUtils.ring(0, 0, saturn_r * 1.55, saturn_r * 1.6)
        
        DrawUtils.end_pose()
        
        # 2. CONFIGURAR CLIPPING CIRCULAR PARA O PLANETA
        DrawUtils.begin_clip_circle(saturn_x, saturn_y, saturn_r)
        
        # 3. PLANETA SATURNO BASE
        DrawUtils.set_color(0.98, 0.94, 0.78, 1.0)
        DrawUtils.circle(saturn_x, saturn_y, saturn_r, True, 128)
        
        # 4. GRADIENTE RADIAL DE PROFUNDIDADE
        self.draw_sphere_gradient(saturn_x, saturn_y, saturn_r, 
                                (0.95, 0.90, 0.70), (0.85, 0.80, 0.60))
        
        # 4.5. GRADIENTE RADIAL ADICIONAL PARA MAIS PROFUNDIDADE
        self.draw_radial_depth(saturn_x, saturn_y, saturn_r, 0.3)
        
        # 5. BANDAS ATMOSFÉRICAS
        # Banda equatorial principal
        DrawUtils.set_color(0.90, 0.84, 0.68, 0.7)
        DrawUtils.ellipse(saturn_x, saturn_y + saturn_r * 0.2, 
                         saturn_r * 0.92, saturn_r * 0.12, True)
        
        # Banda norte
        DrawUtils.set_color(0.88, 0.82, 0.66, 0.6)
        DrawUtils.ellipse(saturn_x, saturn_y + saturn_r * 0.5, 
                         saturn_r * 0.85, saturn_r * 0.08, True)
        
        # Banda sul
        DrawUtils.set_color(0.86, 0.80, 0.64, 0.6)
        DrawUtils.ellipse(saturn_x, saturn_y - saturn_r * 0.3, 
                         saturn_r * 0.88, saturn_r * 0.10, True)
        
        # 6. TEMPESTADE HEXAGONAL NO POLO NORTE
        DrawUtils.set_color(0.82, 0.76, 0.58, 0.8)
        self.draw_hexagon(saturn_x, saturn_y + saturn_r * 0.75, saturn_r * 0.15)
        
        # 7. DETALHES DE NUVENS E TEMPESTADES
        # Pequenas tempestades ovais
        DrawUtils.set_color(0.83, 0.77, 0.61, 0.5)
        DrawUtils.ellipse(saturn_x + saturn_r * 0.3, saturn_y - saturn_r * 0.1, 
                         saturn_r * 0.08, saturn_r * 0.05, True)
        DrawUtils.ellipse(saturn_x - saturn_r * 0.25, saturn_y + saturn_r * 0.35, 
                         saturn_r * 0.06, saturn_r * 0.04, True)
        
        # 8. SOMBREAMENTO HEMISFÉRICO (simulando iluminação solar)
        self.draw_hemisphere_shadow(saturn_x, saturn_y, saturn_r, 0.3)
        
        DrawUtils.end_clip()
        
        # 9. ANÉIS DA FRENTE (parte que fica na frente do planeta)
        DrawUtils.with_pose(saturn_x, saturn_y, rot_deg=-15, scale=(1.0, 0.35))
        
        # Usar clipping invertido para mostrar só a parte da frente
        self.draw_rings_front_part(saturn_r)
        
        DrawUtils.end_pose()
        
        # 10. CONTORNO FINAL
        if self.collision_detected:
            DrawUtils.set_color(1.0, 0.2, 0.2, 1.0)
        else:
            DrawUtils.set_color(0.6, 0.5, 0.2, 0.8)
        glLineWidth(2)
        DrawUtils.circle(saturn_x, saturn_y, saturn_r, False, 128)
    
    def draw_jupiter_advanced(self):
        """Desenha Júpiter com gradientes e detalhes atmosféricos"""
        jupiter_x, jupiter_y = self.jupiter['pos']
        jupiter_r = self.jupiter['radius'] * 0.8
        
        # 1. CONFIGURAR CLIPPING CIRCULAR
        DrawUtils.begin_clip_circle(jupiter_x, jupiter_y, jupiter_r)
        
        # 2. PLANETA JÚPITER BASE
        DrawUtils.set_color(0.88, 0.68, 0.38, 1.0)
        DrawUtils.circle(jupiter_x, jupiter_y, jupiter_r, True, 128)
        
        # 3. GRADIENTE RADIAL DE PROFUNDIDADE
        self.draw_sphere_gradient(jupiter_x, jupiter_y, jupiter_r,
                                (0.85, 0.65, 0.35), (0.65, 0.45, 0.25))
        
        # 3.5. GRADIENTE RADIAL ADICIONAL PARA MAIS PROFUNDIDADE
        self.draw_radial_depth(jupiter_x, jupiter_y, jupiter_r, 0.4)
        
        # 4. BANDAS ATMOSFÉRICAS COMPLEXAS
        # Banda equatorial escura
        DrawUtils.set_color(0.70, 0.50, 0.22, 0.9)
        DrawUtils.ellipse(jupiter_x, jupiter_y + jupiter_r * 0.1, 
                         jupiter_r * 0.95, jupiter_r * 0.18, True)
        
        # Zona tropical norte (clara)
        DrawUtils.set_color(0.92, 0.72, 0.42, 0.7)
        DrawUtils.ellipse(jupiter_x, jupiter_y + jupiter_r * 0.45, 
                         jupiter_r * 0.90, jupiter_r * 0.15, True)
        
        # Banda temperada norte (escura)
        DrawUtils.set_color(0.68, 0.48, 0.20, 0.8)
        DrawUtils.ellipse(jupiter_x, jupiter_y + jupiter_r * 0.7, 
                         jupiter_r * 0.85, jupiter_r * 0.12, True)
        
        # Zona tropical sul (clara)
        DrawUtils.set_color(0.90, 0.70, 0.40, 0.7)
        DrawUtils.ellipse(jupiter_x, jupiter_y - jupiter_r * 0.25, 
                         jupiter_r * 0.92, jupiter_r * 0.14, True)
        
        # Banda temperada sul (escura)
        DrawUtils.set_color(0.66, 0.46, 0.18, 0.8)
        DrawUtils.ellipse(jupiter_x, jupiter_y - jupiter_r * 0.55, 
                         jupiter_r * 0.87, jupiter_r * 0.13, True)
        
        # 5. GRANDE MANCHA VERMELHA (mais realista)
        DrawUtils.set_color(0.95, 0.45, 0.25, 0.95)
        self.draw_great_red_spot(jupiter_x + jupiter_r * 0.25, jupiter_y - jupiter_r * 0.15, 
                               jupiter_r * 0.28, jupiter_r * 0.18)
        
        # 6. PEQUENAS TEMPESTADES E ÓVAIS
        # Óvais brancos (anticiclones)
        DrawUtils.set_color(0.98, 0.88, 0.68, 0.8)
        DrawUtils.ellipse(jupiter_x - jupiter_r * 0.4, jupiter_y + jupiter_r * 0.2, 
                         jupiter_r * 0.12, jupiter_r * 0.08, True)
        DrawUtils.ellipse(jupiter_x + jupiter_r * 0.45, jupiter_y + jupiter_r * 0.6, 
                         jupiter_r * 0.10, jupiter_r * 0.07, True)
        
        # Óvais marrons (ciclones)
        DrawUtils.set_color(0.58, 0.38, 0.15, 0.7)
        DrawUtils.ellipse(jupiter_x - jupiter_r * 0.3, jupiter_y - jupiter_r * 0.4, 
                         jupiter_r * 0.09, jupiter_r * 0.06, True)
        DrawUtils.ellipse(jupiter_x + jupiter_r * 0.15, jupiter_y + jupiter_r * 0.3, 
                         jupiter_r * 0.07, jupiter_r * 0.05, True)
        
        # 7. SOMBREAMENTO HEMISFÉRICO
        self.draw_hemisphere_shadow(jupiter_x, jupiter_y, jupiter_r, 0.4)
        
        DrawUtils.end_clip()
        
        # 8. CONTORNO FINAL
        if self.collision_detected:
            DrawUtils.set_color(1.0, 0.2, 0.2, 1.0)
        else:
            DrawUtils.set_color(0.4, 0.3, 0.1, 0.8)
        glLineWidth(2)
        DrawUtils.circle(jupiter_x, jupiter_y, jupiter_r, False, 128)
    
    def draw_sphere_gradient(self, cx, cy, radius, light_color, dark_color):
        """Desenha gradiente radial central e suave para simular forma esférica"""
        steps = 40  # Mais steps para gradiente ainda mais suave
        
        # Gradiente que ocupa TODO o raio do planeta
        for i in range(steps):
            t = i / (steps - 1)  # Normalizado 0 a 1
            
            # Função suave para transição (ease-out)
            smooth_t = 1 - math.pow(1 - t, 3)  # Cúbica para mais suavidade
            
            # Interpolação suave das cores
            r = light_color[0] * (1 - smooth_t) + dark_color[0] * smooth_t
            g = light_color[1] * (1 - smooth_t) + dark_color[1] * smooth_t
            b = light_color[2] * (1 - smooth_t) + dark_color[2] * smooth_t
            
            # Alpha que garante visibilidade em todo o raio
            alpha = 0.18 * (1 - t * t * 0.8)  # Mais visível, decaimento mais lento
            
            # Raio que vai de 0 até ALÉM do raio do planeta
            current_radius = radius * (t * 1.1 + 0.02)  # 110% do raio para cobertura total
            
            DrawUtils.set_color(r, g, b, alpha)
            DrawUtils.circle(cx, cy, current_radius, True, 64)
        
        # Brilho central estendido
        highlight_steps = 15
        for i in range(highlight_steps):
            t = i / (highlight_steps - 1)
            
            # Brilho que se estende mais pelo planeta
            highlight_alpha = 0.12 * (1 - t * t)  # Mais visível
            highlight_radius = radius * (t * 0.8)  # Brilho ocupa 80% do raio
            
            # Cor mais clara para o brilho
            highlight_r = min(1.0, light_color[0] * 1.15)
            highlight_g = min(1.0, light_color[1] * 1.15)
            highlight_b = min(1.0, light_color[2] * 1.15)
            
            DrawUtils.set_color(highlight_r, highlight_g, highlight_b, highlight_alpha)
            DrawUtils.circle(cx, cy, highlight_radius, True, 64)
        
        # Camada final que garante cobertura até além da borda
        final_steps = 10
        for i in range(final_steps):
            t = 0.8 + (i / (final_steps - 1)) * 0.3  # De 80% até 110% do raio
            
            # Cor da borda com transição suave
            edge_smooth = (t - 0.8) / 0.3  # Normaliza para 0-1 na borda estendida
            r = light_color[0] * (1 - edge_smooth) + dark_color[0] * edge_smooth
            g = light_color[1] * (1 - edge_smooth) + dark_color[1] * edge_smooth
            b = light_color[2] * (1 - edge_smooth) + dark_color[2] * edge_smooth
            
            alpha = 0.1 * (1 - edge_smooth)  # Diminui na borda
            current_radius = radius * t
            
            DrawUtils.set_color(r, g, b, alpha)
            DrawUtils.circle(cx, cy, current_radius, True, 64)
            DrawUtils.circle(cx, cy, highlight_radius, True, 64)
            
            DrawUtils.set_color(highlight_r, highlight_g, highlight_b, highlight_alpha)
            DrawUtils.circle(cx, cy, highlight_radius, True, 64)
    
    def draw_radial_depth(self, cx, cy, radius, intensity):
        """Adiciona gradiente radial suave que ocupa toda a superfície"""
        steps = 50  # Muito mais steps para suavidade máxima
        
        for i in range(steps):
            t = i / (steps - 1)  # 0 a 1
            
            # Função de easing muito suave - combinação de funções
            ease1 = math.sin(t * math.pi / 2)  # Sine easing
            ease2 = 1 - math.pow(1 - t, 3)     # Cubic ease-out
            ease_t = (ease1 + ease2) / 2       # Média das duas para ultra suavidade
            
            # Alpha muito sutil que decresce do centro para a borda
            alpha = intensity * 0.04 * math.pow(1 - t, 2)  # Quadrática invertida, ainda mais sutil
            
            # Raio que cresce do centro até além da borda completa
            current_radius = radius * (t * 1.1 + 0.02)  # 110% do raio para cobertura total
            
            # Cor muito sutil para profundidade
            gray_value = 0.6 - (t * 0.3)  # Varia de 0.6 a 0.3 (mais claro no centro)
            DrawUtils.set_color(gray_value, gray_value, gray_value, alpha)
            DrawUtils.circle(cx, cy, current_radius, True, 64)
        
        # Camada adicional para garantir suavidade na borda estendida
        edge_steps = 20
        for i in range(edge_steps):
            t = 0.8 + (i / (edge_steps - 1)) * 0.3  # De 80% a 110% do raio
            
            # Alpha muito baixo para transição imperceptível na borda
            alpha = intensity * 0.02 * (1 - ((t - 0.8) / 0.3))
            current_radius = radius * t
            
            DrawUtils.set_color(0.4, 0.4, 0.4, alpha)
            DrawUtils.circle(cx, cy, current_radius, True, 64)
    
    def draw_hemisphere_shadow(self, cx, cy, radius, intensity):
        """Desenha sombra hemisférica ultra suave para simular iluminação direcional"""
        steps = 40  # Mais steps para suavidade
        
        for i in range(steps):
            t = i / (steps - 1)
            
            # Função de easing dupla para máxima suavidade
            smooth_t1 = t * t * (3 - 2 * t)  # Smoothstep
            smooth_t2 = math.sin(t * math.pi / 2)  # Sine easing
            smooth_t = (smooth_t1 + smooth_t2) / 2  # Média para ultra suavidade
            
            # Alpha extremamente sutil
            alpha = intensity * 0.08 * (1 - smooth_t) * (1 - t * 0.5)  # Decaimento duplo
            
            # Raio que cresce suavemente
            shadow_radius = radius * (0.2 + smooth_t * 0.9)  # Cobertura de 20% a 110%
            
            # Posição da sombra muito sutil
            shadow_x = cx + radius * 0.08 * (1 + smooth_t * 0.2)
            shadow_y = cy - radius * 0.04 * smooth_t
            
            DrawUtils.set_color(0.0, 0.0, 0.0, alpha)
            DrawUtils.circle(shadow_x, shadow_y, shadow_radius, True, 64)
        
        # Sombra central extremamente sutil
        for i in range(15):
            t = i / 14
            alpha = intensity * 0.05 * (1 - t * t)  # Muito mais sutil
            core_radius = radius * (0.1 + t * 0.2)  # Área menor
            
            DrawUtils.set_color(0.0, 0.0, 0.0, alpha)
            DrawUtils.circle(cx + radius * 0.12, cy - radius * 0.02, core_radius, True, 48)
    
    def draw_hexagon(self, cx, cy, radius):
        """Desenha hexágono para a tempestade polar de Saturno"""
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for i in range(7):  # 6 lados + fechamento
            angle = (i * math.pi) / 3.0
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
    
    def draw_great_red_spot(self, cx, cy, width, height):
        """Desenha a Grande Mancha Vermelha de Júpiter com detalhes"""
        # Mancha principal
        DrawUtils.ellipse(cx, cy, width, height, True)
        
        # Centro mais claro
        DrawUtils.set_color(1.0, 0.6, 0.4, 0.7)
        DrawUtils.ellipse(cx - width * 0.1, cy, width * 0.6, height * 0.7, True)
        
        # Borda mais escura
        DrawUtils.set_color(0.7, 0.2, 0.1, 0.8)
        glLineWidth(2)
        DrawUtils.ellipse(cx, cy, width, height, False)
    
    def draw_rings_front_part(self, saturn_r):
        """Desenha a parte dos anéis que fica na frente do planeta"""
        # Esta função simula os anéis passando na frente do planeta
        # Desenhamos apenas as partes que estariam visíveis
        
        # Parte superior dos anéis (na frente)
        glBegin(GL_TRIANGLE_STRIP)
        for i in range(180, 361):  # Metade superior
            angle = math.radians(i)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            
            # Anel externo
            DrawUtils.set_color(0.88, 0.82, 0.70, 0.6)
            glVertex2f(saturn_r * 1.6 * cos_a, saturn_r * 1.6 * sin_a)
            glVertex2f(saturn_r * 2.0 * cos_a, saturn_r * 2.0 * sin_a)
        glEnd()
        
        # Anel interno na frente
        glBegin(GL_TRIANGLE_STRIP)
        for i in range(180, 361):
            angle = math.radians(i)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            
            DrawUtils.set_color(0.85, 0.80, 0.68, 0.7)
            glVertex2f(saturn_r * 1.05 * cos_a, saturn_r * 1.05 * sin_a)
            glVertex2f(saturn_r * 1.15 * cos_a, saturn_r * 1.15 * sin_a)
        glEnd()
    
    def draw_connection_line(self):
        """Linha de conexão removida para interface minimalista"""
        pass
    
    def draw_vectors(self):
        """Desenha setas simples e minimalistas nos planetas"""
        if self.distance < 0.001:
            return

        saturn_x, saturn_y = self.saturn['pos']
        uranus_x, uranus_y = self.jupiter['pos']

        if self.safe_zone_breach:
            # Calcular intensidade da força baseada na proximidade
            if self.collision_detected:
                force_scale = min(self.overlap * 2.5, 2.0)
                color_saturn = (1.0, 0.2, 0.2)
                color_uranus = (1.0, 0.2, 0.2)
                width = 5
            else:
                safety_invasion = (self.safe_distance - self.distance) / (self.safe_distance - self.collision_threshold)
                force_scale = min(safety_invasion * 1.5, 1.8)
                color_saturn = (1.0, 0.6, 0.1)
                color_uranus = (0.2, 0.8, 1.0)
                width = 4

            # Saturno: seta reta para fora
            self.draw_straight_arrow(
                start=(saturn_x, saturn_y),
                direction=(-self.normalized_vector[0], -self.normalized_vector[1]),
                length=force_scale,
                color=color_saturn,
                width=width,
                head_size=0.25
            )
            # Urano: seta reta para fora
            self.draw_straight_arrow(
                start=(uranus_x, uranus_y),
                direction=(self.normalized_vector[0], self.normalized_vector[1]),
                length=force_scale,
                color=color_uranus,
                width=width,
                head_size=0.25
            )
        else:
            DrawUtils.set_color(0.3, 0.7, 0.3, 0.2)
            glLineWidth(1)
            DrawUtils.line(saturn_x, saturn_y, uranus_x, uranus_y, 1.0)
    def draw_straight_arrow(self, start, direction, length, color, width, head_size):
        """Desenha uma seta reta, tradicional, com corpo afilado e cabeça triangular"""
        import math
        x0, y0 = start
        dx, dy = direction
        x1 = x0 + dx * length
        y1 = y0 + dy * length

        # Glow externo
        for i in range(3, 0, -1):
            alpha = 0.10 * i
            DrawUtils.set_color(*color, alpha)
            glLineWidth(width + i * 2)
            DrawUtils.line(x0, y0, x1, y1, width + i * 2)

        # Corpo principal, afilado
        for j in range(width, 0, -1):
            t = j / width
            DrawUtils.set_color(*color, 0.5 + 0.5 * t)
            glLineWidth(j)
            DrawUtils.line(x0, y0, x1, y1, j)

        # Cabeça da seta
        angle = math.atan2(y1 - y0, x1 - x0)
        self.draw_arrow_head(x1, y1, angle, head_size, color)
    

    
    def draw_arrow_head(self, x, y, angle, size, color):
        """Desenha uma ponta de seta"""
        DrawUtils.set_color(*color, 1.0)
        glBegin(GL_TRIANGLES)
        
        # Ponta da seta
        glVertex2f(x, y)
        
        # Lados da seta
        back_x = x - size * math.cos(angle)
        back_y = y - size * math.sin(angle)
        
        side1_x = back_x + size * 0.3 * math.cos(angle + math.pi/2)
        side1_y = back_y + size * 0.3 * math.sin(angle + math.pi/2)
        
        side2_x = back_x + size * 0.3 * math.cos(angle - math.pi/2)
        side2_y = back_y + size * 0.3 * math.sin(angle - math.pi/2)
        
        glVertex2f(side1_x, side1_y)
        glVertex2f(side2_x, side2_y)
        glEnd()
    

    
    def draw_collision_status(self):
        """Interface minimalista com indicadores de zona segura movimentável"""
        center_x, center_y = self.display_pos
        
        # Fundo do display (área clicável)
        if self.dragging_display:
            DrawUtils.set_color(0.2, 0.2, 0.3, 0.6)
        else:
            DrawUtils.set_color(0.1, 0.1, 0.2, 0.4)
        DrawUtils.circle(center_x, center_y, self.display_size, True, 32)
        
        if self.collision_detected:
            # Círculo vermelho pulsante para colisão real
            import time
            pulse = math.sin(time.time() * 10.0) * 0.08 + 0.2
            DrawUtils.set_color(1.0, 0.1, 0.1, 0.9)
            DrawUtils.circle(center_x, center_y, pulse, True, 16)
            
            # Texto visual "COLISÃO" com múltiplos círculos
            for i in range(3):
                offset_x = (i - 1) * 0.6
                DrawUtils.set_color(1.0, 0.2, 0.2, 0.7 - i * 0.1)
                DrawUtils.circle(center_x + offset_x, center_y + 0.8, 0.1, True, 12)
        
        elif self.safe_zone_breach:
            # Círculo laranja para violação da zona segura
            import time
            pulse = math.sin(time.time() * 6.0) * 0.03 + 0.15
            DrawUtils.set_color(1.0, 0.6, 0.1, 0.8)
            DrawUtils.circle(center_x, center_y, pulse, True, 16)
            
            # Anel de alerta ao redor
            DrawUtils.set_color(1.0, 0.6, 0.1, 0.6)
            glLineWidth(3)
            DrawUtils.circle(center_x, center_y, pulse + 0.1, False, 16)
            
            # Texto visual "ZONA PERIGOSA"
            for i in range(5):
                offset_x = (i - 2) * 0.3
                DrawUtils.set_color(1.0, 0.6, 0.1, 0.6 - i * 0.05)
                DrawUtils.circle(center_x + offset_x, center_y + 0.8, 0.08, True, 8)
        
        else:
            # Círculo verde para sistema seguro
            DrawUtils.set_color(0.2, 1.0, 0.2, 0.7)
            DrawUtils.circle(center_x, center_y, 0.12, True, 12)
            
            # Check mark visual
            DrawUtils.set_color(1.0, 1.0, 1.0, 1.0)
            glLineWidth(3)
            DrawUtils.line(center_x - 0.06, center_y - 0.02, center_x - 0.02, center_y + 0.04, 3.0)
            DrawUtils.line(center_x - 0.02, center_y + 0.04, center_x + 0.06, center_y - 0.04, 3.0)
        
        # Informações adicionais discretas
        info_y = center_y - 1.2
        
        # Distância atual (barra proporcional)
        max_bar_width = 3.0
        distance_bar = min(self.distance * 0.8, max_bar_width)
        
        # Cor da barra baseada no status
        if self.collision_detected:
            DrawUtils.set_color(1.0, 0.2, 0.2, 0.8)
        elif self.safe_zone_breach:
            DrawUtils.set_color(1.0, 0.6, 0.1, 0.8)
        else:
            DrawUtils.set_color(0.2, 1.0, 0.2, 0.8)
        
        glLineWidth(6)
        DrawUtils.line(center_x - distance_bar/2, info_y, center_x + distance_bar/2, info_y, 6.0)
        
        # Marcador da zona segura
        safe_zone_bar = min(self.safe_distance * 0.8, max_bar_width)
        DrawUtils.set_color(1.0, 1.0, 0.3, 0.5)
        glLineWidth(2)
        DrawUtils.line(center_x - safe_zone_bar/2, info_y - 0.15, center_x + safe_zone_bar/2, info_y - 0.15, 2.0)
        
        # Marcador da zona de colisão
        collision_bar = min(self.collision_threshold * 0.8, max_bar_width)
        DrawUtils.set_color(1.0, 0.4, 0.4, 0.7)
        glLineWidth(2)
        DrawUtils.line(center_x - collision_bar/2, info_y - 0.3, center_x + collision_bar/2, info_y - 0.3, 2.0)
        
        # Indicador de que é arrastável (pequenos pontos nas bordas)
        if not self.dragging_display:
            DrawUtils.set_color(0.7, 0.7, 0.7, 0.3)
            glPointSize(3)
            glBegin(GL_POINTS)
            for i in range(8):
                angle = i * math.pi / 4
                px = center_x + (self.display_size - 0.1) * math.cos(angle)
                py = center_y + (self.display_size - 0.1) * math.sin(angle)
                glVertex2f(px, py)
            glEnd()
    
    def is_point_in_display(self, world_x, world_y):
        """Verifica se um ponto está dentro da área clicável do display"""
        dx = world_x - self.display_pos[0]
        dy = world_y - self.display_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        return distance <= self.display_size
    

    
    def handle_mouse(self, button, state, x, y):
        """Manipula eventos do mouse"""
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                world_x, world_y = self.screen_to_world(x, y)
                
                # Verificar se clicou no display
                if self.is_point_in_display(world_x, world_y):
                    self.dragging_display = True
                    self.dragging = False
                else:
                    # Clicou fora do display, mover Saturno
                    self.dragging = True
                    self.dragging_display = False
                    self.saturn['pos'] = [world_x, world_y]
            else:
                self.dragging = False
                self.dragging_display = False
    
    def handle_mouse_motion(self, x, y):
        """Manipula movimento do mouse"""
        world_x, world_y = self.screen_to_world(x, y)
        
        if self.dragging_display:
            # Arrastar o display
            self.display_pos = [world_x, world_y]
            glutPostRedisplay()
        elif self.dragging:
            # Arrastar o Saturno
            self.saturn['pos'] = [world_x, world_y]
            glutPostRedisplay()
    
    def handle_keyboard(self, key, x, y):
        """Manipula eventos do teclado"""
        if key == 27:  # ESC
            sys.exit(0)
        elif key == ord(' '):  # SPACE - resetar
            self.saturn['pos'] = [3.0, 0.0]
            self.jupiter['pos'] = [-3.0, 0.0]  # Agora é Urano
            glutPostRedisplay()
        elif key == ord('v') or key == ord('V'):  # Toggle vetores
            self.show_vectors = not self.show_vectors
            glutPostRedisplay()
    
    def reshape(self, w, h):
        """Redimensiona a janela"""
        glViewport(0, 0, w, h)
        glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_STENCIL)  # Adicionado STENCIL
    glutInitWindowSize(1200, 900)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Demonstracao de Colisao - Saturno vs Urano")
    
    demo = CollisionDemo()
    
    glutDisplayFunc(demo.render)
    glutKeyboardFunc(demo.handle_keyboard)
    glutMouseFunc(demo.handle_mouse)
    glutMotionFunc(demo.handle_mouse_motion)
    glutReshapeFunc(demo.reshape)
    
    print("\n=== CONCEITOS MATEMÁTICOS DEMONSTRADOS ===")
    print("1. DISTÂNCIA EUCLIDIANA: d = √[(x₂-x₁)² + (y₂-y₁)²]")
    print("2. ZONA SEGURA: Repulsão começa a 15% além do raio")
    print("3. DETECÇÃO DE COLISÃO: d < (r₁ + r₂)")
    print("4. VETOR DIREÇÃO: (dx, dy) = (x₂-x₁, y₂-y₁)")
    print("5. NORMALIZAÇÃO: (dx/d, dy/d)")
    print("6. OVERLAP: max(0, (r₁ + r₂) - d)")
    print("7. FORÇA DE REPULSÃO: F = invasion_ratio × k")
    print("\nInteraja com a demonstração para ver os cálculos!")
    print("LARANJA: Zona segura violada - repulsão preventiva")
    print("VERMELHO: Colisão física - repulsão máxima")
    
    glutMainLoop()

if __name__ == '__main__':
    main()