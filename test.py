#!/usr/bin/env python

import common,workspace,likelihoodSpec,signals

def go(iLower = None, iUpper = None, dataset = "2011", ensemble = False) :
    spec = likelihoodSpec.spec(iLower = iLower, iUpper = iUpper,
                               dataset = dataset, separateSystObs = not ensemble)

    model_sel = 2
    signalExampleToStack = {"2011": [signals.t2bb, signals.t1, signals.t2tt2][model_sel],
                            "2012ichep": signals.t1tttt_2012_3,
                            "2012dev": {},
                            }[dataset]
    signalLineStyle = model_sel+1

    nToys = {"2011":3000,
             "2012ichep":1000,
             "2012dev":0,
             }[dataset]

    f = workspace.foo(likelihoodSpec = spec,
                      #signalToTest = signals.t2tt2,
                      signalExampleToStack = signalExampleToStack
                      #signalToInject = signals.t1,
                      #trace = True
                      #rhoSignalMin = 0.1,
                      #fIniFactor = 0.1,
                      #extraSigEffUncSources = ["effHadSumUncRelMcStats"],
                      )

    if ensemble :
        f.ensemble(nToys = nToys, stdout = True)
        return

    #cl = 0.95 if f.likelihoodSpec.standardPoi() else 0.68
    #out = f.interval(cl = cl, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
    #out = f.cls(cl = cl, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0},makePlots = True,
    #            calculatorType = ["frequentist", "asymptotic", "asymptoticNom"][1],
    #            testStatType = 3, nToys = 50, nWorkers = 1,
    #            #plSeedParams = {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 7, "minFactor": 0.5, "maxFactor":2.0},
    #            plSeedParams = {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 10, "minFactor": 0.0, "maxFactor":3.0},
    #            ); print out
    #
    #f.profile()
    #f.writeMlTable()
    f.bestFit(drawMc = False, printValues = True, errorsFromToys = False, pullPlotMax = 4.0, pullThreshold = 5.0)
    #f.bestFit(printPages = True, drawComponents = False, errorsFromToys = nToys, signalLineStyle = signalLineStyle)
    #f.bestFit(drawMc = False, drawComponents = False, errorsFromToys = nToys)
    #f.qcdPlot()
    #print f.clsCustom(nToys = 500, testStatType = 1)
    #f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
    #f.debug()
    #f.cppDrive(tool = "")

kargs = {"dataset" : ["2011", "2012ichep", "2012dev"][0],
         "ensemble": False,
         }
if kargs["dataset"]=="2011" :
    go(**kargs)
else :
    nSelections = len(likelihoodSpec.spec(dataset = kargs["dataset"]).selections())
    for iLower in range(nSelections) :
        args = {"iLower":iLower, "iUpper":1+iLower}
        args.update(kargs)
        go(**args)
