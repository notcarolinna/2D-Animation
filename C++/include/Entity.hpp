#pragma once

#include <vector>

struct Coordinates {
    float x;
    float y;
    float frame;
};

struct BoundingBox {
    float xMin;
    float yMin;
    float xMax;
    float yMax;
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
    BoundingBox calculateBoundingBox(int entityId) const;
    BoundingBox getGlobalBoundingBox() const;
};