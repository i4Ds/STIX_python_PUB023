CFLAGS = -Wall -g $(shell python3-config --cflags) -I .
LIBS   = $(shell python3-config --libs) 
CXX    = g++  -std=c++11 -g $(CFLAGS) -fPIC 

cy=$(shell cython3 -3 --embed )
sources=$(wildcard core/*.py)
csource=$(sources:.py=.c)
objects=$(sources:.py=.o)

targets=UI/parser_gui 

targets_py=$(targets:=.py)
targets_c=$(targets:=.c)
targets_o=$(targets:=.o)

all: $(csource) $(objects) $(targets) $(targets_o)
$(targets): $(objects) $(targets_o)
	$(CXX) -o $@  $^  $(LIBS)


$(objects):$(csources)

%.o: %.c
	$(CXX) -o $@ -c $<  

%.c: %.py
	cython3 -3 $<  

$(targets_c):$(targets_py)
	cython3 -3  $^  --embed

.PHONY: clean
clean:
	-rm -f  $(objects) $(csource) $(targets)
test:
	$(targets_py)
	$(targets_c)
