#!/usr/bin/env python

import common
import likelihoodSpec
import plotting
import signals2
import workspace
import ROOT as r


def go(whiteList=[], dataset="", allCategories=[], ignoreHad=False,
       bestFit=False, interval=False, ensemble=False):

    ls = likelihoodSpec.spec(whiteList=whiteList,
                             dataset=dataset,
                             ignoreHad=ignoreHad,
                             separateSystObs=not ensemble
                             )

    examples_paper = {("0b_le3j",): signals2.t2,
                      ("0b_ge4j",): signals2.t1,
                      ("1b_le3j",): signals2.t2bb,
                      ("1b_ge4j",): signals2.t2tt,
                      ("2b_le3j",): signals2.t2bb,
                      ("2b_ge4j",): signals2.t2tt,
                      ("3b_le3j",): {},
                      ("3b_ge4j",): signals2.t1bbbb,
                      ("ge4b_ge4j",): signals2.t1tttt,
                      }

    examples_t2cc = {("0b_le3j",): signals2.t2cc,
                     ("0b_ge4j",): signals2.t2cc,
                     ("1b_le3j",): signals2.t2cc,
                     ("1b_ge4j",): signals2.t2cc,
                     ("2b_le3j",): signals2.t2cc,
                     ("2b_ge4j",): signals2.t2cc,
                     ("3b_le3j",): {},
                     ("3b_ge4j",): {},
                     ("ge4b_ge4j",): {},
                     }

    examples = examples_paper
    signal = examples[tuple(whiteList)] if tuple(whiteList) in examples else {}

    assert not (interval and bestFit)

    if interval:
        signalToTest = signal
        signalToInject = {}
        signalExampleToStack = {}

    if bestFit:
        signalToTest = {}
        signalToInject = {}
        signalExampleToStack = signal

    f = workspace.foo(likelihoodSpec=ls,
                      signalToTest=signalToTest,
                      signalExampleToStack=signalExampleToStack,
                      signalToInject=signalToInject,
                      #trace=True
                      #rhoSignalMin=0.1,
                      #fIniFactor=0.1,
                      #extraSigEffUncSources=["effHadSumUncRelMcStats"],
                      )

    out = None
    nToys = {"": 0, "2010": 300, "2011eps": 300, "2011": 3000,
             "2012ichep": 1000, "2012hcp": 300,
             "2012hcp2": 300, "2012dev": 300}[dataset]

    if ensemble:
        f.ensemble(nToys=nToys, stdout=True)
        return out

    if interval:
        cl = 0.95 if f.likelihoodSpec.standardPoi() else 0.68
        out = f.interval(cl=cl,
                         method=["profileLikelihood", "feldmanCousins"][0],
                         makePlots=True,
                         )
        print out
        #f.profile()

    #out = f.cls(cl=cl,
    #            makePlots=True,
    #            testStatType=3,
    #            nToys=50,
    #            nWorkers=1,
    #            plusMinus={"OneSigma": 1.0,
    #                       "TwoSigma": 2.0},
    #            calculatorType=["frequentist",
    #                            "asymptotic",
    #                            "asymptoticNom"][1],
    #            #plSeedParams={"usePlSeed": True,
    #            #              "plNIterationsMax": 10,
    #            #              "nPoints": 7,
    #            #              "minFactor": 0.5,
    #            #              "maxFactor":2.0},
    #            plSeedParams={"usePlSeed": True,
    #                          "plNIterationsMax": 10,
    #                          "nPoints": 10,
    #                          "minFactor": 0.0,
    #                          "maxFactor":3.0},
    #            ); print out
    #
    #f.writeMlTable(fileName="mlTables_%s.tex" % "_".join(whiteList),
    #               categories=allCategories)

    if bestFit:
        out = f.bestFit(drawMc=False,
                        drawComponents=False,
                        errorsFromToys=nToys,
                        printPages=False,
                        )

    #f.qcdPlot()
    #f.debug()
    #f.cppDrive(tool="")
    return out

kargs = {"bestFit": True,
         "interval": False,
         "ensemble": False,
         "dataset": ["", "2010", "2011eps", "2011",
                     "2012ichep", "2012hcp", "2012hcp2", "2012dev"][-3],
         }

if kargs["dataset"] == "2011":
    go(**kargs)
else:
    selections = likelihoodSpec.spec(dataset=kargs["dataset"]).selections()
    hMap = {}
    bins = (len(selections), 0.0, len(selections))
    for key in ["chi2ProbSimple", "chi2Prob", "lMax"]:
        hMap[key] = r.TH1D("pValueMap_%s" % key, ";category;p-value", *bins)

    for iSel, sel in enumerate(selections):
        args = {"whiteList": [sel.name],
                "allCategories": sorted([x.name for x in selections]),
                }
        args.update(kargs)
        dct = go(**args)
        if not dct:
            continue
        for key, pValue in dct.iteritems():
            if key not in hMap:
                continue
            hMap[key].GetXaxis().SetBinLabel(1+iSel, sel.name)
            hMap[key].SetBinContent(1+iSel, pValue)

    plotting.pValueCategoryPlots(hMap, )  # logYMinMax=(1.0e-4, 1.0e2))
