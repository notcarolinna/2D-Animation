#pragma once

#include "Entity.hpp"

#include <string>
#include <fstream>
#include <sstream>
#include <map>

class Reader {
private:
    std::string filename;
    int scale;
    Entity entity;

public:
    Reader(const std::string& filename);
    Reader();
    int getScale() const;
    const Entity& getEntity() const;
    void readFile();

};

