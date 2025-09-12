#pragma once

#include "SRU.hpp"
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
    BoundingBox calculateBoundingBox(int entityId) const;
}; 