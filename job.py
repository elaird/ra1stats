#!/usr/bin/env python
import os,sys,cPickle
import ROOT as r
import configuration as conf
import data,utils
import lepton

def pwd() :
    return sys.argv[1]

def fileName() :
    return sys.argv[2]

def funcName() :
    return fileName().split("/")[-1].replace(".C+","").replace(".C","")

def libName() :
    return funcName()+"_C.so"

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(3, len(sys.argv), 3)]

def signalYields(fileName) :
    inFile = open(fileName)
    stuff = cPickle.load(inFile)
    inFile.close()
    os.remove(fileName)

    out = {}
    for key,value in stuff.iteritems() :
        if value is None : continue
        out[key] = value
    return out
    
for lib in ["AutoDict_std__pair_std__string_std__string__cxx.so",
            "AutoDict_std__map_std__string_std__string__cxx.so",
            "AutoDict_std__pair_std__string_std__vector_double____cxx.so",
            "AutoDict_std__map_string_vector_double____cxx.so",
            libName(),
            ] :
    assert not r.gSystem.Load(lib), "Could not load library %s"%lib

for point in points() :
    lepton.Lepton(conf.switches(),
                  conf.histoSpecs(),
                  conf.strings(*point),
                  signalYields(conf.strings(*point)["configFileName"]),
                  utils.stdMap_String_VectorDoubles(data.numbers()),
                  *point
                  )
