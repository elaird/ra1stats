#!/usr/bin/env python

import fresh
from inputData import data2010,data2011

def scaled(t, factor) : return tuple([factor*item for item in t])

lm1_2010 = {"xs": 4.9,
            "effHad":  (0.0,    0.0,    0.02,   0.10),
            "effMuon": (0.0,    0.0,    0.002,  0.01)}

lm6_2011 = {"xs": 0.3104,
            "effHad": (0.0,     0.0,     0.005,   0.012,  0.019,  0.022,  0.018,  0.029),
           #"effMuon":(0.0,     0.0,     0.005/6, 0.012/6,0.019/6,0.022/6,0.018/6,0.029/6),#approx. for pT>20 GeV
            "effMuon":scaled((0.045, 0.045, 0.1568, 0.245, 0.3254, 0.3481, 0.2836, 0.3618), 1.0e-2),#pT>10 GeV, |eta|<2.5
            }

p_2011 = {"xs":0.0413,
          "effMuon":[0.000426, 0.000596, 0.001506, 0.000771, 0.000939, 0.000613, 0.000846, 0.005793],
          "effHad": [0.003254, 0.003499, 0.004932, 0.005420, 0.007190, 0.010089, 0.014170, 0.073909],
          }

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
              REwk = ["", "Linear", "Constant"][2],
              RQcd = ["Zero", "FallingExp"][1],
              nFZinv = ["All", "One", "Two"][0],
              #qcdSearch = True,
              #signal = [{}, p_2011, lm6_2011, lm1_2010, filips_point2, sue_anns_point][1],
              signalExampleToStack = ("LM6 (LO)", lm6_2011),
              #signalExampleToStack = ("m0=280 GeV, m12=540 GeV (NLO)", p_2011),
              #signalExampleToStack = ("m0=540 GeV, m12=440 GeV", filips_point1),
              #signalExampleToStack = ("m_{0} = 500 GeV;  m_{1/2} = 440 GeV", filips_point2),
              #signalExampleToStack = ("m0=100 GeV, m12=100 GeV", sue_anns_point),
              #trace = True
              
              #simpleOneBin = {"b": 3.0},
              #hadTerms = False,
              #photTerms = False,
              #muonTerms = False,
              
              #mumuTerms = True,
              #hadControlSamples = ["52_53"],
              #hadControlSamples = ["53_55"],
              #hadControlSamples = ["52_53", "53_55"],
              )

#out = f.interval(cl = 0.95, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
#out = f.cls(cl = 0.95, nToys = 1000, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True, nWorkers = 1); print out
#f.profile()
f.bestFit()
#f.bestFit(printPages = True)
#f.qcdPlot()
#f.pValue(nToys = 300)
#f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
#f.debug()
