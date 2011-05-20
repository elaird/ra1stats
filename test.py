#!/usr/bin/env python

import fresh
import data2011 as data
f = fresh.foo(inputData = data.data(),
              REwk = ["", "FallingExp", "Constant"][1],
              RQcd = ["FallingExp", "Zero"][1],
              signalXs = 4.9, #pb (LM1); 0 or None means SM only
              signalEff = {"had": (0.006,    0.01,    0.02,   0.029,  0.034,  0.023,  0.011,  0.005, 0.005),
                           "muon":(0.0,     0.001,   0.002,   0.003,  0.003,  0.002,  0.001,  0.0,   0.0  ),
                           },
              #signalEff = {"had": (0.0,    0.0,    0.02,   0.10), #2010 binning
              #             "muon":(0.0,    0.0,    0.002,  0.01),
              )

#ul = f.upperLimit(makePlot = True); print "Upper limit:",ul
#f.profile()
f.bestFit()
#f.pValue(nToys = 200)
#f.debug()
