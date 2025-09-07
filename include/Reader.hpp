#pragma once

#include <string>
#include <fstream>
#include <sstream>
#include <map>
#include <vector>
#include <iostream>

/*
O que eu preciso ter: 
1. Armazenar o primeiro valor de cada arquivo, ignorando o primeiro caractere que é um [, pegar o inteiro e armazenar na variável scale e ignorar o próximo caractere que é um ].
2. Criar uma struct para armazenar o (x,y,frame) de cada entidade
3. Criar um vector com a struct de cada entidade
4. Criar um pair onde a chave é o número de frames que a entidade aparece e o valor é o vector de structs
5. Criar um map onde a chave é o id da entidade e o valor é o pair 
*/

struct coordinates {
    float x;
    float y;
    float frame;
};

class Reader {
    private:
        std::string filename;
        int scale;
        std::vector<coordinates> coordinatesList;
        std::pair<int, std::vector<coordinates>> entity; 
        std::map<int, std::pair<int, std::vector<coordinates>>> allEntities;

    public:
        Reader(const std::string& filename);
        Reader();
        int getScale() const;
        std::vector<coordinates> getCoordinatesList() const;
        std::pair<int, std::vector<coordinates>> getEntity() const;
        std::map<int, std::pair<int, std::vector<coordinates>>> getAllEntities() const;
        void readFile();
};
