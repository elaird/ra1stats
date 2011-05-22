#!/usr/bin/env python

import fresh
import data2011 as data
f = fresh.foo(inputData = data.data(),
              REwk = ["", "FallingExp", "Constant"][2],
              RQcd = ["FallingExp", "Zero"][1],

              ##LM1-like (2011)
              #signalXs = 4.9, #pb
              #signalEff = {"had": (0.006,    0.01,    0.02,   0.029,  0.034,  0.023,  0.011,  0.005),
              #             "muon":(0.0,     0.001,   0.002,   0.003,  0.003,  0.002,  0.001,  0.0, )}

              ##LM1-like (2010)
              #signalXs = 4.9, #pb              
              #signalEff = {"had": (0.0,    0.0,    0.02,   0.10),
              #             "muon":(0.0,    0.0,    0.002,  0.01)}

              #LM6-like (2011)
              signalXs = 0.3104, #pb
              signalEff = {"had": (0.0,     0.0,     0.005,   0.012,  0.019,  0.022,  0.018,  0.029),
                           "muon":(0.0,     0.0,    0.0005,  0.0012, 0.0019, 0.0022, 0.0018, 0.0029)}
              )

#ul = f.upperLimit(makePlot = True); print "Upper limit:",ul
#f.profile()
f.bestFit()
#f.pValue(nToys = 500)
#f.debug()
