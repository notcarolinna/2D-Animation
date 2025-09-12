// main.cpp
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <vector>
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
// Estruturas de apoio
// -----------------------------
struct Ponto {
    float x{0.0f}, y{0.0f};
    Ponto() = default;
    Ponto(float x, float y) : x(x), y(y) {}

    void print() const { std::cout << "Ponto (" << x << ", " << y << ")\n"; }
    void set(float nx, float ny) { x = nx; y = ny; }

    Ponto operator+(const Ponto& o) const { return {x + o.x, y + o.y}; }
    Ponto operator-(const Ponto& o) const { return {x - o.x, y - o.y}; }
    Ponto operator*(float esc) const      { return {x * esc,   y * esc}; }
};

struct Quadrado {
    Ponto pos{0.f, 0.f};   // canto inferior esquerdo
    float w{0.25f};        // largura
    float h{0.25f};        // altura
    float r{0.f};          // rotação em graus
    float cr{1.f}, cg{0.f}, cb{0.f}; // cor

    Quadrado(float w, float h) : w(w), h(h) {}
    Quadrado(float w, float h, float cr, float cg, float cb)
        : w(w), h(h), cr(cr), cg(cg), cb(cb) {}
};

// -----------------------------
// Estado global (como no Python)
// -----------------------------
std::vector<Quadrado> quadrados = { Quadrado(0.25f, 0.25f) };
int num_quadrado = 0;

// câmera (ortho + pan)
float leftV = 0.f, rightV = 0.f, topV = 0.f, bottomV = 0.f;
float panX = 0.f, panY = 0.f;

// tempo/animacao (~30 FPS)
auto  t_last   = std::chrono::steady_clock::now();
double soma_dt = 0.0;

// -----------------------------
// Desenho dos eixos
// -----------------------------
void desenhaEixos() {
    glPushMatrix();
    glLoadIdentity();

    glColor3f(1.f, 1.f, 1.f);
    glLineWidth(1.f);

    glBegin(GL_LINES);
    glVertex2f(leftV,  0.f);
    glVertex2f(rightV, 0.f);
    glVertex2f(0.f, bottomV);
    glVertex2f(0.f, topV);
    glEnd();

    glPopMatrix();
}

// -----------------------------
// Desenho do quadrado (pos + rot)
// -----------------------------
void desenhaQuadrado(float x, float y, float w, float h, float r) {
    glPushMatrix();

    glTranslatef(x, y, 0.f);      // posição
    glRotatef(r, 0.f, 0.f, 1.f);  // rotação no plano XY

    glBegin(GL_QUADS);
    glVertex2f(0.f, 0.f);
    glVertex2f(w,  0.f);
    glVertex2f(w,  h);
    glVertex2f(0.f, h);
    glEnd();

    glPopMatrix();
}

// -----------------------------
// Display
// -----------------------------
void Desenha() {
    // Projeção ortográfica com pan
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(leftV + panX, rightV + panX, bottomV + panY, topV + panY);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // Fundo
    glClearColor(0.f, 0.f, 0.f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);

    // Desenha todos os quadrados
    for (const auto& q : quadrados) {
        glColor3f(q.cr, q.cg, q.cb);
        // Nota: mantendo semântica (w, h).
        desenhaQuadrado(q.pos.x, q.pos.y, q.w, q.h, q.r);
    }

    // Eixos
    desenhaEixos();

    glFlush(); // GLUT_SINGLE
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

        // Atualiza rotação do quadrado ativo (cíclica 0..359)
        Quadrado& q = quadrados[num_quadrado];
        q.r += 1.f;
        if (q.r >= 360.f) q.r -= 360.f;

        glutPostRedisplay();
    }
}

// -----------------------------
// Teclado ASCII (ESC, espaço, WASD)
// -----------------------------
void Teclado(unsigned char key, int, int) {
    if (key == 27) std::exit(0); // ESC

    if (key == ' ') {
        // cria novo quadrado e seleciona como atual
        quadrados.emplace_back(0.25f, 0.25f);
        num_quadrado = static_cast<int>(quadrados.size()) - 1;

        // esquema de cores como no Python:
        // r = ((n/9) % 3) / 2.0
        // g = ((n/3) % 3) / 2.0
        // b = (n % 3) / 2.0
        int n = num_quadrado;
        quadrados[num_quadrado].cr = std::fmod(n / 9.0f, 3.0f) / 2.0f;
        quadrados[num_quadrado].cg = std::fmod(n / 3.0f, 3.0f) / 2.0f;
        quadrados[num_quadrado].cb = (n % 3) / 2.0f;
    }

    const float step = 0.01f; // pan
    if (key == 'a' || key == 'A') panX -= step;
    if (key == 'd' || key == 'D') panX += step;
    if (key == 'w' || key == 'W') panY += step;
    if (key == 's' || key == 'S') panY -= step;

    glutPostRedisplay();
}

// -----------------------------
// Teclas especiais (setas) — move quadrado ativo
// -----------------------------
void TeclasEspeciais(int key, int, int) {
    const float dx = 0.02f, dy = 0.02f;

    if (key == GLUT_KEY_LEFT)  quadrados[num_quadrado].pos = quadrados[num_quadrado].pos - Ponto(dx, 0.f);
    if (key == GLUT_KEY_RIGHT) quadrados[num_quadrado].pos = quadrados[num_quadrado].pos + Ponto(dx, 0.f);
    if (key == GLUT_KEY_UP)    quadrados[num_quadrado].pos = quadrados[num_quadrado].pos + Ponto(0.f, dy);
    if (key == GLUT_KEY_DOWN)  quadrados[num_quadrado].pos = quadrados[num_quadrado].pos - Ponto(0.f, dy);

    glutPostRedisplay();
}

// -----------------------------
// Inicialização
// -----------------------------
void Inicializa() {
    glMatrixMode(GL_PROJECTION);
    leftV = -1.f; rightV = 1.f; topV = 1.f; bottomV = -1.f;
    gluOrtho2D(leftV + panX, rightV + panX, bottomV + panY, topV + panY);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // reset de temporização
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
    glutCreateWindow("Desenha OpenGL (C++ - Rotacao de Quadrado)");

    glutDisplayFunc(Desenha);
    glutIdleFunc(Animacao);
    glutKeyboardFunc(Teclado);
    glutSpecialFunc(TeclasEspeciais);

    Inicializa();
    glutMainLoop();
    return 0;
}
