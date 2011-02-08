#!/usr/bin/env python
import data, ROOT as r
from simpleCLs import *

n_susy = 10.25
print "CLS with n_susy expected = %0.1f" % n_susy

cls = simpleCLs( data.numbers() )
result = cls.CLsHypoTest(n_susy)
result.Print()
canvas = r.TCanvas()
r.RooStats.HypoTestPlot(result,30).Draw() # 30 bins, TS is discrete
