#include "Reader.hpp"
#include <iostream>

int main() {
	Reader reader;
	reader.readFile();

	std::cout << "Scale: " << reader.getScale() << std::endl;
	const auto& allEntities = reader.getAllEntities();
	std::cout << "\nEntidades:" << std::endl;
	for (const auto& entityPair : allEntities) {
		int entityId = entityPair.first;
		const auto& entityData = entityPair.second;
		int framesCount = entityData.first;
		const std::vector<coordinates>& coords = entityData.second;
		std::cout << "EntityId: " << entityId << ", FramesCount: " << framesCount << std::endl;
		for (size_t i = 0; i < coords.size(); ++i) {
			std::cout << "  Coord " << i << ": x=" << coords[i].x << ", y=" << coords[i].y << ", frame=" << coords[i].frame << std::endl;
		}
	}

	return 0;
}
