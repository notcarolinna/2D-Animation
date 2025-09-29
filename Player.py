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

class Quadrado:
    def __init__(self, w, h, cor=(1,1,1)):
        self.pos = Ponto(0, 0)
        self.w = w
        self.h = h
        self.c = cor

class PlayerSystem:
    def __init__(self):
        self.quadrados = [Quadrado(0.8, 0.8)]
        self.num_quadrado = 0
        self.SHOW_GRID = True
        self.SHOW_BBOX = True
        self.MARGIN_PCT = 0.10

    def bbox_of_squares(self):
        if not self.quadrados:
            return (-1, -1, 1, 1)
        xmin = min(q.pos.x for q in self.quadrados)
        ymin = min(q.pos.y for q in self.quadrados)
        xmax = max(q.pos.x + q.w for q in self.quadrados)
        ymax = max(q.pos.y + q.h for q in self.quadrados)
        return (xmin, ymin, xmax, ymax)

    def nice_step(self, span):
        if span <= 0: return 1.0
        raw = span / 10.0
        exp = math.floor(math.log10(raw)) if raw > 0 else 0
        base = raw / (10 ** exp)
        if base < 1.5: m = 1.0
        elif base < 3.5: m = 2.0
        elif base < 7.5: m = 5.0
        else: m = 10.0
        return m * (10 ** exp)

    def desenhaQuadrado(self, x, y, w, h, cor=(1,1,1)):
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

    def desenhaBBox(self):
        if not self.SHOW_BBOX:
            return
        xmin, ymin, xmax, ymax = self.bbox_of_squares()
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

    def fit_to_bbox(self, xmin, ymin, xmax, ymax, margin_pct=None):
        if margin_pct is None:
            margin_pct = self.MARGIN_PCT
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

        return (xmin, xmax, ymin, ymax)

    def fit_to_squares(self):
        xmin, ymin, xmax, ymax = self.bbox_of_squares()
        return self.fit_to_bbox(xmin, ymin, xmax, ymax)
