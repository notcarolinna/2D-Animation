#include "Reader.hpp"

Reader::Reader(const std::string& filename)
    : filename(filename), entity() {}

Reader::Reader(){}

int Reader::getScale() const {
    return sru.getScale(); 
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
        sru.setScale(std::stoi(scaleStr)); // Armazene o scale na SRU
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
                char v1, v2, p2;
                iss >> x >> v1 >> y >> v2 >> frame >> p2;
                if (v1 == ',' && v2 == ',' && p2 == ')') {
                    coords.push_back({x, y, frame});
                }
            }
        }
        entity.addEntity(coords, framesCount);
        ++entityId;
    }
}