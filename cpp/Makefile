CC=g++
CFLAGS=-Wall -Wextra
ROOT=`root-config --cflags --libs` -lRooFitCore -lRooFit -lRooStats -I${ROOFITSYS}/include  -L${ROOFITSYS}/lib
SO=-shared -fPIC

all: drive Poisson_cxx.so

drive: drive.cxx
	$(CC) $(CFLAGS) $(ROOT) $< -o $@

Poisson_cxx.so: Poisson.h Poisson.cxx
	$(CC) $(CFLAGS) $(SO) $(ROOT) $< -o $@

clean:
	rm -rf drive
	rm -rf Poisson_cxx.so
