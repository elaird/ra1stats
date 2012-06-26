#!/usr/bin/env python

import common,workspace,likelihoodSpec,signals

def go(iLower = None, iUpper = None, year = 2011, ensemble = False) :
    f = workspace.foo(likelihoodSpec = likelihoodSpec.spec(iLower = iLower,
                                                           iUpper = iUpper,
                                                           year = year,
                                                           separateSystObs = not ensemble,
                                                           ),
                      #signalToTest = signals.t2tt2,
                      #signalExampleToStack = signals.t2tt2,
                      #signalToInject = signals.t1,
                      #trace = True
                      #rhoSignalMin = 0.1,
                      #fIniFactor = 0.1,
                      #extraSigEffUncSources = ["effHadSumUncRelMcStats"],
                      )

    if ensemble :
        f.ensemble(nToys = 300, stdout = True)
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
    #f.bestFit(drawMc = False, printValues = True, pullPlotMax = 6.0)
    #f.bestFit(drawMc = False, printValues = False, drawComponents = False)
    #f.bestFit(drawMc = False, printValues = False, drawComponents = False, errorsFromToys = False, drawRatios = False)
    #f.bestFit(printPages = True, drawComponents = False, errorsFromToys = True)
    #f.qcdPlot()
    #print f.clsCustom(nToys = 500, testStatType = 1)
    #f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
    #f.debug()
    #f.cppDrive(tool = "")

year2012 = False

if year2012 :
    for iLower in range(5) :
        go(iLower = iLower, iUpper = 1+iLower, year = 2012, ensemble = False)
else :
    go() #2011
