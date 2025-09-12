// main.cpp
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <random>
#include <chrono>

// --- GLUT portátil ---
#if defined(__APPLE__)
  #include <GLUT/glut.h>
#elif defined(_WIN32)
  #include <windows.h>
  #include <GL/freeglut.h>
#else
  #include <GL/glut.h>
#endif

// -----------------------------
// Classes e utilitários
// -----------------------------
struct Ponto {
    float x{0.0f}, y{0.0f};
    Ponto() = default;
    Ponto(float x, float y) : x(x), y(y) {}

    void print() const {
        std::cout << "Ponto (" << x << ", " << y << ")\n";
    }
    void set(float nx, float ny) { x = nx; y = ny; }

    Ponto operator+(const Ponto& o) const { return {x + o.x, y + o.y}; }
    Ponto operator-(const Ponto& o) const { return {x - o.x, y - o.y}; }
    Ponto operator*(float escalar) const  { return {x * escalar, y * escalar}; }
};

// -----------------------------
// Estado global (como no Python)
// -----------------------------
float leftV   = -1.0f;
float rightV  =  1.0f;
float topV    =  1.0f;
float bottomV = -1.0f;
float panX = 0.0f, panY = 0.0f;

Ponto pos_tornado(-1.2f, 0.0f);
Ponto pos_telhado( 0.35f, 0.2f);
float rot_telhado = 0.0f;

// temporização
auto  t_last   = std::chrono::steady_clock::now();
double soma_dt = 0.0;

// RNG para deslocamentos aleatórios do telhado
std::mt19937 rng(std::random_device{}());
std::uniform_real_distribution<float> dist_dx(0.0001f, 0.0060f);
std::uniform_real_distribution<float> dist_dy(-0.0040f, 0.0040f);
std::uniform_real_distribution<float> dist_rot(-0.5f, -0.001f); // negativa, como no Python

// -----------------------------
// Desenho
// -----------------------------
void desenhaEixos() {
    glPushMatrix();
    glLoadIdentity();

    glColor3f(1.f, 1.f, 1.f);
    glLineWidth(1.f);

    glBegin(GL_LINES);
    // eixo X
    glVertex2f(leftV,  0.f);
    glVertex2f(rightV, 0.f);
    // eixo Y
    glVertex2f(0.f, bottomV);
    glVertex2f(0.f, topV);
    glEnd();

    glPopMatrix();
}

void desenhaQuadrado(float x, float y, float w, float h, float r) {
    glPushMatrix();
    glTranslatef(x, y, 0.f);
    glRotatef(r, 0.f, 0.f, 1.f);

    glBegin(GL_QUADS);
    glVertex2f(0.f, 0.f);
    glVertex2f(w,  0.f);
    glVertex2f(w,  h);
    glVertex2f(0.f, h);
    glEnd();

    glPopMatrix();
}

void desenhaTelhado(float x, float y, float r) {
    glPushMatrix();
    glTranslatef(x, y, 0.f);
    glRotatef(r, 0.f, 0.f, 1.f);

    glBegin(GL_TRIANGLES);
    glColor3f(1.f, 1.f, 1.f);
    glVertex2f(-0.2f, 0.1f);
    glColor3f(1.f, 0.f, 0.f);
    glVertex2f( 0.0f, 0.22f);
    glColor3f(0.f, 0.f, 1.f);
    glVertex2f( 0.2f, 0.1f);
    glEnd();

    glPopMatrix();
}

void desenhaTornado(float x, float y) {
    glPushMatrix();
    glTranslatef(x, y, 0.f);

    glBegin(GL_TRIANGLES);
    glColor3f(0.5f, 0.5f, 0.5f);
    glVertex2f(-0.05f, 0.8f);
    glVertex2f( 0.05f, 0.8f);
    glColor3f(1.f, 1.f, 1.f);
    glVertex2f( 0.0f, 0.0f);
    glEnd();

    glPopMatrix();
}

// -----------------------------
// Display
// -----------------------------
void Desenha() {
    // Projeção com pan
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(leftV + panX, rightV + panX, bottomV + panY, topV + panY);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // Fundo
    glClearColor(0.f, 0.f, 0.f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);

    // Casa (corpo)
    glColor3f(1.f, 0.f, 0.3f);
    desenhaQuadrado(0.2f, 0.0f, 0.3f, 0.3f, 0.0f);

    // Telhado
    desenhaTelhado(pos_telhado.x, pos_telhado.y, rot_telhado);

    // Tornado
    desenhaTornado(pos_tornado.x, pos_tornado.y);

    // Eixos
    desenhaEixos();

    glFlush(); // usando GLUT_SINGLE
}

// -----------------------------
// Idle / Animação (~30 FPS)
// -----------------------------
void Animacao() {
    auto t_now = std::chrono::steady_clock::now();
    std::chrono::duration<double> dt = t_now - t_last;
    t_last = t_now;

    soma_dt += dt.count();
    if (soma_dt > (1.0 / 30.0)) {
        soma_dt = 0.0;

        // move tornado
        pos_tornado = pos_tornado + Ponto(0.005f, 0.0f);

        // quando passa da casa, mexe o telhado
        if (pos_tornado.x > 0.35f) {
            pos_telhado = pos_telhado + Ponto(dist_dx(rng), dist_dy(rng));
            rot_telhado += dist_rot(rng); // negativo (gira no mesmo sentido do Python)
        }

        glutPostRedisplay();
    }
}

// -----------------------------
// Teclado
// -----------------------------
void Teclado(unsigned char key, int, int) {
    if (key == 27) std::exit(0); // ESC

    const float step = 0.01f;
    if (key == 'a' || key == 'A') panX -= step;
    if (key == 'd' || key == 'D') panX += step;
    if (key == 'w' || key == 'W') panY += step;
    if (key == 's' || key == 'S') panY -= step;

    glutPostRedisplay();
}

void TeclasEspeciais(int /*key*/, int /*x*/, int /*y*/) {
    // habilite se quiser movimentar com setas
    // const float step = 0.01f;
    // if (key == GLUT_KEY_UP)    panY += step;
    // if (key == GLUT_KEY_DOWN)  panY -= step;
    // if (key == GLUT_KEY_LEFT)  panX -= step;
    // if (key == GLUT_KEY_RIGHT) panX += step;
    glutPostRedisplay();
}

// -----------------------------
// Inicialização
// -----------------------------
void Inicializa() {
    glMatrixMode(GL_PROJECTION);
    gluOrtho2D(leftV, rightV, bottomV, topV);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // zera temporização
    t_last   = std::chrono::steady_clock::now();
    soma_dt  = 0.0;
}

// -----------------------------
// main
// -----------------------------
int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize(800, 800);
    glutCreateWindow("Desenha OpenGL (C++ - Tornado & Casa)");

    glutDisplayFunc(Desenha);
    glutIdleFunc(Animacao);
    glutKeyboardFunc(Teclado);
    glutSpecialFunc(TeclasEspeciais);

    Inicializa();
    glutMainLoop();
    return 0;
}
