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

class GLDraw:
    
    def circle(cx, cy, radius, filled=True, segments=32):
        DrawUtils.circle(cx, cy, radius, filled, segments)
    
    def ellipse(cx, cy, width, height, filled=True, segments=32):
        DrawUtils.ellipse(cx, cy, width, height, filled, segments)