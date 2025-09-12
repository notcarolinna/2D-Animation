// main.cpp
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <vector>

// --- Inclui GLUT de forma portátil ---
#if defined(__APPLE__)
  #include <GLUT/glut.h>
#elif defined(_WIN32)
  #include <windows.h>
  #include <GL/freeglut.h>  // Instale o freeglut
#else
  #include <GL/glut.h>
#endif

// -----------------------------
// Classes de apoio
// -----------------------------
struct Ponto {
    float x{0.0f};
    float y{0.0f};

    Ponto() = default;
    Ponto(float x, float y) : x(x), y(y) {}

    void print() const {
        std::cout << "Ponto (" << x << ", " << y << ")\n";
    }

    void set(float nx, float ny) {
        x = nx; y = ny;
    }

    Ponto operator+(const Ponto& o) const { return Ponto(x + o.x, y + o.y); }
    Ponto operator-(const Ponto& o) const { return Ponto(x - o.x, y - o.y); }
    Ponto operator*(float escalar) const  { return Ponto(x * escalar, y * escalar); }
};

struct Quadrado {
    float x, y, w, h; // posição e tamanho (em "unidades" normalizadas/1000)
    float r, g, b;    // cor RGB

    Quadrado(float x, float y, float w, float h, float r, float g, float b)
        : x(x), y(y), w(w), h(h), r(r), g(g), b(b) {}
};

// -----------------------------
// Estado global (como no Python)
// -----------------------------
std::vector<Quadrado> quadrados = {
    {  0,   0, 30, 30, 1,0,0},   { 60,  30, 30, 30, 1,0,1},
    { 40,  80, 30, 30, 0,1,0},   { 90,  70, 30, 30, 0,1,1},
    { 20, 120, 30, 30, 0,0,1},   {225,  30, 30, 30, 1,0,1},
    {115, 210, 30, 30, 1,0,0},   {312, 112, 30, 30, 1,0,1},
    { 50, 260, 30, 30, 0,1,0},   {444, 444, 30, 30, 0,1,1},
    { 30, 330, 30, 30, 0,0,1},   {447, 301, 30, 30, 1,0,1}
};

int num_quadrado = 0;

// “câmera” (janela ortográfica) + pan
float leftV = -1.0f;
float rightV =  1.0f;
float topV =    1.0f;
float bottomV =-1.0f;
float panX = 0.0f;
float panY = 0.0f;

// -----------------------------
// Desenho de eixos
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

// -----------------------------
// Desenho de um quadrado
// -----------------------------
void desenhaQuadrado(float x, float y, float w, float h) {
    glPushMatrix();
    // normaliza (como no Python: divide por 1000.0)
    glTranslatef(x / 1000.0f, y / 1000.0f, 0.0f);

    glBegin(GL_QUADS);
    glVertex2f(0.0f,          0.0f);
    glVertex2f(w / 1000.0f,   0.0f);
    glVertex2f(w / 1000.0f,   h / 1000.0f);
    glVertex2f(0.0f,          h / 1000.0f);
    glEnd();

    glPopMatrix();
}

// -----------------------------
// Callback de display
// -----------------------------
void Desenha() {
    // define a projeção ortográfica com pan
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluOrtho2D(leftV + panX, rightV + panX, bottomV + panY, topV + panY);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // fundo
    glClearColor(0.f, 0.f, 0.f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);

    // desenha todos os quadrados
    for (const auto& q : quadrados) {
        glColor3f(q.r, q.g, q.b);

        // Nota: o seu Python chama desenhaQuadrado(x, y, h, w).
        // Para reproduzir exatamente, faria: desenhaQuadrado(q.x, q.y, q.h, q.w);
        // Porém, semanticamente faz mais sentido (x,y,w,h). Abaixo uso (w,h).
        desenhaQuadrado(q.x, q.y, q.w, q.h);
    }

    // por cima, eixos
    desenhaEixos();

    glFlush(); // GLUT_SINGLE
}

// -----------------------------
// Teclado (ASCII) - WASD + ESC
// -----------------------------
void Teclado(unsigned char key, int, int) {
    if (key == 27) { // ESC
        std::exit(0);
    }

    const float step = 0.01f;
    if (key == 'a' || key == 'A') panX -= step;
    if (key == 'd' || key == 'D') panX += step;
    if (key == 'w' || key == 'W') panY += step;
    if (key == 's' || key == 'S') panY -= step;

    glutPostRedisplay();
}

// -----------------------------
// Teclas especiais (setas) - opcional
// -----------------------------
void TeclasEspeciais(int /*key*/, int /*x*/, int /*y*/) {
    // você pode adicionar controles pelas setas aqui, se quiser
    glutPostRedisplay();
}

// -----------------------------
// Inicialização
// -----------------------------
void Inicializa() {
    glMatrixMode(GL_PROJECTION);
    leftV = -1.0f; rightV = 1.0f; topV = 1.0f; bottomV = -1.0f;
    gluOrtho2D(leftV + panX, rightV + panX, bottomV + panY, topV + panY);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();
}

// -----------------------------
// main
// -----------------------------
int main(int argc, char** argv) {
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB);
    glutInitWindowSize(800, 800);
    glutCreateWindow("Desenha OpenGL (C++)");

    glutDisplayFunc(Desenha);
    glutKeyboardFunc(Teclado);
    glutSpecialFunc(TeclasEspeciais);

    Inicializa();

    glutMainLoop();
    return 0;
}
