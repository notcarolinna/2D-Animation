#include "Entity.hpp"

Entity::Entity() {}

void Entity::addEntity(const std::vector<Coordinates>& coords, int framesCount) {
    entities.push_back(coords);
    this->framesCount.push_back(framesCount);
}

const std::vector<std::vector<Coordinates>>& Entity::getEntities() const {
    return entities;
}

const std::vector<int>& Entity::getFramesCount() const {
    return framesCount;
}

BoundingBox Entity::calculateBoundingBox(int entityId) const {
    BoundingBox box{0, 0, 0, 0};
    if (entityId < 0 || entityId >= static_cast<int>(entities.size())) return box;
    const auto& coords = entities[entityId];
    if (coords.empty()) return box;
    box.xMin = box.xMax = coords[0].x;
    box.yMin = box.yMax = coords[0].y;
    for (const auto& c : coords) {
        if (c.x < box.xMin) box.xMin = c.x;
        if (c.x > box.xMax) box.xMax = c.x;
        if (c.y < box.yMin) box.yMin = c.y;
        if (c.y > box.yMax) box.yMax = c.y;
    }
    return box;
}