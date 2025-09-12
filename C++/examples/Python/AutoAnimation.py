import math
import time
import random
import sys

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

# Classe para representar um ponto 2D (com sobrecarga de operadores)
class Ponto:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def print(self) -> None:
        print("Ponto (", self.x, ",", self.y, ")")

    def set(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        return Ponto(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Ponto(self.x - other.x, self.y - other.y)

    def __mul__(self, escalar: float):
        return Ponto(self.x * escalar, self.y * escalar)

# Controle de tempo para animação
tempo_antes = time.time()
soma_dt = 0

# Variáveis da câmera (viewport + pan)
left = -1
right = 1
top = 1
bottom = -1
panX = 0
panY = 0

# Posições iniciais dos objetos da cena
pos_tornado = Ponto(-1.2, 0)
pos_telhado = Ponto(0.35, 0.2)
rot_telhado = 0

# Desenha os eixos X e Y no mundo
def desenhaEixos():
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)
    glLineWidth(1)

    glBegin(GL_LINES)
    glVertex2f(left, 0)
    glVertex2f(right, 0)
    glVertex2f(0, bottom)
    glVertex2f(0, top)
    glEnd()

    glPopMatrix()

# Desenha um quadrado com rotação e translação
def desenhaQuadrado(x, y, w, h, r):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(r, 0, 0, 1)

    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(w, 0)
    glVertex2f(w, h)
    glVertex2f(0, h)
    glEnd()

    glPopMatrix()

# Desenha o telhado da casa com rotação
def desenhaTelhado(x, y, r):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(r, 0, 0, 1)

    glBegin(GL_TRIANGLES)
    glColor3f(1, 1, 1)
    glVertex2f(-0.2, 0.1)
    glColor3f(1, 0, 0)
    glVertex2f(0.0, 0.22)
    glColor3f(0, 0, 1)
    glVertex2f(0.2, 0.1)
    glEnd()

    glPopMatrix()

# Desenha o tornado em forma de triângulo
def desenhaTornado(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)

    glBegin(GL_TRIANGLES)
    glColor3f(0.5, 0.5, 0.5)
    glVertex2f(-0.05, 0.8)
    glVertex2f(0.05, 0.8)
    glColor3f(1, 1, 1)
    glVertex2f(0.0, 0.0)
    glEnd()

    glPopMatrix()

# Função de redesenho da cena
def Desenha():
    global left, right, top, bottom, panX, panY

    # Define a projeção 2D com deslocamento (pan)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    # Limpa a tela com cor preta
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    # Desenha o corpo da casa (quadrado fixo)
    glColor3f(1, 0, 0.3)
    desenhaQuadrado(0.2, 0, 0.3, 0.3, 0)

    # Desenha o telhado (pode ser rotacionado e deslocado na animação)
    desenhaTelhado(pos_telhado.x, pos_telhado.y, rot_telhado)

    # Desenha o tornado se aproximando
    desenhaTornado(pos_tornado.x, pos_tornado.y)

    # Desenha os eixos X e Y
    desenhaEixos()

    # Envia os comandos para a GPU
    glFlush()

# Função chamada constantemente no "modo ocioso" (idle) para animar a cena
def Animacao():
    global soma_dt, tempo_antes, pos_tornado, pos_telhado, rot_telhado

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora
    soma_dt += delta_time

    if soma_dt > 1.0 / 30:  # Atualiza ~30 vezes por segundo
        soma_dt = 0

        # Move o tornado horizontalmente
        pos_tornado += Ponto(0.005, 0)

        # Quando o tornado passa da casa, começa a mover o telhado
        if pos_tornado.x > 0.35:
            pos_telhado += Ponto(random.uniform(0.0001, 0.006),
                                 random.uniform(-0.004, 0.004))
            rot_telhado -= random.uniform(0.001, 0.5)

        # Solicita redesenho
        glutPostRedisplay()

# Função para teclado (ESC fecha, espaço não faz nada aqui)
def Teclado(key: chr, x: int, y: int):
    global panX, panY

    if key == 27:  # ESC
        exit(0)

      # Teclas WASD para mover a câmera (pan)
    if key == b'a':
        panX -= 0.01
    if key == b'd':
        panX += 0.01
    if key == b'w':
        panY += 0.01
    if key == b's':
        panY -= 0.01

    glutPostRedisplay()

# Teclas especiais (setas) para mover a câmera
def TeclasEspeciais(key: int, x: int, y: int):
    global panX, panY

    
    #if key == GLUT_KEY_UP:
     #   panY += 0.01
    #if key == GLUT_KEY_DOWN:
     #   panY -= 0.01
    #if key == GLUT_KEY_LEFT:
     #   panX -= 0.01
    #if key == GLUT_KEY_RIGHT:
     #   panX += 0.01

    glutPostRedisplay()

# Inicializa a projeção ortográfica
def Inicializa():
    global left, right, top, bottom

    glMatrixMode(GL_PROJECTION)
    gluOrtho2D(left, right, bottom, top)
    glMatrixMode(GL_MODELVIEW)

# Função principal da aplicação
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"Desenha OpenGL")

    glutDisplayFunc(Desenha)
    glutIdleFunc(Animacao)
    glutKeyboardFunc(Teclado)
    glutSpecialFunc(TeclasEspeciais)

    Inicializa()

    try:
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()