#!/usr/bin/env python
import sys,cPickle,fresh
import configuration as conf

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def writeNumbers(fileName = None, d = None) :
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()

def go() :
    for point in points() :
        f = fresh.foo(REwk = ["", "FallingExp", "Constant"][0],
                      RQcd = ["FallingExp", "Zero"][0],
                      signalXs = 4.9, #pb (LM1); 0 or None means SM only
                      signalEff = {"had": (0.0,    0.0,    0.02,   0.10),
                                   "muon":(0.0,    0.0,    0.002,  0.01),
                                   },
                      )
        ul = f.upperLimit()
        writeNumbers(conf.strings(*point)["pickledFileName"], {"upperLimit":ul})

profile = False
if profile :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
