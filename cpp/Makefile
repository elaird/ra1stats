CC=g++
CFLAGS=-Wall -Wextra
ROOT=`root-config --cflags --libs` -lRooFitCore -lRooFit -lRooStats -I${ROOFITSYS}/include  -L${ROOFITSYS}/lib

drive: drive.cxx
	$(CC) $(CFLAGS) $(ROOT) $< -o $@

clean:
	rm -rf drive