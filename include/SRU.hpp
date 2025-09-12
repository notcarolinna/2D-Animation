#pragma once

// A bounding box da SRU é um valor estático definido (geralmente o tamanho da tela)
// Então screenSize = 800x800

class SRU {
    private:
    int scale;

    public: 
    SRU();
    void setScale(int s);
    int getScale() const;
}; 
