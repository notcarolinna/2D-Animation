import math
import sys

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

# Classe que representa um ponto 2D
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

# Classe que representa um quadrado (ou retângulo)
class Quadrado():
    def __init__(self, x, y, w, h, c=(1, 0, 0)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c  # cor em RGB

# Lista de quadrados iniciais
quadrados = [
    Quadrado(0, 0, 30, 30, (1, 0, 0)), Quadrado(60, 30, 30, 30, (1, 0, 1)),
    Quadrado(40, 80, 30, 30, (0, 1, 0)), Quadrado(90, 70, 30, 30, (0, 1, 1)),
    Quadrado(20, 120, 30, 30, (0, 0, 1)), Quadrado(225, 30, 30, 30, (1, 0, 1)),
    Quadrado(115, 210, 30, 30, (1, 0, 0)), Quadrado(312, 112, 30, 30, (1, 0, 1)),
    Quadrado(50, 260, 30, 30, (0, 1, 0)), Quadrado(444, 444, 30, 30, (0, 1, 1)),
    Quadrado(30, 330, 30, 30, (0, 0, 1)), Quadrado(447, 301, 30, 30, (1, 0, 1))
]
num_quadrado = 0

# Variáveis de controle da câmera (pan e viewport)
left = -1
right = 1
top = 1
bottom = -1
panX = 0
panY = 0

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

# Desenha um quadrado na posição (x, y), com tamanho (w, h)
def desenhaQuadrado(x, y, w, h):
    glPushMatrix()

    # Normaliza as coordenadas (dividido por 1000)
    glTranslatef(x / 1000.0, y / 1000.0, 0.0)

    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(w / 1000.0, 0)
    glVertex2f(w / 1000.0, h / 1000.0)
    glVertex2f(0, h / 1000.0)
    glEnd()

    glPopMatrix()

# Função de redesenho da tela
def Desenha():
    global left, right, top, bottom, panX, panY

    # Define projeção ortográfica 2D com pan (movimento de câmera)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    # Limpa o fundo da tela
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    # Desenha todos os quadrados
    for quadrado in quadrados:
        glColor3f(*quadrado.c)
        desenhaQuadrado(quadrado.x, quadrado.y, quadrado.h, quadrado.w)

    # Desenha os eixos após os quadrados (por cima)
    desenhaEixos()

    # Envia os comandos para a GPU
    glFlush()

# Gerencia teclas comuns (ASCII)
def Teclado(key: chr, x: int, y: int):
    global num_quadrado, panY, panX

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

# Gerencia teclas especiais (setas) para pan da câmera
def TeclasEspeciais(key: int, x: int, y: int):
    global panX, panY

    glutPostRedisplay()

# Inicializa variáveis e configurações de viewport
def Inicializa():
    global left, right, top, bottom, panX, panY

    glMatrixMode(GL_PROJECTION)
    left = -1
    right = 1
    top = 1
    bottom = -1
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

# Função principal que configura GLUT e inicia o loop principal
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"Desenha OpenGL")

    glutDisplayFunc(Desenha)
    glutKeyboardFunc(Teclado)
    glutSpecialFunc(TeclasEspeciais)

    Inicializa()

    try:
        glutMainLoop()
    except SystemExit:
        pass

if __name__ == '__main__':
    main()