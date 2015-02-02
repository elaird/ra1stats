CC=g++
CFLAGS=-Wall -Wextra
ROOT=`root-config --cflags --libs` -lRooFitCore -lRooFit -lRooStats -I${ROOFITSYS}/include  -L${ROOFITSYS}/lib
SO=-shared -fPIC

all: drive StandardHypoTestInvDemo_cxx.so PDFs.so

drive: drive.cxx
	$(CC) $(CFLAGS) $(ROOT) $< -o $@

StandardHypoTestInvDemo_cxx.so: StandardHypoTestInvDemo.cxx
	$(CC) $(CFLAGS) $(SO) $(ROOT) $< -o $@

PDFs.so: Poisson.h Poisson.cxx Gaussian.h Gaussian.cxx Lognormal.h Lognormal.cxx
	rootcling PDFs.cpp Poisson.h Gaussian.h Lognormal.h LinkDef.h
	$(CC) $(CFLAGS) $(SO) $(ROOT) Poisson.cxx Gaussian.cxx Lognormal.cxx PDFs.cpp -o $@

clean:
	rm -f drive
	rm -f PDFs.cpp
	rm -f *.pcm
	rm -f *.d
	rm -f *.so
