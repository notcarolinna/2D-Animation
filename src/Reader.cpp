#include "Reader.hpp"

Reader::Reader(const std::string& filename)
    : filename(filename), scale(0) {}

Reader::Reader(){
    scale = 0;
}

int Reader::getScale() const {
    return this->scale;
}

std::vector<coordinates> Reader::getCoordinatesList() const {
    return this->coordinatesList;
}

std::pair<int, std::vector<coordinates>> Reader::getEntity() const {
    return this->entity;
}

std::map<int, std::pair<int, std::vector<coordinates>>> Reader::getAllEntities() const {
    return this->allEntities;
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
        scale = std::stoi(firstLine.substr(1, firstLine.size() - 2));
    }


    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::istringstream iss(line);
        int framesCount;
        iss >> framesCount;

        std::vector<coordinates> coordinatesList;
        char c;
        while (iss >> c) {
            if (c == '(') {
                coordinates coord;
                char comma1, comma2, closeParen;
                iss >> coord.x >> comma1 >> coord.y >> comma2 >> coord.frame >> closeParen;
                if (comma1 == ',' && comma2 == ',' && closeParen == ')') {
                    coordinatesList.push_back(coord);
                }
            }
        }
        allEntities[entityId++] = std::make_pair(framesCount, coordinatesList);
    }
}