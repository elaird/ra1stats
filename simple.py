#!/usr/bin/env python

import math,plotting,utils
import ROOT as r
from runInverter import RunInverter

def clsPoisson(n = None, b = None, s = None) :
    num = 0.0
    den = 0.0
    for i in range(1+n) :
        num+=r.TMath.PoissonI(i, b+s)
        den+=r.TMath.PoissonI(i, b)
    return num/den

def oneGraph(n = None, b = None, npoints = None, poimin = None, poimax = None) :
    gr = r.TGraph()
    gr.SetMarkerStyle(26)
    gr.SetLineColor(r.kCyan)
    gr.SetLineWidth(2)
    gr.SetMarkerColor(r.kMagenta)
    for i in range(npoints) :
        s = poimin
        if i : s += i*(poimax-poimin)/(npoints-1)
        gr.SetPoint(i, s, clsPoisson(n, b, s))

    #gr.Draw("apl")
    #gr.GetXaxis().SetTitle("s")
    #gr.GetYaxis().SetTitle("CL_{s}")
    #gr.SetTitle("L = Pois( %d | %g + s )"%(n,b))

    #line = r.TLine()
    #line.SetLineColor(r.kRed)
    #line.DrawLine(0.0, 0.05, 10.0, 0.05)
    #r.gPad.Print("analytic_b%d_n%d.png"%(b, n))
    return gr

def clsPoissonGraph() :
    r.gROOT.SetBatch(True)
    for n in [1,2,4,6] :
        oneGraph(n = n, b = 4)

def modelConfiguration(w) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(pdf(w))
    modelConfig.SetObservables(w.set("obs"))
    modelConfig.SetParametersOfInterest(w.set("poi"))
    modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def hadTerms(w) :
    wimport(w, r.RooRealVar("b", "b", 3.0))
    wimport(w, r.RooRealVar("nHad", "nHad", 1.0))
    wimport(w, r.RooRealVar("s", "s", 1.0, 0.0, 30.0))
    wimport(w, r.RooAddition("exp", "exp", r.RooArgSet(w.function("b"), w.function("s"))))
    wimport(w, r.RooPoisson("hadPois", "hadPois", w.var("nHad"), w.function("exp")))

def setupLikelihood(w) :
    terms = []
    obs = []
    nuis = []

    hadTerms(w)
    terms.append("hadPois")
    obs.append("nHad")
    w.factory("PROD::model(%s)"%",".join(terms))

    w.defineSet("poi", "s")
    w.defineSet("obs", ",".join(obs))
    w.defineSet("nuis", ",".join(nuis))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out

def plInterval(dataset, modelconfig, wspace, note, smOnly, cl = None, makePlots = True) :
    assert not smOnly
    out = {}
    calc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()
    out["upperLimit"] = lInt.UpperLimit(wspace.var("s"))
    out["lowerLimit"] = lInt.LowerLimit(wspace.var("s"))

    if makePlots :
        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        psFile = "intervalPlot_%s_%g.ps"%(note, 100*cl)
        plot = r.RooStats.LikelihoodIntervalPlot(lInt)
        plot.SetMaximum(3.0)
        plot.Draw(); print
        canvas.Print(psFile)
        utils.ps2pdf(psFile)
        f = r.TFile(psFile.replace(".ps", ".root"), "RECREATE")
        canvas.Write()
        f.Close()

    #utils.delete(lInt)
    return out

def fcExcl(dataset, modelconfig, wspace, note, smOnly, cl = None, makePlots = True) :
    assert not smOnly

    nPoints = 200
    out = {}
    calc = r.RooStats.FeldmanCousins(dataset, modelconfig)
    #calc.SetPOIPointsToTest(poiValues)
    calc.FluctuateNumDataEntries(False)
    calc.UseAdaptiveSampling(True)
    #calc.AdditionalNToysFactor(4)
    calc.SetNBins(nPoints)
    #calc.GetTestStatSampler().SetProofConfig(r.RooStats.ProofConfig(wspace, 1, "workers=4", False))

    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()

    out["upperLimit"] = lInt.UpperLimit(wspace.var("s"))

    #if makePlots :
    #    cb = calc.GetConfidenceBelt()
    #    cb.GetParameters().Print("v")
    #    
    #    s = r.RooRealVar("s", "s", 1.0)
    #    for i in range(nPoints) :
    #        point = 5.0*(i+0.5)/nPoints
    #        s.setVal(point)
    #        min = cb.GetAcceptanceRegionMin(r.RooArgSet(s))#, Double_t cl = -1., Double_t leftside = -1.)
    #        max = cb.GetAcceptanceRegionMax(r.RooArgSet(s))#, Double_t cl = -1., Double_t leftside = -1.)
    #        print point,min,max

    return out

def cls(dataset, modelconfig, wspace, smOnly) :
    assert not smOnly

    testStatType = 3

    npoints = 11
    poimin = 0.0
    poimax = 30.0

    n = wspace.var("nHad").getVal()
    b = wspace.var("b").getVal()

    desc = "n_%d_b_%g_TS%d"%(n, b, testStatType)
    
    wimport(wspace, dataset)
    wimport(wspace, modelconfig)
    result = RunInverter(w = wspace, modelSBName = "modelConfig", dataName = "dataName",
                         nworkers = 6, type = 0, testStatType = testStatType, ntoys = 2000,
                         npoints = npoints, poimin = poimin, poimax = poimax)

    print "upper limit = %g +- %g"%(result.UpperLimit(), result.UpperLimitEstimatedError())
    plot = r.RooStats.HypoTestInverterPlot("HTI_Result_Plot", "", result)
    plot.Draw("CLb 2CL")

    gr = oneGraph(n = n, b = b, npoints = 3*npoints, poimin = poimin, poimax = poimax)
    gr.Draw("lpsame")

    for s in [3.0, 30.0] :
        tsPlot = plot.MakeTestStatPlot(result.FindIndex(s))
        #tsPlot.SetLogYaxis(True)
        t = "tsPlot_s_%g_%s"%(s, desc)
        tsPlot.Draw()
        tsPlot.SetTitle(t)
        r.gPad.Print("%s.png"%t)
    
    plot.SetTitle(desc)
    r.gPad.Print("simple_%s.png"%desc)
    return result

def profilePlots(dataset, modelconfig, note, smOnly) :
    assert not smOnly

    canvas = r.TCanvas()
    canvas.SetTickx()
    canvas.SetTicky()
    psFile = "profilePlots_%s.ps"%note
    canvas.Print(psFile+"[")

    plots = r.RooStats.ProfileInspector().GetListOfProfilePlots(dataset, modelconfig); print
    for i in range(plots.GetSize()) :
        plots.At(i).Draw("al")
        canvas.Print(psFile)
    canvas.Print(psFile+"]")
    utils.ps2pdf(psFile)

def pValue(wspace, data, nToys = 100, note = "", plots = True) :
    def lMax(results) :
        return math.exp(-results.minNll())
    
    def indexFraction(item, l) :
        totalList = sorted(l+[item])
        assert totalList.count(item)==1
        return totalList.index(item)/(0.0+len(totalList))
        
    results = utils.rooFitResults(pdf(wspace), data) #fit to data
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
        #wspace.var("A").setVal(initialA())
        #wspace.var("k").setVal(initialk())
        results = utils.rooFitResults(pdf(wspace), data)
        lMaxs.append(lMax(results))
        graph.SetPoint(i, i, indexFraction(lMaxData, lMaxs))
        #utils.delete(results)
    
    out = indexFraction(lMaxData, lMaxs)
    if plots : plotting.pValuePlots(pValue = out, lMaxData = lMaxData, lMaxs = lMaxs, graph = graph, note = note)
    return out

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def pdf(w) :
    return w.pdf("model")

class foo(object) :
    def __init__(self, trace = False) :
        r.gROOT.SetBatch(True)
        r.RooRandom.randomGenerator().SetSeed(1)

        self.wspace = r.RooWorkspace("Workspace")
        setupLikelihood(self.wspace)
        self.data = dataset(self.wspace.set("obs"))
        self.modelConfig = modelConfiguration(self.wspace)

        self.note = ""
        if trace :
            #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
            #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
            r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    def smOnly(self) :
        return False
    
    def debug(self) :
        self.wspace.Print("v")
        plotting.writeGraphVizTree(self.wspace)
        #pars = utils.rooFitResults(pdf(wspace), data).floatParsFinal(); pars.Print("v")
        utils.rooFitResults(pdf(self.wspace), self.data).Print("v")
        #wspace.Print("v")

    def interval(self, cl = 0.95, method = "profileLikelihood", makePlots = False) :
        if method=="profileLikelihood" :
            return plInterval(self.data, self.modelConfig, self.wspace, self.note, self.smOnly(), cl = cl, makePlots = makePlots)
        elif method=="feldmanCousins" :
            return fcExcl(self.data, self.modelConfig, self.wspace, self.note, self.smOnly(), cl = cl, makePlots = makePlots)

    def cls(self) :
        return cls(self.data, self.modelConfig, self.wspace, self.smOnly())

    def profile(self) :
        profilePlots(self.data, self.modelConfig, self.note, self.smOnly())

    def pValue(self, nToys = 200) :
        pValue(self.wspace, self.data, nToys = nToys, note = self.note)

    def bestFit(self) :
        plotting.validationPlots(self.wspace, utils.rooFitResults(pdf(self.wspace), self.data), self.inputData, self.REwk, self.RQcd, self.smOnly())


f = foo()
#out = f.interval(cl = 0.95, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
out = f.cls(); print out
#clsPoissonGraph()
#f.profile()
#f.bestFit()
#f.pValue(nToys = 500)
#f.debug()
#oneGraph(n = 1, b = 3.0)
