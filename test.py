#!/usr/bin/env python

import driver
import likelihood
import plotting
from signals import t2, two, t2cc

import ROOT as r


def printReport(report={}):
    header = None
    for cat, dct in sorted(report.iteritems()):
        if not header:
            keys = sorted(dct.keys())
            l = max([len(key) for key in keys])
            fmt = "%"+str(l)+"s"
            header = " ".join([fmt % "cat"] + [fmt % key for key in keys])
            print header
            print "-"*len(header)
        out = [fmt % cat]
        for key in keys:
            value = dct[key]
            sValue =  str(value) if type(value) is int else "%6.4f" % value
            out.append(fmt % sValue)
        print " ".join(out)


def go(whiteList=[], llk="", allCategories=[], ignoreHad=False, sigMcUnc=False,
       bestFit=False, interval=False, ensemble=False, ensembleReuse=False):

    examples_paper = {("0b_le3j",): t2.a,
                      ("0b_ge4j",): two.t1,
                      ("1b_le3j",): two.t2bb,
                      ("1b_ge4j",): two.t2tt,
                      ("2b_le3j",): two.t2bb,
                      ("2b_ge4j",): two.t2tt,
                      ("3b_le3j",): {},
                      ("3b_ge4j",): two.t1bbbb,
                      ("ge4b_ge4j",): two.t1tttt,
                      }

    examples_t2cc = {("0b_le3j",): t2cc.far10,
                     ("0b_ge4j",): t2cc.far10,
                     ("1b_le3j",): t2cc.far10,
                     ("1b_ge4j",): t2cc.far10,
                     ("2b_le3j",): {},
                     ("2b_ge4j",): {},
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
        signalExampleToStack = {}#signal

    f = driver.driver(llkName=llk,
                      whiteList=whiteList,
                      ignoreHad=ignoreHad,
                      separateSystObs=not ensemble,
                      signalToTest=signalToTest,
                      signalExampleToStack=signalExampleToStack,
                      signalToInject=signalToInject,
                      #trace=True
                      #rhoSignalMin=0.1,
                      #fIniFactor=0.1,
                      )

    out = None
    nToys = {"": 0, "2010": 300, "2011eps": 300, "2011": 3000,
             "2012ichep": 1000, "2012hcp": 300,
             "2012hcp2": 300, "2012dev": 0}[llk]

    if ensemble:
        f.ensemble(nToys=nToys, stdout=True, reuseResults=ensembleReuse)
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
                        drawRatios=False,
                        significance=ignoreHad,
                        #msgThreshold=r.RooFit.DEBUG,
                        msgThreshold=r.RooFit.WARNING,
                        )

    #f.qcdPlot()
    #f.debug()
    #f.cppDrive(tool="")
    return out

kargs = {"bestFit": True,
         "interval": False,
         "ensemble": False,
         "ensembleReuse": False,
         "llk": ["", "2010", "2011eps", "2011",
                 "2012ichep", "2012hcp", "2012hcp2", "2012dev"][-1],
         }


if kargs["llk"] == "2011":
    go(**kargs)
else:
    selections = likelihood.spec(name=kargs["llk"]).selections()
    report = {}
    hMap = {}
    bins = (len(selections), 0.0, len(selections))
    for key in ["chi2ProbSimple", "chi2Prob", "lMax"]:
        hMap[key] = r.TH1D("pValueMap_%s" % key, ";category;p-value", *bins)

    for iSel, sel in enumerate(selections):
        args = {"whiteList": [sel.name],
                "allCategories": sorted([x.name for x in selections]),
                "sigMcUnc": False,
                }
        args.update(kargs)
        dct = go(**args)
        if not dct:
            continue

        report[sel.name] = dct
        for key, pValue in dct.iteritems():
            if key not in hMap:
                continue
            hMap[key].GetXaxis().SetBinLabel(1+iSel, sel.name)
            hMap[key].SetBinContent(1+iSel, pValue)

    plotting.pValueCategoryPlots(hMap, )  # logYMinMax=(1.0e-4, 1.0e2))
    printReport(report)
