#include "Reader.hpp"
#include "Entity.hpp"
#include <iostream>

int main() {
	Reader reader;
	reader.readFile();

	std::cout << "Scale: " << reader.getScale() << std::endl;
	
	const Entity& entity = reader.getEntity();
	const auto& entities = entity.getEntities();
	const auto& framesCount = entity.getFramesCount();

	std::cout << "Entities:" << std::endl;
	for (size_t entityId = 0; entityId < entities.size(); ++entityId) {
		std::cout << "EntityId: " << entityId << ", FramesCount: " << framesCount[entityId] << std::endl;
		const auto& coords = entities[entityId];
		for (size_t i = 0; i < coords.size(); ++i) {
			std::cout << "  Coord " << i << ": x=" << coords[i].x << ", y=" << coords[i].y << ", frame=" << coords[i].frame << std::endl;
		}
		BoundingBox box = entity.calculateBoundingBox(entityId);
		std::cout << "  BoundingBox: xMin=" << box.xMin << ", xMax=" << box.xMax << ", yMin=" << box.yMin << ", yMax=" << box.yMax << std::endl;
	}

	BoundingBox globalBox = entity.getGlobalBoundingBox();
	std::cout << "\nGlobal BoundingBox: xMin=" << globalBox.xMin << ", xMax=" << globalBox.xMax << ", yMin=" << globalBox.yMin << ", yMax=" << globalBox.yMax << std::endl;
	return 0;
}
