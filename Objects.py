import math
from collections import deque
from dataclasses import dataclass
from OpenGL.GL import *

def set_color(r, g, b, a=1.0): glColor4f(r, g, b, a)

def circle(cx, cy, r, fill=True, seg=96):
    if r <= 0: return
    glBegin(GL_TRIANGLE_FAN if fill else GL_LINE_LOOP)
    if fill: glVertex2f(cx, cy)
    for i in range(seg + 1):
        a = 2.0 * math.pi * i / seg
        glVertex2f(cx + r * math.cos(a), cy + r * math.sin(a))
    glEnd()

def ellipse(cx, cy, rx, ry, fill=True, seg=96):
    glBegin(GL_TRIANGLE_FAN if fill else GL_LINE_LOOP)
    if fill: glVertex2f(cx, cy)
    for i in range(seg + 1):
        a = 2.0 * math.pi * i / seg
        glVertex2f(cx + rx * math.cos(a), cy + ry * math.sin(a))
    glEnd()

def ring(cx, cy, r_in, r_out, seg=160):
    if r_out <= r_in: return
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(seg + 1):
        a = 2.0 * math.pi * i / seg
        c, s = math.cos(a), math.sin(a)
        glVertex2f(cx + r_out * c, cy + r_out * s)
        glVertex2f(cx + r_in  * c, cy + r_in  * s)
    glEnd()

def line(x1, y1, x2, y2, w=2.0):
    glLineWidth(w)
    glBegin(GL_LINES); glVertex2f(x1, y1); glVertex2f(x2, y2); glEnd()

def radial_shade(cx, cy, r, inner_alpha=0.0, outer_alpha=0.30, steps=24):
    for i in range(steps, 0, -1):
        t = i / steps
        a = inner_alpha*(1-t) + outer_alpha*t
        set_color(0,0,0,a); circle(cx, cy, r*t, True, 96)

def begin_clip_circle(cx, cy, r, seg=128):
    glEnable(GL_STENCIL_TEST); glClear(GL_STENCIL_BUFFER_BIT)
    glStencilFunc(GL_ALWAYS, 1, 0xFF); glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE); circle(cx, cy, r, True, seg)
    glColorMask(GL_TRUE,  GL_TRUE,  GL_TRUE,  GL_TRUE)
    glStencilFunc(GL_EQUAL, 1, 0xFF); glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

def end_clip(): glDisable(GL_STENCIL_TEST)

def with_pose(cx, cy, rot_deg=0.0, scale=(1.0,1.0)):
    """Contexto manual: usar push()/pop() em pares."""
    glPushMatrix(); glTranslatef(cx, cy, 0)
    if rot_deg: glRotatef(rot_deg, 0, 0, 1)
    if scale!=(1.0,1.0): glScalef(scale[0], scale[1], 1.0)

def end_pose(): glPopMatrix()

class Ponto:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __add__(self, o): return Ponto(self.x+o.x, self.y+o.y)
    def __sub__(self, o): return Ponto(self.x-o.x, self.y-o.y)
    def __mul__(self, k: float): return Ponto(self.x*k, self.y*k)

class TrailSeg:
    def __init__(self, p0: Ponto, p1: Ponto, t0: float):
        self.p0 = p0
        self.p1 = p1
        self.t0 = t0

class Starship:
    def __init__(self, x=-1.8, y=0.0):
        self.pos = Ponto(x, y)
        self.prev = Ponto(x, y)
        self.vx = 0.015
        self.trail = deque(maxlen=512)
        self.trail_ttl = 2.0
        self.trail_every = 3      # frames
        self.dash_frac = 0.55
        self._frames = 0

    # helpers de trilha
    def add_trail(self, t_now):
        dx, dy = self.pos.x - self.prev.x, self.pos.y - self.prev.y
        p1 = Ponto(self.prev.x + dx*self.dash_frac, self.prev.y + dy*self.dash_frac)
        self.trail.append(TrailSeg(self.prev, p1, t_now))

    def prune_trail(self, t_now):
        while self.trail and (t_now - self.trail[0].t0) > self.trail_ttl:
            self.trail.popleft()

    def update(self, t_now, dt):
        self._frames += 1
        self.prev = Ponto(self.pos.x, self.pos.y)
        self.pos.x += self.vx
        # trajetória suave
        self.pos.y = (0.8*math.sin(t_now*1.5)
                      + 0.2*math.sin(t_now*3.2)
                      + 0.3*math.cos(t_now*0.8))
        if self._frames % self.trail_every == 0:
            self.add_trail(t_now)
        self.prune_trail(t_now)

    def should_reset(self): return self.pos.x > 4.0

    def reset(self):
        self.pos = Ponto(-1.8, 0.0); self.prev = Ponto(-1.8, 0.0)
        self.trail.clear(); self._frames = 0

    def draw(self):
        with_pose(self.pos.x, self.pos.y);  # corpo 2x do seu exemplo
        glBegin(GL_TRIANGLES)
        set_color(1,1,1);   glVertex2f(0.24, 0.0)
        set_color(0.9,0.9,0.9); glVertex2f(-0.12, 0.09); glVertex2f(-0.12, -0.09)
        glEnd()
        glBegin(GL_QUADS)
        set_color(0.1,0.1,0.1); glVertex2f(-0.06, 0.03); glVertex2f(0.06, 0.03); glVertex2f(0.06,-0.03); glVertex2f(-0.06,-0.03)
        glEnd()
        glBegin(GL_TRIANGLES)
        set_color(0.2,0.2,0.2); glVertex2f(-0.12, 0.045); glVertex2f(-0.12,-0.045); set_color(0.8,0.8,0.8); glVertex2f(-0.21,0.0)
        glEnd()
        end_pose()

    def draw_trail(self, t_now):
        if not self.trail: return
        glLineWidth(3)
        for seg in self.trail:
            age = t_now - seg.t0
            if age > self.trail_ttl: continue
            a = 1.0 - age/self.trail_ttl
            glColor4f(0.9, 0.9, 0.9, a)
            # dois “dashes” curtos no segmento
            dx, dy = seg.p1.x - seg.p0.x, seg.p1.y - seg.p0.y
            for j in (0,1):
                s0, s1 = j/2.0, (j+0.7)/2.0
                glBegin(GL_LINES)
                glVertex2f(seg.p0.x + dx*s0, seg.p0.y + dy*s0)
                glVertex2f(seg.p0.x + dx*s1, seg.p0.y + dy*s1)
                glEnd()

C = {  
    "sun": (1.00, 0.84, 0.25, 1.0),
    "mercury": (0.55, 0.56, 0.60, 1.0),
    "venus": (0.96, 0.83, 0.62, 1.0),
    "earth": (0.24, 0.55, 0.93, 1.0),
    "earthLand": (0.28, 0.73, 0.44, 1.0),
    "mars": (0.86, 0.43, 0.28, 1.0),
    "jupiter": (0.92, 0.82, 0.68, 1.0),
    "saturn": (0.92, 0.84, 0.63, 1.0),
    "uranus": (0.58, 0.78, 0.90, 1.0),
    "neptune": (0.26, 0.49, 0.93, 1.0),
}

def draw_sun(cx, cy, r):
    set_color(*C["sun"]); circle(cx, cy, r, True, 128)
    begin_clip_circle(cx, cy, r)
    # textura minimal (poucos elementos)
    set_color(1.00,0.92,0.55,0.45); ellipse(cx-0.10*r, cy+0.25*r, 0.70*r, 0.18*r, True)
    set_color(1.00,0.60,0.10,0.28); ellipse(cx+0.15*r, cy-0.30*r, 0.55*r, 0.15*r, True)
    end_clip()
    set_color(1.00, 0.92, 0.50, 0.35); circle(cx, cy, 0.75*r, True, 96)
    radial_shade(cx, cy, r, 0.0, 0.15)

def draw_mercury(cx, cy, r):
    set_color(*C["mercury"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(0,0,0,0.30); circle(cx-0.30*r, cy+0.20*r, 0.20*r, True)
    circle(cx+0.20*r, cy-0.15*r, 0.15*r, True); circle(cx-0.10*r, cy-0.30*r, 0.10*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.25)

def draw_venus(cx, cy, r):
    set_color(*C["venus"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(1,1,1,0.30); ellipse(cx, cy+0.30*r, 0.80*r, 0.10*r, True)
    ellipse(cx, cy, 0.90*r, 0.08*r, True); ellipse(cx, cy-0.30*r, 0.80*r, 0.10*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.20)

def draw_earth(cx, cy, r):
    set_color(*C["earth"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(*C["earthLand"])
    circle(cx-0.30*r, cy+0.10*r, 0.40*r, True)
    circle(cx+0.30*r, cy-0.05*r, 0.30*r, True)
    circle(cx+0.10*r, cy-0.40*r, 0.20*r, True)
    set_color(1,1,1,0.80); ellipse(cx, cy+0.85*r, 0.30*r, 0.08*r, True); ellipse(cx, cy-0.85*r, 0.30*r, 0.08*r, True)
    set_color(1,1,1,0.40); ellipse(cx, cy+0.20*r, 0.70*r, 0.10*r, True); ellipse(cx, cy-0.20*r, 0.80*r, 0.08*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.20)

def draw_mars(cx, cy, r):
    set_color(*C["mars"]); circle(cx, cy, r, True)
    set_color(1,1,1,0.60); ellipse(cx, cy+0.85*r, 0.30*r, 0.08*r, True); ellipse(cx, cy-0.85*r, 0.30*r, 0.08*r, True)
    set_color(0.5,0.2,0.1,0.8); line(cx-0.8*r, cy+0.1*r, cx+0.6*r, cy-0.1*r, 4.0)
    radial_shade(cx, cy, r, 0.0, 0.20)

def draw_jupiter(cx, cy, r):
    set_color(*C["jupiter"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(0.80,0.70,0.60,0.8)
    ellipse(cx, cy+0.40*r, 0.90*r, 0.10*r, True); ellipse(cx, cy+0.10*r, 0.95*r, 0.12*r, True)
    ellipse(cx, cy-0.20*r, 0.90*r, 0.10*r, True); ellipse(cx, cy-0.50*r, 0.85*r, 0.08*r, True)
    set_color(0.80,0.30,0.20,0.9); ellipse(cx+0.40*r, cy-0.10*r, 0.25*r, 0.15*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.18)

def draw_saturn(cx, cy, r):
    with_pose(cx, cy, rot_deg=-20, scale=(1.0, 0.40))
    set_color(0.90,0.86,0.78,0.8); ring(0, 0, 1.20*r, 1.80*r)
    set_color(0.82,0.78,0.72,0.8); ring(0, 0, 1.35*r, 1.55*r)
    end_pose()
    set_color(*C["saturn"]); circle(cx, cy, r, True)
    set_color(0.80,0.70,0.50,0.6); ellipse(cx, cy+0.10*r, 0.90*r, 0.08*r, True)
    radial_shade(cx, cy, r, 0.0, 0.20)

def draw_uranus(cx, cy, r):
    set_color(*C["uranus"]); circle(cx, cy, r, True)
    with_pose(cx, cy, rot_deg=85, scale=(1.0, 0.20))
    set_color(0.80,0.90,1.00,0.6); ring(0, 0, 1.10*r, 1.30*r)
    end_pose()
    set_color(0.40,0.60,0.80,0.4); ellipse(cx, cy, 0.90*r, 0.10*r, True)
    radial_shade(cx, cy, r, 0.0, 0.18)

def draw_neptune(cx, cy, r):
    set_color(*C["neptune"]); circle(cx, cy, r, True)
    set_color(0.20,0.40,0.80,0.7); line(cx-0.8*r, cy+0.1*r, cx+0.8*r, cy-0.1*r, 5.0)
    set_color(0.10,0.20,0.50,0.8); ellipse(cx+0.30*r, cy-0.25*r, 0.15*r, 0.12*r, True)
    radial_shade(cx, cy, r, 0.0, 0.20)

DRAWERS = {
    "sun": draw_sun, "mercury": draw_mercury, "venus": draw_venus, "earth": draw_earth,
    "mars": draw_mars, "jupiter": draw_jupiter, "saturn": draw_saturn,
    "uranus": draw_uranus, "neptune": draw_neptune
}

class Planet:
    def __init__(self, name, x=0, y=0, radius=1.0, color=(1,1,1)):
        self.name, self.x, self.y, self.radius, self.color = name, x, y, radius, color
        self.rotation = 0.0
        self.orbital_radius = 0.0; self.orbital_speed = 0.0; self.orbital_angle = 0.0

    def update(self, dt):
        self.rotation += {
            "Sun":10.0, "Mercury":50.0, "Venus":30.0, "Earth":40.0, "Mars":35.0,
            "Jupiter":60.0, "Saturn":45.0, "Uranus":25.0, "Neptune":30.0
        }.get(self.name, 30.0) * dt

    def draw(self):
        with_pose(self.x, self.y, rot_deg=self.rotation, scale=(self.radius, self.radius))
        fn = DRAWERS.get(self.name.lower())
        if fn: fn(0,0,1.0)
        else:  set_color(*self.color); circle(0,0,1.0,True)
        end_pose()

def create_starship(x=-1.8, y=0.0): return Starship(x, y)

def create_planets():
    cfg = [
        ("Sun",0.0,0.0,1.2,(1,1,0)), ("Mercury",2.0,4.0,0.3,C["mercury"]),
        ("Venus",3.0,3.0,0.4,C["venus"]), ("Earth",4.5,2.0,0.5,C["earth"]),
        ("Mars",6.0,1.5,0.4,C["mars"]), ("Jupiter",9.0,0.8,1.0,C["jupiter"]),
        ("Saturn",12.0,0.6,0.8,C["saturn"]), ("Uranus",15.0,0.4,0.6,C["uranus"]),
        ("Neptune",18.0,0.3,0.6,C["neptune"])
    ]
    planets = []
    for name, r_orb, v_orb, size, color in cfg:
        p = Planet(name, 0, 0, size, color)
        p.orbital_radius, p.orbital_speed = r_orb, v_orb
        p.orbital_angle = (hash(name) % 100) / 100.0 * 2 * math.pi
        planets.append(p)
    return planets

def draw_orbit(radius, flatten_factor=0.3):
    if radius <= 0: return
    set_color(0.3, 0.3, 0.3); glLineWidth(1)
    glBegin(GL_LINE_LOOP)
    for i in range(64):
        a = 2.0 * math.pi * i / 64
        glVertex2f(radius*math.cos(a), radius*math.sin(a)*flatten_factor)
    glEnd()