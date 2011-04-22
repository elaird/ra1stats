#!/usr/bin/env python

import math,array,os
import ROOT as r

def rootSetup() :
    r.gROOT.SetStyle("Plain")
    r.gErrorIgnoreLevel = 2000

def ps2pdf(psFileName) :
    os.system("ps2pdf %s"%psFileName)
    os.remove(psFileName)

def lumi() : #recorded lumi for analyzed sample
    return 35.0 #/pb

def htBinLowerEdges() :
    return (250.0, 300.0, 350.0, 450.0)

def htMaxForPlot() :
    return 600.0

def observations() :
    return {"htMean":( 265.0,  315.0,  375.0,  475.0),#place-holder values
            "nBulk": (844459, 331948, 225649, 110034),
            "nSel":  (    33,     11,      8,      5),
            "nPhot": (    -1,     -1,      6,      1),
            "nMuon": (    -1,     -1,      5,      2),
            }

def mcExpectations() : #events / lumi
    return {"mcMuon":(    -1,     -1,    4.1,    1.9  ),
            "mcTtw": (    -1,     -1,    3.415,  1.692),
            "mcPhot":(    -1,     -1,    4.4,    2.1  ),
            "mcZinv":(    -1,     -1,    2.586,  1.492),
            "signalEff":(0.0,    0.0,    0.02,   0.10),
            }

def fixedParameters() :
    return {"sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }

def modelConfiguration(w) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(w.pdf("model"))
    #modelConfig.SetParametersOfInterest(w.set("poi"))
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

def hadTerms(w, method) :
    terms = []
    wimport(w, r.RooRealVar("A", "A", initialA(), 0.0, 10.0*initialA()))
    wimport(w, r.RooRealVar("k", "k", initialk(), 0.0, 10.0*initialk()))

    o = observations()
    for i,htMeanValue,nBulkValue,nSelValue in zip(range(len(o["htMean"])), o["htMean"], o["nBulk"], o["nSel"]) :
        for item in ["htMean", "nBulk", "nSel"] :
            wimport(w, r.RooRealVar("%s%d"%(item, i), "%s%d"%(item, i), eval("%sValue"%item)))
        if "HtMethod" in method :
            wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("A"), w.var("nBulk%d"%i), w.var("k"), w.var("htMean%d"%i))))
        elif all([w.var("zInv%d"%i), w.var("ttw%d"%i)]) :
            if "Qcd=0" in method :
                wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)", r.RooArgList(w.var("zInv%d"%i), w.var("ttw%d"%i))))
            else :
                wimport(w, r.RooFormulaVar("qcd%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("A"), w.var("nBulk%d"%i), w.var("k"), w.var("htMean%d"%i))))
                wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)+(@2)", r.RooArgList(w.var("zInv%d"%i), w.var("ttw%d"%i), w.function("qcd%d"%i))))
        else :
            continue
        wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nSel%d"%i), w.function("hadB%d"%i)))
        terms.append("hadPois%d"%i)
    
    w.factory("PROD::hadTerms(%s)"%",".join(terms))

def photTerms(w) :
    terms = []
    wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("onePhot", "onePhot", 1.0))
    wimport(w, r.RooRealVar("sigmaPhotZ", "sigmaPhotZ", fixedParameters()["sigmaPhotZ"]))
    wimport(w, r.RooGaussian("photGaus", "photGaus", w.var("onePhot"), w.var("rhoPhotZ"), w.var("sigmaPhotZ")))
    terms.append("photGaus")

    for i,nPhotValue,mcPhotValue,mcZinvValue in zip(range(len(observations()["nPhot"])), observations()["nPhot"], mcExpectations()["mcPhot"], mcExpectations()["mcZinv"]) :
        if nPhotValue<0 : continue
        wimport(w, r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue))
        wimport(w, r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, mcPhotValue/mcZinvValue))
        wimport(w, r.RooRealVar("zInv%d"%i,  "zInv%d"%i,  max(1, nPhotValue), 0.0, 10*max(1, nPhotValue)))
        wimport(w, r.RooFormulaVar("photExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoPhotZ"), w.var("rPhot%d"%i), w.var("zInv%d"%i))))
        wimport(w, r.RooPoisson("photPois%d"%i, "photPois%d"%i, w.var("nPhot%d"%i), w.function("photExp%d"%i)))
        terms.append("photPois%d"%i)
    
    w.factory("PROD::photTerms(%s)"%",".join(terms))

def muonTerms(w) :
    terms = []
    wimport(w, r.RooRealVar("rhoMuonW", "rhoMuonW", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("oneMuon", "oneMuon", 1.0))
    wimport(w, r.RooRealVar("sigmaMuonW", "sigmaMuonW", fixedParameters()["sigmaMuonW"]))
    wimport(w, r.RooGaussian("muonGaus", "muonGaus", w.var("oneMuon"), w.var("rhoMuonW"), w.var("sigmaMuonW")))
    terms.append("muonGaus")

    for i,nMuonValue,mcMuonValue,mcTtwValue in zip(range(len(observations()["nMuon"])), observations()["nMuon"], mcExpectations()["mcMuon"], mcExpectations()["mcTtw"]) :
        if nMuonValue<0 : continue
        wimport(w, r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue))
        wimport(w, r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue))
        wimport(w, r.RooRealVar("ttw%d"%i,   "ttw%d"%i,   max(1, nMuonValue), 0.0, 10*max(1, nMuonValue)))
        wimport(w, r.RooFormulaVar("muonExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMuonW"), w.var("rMuon%d"%i), w.var("ttw%d"%i))))
        wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonExp%d"%i)))
        terms.append("muonPois%d"%i)
    
    w.factory("PROD::muonTerms(%s)"%",".join(terms))

def constraintTerms(w) :
    terms = []
    wimport(w, r.RooRealVar("one", "one", 1.0))
    wimport(w, r.RooRealVar("small", "small", 0.1))
    for i in range(len(observations()["nSel"])) :
        b    = w.function("hadB%d"%i)
        zInv = w.var("zInv%d"%i)
        ttw  = w.var("ttw%d"%i)
        if not all([b, zInv, ttw]) : continue
        wimport(w, r.RooFormulaVar("fqcd%d"%i, "fqcd%d"%i, "(@0)>=((@1)+(@2))", r.RooArgList(b, zInv, ttw)))
        wimport(w, r.RooGaussian("qcdConstraint%d"%i, "qcdConstraint%d"%i, w.var("one"), w.function("fqcd%d"%i), w.var("small")))
        terms.append("qcdConstraint%d"%i)
    
    w.factory("PROD::constraintTerms(%s)"%",".join(terms))

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def setupLikelihood(w, method = "") :
    terms = []
    obs = []
    items = []

    if "Ewk" in method :
        photTerms(w)
        muonTerms(w)
        terms += ["photTerms", "muonTerms"]
        obs += ["onePhot", "oneMuon"]
        items += ["nPhot", "nMuon"]

    hadTerms(w, method)
    terms.append("hadTerms")
    items.append("nSel")

    if method=="HtMethod_Ewk" :
        constraintTerms(w)
        obs.append("one")
        terms.append("constraintTerms")

    w.factory("PROD::model(%s)"%",".join(terms))

    #w.defineSet("poi", "A,k")
    for item in items :
        for i,value in enumerate(observations()[item]) :
            if value<0 : continue
            obs.append("%s%d"%(item,i))
    w.defineSet("obs", ",".join(obs))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    out.add(obsSet)
    #out.Print("v")
    return out

def interval(dataset, modelconfig, wspace) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()

    #ul = plInt.UpperLimit(wspace.var("A"))
    #print "UpperLimit =",ul

    #plot = r.RooStats.LikelihoodIntervalPlot(plInt)
    #plot.Draw(); return plot

def pValue(wspace, data, nToys = 100, validate = False) :
    def lMax(results) :
        return math.exp(-results.minNll())
    
    def indexFraction(item, l) :
        totalList = sorted(l+[item])
        assert totalList.count(item)==1
        return totalList.index(item)/(0.0+len(totalList))
        
    results = rooFitResults(wspace, data) #fit to data
    #results.Print()
    lMaxData = lMax(results)
    dataset = wspace.pdf("model").generate(wspace.set("obs"), nToys) #make pseudo experiments with final parameter values

    graph = r.TGraph()
    lMaxs = []
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        pseudoData = r.RooDataSet("pseudoData%d"%i, "title", argSet)
        data.reset()
        data.add(argSet)
        #data.Print("v")
        wspace.var("A").setVal(initialA())
        wspace.var("k").setVal(initialk())
        results = rooFitResults(wspace, data)
        lMaxs.append(lMax(results))
        graph.SetPoint(i, i, indexFraction(lMaxData, lMaxs))
    
    out = indexFraction(lMaxData, lMaxs)
    if validate :
        print "pValue =",out

        ps = "pValue.ps"
        canvas = r.TCanvas("canvas")
        canvas.SetTickx()
        canvas.SetTicky()
        canvas.Print(ps+"[")

        graph.SetMarkerStyle(20)
        graph.SetTitle(";toy number;p-value")
        graph.Draw("ap")
        canvas.Print(ps)

        totalList = lMaxs+[lMaxData]
        histo = r.TH1D("lMaxHisto",";L_{max};pseudo experiments / bin", 100, 0.0, max(totalList)*1.1)
        for item in lMaxs :
            histo.Fill(item)
        histo.SetStats(False)
        histo.SetMinimum(0.0)
        histo.Draw()

        line = r.TLine()
        line.SetLineColor(r.kBlue)
        line.SetLineWidth(2)
        line = line.DrawLine(lMaxData, histo.GetMinimum(), lMaxData, histo.GetMaximum())

        legend = r.TLegend(0.5, 0.7, 0.9, 0.9)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.AddEntry(histo, "L_{max} in pseudo-experiments", "l")
        legend.AddEntry(line, "L_{max} observed", "l")
        legend.Draw()

        canvas.Print(ps)
        canvas.Print(ps+"]")
        ps2pdf(ps)

    return out

def pValueOld(dataset, modelconfig) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetNullParameters(modelconfig.GetParametersOfInterest())
    htr = plc.GetHypoTest()
    print "p-value = %g +/- %g"%(htr.NullPValue(), htr.NullPValueError())
    print "significance = %g"%htr.Significance()

def writeGraphVizTree(wspace, pdfName = "model") :
    dotFile = "%s.dot"%pdfName
    wspace.pdf(pdfName).graphVizTree(dotFile, ":", True, False)
    cmd = "dot -Tps %s -o %s"%(dotFile, dotFile.replace(".dot", ".ps"))
    os.system(cmd)
    
def rooFitResults(wspace, data) :
    return wspace.pdf("model").fitTo(data, r.RooFit.Verbose(False), r.RooFit.PrintLevel(-1), r.RooFit.Save(True))

def errorsPlot(wspace, data) :
    results = rooFitResults(wspace, data)
    results.Print("v")
    k = wspace.var("k")
    A = wspace.var("A")
    plot = r.RooPlot(k, A, 0.0, 1.0e-5, 0.0, 1.0e-4)
    results.plotOn(plot, k, A, "ME12VHB")
    plot.Draw()
    return plot

def validationPlot(wspace = None, canvas = None, psFileName = None, note = "", legendX1 = 0.3, obsKey = None, obsLabel = None, otherVars = []) :
    def inputHisto() :
        bins = array.array('d', list(htBinLowerEdges())+[htMaxForPlot()])
        out = r.TH1D(obsKey, "%s;H_{T} (GeV);counts / bin"%note, len(bins)-1, bins)
        out.Sumw2()
        for i,content in enumerate(observations()[obsKey]) :
            for count in range(content) : out.Fill(bins[i])
        return out
    
    def varHisto(inp, wspace, varName, color, style, wspaceMemberFunc = None) :
        out = inp.Clone(varName)
        out.Reset()
        out.SetMarkerStyle(1)
        out.SetLineColor(color)
        out.SetLineStyle(style)
        out.SetMarkerColor(color)
        for i in range(len(htBinLowerEdges())) :
            if wspaceMemberFunc :
                var = getattr(wspace, wspaceMemberFunc)("%s%d"%(varName,i))
                if not var : continue
                out.SetBinContent(i+1, var.getVal())
            else :
                out.SetBinContent(i+1, mcExpectations()[varName][i])
                
        return out

    stuff = []
    leg = r.TLegend(legendX1, 0.6, 0.9, 0.85)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    inp = inputHisto()
    inp.SetMarkerStyle(20)
    inp.SetStats(False)
    inp.Draw("p")
    inp.SetMinimum(0.0)
    leg.AddEntry(inp, obsLabel, "lp")

    stack = r.THStack("stack", "stack")
    stuff += [leg,inp,stack]
    for d in otherVars :
        hist = varHisto(inp, wspace, d["var"], d["color"], d["style"], d["type"])
        stuff.append(hist)
        more = " (stacked)" if d["stack"] else ""
        leg.AddEntry(hist, d["desc"]+more, "l")
        if d["stack"] : stack.Add(hist)
        else : hist.Draw("same")

    stack.Draw("same")

    leg.Draw()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Update()

    canvas.Print(psFileName)
    return stuff
    
def validationPlots(wspace, data, method) :
    out = []
    results = rooFitResults(wspace, data)

    canvas = r.TCanvas()
    psFileName = "bestFit.ps"
    canvas.Print(psFileName+"[")
    
    vp = validationPlot(wspace, canvas, psFileName, note = method, legendX1 = 0.3, obsKey = "nSel", obsLabel = "2010 hadronic data", otherVars = [
            {"var":"hadB", "type":"function", "color":r.kBlue,    "style":1, "desc":"best fit expected total background", "stack":False},
            {"var":"zInv", "type":"var",      "color":r.kRed,     "style":2, "desc":"best fit Z->inv",                    "stack":True},
            {"var":"ttw",  "type":"var",      "color":r.kGreen,   "style":3, "desc":"best fit t#bar{t} + W",              "stack":True},
            {"var":"qcd",  "type":"function", "color":r.kMagenta, "style":3, "desc":"best fit QCD",                       "stack":True},
            ]); out.append(vp)
    
    if "Ewk" in method :
        vp = validationPlot(wspace, canvas, psFileName, note = method, legendX1 = 0.6, obsKey = "nPhot", obsLabel = "2010 photon data", otherVars = [
                {"var":"photExp", "type":"function", "color":r.kBlue, "style":1, "desc":"best fit expectation", "stack":False},
                {"var":"mcPhot",  "type":None,       "color":r.kRed,  "style":2, "desc":"2010 MC",              "stack":False},
                ]); out.append(vp)

        vp = validationPlot(wspace, canvas, psFileName, note = method, legendX1 = 0.6, obsKey = "nMuon", obsLabel = "2010 muon data", otherVars = [
                {"var":"muonExp", "type":"function", "color":r.kBlue, "style":1, "desc":"best fit expectation", "stack":False},
                {"var":"mcMuon",  "type":None,       "color":r.kRed,  "style":2, "desc":"2010 MC",              "stack":False},
                ]); out.append(vp)

    canvas.Print(psFileName+"]")
    ps2pdf(psFileName)
    return out

def go() :
    out = []
    r.RooRandom.randomGenerator().SetSeed(1)
    wspace = r.RooWorkspace("Workspace")

    method = ["HtMethod_Ewk", "HtMethod_Only", "Qcd=0_Ewk", "ExpQcd_Ewk"][1]
    setupLikelihood(wspace, method)

    #wspace.Print("v")
    #writeGraphVizTree(wspace)

    data = dataset(wspace.set("obs"))
    modelConfig = modelConfiguration(wspace)

    #out.append(interval(data, modelConfig, wspace))
    out.append(pValue(wspace, data, nToys = 400, validate = False))
    #out.append(errorsPlot(wspace, data))
    #out.append(validationPlots(wspace, data, method))

    #pars = rooFitResults(wspace, data).floatParsFinal(); pars.Print("v")
    return out

rootSetup()
stuff = go()
