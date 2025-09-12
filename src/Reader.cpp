#include "Reader.hpp"

Reader::Reader(const std::string& filename)
    : filename(filename), scale(0), entity() {}

Reader::Reader(){}

int Reader::getScale() const {
    return this->scale;
}

const Entity& Reader::getEntity() const {
    return this->entity;
}

void Reader::readFile() {
    std::ifstream file("./resources/teste.txt");
    int entityId = 0;

    if(!file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    std::string firstLine;
    std::getline(file, firstLine);

    if (!firstLine.empty() && firstLine.front() == '[' && firstLine.back() == ']') {
        std::string scaleStr = firstLine.substr(1, firstLine.size() - 2);
        scale = std::stoi(scaleStr);
    }

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::istringstream iss(line);
        int framesCount;
        iss >> framesCount;

        std::vector<Coordinates> coords;
        char p1;
        while (iss >> p1) {
            if (p1 == '(') {
                float x, y, frame;
                char c1, c2, p2;
                iss >> x >> c1 >> y >> c2 >> frame >> p2;
                if (c1 == ',' && c2 == ',' && p2 == ')') {
                    coords.push_back({x, y, frame});
                }
            }
        }
    entity.addEntity(coords, framesCount);
        ++entityId;
    }
}
