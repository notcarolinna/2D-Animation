#pragma once

#include "Entity.hpp"
#include "SRU.hpp"

#include <string>
#include <fstream>
#include <sstream>
#include <map>

class Reader {
private:
    std::string filename;
    SRU sru;
    Entity entity;

public:
    Reader(const std::string& filename);
    Reader();
    int getScale() const;
    const Entity& getEntity() const;
    void readFile();
};

