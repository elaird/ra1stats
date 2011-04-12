#!/usr/bin/env python

import math
import ROOT as r

def lumi() : #recorded lumi for analyzed sample
    return 35.0 #/pb

def binLowerEdges() :
    return (250.0, 300.0, 350.0, 450.0)

def observations() :
    return {"htMean":( 265.0,  315.0,  375.0,  465.0),#place-holder values
            "nBulk": (844459, 331948, 225649, 110034),
            "nSel":  (    33,     11,      8,      5),
            "nPhot": (    -1,     -1,      6,      1),
            "nMuon": (    -1,     -1,      5,      2),
            "mcMuon":(    -1,     -1,    4.1,    1.9),
            }

def mcExpectations() : #events / lumi
    return {"mcMuon":(    -1,     -1,    4.1,    1.9  ),
            "mcTtW": (    -1,     -1,    3.415,  1.692),
            "mcPhot":(    -1,     -1,    4.4,    2.1  ),
            "mcZinv":(    -1,     -1,    2.586,  1.492),
            }

def fixedParameters() :
    return {"sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuTtW": 0.30,
            }

def modelConfiguration(w) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(w.pdf("model"))
    modelConfig.SetParametersOfInterest(w.set("poi"))
    #modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def initialA(i = 0) :
    o = observations()
    return (0.0+o["nSel"][i])*math.exp(initialk()*o["htMean"][i])/o["nBulk"][i]

def initialk() :
    o = observations()
    lengthMatch = len(set(map(lambda x:len(o[x]),["nSel", "nBulk", "htMean"])))==1
    assert lengthMatch and (len(o["nSel"])>1)

    rAlphaT = [(o["nSel"][i]+0.0)/o["nBulk"][i] for i in range(2)]
    return math.log(rAlphaT[1]/rAlphaT[0])/(o["htMean"][0]-o["htMean"][1])

def hadTerms() :
    terms = r.RooArgList("hadTermsList")
    stuffToImport = [] #keep references to objects to avoid seg-faults and later inform workspace

    A = r.RooRealVar("A", "A", initialA(), 0.0, 10.0*initialA())
    k = r.RooRealVar("k", "k", initialk(), 0.0, 10.0*initialk())
    stuffToImport += [A,k]

    o = observations()
    for i,htMeanValue,nBulkValue,nSelValue in zip(range(len(o["htMean"])), o["htMean"], o["nBulk"], o["nSel"]) :
        for item in ["htMean", "nBulk", "nSel"] :
            exec('%s = r.RooRealVar("%s%d", "%s%d", %sValue)'%(item, item,i, item,i, item))
            stuffToImport.append(eval(item))

        b = r.RooFormulaVar("hadB%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(A, nBulk, k, htMean) ); stuffToImport.append(b)
        pois = r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, nSel, b); stuffToImport.append(pois)
        terms.add(pois)
    
    stuffToImport.append(r.RooProdPdf("hadTerms", "hadTerms", terms))
    return stuffToImport

def importVariablesAndLikelihoods(w, stuffToImport) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING)
    blackList = ["hadB", "hadPois"]
    for item in stuffToImport :
        bail = False
        for blackItem in blackList :
            if item.GetName()[:len(blackItem)]==blackItem : bail = True
        if bail : continue #avoid "errors" about duplicates
        getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)

def setupLikelihood(w) :
    importVariablesAndLikelihoods(w, hadTerms())
    w.factory("PROD::model(hadTerms)")
    setSets(w)

def setSets(wspace) :
    wspace.defineSet("poi","A,k")
    #wspace.defineSet("nuis","tau")
    sels = ",".join(["nSel%d"%i for i in range(len(observations()["nSel"]))])
    wspace.defineSet("obs", ",".join([sels]))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    out.add(obsSet)
    #out.Print("v")
    return out

def computeInterval(dataset, modelconfig) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()
    #print "UpperLimit=",plInt.UpperLimit(wspace.var("s"))

r.RooRandom.randomGenerator().SetSeed(1)
wspace = r.RooWorkspace("Workspace")
setupLikelihood(wspace)
data = dataset(wspace.set("obs"))
modelConfig = modelConfiguration(wspace)
computeInterval(data, modelConfig)
