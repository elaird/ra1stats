#!/usr/bin/env python
import ROOT as r
import common,workspace,likelihoodSpec,signals,signals2,plotting

def go(whiteList = [], dataset = "2011", ensemble = False, allCategories = [], ignoreHad = False) :
    examples = {("0b_le3j",):signals2.t2,
                ("0b_ge4j",):signals2.t1,
                ("1b_le3j",):signals2.t2bb,
                ("1b_ge4j",):signals2.t2tt,
                ("2b_le3j",):signals2.t2bb,
                ("2b_ge4j",):signals2.t2tt,
                ("3b_le3j",):{},
                ("3b_ge4j",):signals2.t1bbbb,
                ("ge4b_ge4j",):signals2.t1tttt,
                }
    signal = examples[tuple(whiteList)] if tuple(whiteList) in examples else {}
    f = workspace.foo(likelihoodSpec = likelihoodSpec.spec(whiteList = whiteList, dataset = dataset, ignoreHad = ignoreHad,
                                                           separateSystObs = not ensemble
                                                           ),
                      #signalToTest = signal,
                      signalExampleToStack = signal,
                      #signalToInject = signal,
                      #trace = True
                      #rhoSignalMin = 0.1,
                      #fIniFactor = 0.1,
                      #extraSigEffUncSources = ["effHadSumUncRelMcStats"],
                      )

    out = None
    nToys = {"2011":3000, "2012ichep":1000, "2012dev":300}[dataset]

    if ensemble :
        f.ensemble(nToys = nToys, stdout = True)
        return out

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
    #f.writeMlTable(fileName = "mlTables_%s.tex"%"_".join(whiteList), categories = allCategories)
    #f.bestFit(printPages = True, drawComponents = False, errorsFromToys = nToys)
    out = f.bestFit(drawMc = False, drawComponents = False, errorsFromToys = nToys)
    #f.qcdPlot()
    #f.debug()
    #f.cppDrive(tool = "")
    return out

kargs = {"dataset" : ["2011", "2012ichep", "2012dev"][2],
         "ensemble": False,
         }
if kargs["dataset"]=="2011" :
    go(**kargs)
else :
    selections = likelihoodSpec.spec(dataset = kargs["dataset"]).selections()
    hMap = {}
    bins = (len(selections), 0.0, len(selections))
    for key in ["chi2ProbSimple", "chi2Prob", "lMax"] :
        hMap[key] = r.TH1D("pValueMap_%s"%key, ";category;p-value", *bins)

    for iSel,sel in enumerate(selections) :
        args = {"whiteList":[sel.name], "allCategories":sorted([x.name for x in selections])}
        args.update(kargs)
        dct = go(**args)
        if not dct : continue
        for key,pValue in dct.iteritems() :
            if key not in hMap : continue
            hMap[key].GetXaxis().SetBinLabel(1+iSel, sel.name)
            hMap[key].SetBinContent(1+iSel, pValue)

    plotting.pValueCategoryPlots(hMap)
