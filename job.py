#!/usr/bin/env python
import sys
import ROOT as r
import configuration as conf
import data,lepton

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(2, len(sys.argv), 3)]

for point in points() :
    lepton.Lepton(conf.switches(),
                  conf.histoSpecs(),
                  conf.strings(*point),
                  data.numbers(),
                  *point
                  )
