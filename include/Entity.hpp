#pragma once

/*
1. Classe Entity
Responsável por representar um objeto na tela (posição, cor, raio, frames, desenho, atualização).
Atributos:
id
x, y
radius
color, alpha
closest (distância até entidade mais próxima)
closestEntity (ponteiro para outra Entity)
index

Métodos principais
update(int w, int h)
normalizeCoords(...)
draw()
getNextFrame()

Features adicionais:
- controlar a bolinha principal (player) com wsad e poder atirar com espaço:
    - se o projétil acertar as outras bolinhas, elas explodem e somem
    - se a bolinha principal acertar as outras bolinhas, o jogo acaba
- adicionar pontuação (score) e mostrar na tela
- adicionar níveis (levels) com mais bolinhas
- adicionar sons (sound effects) para colisões e tiros
*/
#include <vector>

struct Coordinates {
    int x, y, frame;
};

class Entity {
private:
    std::vector<std::vector<Coordinates>> entities;
    std::vector<int> framesCount; 

public:
    Entity();
    void addEntity(const std::vector<Coordinates>& coords, int framesCount);
    const std::vector<std::vector<Coordinates>>& getEntities() const;
    const std::vector<int>& getFramesCount() const;
}; 