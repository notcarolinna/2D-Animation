import math
from OpenGL.GL import *

class DrawingUtils:   
    @staticmethod
    def set_color(r, g, b, a=1.0): 
        glColor4f(r, g, b, a)

    @staticmethod
    def circle(cx, cy, r, fill=True, seg=96):
        if r <= 0: return
        glBegin(GL_TRIANGLE_FAN if fill else GL_LINE_LOOP)
        if fill: glVertex2f(cx, cy)
        for i in range(seg + 1):
            a = 2.0 * math.pi * i / seg
            glVertex2f(cx + r * math.cos(a), cy + r * math.sin(a))
        glEnd()

    @staticmethod
    def ellipse(cx, cy, rx, ry, fill=True, seg=96):
        glBegin(GL_TRIANGLE_FAN if fill else GL_LINE_LOOP)
        if fill: glVertex2f(cx, cy)
        for i in range(seg + 1):
            a = 2.0 * math.pi * i / seg
            glVertex2f(cx + rx * math.cos(a), cy + ry * math.sin(a))
        glEnd()

    @staticmethod
    def ring(cx, cy, r_in, r_out, seg=160):
        if r_out <= r_in: return
        glBegin(GL_TRIANGLE_STRIP)
        for i in range(seg + 1):
            a = 2.0 * math.pi * i / seg
            c, s = math.cos(a), math.sin(a)
            glVertex2f(cx + r_out * c, cy + r_out * s)
            glVertex2f(cx + r_in  * c, cy + r_in  * s)
        glEnd()

    @staticmethod
    def line(x1, y1, x2, y2, w=2.0):
        glLineWidth(w)
        glBegin(GL_LINES); glVertex2f(x1, y1); glVertex2f(x2, y2); glEnd()

    @staticmethod
    def radial_shade(cx, cy, r, inner_alpha=0.0, outer_alpha=0.30, steps=24):
        for i in range(steps, 0, -1):
            t = i / steps
            a = inner_alpha*(1-t) + outer_alpha*t
            DrawingUtils.set_color(0,0,0,a)
            DrawingUtils.circle(cx, cy, r*t, True, 96)

    @staticmethod
    def begin_clip_circle(cx, cy, r, seg=128):
        glEnable(GL_STENCIL_TEST); glClear(GL_STENCIL_BUFFER_BIT)
        glStencilFunc(GL_ALWAYS, 1, 0xFF); glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        DrawingUtils.circle(cx, cy, r, True, seg)
        glColorMask(GL_TRUE,  GL_TRUE,  GL_TRUE,  GL_TRUE)
        glStencilFunc(GL_EQUAL, 1, 0xFF); glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)

    @staticmethod
    def end_clip(): 
        glDisable(GL_STENCIL_TEST)

    @staticmethod
    def with_pose(cx, cy, rot_deg=0.0, scale=(1.0,1.0)):
        glPushMatrix(); glTranslatef(cx, cy, 0)
        if rot_deg: glRotatef(rot_deg, 0, 0, 1)
        if scale!=(1.0,1.0): glScalef(scale[0], scale[1], 1.0)

    @staticmethod
    def end_pose(): 
        glPopMatrix()

set_color = DrawingUtils.set_color
circle = DrawingUtils.circle
ellipse = DrawingUtils.ellipse
ring = DrawingUtils.ring
line = DrawingUtils.line
radial_shade = DrawingUtils.radial_shade
begin_clip_circle = DrawingUtils.begin_clip_circle
end_clip = DrawingUtils.end_clip
with_pose = DrawingUtils.with_pose
end_pose = DrawingUtils.end_pose

# Definir edge_ring fora da classe Planet
def edge_ring(cx, cy, r, k=0.985, rgba=(1,1,1,0.20)):
    set_color(*rgba)
    ring(cx, cy, r*k, r, seg=140)

class Comet:
    def __init__(self, x=0, y=0, vx=0, vy=0, size=0.1, tail_length=20):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.tail_length = tail_length
        self.tail_positions = [(x, y)]
        self.brightness = 1.0
        self.life_time = 0.0
        
    def update(self, dt):
        """Método vazio - sem movimento automático"""
        pass
        
    def set_position(self, x, y):
        """Define a posição do cometa (controlado externamente)"""
        self.x = x
        self.y = y
        if len(self.tail_positions) == 0 or \
           abs(self.tail_positions[-1][0] - x) > 0.01 or \
           abs(self.tail_positions[-1][1] - y) > 0.01:
            self.tail_positions.append((x, y))
            
        if len(self.tail_positions) > self.tail_length:
            self.tail_positions.pop(0)
    
    def is_visible(self, screen_bounds):
        """Verifica se o cometa ainda está visível na tela"""
        margin = 2.0
        return (self.x > screen_bounds[0] - margin and 
                self.x < screen_bounds[1] + margin and
                self.y > screen_bounds[2] - margin and 
                self.y < screen_bounds[3] + margin)
        
    def draw(self):
        """Desenha o cometa com sua cauda"""
        self._draw_tail()
        self._draw_nucleus()
        self._draw_coma()
        
    def _draw_tail(self):
        """Desenha a cauda do cometa"""
        if len(self.tail_positions) < 2:
            return
            
        # Cauda de poeira (amarelada)
        for i in range(len(self.tail_positions) - 1):
            t = i / (len(self.tail_positions) - 1)
            alpha = t * 0.5 + 0.1
            width = max(1.0, self.size * 20 * t)
            
            x1, y1 = self.tail_positions[i]
            x2, y2 = self.tail_positions[i + 1]
            
            set_color(1.0, 0.9, 0.6, alpha)
            line(x1, y1, x2, y2, width)
            
        # Cauda de íons (azulada, mais fina)
        for i in range(len(self.tail_positions) - 1):
            t = i / (len(self.tail_positions) - 1)
            alpha = t * 0.4 + 0.05
            width = max(0.5, self.size * 15 * t)
            
            x1, y1 = self.tail_positions[i]
            x2, y2 = self.tail_positions[i + 1]
            
            offset_x = 0.02 * (1 - t)
            offset_y = 0.01 * (1 - t)
            
            set_color(0.6, 0.8, 1.0, alpha)
            line(x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y, width)
    
    def _draw_nucleus(self):
        """Desenha o núcleo rochoso do cometa"""
        set_color(0.4, 0.3, 0.2, 1.0)
        circle(self.x, self.y, self.size, True)
        
        set_color(0.2, 0.15, 0.1, 0.8)
        circle(self.x - self.size * 0.3, self.y + self.size * 0.2, self.size * 0.2, True)
        circle(self.x + self.size * 0.2, self.y - self.size * 0.3, self.size * 0.15, True)
    
    def _draw_coma(self):
        """Desenha a coma (atmosfera brilhante) ao redor do núcleo"""
        set_color(1.0, 1.0, 0.9, 0.3 * self.brightness)
        circle(self.x, self.y, self.size * 2, True)
        
        set_color(1.0, 0.9, 0.7, 0.15 * self.brightness)
        circle(self.x, self.y, self.size * 4, True)
        
        set_color(1.0, 1.0, 1.0, 0.6 * self.brightness)
        circle(self.x, self.y, self.size * 0.8, True)

class Planet:
    def __init__(self, name, x=0, y=0, radius=1.0, color=(1,1,1)):
        self.name, self.x, self.y, self.radius, self.color = name, x, y, radius, color
        self.rotation = 0.0
        self.orbital_radius = 0.0; self.orbital_speed = 0.0; self.orbital_angle = 0.0

    def update(self, dt):
        """Método vazio - sem animação automática"""
        pass

    def draw(self):
        with_pose(self.x, self.y, rot_deg=self.rotation, scale=(self.radius, self.radius))
        fn = DRAWERS.get(self.name.lower())
        if fn: fn(0,0,1.0)
        else:  set_color(*self.color); circle(0,0,1.0,True)
        end_pose()

C = {
    "sun":       (1.00, 0.65, 0.15, 1.0),  
    "mercury":   (0.70, 0.50, 0.30, 1.0),  
    "venus":     (1.00, 0.95, 0.20, 1.0), 
    "earth":     (0.25, 0.66, 0.96, 1.0),  
    "earthLand": (0.42, 0.82, 0.42, 1.0),  
    "mars":      (0.90, 0.20, 0.10, 1.0),  
    "jupiter":   (0.74, 0.53, 0.33, 1.0),  
    "saturn":    (0.95, 0.66, 0.27, 1.0),  
    "uranus":    (0.43, 0.86, 0.79, 1.0),  
    "neptune":   (0.29, 0.39, 0.85, 1.0),  
}

def draw_sun(cx, cy, r):
    set_color(*C["sun"]); circle(cx, cy, r, True, 128)
    begin_clip_circle(cx, cy, r)
    set_color(1.00,0.92,0.55,0.45); ellipse(cx-0.10*r, cy+0.25*r, 0.70*r, 0.18*r, True)
    set_color(1.00,0.60,0.10,0.28); ellipse(cx+0.15*r, cy-0.30*r, 0.55*r, 0.15*r, True)
    end_clip()
    set_color(1.00, 0.92, 0.50, 0.35); circle(cx, cy, 0.75*r, True, 96)
    radial_shade(cx, cy, r, 0.0, 0.15)

def draw_mercury(cx, cy, r):
    set_color(*C["mercury"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(0.46, 0.33, 0.23, 1.0); circle(cx-0.26*r, cy+0.16*r, 0.26*r, True)
    set_color(0.38, 0.27, 0.20, 1.0); circle(cx+0.22*r, cy-0.14*r, 0.18*r, True)
    set_color(0.54, 0.40, 0.29, 1.0); circle(cx-0.06*r, cy-0.28*r, 0.12*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_venus(cx, cy, r):
    set_color(*C["venus"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(1.00, 0.84, 0.45, 1.0); ellipse(cx, cy+0.26*r, 0.95*r, 0.12*r, True)
    set_color(1.00, 0.90, 0.68, 1.0); ellipse(cx, cy-0.02*r, 0.99*r, 0.11*r, True)
    set_color(0.98, 0.78, 0.42, 1.0); ellipse(cx, cy-0.30*r, 0.93*r, 0.12*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

def draw_earth(cx, cy, r):
    set_color(*C["earth"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(*C["earthLand"])
    circle(cx-0.30*r, cy+0.10*r, 0.42*r, True)
    circle(cx+0.32*r, cy-0.02*r, 0.30*r, True)
    circle(cx+0.12*r, cy-0.36*r, 0.18*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r, rgba=(1,1,1,0.35))

def draw_mars(cx, cy, r):
    set_color(*C["mars"]); circle(cx, cy, r, True)
    begin_clip_circle(cx, cy, r)
    set_color(0.70, 0.18, 0.12, 1.0); ellipse(cx-0.12*r, cy+0.16*r, 0.34*r, 0.14*r, True)
    set_color(0.62, 0.16, 0.10, 1.0); ellipse(cx+0.22*r, cy-0.12*r, 0.26*r, 0.12*r, True)
    set_color(0.55, 0.10, 0.10, 1.0); circle(cx+0.10*r, cy-0.08*r, 0.16*r, True)
    set_color(0.58, 0.14, 0.12, 1.0); circle(cx-0.26*r, cy+0.02*r, 0.12*r, True)
    end_clip(); radial_shade(cx, cy, r, 0.0, 0.10)
    edge_ring(cx, cy, r)

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

def create_planets():
    cfg = [
        ("Sun",0.0,0.0,1.2,(1,1,0)), ("Mercury",2.0,0.0,0.3,C["mercury"]),
        ("Venus",3.0,0.0,0.4,C["venus"]), ("Earth",4.5,0.0,0.5,C["earth"]),
        ("Mars",6.0,0.0,0.4,C["mars"]), ("Jupiter",9.0,0.0,1.0,C["jupiter"]),
        ("Saturn",12.0,0.0,0.8,C["saturn"]), ("Uranus",15.0,0.0,0.6,C["uranus"]),
        ("Neptune",18.0,0.0,0.6,C["neptune"])
    ]
    planets = []
    for name, x, y, size, color in cfg:
        p = Planet(name, x, y, size, color)
        planets.append(p)
    return planets

def create_comet(x=0, y=0, vx=0, vy=0, size=0.08):
    return Comet(x, y, vx, vy, size)