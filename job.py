#!/usr/bin/env python
import sys
import ROOT as r

def pwd() :
    return sys.argv[1]

def fileName() :
    return sys.argv[2]

def funcName() :
    return fileName().split("/")[-1].replace(".C","")

def points() :
    return [(float(sys.argv[i]), float(sys.argv[i+1])) for i in range(3, len(sys.argv), 2)]

r.gROOT.LoadMacro("%s+"%fileName())

for point in points() :
    h = getattr(r, funcName())(*point)
    h.Print()
