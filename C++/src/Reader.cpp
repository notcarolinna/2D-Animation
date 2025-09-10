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
        char c;
        while (iss >> c) {
            if (c == '(') {
                float x, y, frame;
                char comma1, comma2, closeParen;
                iss >> x >> comma1 >> y >> comma2 >> frame >> closeParen;
                if (comma1 == ',' && comma2 == ',' && closeParen == ')') {
                    coords.push_back({x, y, frame});
                }
            }
        }
    entity.addEntity(coords, framesCount);
        ++entityId;
    }
}

/*
Para cada linha lida, eu preciso:
1. Se for a primeira linha, pegar o valor do scale (ignorando os colchetes)
2. Para o restante do arquivo, eu preciso:
    2.1 Chamar a função getFramesCount da classe Entity para pegar o número de frames da entidade atual
    2.2 Chamar a função addEntity da classe Entity para adicionar os pontos da entidade atual
     *Deve-se ignorar os () e as vírgulas
3. Incrementar o entityId para a próxima entidade
*/