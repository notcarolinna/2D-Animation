import math

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

class Ponto:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def __add__(self, other): return Ponto(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Ponto(self.x - other.x, self.y - other.y)
    def __mul__(self, escalar: float): return Ponto(self.x * escalar, self.y * escalar)

class Quadrado():
    def __init__(self, w, h, cor=(1,1,1)):
        self.pos = Ponto(0, 0)
        self.w = w
        self.h = h
        self.c = cor

quadrados = [Quadrado(0.1, 0.1)]
num_quadrado = 0

left = -1.0
right = 1.0
top = 1.0
bottom = -1.0
panX = 0.0
panY = 0.0

SHOW_GRID = True
SHOW_BBOX = True
MARGIN_PCT = 0.10

def set_ortho(l, r, b, t):
    global left, right, bottom, top
    left, right, bottom, top = l, r, b, t
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

def reset_ortho():
    set_ortho(-1.0, 1.0, -1.0, 1.0)

def bbox_of_squares():
    if not quadrados:
        return (-1, -1, 1, 1)
    xmin = min(q.pos.x for q in quadrados)
    ymin = min(q.pos.y for q in quadrados)
    xmax = max(q.pos.x + q.w for q in quadrados)
    ymax = max(q.pos.y + q.h for q in quadrados)
    return (xmin, ymin, xmax, ymax)

def nice_step(span):
    if span <= 0: return 1.0
    raw = span / 10.0
    exp = math.floor(math.log10(raw)) if raw > 0 else 0
    base = raw / (10 ** exp)
    if base < 1.5: m = 1.0
    elif base < 3.5: m = 2.0
    elif base < 7.5: m = 5.0
    else: m = 10.0
    return m * (10 ** exp)

def fit_to_bbox(xmin, ymin, xmax, ymax, margin_pct=MARGIN_PCT):
    w = xmax - xmin
    h = ymax - ymin
    if w <= 0 or h <= 0:
        w = h = 1.0
        xmin, ymin = -0.5, -0.5
        xmax, ymax = 0.5, 0.5
    xmin -= w * margin_pct
    xmax += w * margin_pct
    ymin -= h * margin_pct
    ymax += h * margin_pct

    vp = glGetIntegerv(GL_VIEWPORT)
    win_w = max(1, vp[2])
    win_h = max(1, vp[3])
    aspect_win = win_w / win_h
    w = xmax - xmin
    h = ymax - ymin
    aspect_world = w / h

    if aspect_world > aspect_win:
        h_needed = w / aspect_win
        delta = (h_needed - h) * 0.5
        ymin -= delta
        ymax += delta
    else:
        w_needed = h * aspect_win
        delta = (w_needed - w) * 0.5
        xmin -= delta
        xmax += delta

    set_ortho(xmin, xmax, ymin, ymax)

def fit_to_squares():
    xmin, ymin, xmax, ymax = bbox_of_squares()
    fit_to_bbox(xmin, ymin, xmax, ymax)

def fit_to_points(points):
    if not points:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    fit_to_bbox(min(xs), min(ys), max(xs), max(ys))

def desenhaEixos():
    glPushMatrix()
    glColor3f(1, 1, 1)
    glLineWidth(1)
    glBegin(GL_LINES)
    glVertex2f(left + panX, 0); glVertex2f(right + panX, 0)
    glVertex2f(0, bottom + panY); glVertex2f(0, top + panY)
    glEnd()
    glPopMatrix()

def desenhaGrid():
    if not SHOW_GRID: 
        return
    glPushMatrix()
    glColor3f(0.15, 0.15, 0.15)
    glLineWidth(1)

    w = (right - left)
    h = (top - bottom)
    sx = nice_step(w)
    sy = nice_step(h)

    x0 = math.floor((left + panX) / sx) * sx
    x = x0
    glBegin(GL_LINES)
    while x <= right + panX + 1e-6:
        glVertex2f(x, bottom + panY); glVertex2f(x, top + panY)
        x += sx
    y0 = math.floor((bottom + panY) / sy) * sy
    y = y0
    while y <= top + panY + 1e-6:
        glVertex2f(left + panX, y); glVertex2f(right + panX, y)
        y += sy
    glEnd()
    glPopMatrix()

def desenhaBBox():
    if not SHOW_BBOX:
        return
    xmin, ymin, xmax, ymax = bbox_of_squares()
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(xmin, ymin)
    glVertex2f(xmax, ymin)
    glVertex2f(xmax, ymax)
    glVertex2f(xmin, ymax)
    glEnd()
    glPopMatrix()

def desenhaQuadrado(x, y, w, h, cor=(1,1,1)):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(*cor)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(w, 0)
    glVertex2f(w, h)
    glVertex2f(0, h)
    glEnd()
    glPopMatrix()

# ----------------- Loop de desenho -----------------
def Desenha():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left + panX, right + panX, bottom + panY, top + panY)
    glMatrixMode(GL_MODELVIEW)

    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    # plano de fundo: grade
    desenhaGrid()

    # conteúdo
    for q in quadrados:
        desenhaQuadrado(q.pos.x, q.pos.y, q.w, q.h, q.c)

    # overlay: eixos + bbox
    desenhaEixos()
    desenhaBBox()

    glFlush()

# ----------------- Controles -----------------
def Teclado(key: chr, x: int, y: int):
    global num_quadrado, panX, panY, SHOW_GRID, SHOW_BBOX

    if key == 27:  # ESC
        exit(0)

    if key == b' ':  # novo quadrado
        quadrados.append(Quadrado(0.1, 0.1))
        num_quadrado = len(quadrados) - 1

    # mover quadrado atual (WASD)
    if key == b'a': quadrados[num_quadrado].pos -= Ponto(0.02, 0)
    if key == b'd': quadrados[num_quadrado].pos += Ponto(0.02, 0)
    if key == b'w': quadrados[num_quadrado].pos += Ponto(0, 0.02)
    if key == b's': quadrados[num_quadrado].pos -= Ponto(0, 0.02)

    # debug / visual
    if key == b'f':  # fit ao conteúdo
        fit_to_squares()
    if key == b'g':  # grid on/off
        SHOW_GRID = not SHOW_GRID
    if key == b'b':  # bbox on/off
        SHOW_BBOX = not SHOW_BBOX
    if key == b'0':  # reset ortho
        reset_ortho()

    glutPostRedisplay()

def TeclasEspeciais(key: int, x: int, y: int):
    global panX, panY
    # pan (setas)
    if key == GLUT_KEY_LEFT:  panX += 0.01
    if key == GLUT_KEY_RIGHT: panX -= 0.01
    if key == GLUT_KEY_UP:    panY -= 0.01
    if key == GLUT_KEY_DOWN:  panY += 0.01
    glutPostRedisplay()

# ----------------- Inicialização -----------------
def Inicializa():
    reset_ortho()  # começa com [-1,1]x[-1,1]

# ----------------- Main -----------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(800, 800)
    glutCreateWindow(b"Desenha OpenGL - Auto-fit, Grid e BBox")

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