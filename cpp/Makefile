CC=g++
CFLAGS=-Wall -Wextra
ROOT=`root-config --cflags --libs` -lRooFitCore -lRooFit -lRooStats -I${ROOFITSYS}/include  -L${ROOFITSYS}/lib
SO=-shared -fPIC

all: drive Poisson_cxx.so Gaussian_cxx.so Lognormal_cxx.so

drive: drive.cxx
	$(CC) $(CFLAGS) $(ROOT) $< -o $@

Poisson_cxx.so: Poisson.h Poisson.cxx
	$(CC) $(CFLAGS) $(SO) $(ROOT) $< -o $@

Gaussian_cxx.so: Gaussian.h Gaussian.cxx
	$(CC) $(CFLAGS) $(SO) $(ROOT) $< -o $@

Lognormal_cxx.so: Lognormal.h Lognormal.cxx
	$(CC) $(CFLAGS) $(SO) $(ROOT) $< -o $@

clean:
	rm -rf drive
	rm -rf Poisson_cxx.so
	rm -rf Gaussian_cxx.so
	rm -rf Lognormal_cxx.so
