#!/usr/bin/env python
import sys
import ROOT as r

def pwd() :
    return sys.argv[1]

def points() :
    return [(float(sys.argv[i]), float(sys.argv[i+1])) for i in range(2, len(sys.argv), 2)]

r.gROOT.LoadMacro("%s/dummy.C"%pwd())

for point in points() :
    h = r.dummy(*point)
    h.Print()
