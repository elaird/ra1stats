#!/usr/bin/env python
import sys
import ROOT as r

def m0m12() :
    return (float(sys.argv[2]), float(sys.argv[3]))

def pwd() :
    return sys.argv[1]

r.gROOT.LoadMacro("%s/dummy.C"%pwd())
h = r.dummy(*m0m12())
h.Print()
