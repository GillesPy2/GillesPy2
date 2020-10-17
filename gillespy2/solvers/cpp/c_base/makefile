CC=g++
CFLAGS=-c -std=c++14 -Wall -O3
SIMFLAGS = -L. -std=c++14 -Wall -O3
DEPS = model.h ssa.h
OBJ = model.o ssa.o
.PHONY: all

all: UserSimulation

%.o: %.cpp $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

UserSimulation.o:
	$(CC) -c -o UserSimulation.o UserSimulation.cpp $(CFLAGS)

UserSimulation: $(OBJ) UserSimulation.o
	$(CC) -o UserSimulation $(OBJ) UserSimulation.o $(SIMFLAGS)

model.o:
	$(CC) -c -o model.o model.cpp $(CFLAGS)

ssa.o:
	$(CC) -c -o ssa.o ssa.cpp $(CFLAGS)

assembleSolvers: $(OBJ)

cleanSimulation:
	rm -f UserSimulation

clean:
	rm -f *.o *~
