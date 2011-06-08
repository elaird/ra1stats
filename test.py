#!/usr/bin/env python

import fresh
from inputData import data2010,data2011

lm1_2011 = {"xs": 4.9,
            "effHad":  (0.006,    0.01,    0.02,   0.029,  0.034,  0.023,  0.011,  0.005),
            "effMuon": (0.0,     0.001,   0.002,   0.003,  0.003,  0.002,  0.001,  0.0, )}

lm1_2010 = {"xs": 4.9,
            "effHad":  (0.0,    0.0,    0.02,   0.10),
            "effMuon": (0.0,    0.0,    0.002,  0.01)}

lm6_2011 = {"xs": 0.3104,
            "effHad": (0.0,     0.0,     0.005,   0.012,  0.019,  0.022,  0.018,  0.029),
            "effMuon":(0.0,     0.0,     0.005/6, 0.012/6,0.019/6,0.022/6,0.018/6,0.029/6)}

f = fresh.foo(inputData = data2011(),
              REwk = ["", "FallingExp", "Constant"][2],
              RQcd = ["FallingExp", "Zero"][1],
              signal = [{}, lm6_2011, lm1_2011, lm1_2010][0],
              signalExampleToStack = ("LM6", lm6_2011),
              )


#out = f.interval(cl = 0.95, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
#out = f.cls(method = ["CLs", "CLsViaToys"][1], nToys = 100, makePlots = False); print out
#f.profile()
f.bestFit()
#f.pValue(nToys = 500)
#f.debug()
