
CXX = g++
CXXFLAGS = -Wall -Iinclude -std=c++17
SRC = src/Reader.cpp src/Entity.cpp 2D-Animation.cpp
OBJ = $(addprefix build/, $(notdir $(SRC:.cpp=.o)))
TARGET = build/2D-Animation.exe

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJ)

build/%.o: src/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

build/2D-Animation.o: 2D-Animation.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	del build\Reader.o
	del build\Entity.o
	del build\2D-Animation.o
	del build\2D-Animation.exe

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean
