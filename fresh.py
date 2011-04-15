#!/usr/bin/env python

import math,array,os
import ROOT as r

def lumi() : #recorded lumi for analyzed sample
    return 35.0 #/pb

def htBinLowerEdges() :
    return (250.0, 300.0, 350.0, 450.0)

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
            }

def fixedParameters() :
    return {"sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
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

def photTerms() :
    terms = r.RooArgList("photTermsList")
    stuffToImport = [] #keep references to objects to avoid seg-faults and later inform workspace

    rhoPhotZ = r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 0.0, 2.0)
    onePhot = r.RooRealVar("onePhot", "onePhot", 1.0)
    sigmaPhotZ = r.RooRealVar("sigmaPhotZ", "sigmaPhotZ", fixedParameters()["sigmaPhotZ"])
    gaus = r.RooGaussian("photGaus", "photGaus", onePhot, rhoPhotZ, sigmaPhotZ)
    stuffToImport += [rhoPhotZ, onePhot, sigmaPhotZ, gaus]
    terms.add(gaus)

    for i,nPhotValue,mcPhotValue,mcZinvValue in zip(range(len(observations()["nPhot"])), observations()["nPhot"], mcExpectations()["mcPhot"], mcExpectations()["mcZinv"]) :
        if nPhotValue<0 : continue
        nPhot = r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue)
        rPhot = r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, mcPhotValue/mcZinvValue)
        zInv  = r.RooRealVar("zInv%d"%i,  "zInv%d"%i,  max(1, nPhotValue), 0.0, 10*max(1, nPhotValue))
        stuffToImport += [nPhot, rPhot, zInv]

        expPhot = r.RooFormulaVar("photExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(rhoPhotZ, rPhot, zInv) ); stuffToImport.append(expPhot)
        pois = r.RooPoisson("photPois%d"%i, "photPois%d"%i, nPhot, expPhot); stuffToImport.append(pois)
        terms.add(pois)
    
    stuffToImport.append(r.RooProdPdf("photTerms", "photTerms", terms))
    return stuffToImport

def muonTerms() :
    terms = r.RooArgList("muonTermsList")
    stuffToImport = [] #keep references to objects to avoid seg-faults and later inform workspace

    rhoMuonW = r.RooRealVar("rhoMuonW", "rhoMuonW", 1.0, 0.0, 2.0)
    oneMuon = r.RooRealVar("oneMuon", "oneMuon", 1.0)
    sigmaMuonW = r.RooRealVar("sigmaMuonW", "sigmaMuonW", fixedParameters()["sigmaMuonW"])
    gaus = r.RooGaussian("muonGaus", "muonGaus", oneMuon, rhoMuonW, sigmaMuonW)
    stuffToImport += [rhoMuonW, oneMuon, sigmaMuonW, gaus]
    terms.add(gaus)

    for i,nMuonValue,mcMuonValue,mcTtwValue in zip(range(len(observations()["nMuon"])), observations()["nMuon"], mcExpectations()["mcMuon"], mcExpectations()["mcTtw"]) :
        if nMuonValue<0 : continue
        nMuon = r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue)
        rMuon = r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue)
        ttw   = r.RooRealVar("ttw%d"%i,   "ttw%d"%i,   max(1, nMuonValue), 0.0, 10*max(1, nMuonValue))
        stuffToImport += [nMuon, rMuon, ttw]

        expMuon = r.RooFormulaVar("muonExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(rhoMuonW, rMuon, ttw) ); stuffToImport.append(expMuon)
        pois = r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, nMuon, expMuon); stuffToImport.append(pois)
        terms.add(pois)
    
    stuffToImport.append(r.RooProdPdf("muonTerms", "muonTerms", terms))
    return stuffToImport

def constraintTerms(wspace) :
    terms = r.RooArgList("constraintTermsList")
    stuffToImport = [] #keep references to objects to avoid seg-faults and later inform workspace

    smallNeg = r.RooRealVar("smallNeg", "smallNeg", -1.0e-3)
    stuffToImport.append(smallNeg)

    for i in range(len(observations()["nSel"])) :
        b    = wspace.function("hadB%d"%i)
        zInv = wspace.var("zInv%d"%i)
        ttw  = wspace.var("ttw%d"%i)
        if not all([b, zInv, ttw]) : continue
        qcd = r.RooFormulaVar("qcd%d"%i, "(@0)-(@1)-(@2)", r.RooArgList(b, zInv, ttw) ); stuffToImport.append(qcd)
        constraint = r.RooExponential("qcdConstraint%d"%i, "qcdConstraint%d"%i, qcd, smallNeg); stuffToImport.append(constraint)
        terms.add(constraint)
    
    stuffToImport.append(r.RooProdPdf("constraintTerms", "constraintTerms", terms))
    return stuffToImport

def importVariablesAndLikelihoods(w, stuffToImport, blackList) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    for item in stuffToImport :
        if any(map(lambda x:item.GetName()[:len(x)]==x, blackList)) : continue #avoid duplicates
        getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def setupLikelihood(w) :
    importVariablesAndLikelihoods(w, hadTerms(), ["hadB", "hadPois"])
    importVariablesAndLikelihoods(w, photTerms(), ["photExp", "photPois", "photGaus"])
    importVariablesAndLikelihoods(w, muonTerms(),["muonExp", "muonPois", "muonGaus"])
    #w.factory("PROD::model(hadTerms,photTerms,muonTerms)")
    importVariablesAndLikelihoods(w, constraintTerms(w), ["qcd"])
    w.factory("PROD::model(hadTerms,photTerms,muonTerms,constraintTerms)")

    setSets(w)

def setSets(wspace) :
    wspace.defineSet("poi","A,k")
    #wspace.defineSet("nuis","tau")
    obs = ["onePhot", "oneMuon"]
    for item in ["nSel", "nPhot", "nMuon"] :
        for i,value in enumerate(observations()[item]) :
            if value<0 : continue
            obs.append("%s%d"%(item,i))
    wspace.defineSet("obs", ",".join(obs))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    out.add(obsSet)
    #out.Print("v")
    return out

def interval(dataset, modelconfig) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()
    #print "UpperLimit=",plInt.UpperLimit(wspace.var("s"))
    #plot = r.RooStats.LikelihoodIntervalPlot(plInt)
    #plot.Draw(); return plot

def pValue(dataset, modelconfig) :
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

def validationPlot(wspace, data) :
    def inputHisto() :
        bins = array.array('d', list(htBinLowerEdges())+[600.0])
        out = r.TH1D("inputData", ";H_{T} (GeV);counts / bin", len(bins)-1, bins)
        out.Sumw2()
        for i,content in enumerate(observations()["nSel"]) :
            for count in range(content) : out.Fill(bins[i])
        return out
    
    def totalBackgroundHisto(inp, wspace, color) :
        out = inp.Clone("totalBackground")
        out.Reset()
        out.SetLineColor(color)
        out.SetMarkerColor(color)
        for i in range(len(htBinLowerEdges())) :
            out.SetBinContent(i+1, wspace.function("hadB%d"%i).getVal())
        return out

    def varHisto(inp, wspace, varName, color) :
        out = inp.Clone(varName)
        out.Reset()
        out.SetMarkerStyle(1)
        out.SetLineColor(color)
        out.SetMarkerColor(color)
        for i in range(len(htBinLowerEdges())) :
            var = wspace.var("%s%d"%(varName,i))
            if not var : continue
            out.SetBinContent(i+1, var.getVal())
        return out

    results = rooFitResults(wspace, data)

    r.gROOT.SetStyle("Plain")
    leg = r.TLegend(0.3, 0.6, 0.9, 0.85)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    inp = inputHisto()
    inp.SetMarkerStyle(20)
    inp.SetStats(False)
    inp.Draw("p")
    inp.SetMinimum(0.0)
    leg.AddEntry(inp, "2010 hadronic data", "lp")

    total = totalBackgroundHisto(inp, wspace, r.kBlue)
    total.Draw("same")
    leg.AddEntry(total, "best fit expected total background", "l")

    stack = r.THStack("stack", "stack")

    zInv = varHisto(inp, wspace, "zInv", r.kRed)
    stack.Add(zInv)
    leg.AddEntry(zInv, "best fit Z->inv (stacked)")

    ttw = varHisto(inp, wspace, "ttw", r.kGreen)
    stack.Add(ttw)
    leg.AddEntry(ttw, "best fit t#bar{t} + W (stacked)", "l")

    stack.Draw("same")

    leg.Draw()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Update()

    fileName = "bestFit.eps"
    r.gPad.Print(fileName)
    os.system("epstopdf %s"%fileName)
    os.remove(fileName)
    return inp,total,zInv,ttw,stack,leg
    
def go() :
    out = []
    r.RooRandom.randomGenerator().SetSeed(1)
    wspace = r.RooWorkspace("Workspace")
    setupLikelihood(wspace)
    #wspace.Print("v")

    data = dataset(wspace.set("obs"))
    modelConfig = modelConfiguration(wspace)

    out.append(interval(data, modelConfig))
    #out.append(pValue(data, modelConfig))

    #writeGraphVizTree(wspace)
    #ep = errorsPlot(wspace, data); return ep
    #vp = validationPlot(wspace, data); return vp
    #pars = rooFitResults(wspace, data).floatParsFinal(); pars.Print("v")
    return out

stuff = go()
