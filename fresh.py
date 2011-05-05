#!/usr/bin/env python

import data2,utils
import plotting
from utils import rooFitResults
import math
import ROOT as r

def init() :
    r.gROOT.SetBatch(True)

def modelConfiguration(w, smOnly) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(pdf(w))
    if not smOnly :
        modelConfig.SetParametersOfInterest(w.set("poi"))
        modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def initialA(i = 0) :
    o = data2.observations()
    return (0.0+o["nSel"][i])*math.exp(initialk()*o["htMean"][i])/o["nBulk"][i]

def initialk() :
    o = data2.observations()
    lengthMatch = len(set(map(lambda x:len(o[x]),["nSel", "nBulk", "htMean"])))==1
    assert lengthMatch and (len(o["nSel"])>1)

    rAlphaT = [(o["nSel"][i]+0.0)/o["nBulk"][i] for i in range(2)]
    return math.log(rAlphaT[1]/rAlphaT[0])/(o["htMean"][0]-o["htMean"][1])

def hadTerms(w, method, smOnly) :
    o = data2.observations()

    terms = []
    wimport(w, r.RooRealVar("A", "A", initialA(), 0.0, 30.0*initialA()))
    wimport(w, r.RooRealVar("k", "k", initialk(), 0.0, 30.0*initialk()))

    for i,htMeanValue,nBulkValue,nSelValue in zip(range(len(o["htMean"])), o["htMean"], o["nBulk"], o["nSel"]) :
        for item in ["htMean", "nBulk"] :
            wimport(w, r.RooRealVar("%s%d"%(item, i), "%s%d"%(item, i), eval("%sValue"%item)))
        if "HtMethod" in method :
            wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("nBulk%d"%i), w.var("A"), w.var("k"), w.var("htMean%d"%i))))
        elif all([w.var("zInv%d"%i), w.var("ttw%d"%i)]) :
            if "Qcd=0" in method :
                wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)", r.RooArgList(w.var("zInv%d"%i), w.var("ttw%d"%i))))
            else :
                wimport(w, r.RooFormulaVar("qcd%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("nBulk%d"%i), w.var("A"), w.var("k"), w.var("htMean%d"%i))))
                wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)+(@2)", r.RooArgList(w.var("zInv%d"%i), w.var("ttw%d"%i), w.function("qcd%d"%i))))
        else :
            continue

        wimport(w, r.RooRealVar("nSel%d"%i, "nSel%d"%i, nSelValue))
        if smOnly :
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nSel%d"%i), w.function("hadB%d"%i)))
        else :
            wimport(w, r.RooProduct("hadS%d"%i, "hadS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("hadLumi"), w.var("hadSignalEff%d"%i))))
            wimport(w, r.RooAddition("hadExp%d"%i, "hadExp%d"%i, r.RooArgSet(w.function("hadB%d"%i), w.function("hadS%d"%i))))
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nSel%d"%i), w.function("hadExp%d"%i)))
        terms.append("hadPois%d"%i)
    
    if not smOnly :
        terms.append("signalGaus") #defined in signalVariables()
    w.factory("PROD::hadTerms(%s)"%",".join(terms))

def photTerms(w) :
    terms = []
    #wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 1.0e-3, 2.0))
    wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 1.0e-3, 3.0))
    wimport(w, r.RooRealVar("onePhot", "onePhot", 1.0))
    wimport(w, r.RooRealVar("sigmaPhotZ", "sigmaPhotZ", data2.fixedParameters()["sigmaPhotZ"]))
    wimport(w, r.RooGaussian("photGaus", "photGaus", w.var("onePhot"), w.var("rhoPhotZ"), w.var("sigmaPhotZ")))
    terms.append("photGaus")

    for i,nPhotValue,mcPhotValue,mcZinvValue in zip(range(len(data2.observations()["nPhot"])),
                                                    data2.observations()["nPhot"],
                                                    data2.mcExpectations()["mcPhot"],
                                                    data2.mcExpectations()["mcZinv"]) :
        if nPhotValue<0 : continue
        wimport(w, r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue))
        wimport(w, r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, mcPhotValue/mcZinvValue))
        wimport(w, r.RooRealVar("zInv%d"%i,  "zInv%d"%i,  max(1, nPhotValue), 0.0, 10*max(1, nPhotValue)))
        wimport(w, r.RooFormulaVar("photExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoPhotZ"), w.var("rPhot%d"%i), w.var("zInv%d"%i))))
        wimport(w, r.RooPoisson("photPois%d"%i, "photPois%d"%i, w.var("nPhot%d"%i), w.function("photExp%d"%i)))
        terms.append("photPois%d"%i)
    
    w.factory("PROD::photTerms(%s)"%",".join(terms))

def muonTerms(w, smOnly) :
    terms = []
    wimport(w, r.RooRealVar("rhoMuonW", "rhoMuonW", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("oneMuon", "oneMuon", 1.0))
    wimport(w, r.RooRealVar("sigmaMuonW", "sigmaMuonW", data2.fixedParameters()["sigmaMuonW"]))
    wimport(w, r.RooGaussian("muonGaus", "muonGaus", w.var("oneMuon"), w.var("rhoMuonW"), w.var("sigmaMuonW")))
    terms.append("muonGaus")

    for i,nMuonValue,mcMuonValue,mcTtwValue in zip(range(len(data2.observations()["nMuon"])),
                                                   data2.observations()["nMuon"],
                                                   data2.mcExpectations()["mcMuon"],
                                                   data2.mcExpectations()["mcTtw"]) :
        if nMuonValue<0 : continue
        wimport(w, r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue))
        wimport(w, r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue))
        wimport(w, r.RooRealVar("ttw%d"%i,   "ttw%d"%i,   max(1, nMuonValue), 0.0, 10*max(1, nMuonValue)))
        wimport(w, r.RooFormulaVar("muonB%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMuonW"), w.var("rMuon%d"%i), w.var("ttw%d"%i))))

        if smOnly :
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonB%d"%i)))
        else :
            wimport(w, r.RooProduct("muonS%d"%i, "muonS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("muonLumi"), w.var("muonSignalEff%d"%i))))
            wimport(w, r.RooAddition("muonExp%d"%i, "muonExp%d"%i, r.RooArgSet(w.function("muonB%d"%i), w.function("muonS%d"%i))))
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonExp%d"%i)))
        
        terms.append("muonPois%d"%i)
    
    w.factory("PROD::muonTerms(%s)"%",".join(terms))

def constraintTerms(w) :
    terms = []
    wimport(w, r.RooRealVar("small", "small", 0.1))
    for i in range(len(data2.observations()["nSel"])) :
        b    = w.function("hadB%d"%i)
        zInv = w.var("zInv%d"%i)
        ttw  = w.var("ttw%d"%i)
        if not all([b, zInv, ttw]) : continue
        wimport(w, r.RooRealVar("oneConstraint%d"%i, "oneConstraint%d"%i, 1.0))
        wimport(w, r.RooFormulaVar("fqcd%d"%i, "fqcd%d"%i, "(@0)>=((@1)+(@2))", r.RooArgList(b, zInv, ttw)))
        wimport(w, r.RooGaussian("qcdConstraint%d"%i, "qcdConstraint%d"%i, w.var("oneConstraint%d"%i), w.function("fqcd%d"%i), w.var("small")))
        terms.append("qcdConstraint%d"%i)
    
    w.factory("PROD::constraintTerms(%s)"%",".join(terms))

def signalVariables(w) :
    wimport(w, r.RooRealVar("hadLumi", "hadLumi", data2.lumi()["had"]))
    wimport(w, r.RooRealVar("muonLumi", "muonLumi", data2.lumi()["muon"]))
    wimport(w, r.RooRealVar("xs", "xs", data2.signalXs()))
    wimport(w, r.RooRealVar("f", "f", 1.0, 0.0, 5.0))

    wimport(w, r.RooRealVar("oneRhoSignal", "oneRhoSignal", 1.0))
    wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("deltaSignal", "deltaSignal", 2.0*data2.fixedParameters()["sigmaLumi"]))
    wimport(w, r.RooGaussian("signalGaus", "signalGaus", w.var("oneRhoSignal"), w.var("rhoSignal"), w.var("deltaSignal")))

    for box,effs in data2.signalEff().iteritems() :
        for iBin,eff in enumerate(effs) :
            name = "%sSignalEff%d"%(box, iBin)
            wimport(w, r.RooRealVar(name, name, eff))

def multi(w, variables) :
    out = []
    bins = range(len(data2.observations()["nSel"]))
    for item in variables :
        for i in bins :
            name = "%s%d"%(item,i)
            if not w.var(name) : continue
            out.append(name)
    return out

def setupLikelihood(w, method = "", smOnly = True) :
    terms = []
    obs = []
    nuis = []
    multiBinObs = []
    multiBinNuis = []

    if not smOnly :
        signalVariables(w)

    if "Ewk" in method :
        photTerms(w)
        muonTerms(w, smOnly)
        terms += ["photTerms", "muonTerms"]
        obs += ["onePhot", "oneMuon"]
        multiBinObs += ["nPhot", "nMuon"]
        nuis += ["rhoPhotZ", "rhoMuonW"]
        multiBinNuis += ["zInv", "ttw"]

    if "HtMethod" or "ExpQcd" in method :
        nuis += ["A","k"]

    hadTerms(w, method, smOnly)
    terms.append("hadTerms")
    multiBinObs.append("nSel")

    if method=="HtMethod_Ewk" :
        constraintTerms(w)
        multiBinObs += ["oneConstraint"]
        terms.append("constraintTerms")

    w.factory("PROD::model(%s)"%",".join(terms))

    if not smOnly :
        obs.append("oneRhoSignal")
        nuis.append("rhoSignal")
        w.defineSet("poi", "f")

    obs += multi(w, multiBinObs)
    nuis += multi(w, multiBinNuis)
    w.defineSet("obs", ",".join(obs))
    w.defineSet("nuis", ",".join(nuis))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out

def interval(dataset, modelconfig, wspace, method, smOnly) :
    assert not smOnly

    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()
    ul = plInt.UpperLimit(wspace.var("f"))
    print "UpperLimit =",ul

    canvas = r.TCanvas()
    canvas.SetTickx()
    canvas.SetTicky()
    psFile = "intervalPlot_%s.ps"%method

    plot = r.RooStats.LikelihoodIntervalPlot(plInt)
    plot.Draw(); print
    canvas.Print(psFile)
    utils.ps2pdf(psFile)

def profilePlots(dataset, modelconfig, method, smOnly) :
    assert not smOnly

    canvas = r.TCanvas()
    canvas.SetTickx()
    canvas.SetTicky()
    psFile = "profilePlots_%s.ps"%method
    canvas.Print(psFile+"[")

    plots = r.RooStats.ProfileInspector().GetListOfProfilePlots(dataset, modelconfig); print
    for i in range(plots.GetSize()) :
        plots.At(i).Draw("al")
        canvas.Print(psFile)
    canvas.Print(psFile+"]")
    utils.ps2pdf(psFile)

def pValue(wspace, data, nToys = 100, validate = False) :
    def lMax(results) :
        return math.exp(-results.minNll())
    
    def indexFraction(item, l) :
        totalList = sorted(l+[item])
        assert totalList.count(item)==1
        return totalList.index(item)/(0.0+len(totalList))
        
    results = rooFitResults(pdf(wspace), data) #fit to data
    #wspace.saveSnapshot("snap", wspace.allVars(), False)
    #results.Print()
    lMaxData = lMax(results)
    dataset = pdf(wspace).generate(wspace.set("obs"), nToys) #make pseudo experiments with final parameter values

    graph = r.TGraph()
    lMaxs = []
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        pseudoData = r.RooDataSet("pseudoData%d"%i, "title", argSet)
        data.reset()
        data.add(argSet)
        #data.Print("v")
        #wspace.loadSnapshot("snap")
        wspace.var("A").setVal(initialA())
        wspace.var("k").setVal(initialk())
        results = rooFitResults(pdf(wspace), data)
        lMaxs.append(lMax(results))
        graph.SetPoint(i, i, indexFraction(lMaxData, lMaxs))
        #utils.delete(results)
    
    out = indexFraction(lMaxData, lMaxs)
    if validate : plotting.pValuePlots(pValue = out, lMaxData = lMaxData, lMaxs = lMaxs, graph = graph)
    return out

def pValueOld(dataset, modelconfig) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetNullParameters(modelconfig.GetParametersOfInterest())
    htr = plc.GetHypoTest()
    print "p-value = %g +/- %g"%(htr.NullPValue(), htr.NullPValueError())
    print "significance = %g"%htr.Significance()

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def pdf(w) :
    return w.pdf("model")

def go(methodIndex, smOnly, debug = False, trace = False) :
    out = []
    r.RooRandom.randomGenerator().SetSeed(1)
    wspace = r.RooWorkspace("Workspace")

    method = ["HtMethod_Ewk", "HtMethod_Only", "Qcd=0_Ewk", "ExpQcd_Ewk"][methodIndex]
    setupLikelihood(wspace, method, smOnly = smOnly)

    if debug :
        wspace.Print("v")
        plotting.writeGraphVizTree(wspace)

    data = dataset(wspace.set("obs"))
    modelConfig = modelConfiguration(wspace, smOnly)

    if trace :
        #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
        #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
        r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    #interval(data, modelConfig, wspace, method, smOnly)
    #profilePlots(data, modelConfig, method, smOnly)
    #pValue(wspace, data, nToys = 200, validate = True)
    #plotting.errorsPlot(wspace, rooFitResults(pdf(wspace), data))
    plotting.validationPlots(wspace, rooFitResults(pdf(wspace), data), method, smOnly)

    if debug :
        #pars = rooFitResults(pdf(wspace), data).floatParsFinal(); pars.Print("v")
        rooFitResults(pdf(wspace), data).Print("v")
        wspace.Print("v")

    return out

init()
stuff = go(methodIndex = 3, smOnly = False, debug = False)
