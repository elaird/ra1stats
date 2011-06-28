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

filips_point1 = {'xs': 0.0909,
                'effMuon': [0.0003, 0.0003, 0.0004, 0.0007, 0.0012, 0.0011, 0.0015, 0.0032],
                'effHad':  [0.0015, 0.0014, 0.0043, 0.0043, 0.0067, 0.0091, 0.0115, 0.0392]}

filips_point2 = {"xs":0.0962,
                 "effMuon":[0.0002, 0.0002, 0.0005, 0.0007, 0.0013, 0.0011, 0.0016, 0.0037],
                 "effHad":[0.0014, 0.0017, 0.0026, 0.0054, 0.0084, 0.0107, 0.0153, 0.0451]}

sue_anns_point = {'xs': 2004.,
                  'effMuon': [0.0, 0.0, 9.99e-05, 0.0, 9.99-05, 0.0, 0.0, 0.0],
                  'effHad': [0.0009, 0.0006, 0.0009, 0.0003, 0.0003, 9.99e-05, 0.0, 0.0]}

f = fresh.foo(inputData = data2011(),
              REwk = ["", "FallingExp", "Constant"][2],
              RQcd = ["FallingExp", "Zero"][0],
              #signal = [{}, lm6_2011, lm1_2011, lm1_2010, filips_point, sue_anns_point][-2],
              signalExampleToStack = ("LM6", lm6_2011),
              #signalExampleToStack = ("m0=540 GeV, m12=440 GeV", filips_point1),
              #signalExampleToStack = ("m_{0} = 500 GeV;  m_{1/2} = 440 GeV", filips_point2),
              #signalExampleToStack = ("m0=100 GeV, m12=100 GeV", sue_anns_point),
              #trace = True
              #hadTerms = False,
              #hadControlTerms = False,
              #photTerms = False,
              #muonTerms = False,
              #mumuTerms = True,
              )

#out = f.interval(cl = 0.95, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
#out = f.cls(method = ["CLs", "CLsViaToys"][1], nToys = 100, makePlots = False); print out
#f.profile()
f.bestFit()
#f.bestFit(printPages = True)
#f.pValue(nToys = 300)
#f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
#f.debug()
