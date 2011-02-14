#!/usr/bin/env python
import sys
import configuration as conf
import data,lepton

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(3, len(sys.argv), 3)]

def go() :
    for point in points() :
        lepton.Lepton(conf.switches(),
                      conf.histoSpecs(),
                      conf.strings(*point),
                      data.numbers(),
                      *point
                      )

profile = False
if profile :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
