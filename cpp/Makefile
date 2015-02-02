CC=g++
CFLAGS=-Wall -Wextra
ROOT=`root-config --cflags --libs` -lRooFitCore -lRooFit -lRooStats -I${ROOFITSYS}/include  -L${ROOFITSYS}/lib
SO=-shared -fPIC
PDF=PDFs.cpp
HS=Poisson.h Gaussian.h Lognormal.h
CXXS=Poisson.cxx Gaussian.cxx Lognormal.cxx

all: drive StandardHypoTestInvDemo_cxx.so PDFs.so

drive: drive.cxx
	$(CC) $(CFLAGS) $(ROOT) $< -o $@

StandardHypoTestInvDemo_cxx.so: StandardHypoTestInvDemo.cxx
	$(CC) $(CFLAGS) $(SO) $(ROOT) $< -o $@

PDFs.so: $(HS) $(CXXS)
	rootcling $(PDF) $(HS) LinkDef.h
	$(CC) $(CFLAGS) $(SO) $(ROOT) $(CXXS) $(PDF) -o $@

clean:
	rm -f drive $(PDF) *.pcm *.d *.so
