#!/usr/bin/env python

import fresh
import data2011
f = fresh.foo(inputData = data2011.data(),
              REwk = ["", "FallingExp", "Constant"][0],
              RQcd = ["FallingExp", "Zero"][0],
              signalXs = 4.9, #pb (LM1); 0 or None means SM only
              signalEff = {"had": (0.0,    0.0,    0.02,   0.10),
                           "muon":(0.0,    0.0,    0.002,  0.01),
                           },
              )

#ul = f.upperLimit(makePlot = True); print "Upper limit:",ul
#f.profile()
f.bestFit()
#f.pValue(nToys = 200)
#f.debug()
