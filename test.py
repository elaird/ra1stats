#!/usr/bin/env python

import common,workspace,likelihoodSpec,signals


f = workspace.foo(likelihoodSpec = likelihoodSpec.spec(),
                  #signalToTest = signals.simple,
                  signalExampleToStack = signals.t1bbbb,
                  #signalToInject = signals.t1,

                  #trace = True
                  #rhoSignalMin = 0.1,
                  #fIniFactor = 0.1,
                  #extraSigEffUncSources = ["effHadSumUncRelMcStats"],
                  )

cl = 0.95 if f.likelihoodSpec.standardPoi() else 0.68
#out = f.interval(cl = cl, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
#out = f.cls(cl = cl, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0},makePlots = True,
#            calculatorType = ["frequentist", "asymptotic", "asymptoticNom"][1],
#            testStatType = 3, nToys = 50, nWorkers = 1,
#            #plSeedParams = {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 7, "minFactor": 0.5, "maxFactor":2.0},
#            plSeedParams = {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 10, "minFactor": 0.0, "maxFactor":3.0},
#            ); print out

#f.profile()
#f.writeMlTable()
f.bestFit(drawMc = False, printValues = True)
#f.bestFit(drawMc = False, printValues = False, drawComponents = False, errorsFromToys = False, drawRatios = False)
#f.bestFit(printPages = True, drawComponents = False, errorsFromToys = True)
#f.qcdPlot()
#f.ensemble(nToys = 3000, stdout = True)
#print f.clsCustom(nToys = 500, testStatType = 1)
#f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
#f.debug()
#f.cppDrive(tool = "")
