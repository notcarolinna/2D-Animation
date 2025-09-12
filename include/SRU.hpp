#pragma once

// Eu puxo a bounding box das entidades para calcular a bounding box do mundo
// Então preciso declarar a classe BoundingBox aqui

class Entity;

struct BoundingBox {
    float xMin, yMin, xMax, yMax;
};

class SRU {
    private:
    int scale;
    BoundingBox worldBoundingBox;

    public: 
    SRU();
    void setScale(int s);
    int getScale() const;
    BoundingBox getWorldBoundingBox() const;
}; 