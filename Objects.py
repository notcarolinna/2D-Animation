import math
from OpenGL.GL import *

class DrawUtils:   
    def set_color(r, g, b, a=1.0): 
        glColor4f(r, g, b, a)

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
        if w <= 0: w = 0.1
        glLineWidth(w)
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    def radial_shade(cx, cy, r, inner_alpha=0.0, outer_alpha=0.30, steps=24):
        for i in range(steps, 0, -1):
            t = i / steps
            a = inner_alpha*(1-t) + outer_alpha*t
            DrawUtils.set_color(0, 0, 0, a)
            DrawUtils.circle(cx, cy, r*t, True, 96)

    def begin_clip_circle(cx, cy, r, seg=128):
        glEnable(GL_STENCIL_TEST)
        glClear(GL_STENCIL_BUFFER_BIT)
        glStencilFunc(GL_ALWAYS, 1, 0xFF)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        DrawUtils.circle(cx, cy, r, True, seg)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glStencilFunc(GL_EQUAL, 1, 0xFF)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

    def end_clip(): 
        glDisable(GL_STENCIL_TEST)

    def with_pose(cx, cy, rot_deg=0.0, scale=(1.0,1.0)):
        glPushMatrix()
        glTranslatef(cx, cy, 0)
        if rot_deg: glRotatef(rot_deg, 0, 0, 1)
        if scale != (1.0,1.0): glScalef(scale[0], scale[1], 1.0)

    def end_pose(): 
        glPopMatrix()

def edge_ring(cx, cy, r, k=0.985, rgba=(1,1,1,0.20)):
    DrawUtils.set_color(*rgba)
    DrawUtils.ring(cx, cy, r*k, r, seg=140)

class Star:
    def __init__(self, x=0, y=0, vx=0, vy=0, size=0.05):
        self.x, self.y, self.vx, self.vy, self.size = x, y, vx, vy, size
        self.tail_positions = [(x, y)]
        self.life_time = 0.0
        
    def update(self, dt):
        self.life_time += dt
        
    def set_position(self, x, y):
        self.x, self.y = x, y
        if not self.tail_positions or abs(self.tail_positions[-1][0] - x) > 0.01:
            self.tail_positions.append((x, y))
            if len(self.tail_positions) > 20:
                self.tail_positions.pop(0)
        
    def draw(self):
        brightness = math.sin(self.life_time * 8.0) * 0.3 + 0.7
        
        # Trail
        for i in range(len(self.tail_positions) - 1):
            t = i / max(1, len(self.tail_positions) - 1)
            width = max(0.5, self.size * 25 * t)
            DrawUtils.set_color(1.0, 1.0, 0.9, (t * 0.6 + 0.1) * brightness)
            DrawUtils.line(*self.tail_positions[i], *self.tail_positions[i + 1], width)
        
        # Rays
        DrawUtils.set_color(1.0, 1.0, 0.8, 0.8 * brightness)
        ray_len = self.size * 4
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            DrawUtils.line(self.x, self.y, 
                         self.x + ray_len * math.cos(rad), 
                         self.y + ray_len * math.sin(rad), 2.0)
        
        # Core layers
        for size_mult, alpha_mult, color_shift in [(0.8, 1.0, 0.0), (1.5, 0.7, 0.1), (2.5, 0.4, 0.2), (4.0, 0.2, 0.3)]:
            DrawUtils.set_color(1.0, 1.0 - color_shift, 1.0 - color_shift, alpha_mult * brightness)
            DrawUtils.circle(self.x, self.y, self.size * size_mult, True)

class Planet:
    def __init__(self, name, x=0, y=0, radius=1.0, color=(1,1,1)):
        self.name, self.x, self.y, self.radius, self.color = name, x, y, radius, color

    def update(self, dt): pass

    def draw(self):
        DrawUtils.with_pose(self.x, self.y, scale=(self.radius, self.radius))
        drawer = PLANET_DRAWERS.get(self.name.lower())
        if drawer:
            drawer(0, 0, 1.0)
        else:
            DrawUtils.set_color(*self.color)
            DrawUtils.circle(0, 0, 1.0, True)
        DrawUtils.end_pose()

COLORS = {
    "sun": (1.00, 0.65, 0.15, 1.0), "mercury": (0.70, 0.50, 0.30, 1.0), "venus": (1.00, 0.95, 0.20, 1.0),
    "earth": (0.25, 0.66, 0.96, 1.0), "earthLand": (0.42, 0.82, 0.42, 1.0), "mars": (0.90, 0.20, 0.10, 1.0),
    "jupiter": (0.74, 0.53, 0.33, 1.0), "saturn": (0.90, 0.82, 0.70, 1.0), 
    "uranus": (0.43, 0.86, 0.79, 1.0), "neptune": (0.29, 0.39, 0.85, 1.0)
}

def draw_sun(cx, cy, r):
    DrawUtils.set_color(*COLORS["sun"])
    DrawUtils.circle(cx, cy, r, True, 128)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(1.00, 0.92, 0.55, 0.45)
    DrawUtils.ellipse(cx-0.10*r, cy+0.25*r, 0.70*r, 0.18*r, True)
    DrawUtils.set_color(1.00, 0.60, 0.10, 0.28)
    DrawUtils.ellipse(cx+0.15*r, cy-0.30*r, 0.55*r, 0.15*r, True)
    DrawUtils.end_clip()
    DrawUtils.set_color(1.00, 0.92, 0.50, 0.35)
    DrawUtils.circle(cx, cy, 0.75*r, True, 96)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.25)

def draw_mercury(cx, cy, r):
    DrawUtils.set_color(*COLORS["mercury"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(0.46, 0.33, 0.23, 1.0)
    DrawUtils.circle(cx-0.26*r, cy+0.16*r, 0.26*r, True)
    DrawUtils.set_color(0.38, 0.27, 0.20, 1.0)
    DrawUtils.circle(cx+0.22*r, cy-0.14*r, 0.18*r, True)
    DrawUtils.set_color(0.54, 0.40, 0.29, 1.0)
    DrawUtils.circle(cx-0.06*r, cy-0.28*r, 0.12*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_venus(cx, cy, r):
    DrawUtils.set_color(*COLORS["venus"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(1.00, 0.84, 0.45, 1.0)
    DrawUtils.ellipse(cx, cy+0.26*r, 0.95*r, 0.12*r, True)
    DrawUtils.set_color(1.00, 0.90, 0.68, 1.0)
    DrawUtils.ellipse(cx, cy-0.02*r, 0.99*r, 0.11*r, True)
    DrawUtils.set_color(0.98, 0.78, 0.42, 1.0)
    DrawUtils.ellipse(cx, cy-0.30*r, 0.93*r, 0.12*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_earth(cx, cy, r):
    DrawUtils.set_color(*COLORS["earth"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(*COLORS["earthLand"])
    DrawUtils.circle(cx-0.30*r, cy+0.10*r, 0.42*r, True)
    DrawUtils.circle(cx+0.32*r, cy-0.02*r, 0.30*r, True)
    DrawUtils.circle(cx+0.12*r, cy-0.36*r, 0.18*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r, rgba=(1,1,1,0.35))

def draw_mars(cx, cy, r):
    DrawUtils.set_color(*COLORS["mars"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(0.70, 0.18, 0.12, 1.0)
    DrawUtils.ellipse(cx-0.12*r, cy+0.16*r, 0.34*r, 0.14*r, True)
    DrawUtils.set_color(0.62, 0.16, 0.10, 1.0)
    DrawUtils.ellipse(cx+0.22*r, cy-0.12*r, 0.26*r, 0.12*r, True)
    DrawUtils.set_color(0.55, 0.10, 0.10, 1.0)
    DrawUtils.circle(cx+0.10*r, cy-0.08*r, 0.16*r, True)
    DrawUtils.set_color(0.58, 0.14, 0.12, 1.0)
    DrawUtils.circle(cx-0.26*r, cy+0.02*r, 0.12*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_jupiter(cx, cy, r):
    DrawUtils.set_color(*COLORS["jupiter"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.begin_clip_circle(cx, cy, r)
    DrawUtils.set_color(0.80, 0.70, 0.60, 0.8)
    DrawUtils.ellipse(cx, cy+0.40*r, 0.90*r, 0.10*r, True)
    DrawUtils.ellipse(cx, cy+0.10*r, 0.95*r, 0.12*r, True)
    DrawUtils.ellipse(cx, cy-0.20*r, 0.90*r, 0.10*r, True)
    DrawUtils.ellipse(cx, cy-0.50*r, 0.85*r, 0.08*r, True)
    DrawUtils.set_color(0.80, 0.30, 0.20, 0.9)
    DrawUtils.ellipse(cx+0.40*r, cy-0.10*r, 0.25*r, 0.15*r, True)
    DrawUtils.end_clip()
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.18)

def draw_saturn(cx, cy, r):
    DrawUtils.with_pose(cx, cy, rot_deg=-20, scale=(1.0, 0.40))
    DrawUtils.set_color(0.90, 0.86, 0.78, 0.8)
    DrawUtils.ring(0, 0, 1.20*r, 1.80*r)
    DrawUtils.set_color(0.82, 0.78, 0.72, 0.8)
    DrawUtils.ring(0, 0, 1.35*r, 1.55*r)
    DrawUtils.end_pose()
    DrawUtils.set_color(*COLORS["saturn"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.set_color(0.80, 0.70, 0.50, 0.6)
    DrawUtils.ellipse(cx, cy+0.10*r, 0.90*r, 0.08*r, True)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.20)

def draw_uranus(cx, cy, r):
    DrawUtils.set_color(*COLORS["uranus"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.with_pose(cx, cy, rot_deg=85, scale=(1.0, 0.20))
    DrawUtils.set_color(0.80, 0.90, 1.00, 0.6)
    DrawUtils.ring(0, 0, 1.10*r, 1.30*r)
    DrawUtils.end_pose()
    DrawUtils.set_color(0.40, 0.60, 0.80, 0.4)
    DrawUtils.ellipse(cx, cy, 0.90*r, 0.10*r, True)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.18)

def draw_neptune(cx, cy, r):
    DrawUtils.set_color(*COLORS["neptune"])
    DrawUtils.circle(cx, cy, r, True)
    DrawUtils.set_color(0.20, 0.40, 0.80, 0.7)
    DrawUtils.line(cx-0.8*r, cy+0.1*r, cx+0.8*r, cy-0.1*r, 5.0)
    DrawUtils.set_color(0.10, 0.20, 0.50, 0.8)
    DrawUtils.ellipse(cx+0.30*r, cy-0.25*r, 0.15*r, 0.12*r, True)
    DrawUtils.radial_shade(cx, cy, r, 0.0, 0.20)

PLANET_DRAWERS = {
    "sun": draw_sun, "mercury": draw_mercury, "venus": draw_venus, "earth": draw_earth,
    "mars": draw_mars, "jupiter": draw_jupiter, "saturn": draw_saturn,
    "uranus": draw_uranus, "neptune": draw_neptune
}

def create_planets():
    cfg = [
        ("Sun", 0.0, 0.0, 1.2), ("Mercury", 2.0, 0.0, 0.3), ("Venus", 3.0, 0.0, 0.4),
        ("Earth", 4.5, 0.0, 0.5), ("Mars", 6.0, 0.0, 0.4), ("Jupiter", 9.0, 0.0, 1.0),
        ("Saturn", 12.0, 0.0, 0.8), ("Uranus", 15.0, 0.0, 0.6), ("Neptune", 18.0, 0.0, 0.6)
    ]
    return [Planet(name, x, y, size, COLORS.get(name.lower(), (1,1,1))) for name, x, y, size in cfg]

def create_star(x=0, y=0, vx=0, vy=0, size=0.04):
    return Star(x, y, vx, vy, size)

def create_comet(x=0, y=0, vx=0, vy=0, size=0.04):
    return create_star(x, y, vx, vy, size)