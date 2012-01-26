#!/usr/bin/env python

import workspace
import likelihoodSpec

def signal(i) :

    def scaled(t, factor) :
        return tuple([factor*item for item in t])

    lm1_2010 = {"xs": 4.9,
                "effHad":  (0.0,    0.0,    0.02,   0.10),
                "effMuon": (0.0,    0.0,    0.002,  0.01),
                "label":"LM1 (LO)",
                }

    lm6_2011 = {"xs": 0.3104,
                "effHad": (0.0,     0.0,     0.005,   0.012,  0.019,  0.022,  0.018,  0.029),
                #"effMuon":(0.0,     0.0,     0.005/6, 0.012/6,0.019/6,0.022/6,0.018/6,0.029/6),#approx. for pT>20 GeV
                "effMuon":scaled((0.045, 0.045, 0.1568, 0.245, 0.3254, 0.3481, 0.2836, 0.3618), 1.0e-2),#pT>10 GeV, |eta|<2.5
                "label":"LM6 (LO)",
                }

    lm1_2011 = {"xs":4.9,
                "effHad":(0.0059, 0.0091, 0.0285, 0.0328, 0.0218, 0.0105, 0.0046, 0.0042),
                "effMuon":tuple([0.0]*8),
                }

    p_29_25 = {"xs":5.4534794,
               "effMuon":[0.000146, 0.000833, 0.001835, 0.001565, 0.001366, 0.001371, 0.000196, 8.888631e-05],
               "effHad": [0.001417, 0.003229, 0.018751, 0.021711, 0.023040, 0.013011, 0.007199, 0.005279],
               "label":"m0= 280 GeV, m12=240 GeV (NLO)",
               }
    
    p_29_55 = {"xs":0.0413,
               "effMuon":[0.000426, 0.000596, 0.001506, 0.000771, 0.000939, 0.000613, 0.000846, 0.005793],
               "effHad": [0.003254, 0.003499, 0.004932, 0.005420, 0.007190, 0.010089, 0.014170, 0.073909],
               "label":"m0= 280 GeV, m12=540 GeV (NLO)"
               }
    
    p_181_19 = {"xs":5.6887135,
                "effMuon":[0.000147, 0.000000, 0.000441, 0.000588, 0.000147, 0.000147, 0.000147, 0.000000],
                "effHad": [0.000231, 0.001030, 0.003325, 0.003974, 0.001766, 0.000588, 0.000000, 0.000000],
                "label":"m_{0}=1800 GeV, m_{1/2}=180 GeV (NLO)",
                }
    
    filips_point1 = {'xs': 0.0909,
                     'effMuon': [0.0003, 0.0003, 0.0004, 0.0007, 0.0012, 0.0011, 0.0015, 0.0032],
                     'effHad':  [0.0015, 0.0014, 0.0043, 0.0043, 0.0067, 0.0091, 0.0115, 0.0392],
                     "label": "m0=540 GeV, m12=440 GeV",
                     }
    
    filips_point2 = {"xs":0.0962,
                     "effMuon":[0.0002, 0.0002, 0.0005, 0.0007, 0.0013, 0.0011, 0.0016, 0.0037],
                     "effHad":[0.0014, 0.0017, 0.0026, 0.0054, 0.0084, 0.0107, 0.0153, 0.0451],
                     "label":"m_{0} = 500 GeV;  m_{1/2} = 440 GeV",
                     }
    
    sue_anns_point = {'xs': 2004.,
                      'effMuon': [0.0, 0.0, 9.99e-05, 0.0, 9.99-05, 0.0, 0.0, 0.0],
                      'effHad': [0.0009, 0.0006, 0.0009, 0.0003, 0.0003, 9.99e-05, 0.0, 0.0],
                      "label": "m0=100 GeV, m12=100 GeV",
                      }
    
    t1_600_100 = {"xs":1.0,
                  "effMuon":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  "effHad":[0.0016, 0.0033, 0.0142, 0.0283, 0.0341, 0.0210, 0.0099, 0.0075],
                  "label":"T1 m_{gluino} = 600 GeV, m_{LSP} = 100 GeV, xs = 1.0 pb",
                  }
    
    t2_39_7 = {"xs":1.0,
               "effMuon":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               "effHad":[0.0006, 0.0015, 0.0058, 0.0129, 0.0252, 0.0399, 0.0494, 0.2123],
               "label":"T2 39 7, xs = 1.0 pb",
               }
    
    broken = {
        "nEventsHad":328.0,
        "nEventsIn":10000.0,
        "effHadSumUncRelMcStats":0.0552157630374,
        "effMuonSum":0.0,
        "effHadSum":0.0328,
        "effMuon":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "effHad":[0.0159, 0.0089, 0.0058, 0.0017, 0.0003, 0.0002, 0.0, 0.0],
        "nEventsMuon":0.0,
        "xs":1.0,
        }
    
    return [{}, p_29_25, p_29_55, p_181_19, lm6_2011, lm1_2010, filips_point2, sue_anns_point, t1_600_100, t2_39_7, broken][i]

f = workspace.foo(likelihoodSpec = likelihoodSpec.spec(),
                  #signal = {"55":signal(3), "2010":signal(5)},
                  signalExampleToStack = {"55":signal(3), "2010":signal(5)},

                  #trace = True
                  #rhoSignalMin = 0.1,
                  #extraSigEffUncSources = ["effHadSumUncRelMcStats"],
                  )

cl = 0.95 if not f.likelihoodSpec["qcdSearch"] else 0.68
#out = f.interval(cl = cl, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
#out = f.cls(cl = cl, calculatorType = 0, testStatType = 3, nToys = 2000,
#            plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True, nWorkers = 6); print out
#f.profile()
f.bestFit()
#f.bestFit(printPages = True)
#f.qcdPlot()
#f.pValue(nToys = 300)
#f.ensemble(nToys = 1000)
#print f.clsCustom(nToys = 500, testStatType = 1)
#f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
#f.debug()
