import os
import ROOT as r


def wimport(w, item):
    """from utils"""
    # suppress info messages
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING)
    getattr(w, "import")(item)
    # re-enable all messages
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG)


def delete(thing):
    """from utils"""
    # free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
    thing.IsA().Destructor(thing)


def rooFitResults(pdf, data, options=(r.RooFit.Verbose(False),
                                      r.RooFit.PrintLevel(-1),
                                      r.RooFit.Save(True))):
    """from utils"""
    return pdf.fitTo(data, *options)


def plInterval(w=None, dataset=None, modelconfig=None, cl=None, plot=True):
    """from calc"""
    assert cl
    out = {}
    calc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()

    out["lowerLimit"] = lInt.LowerLimit(w.var("mu"))
    out["upperLimit"] = lInt.UpperLimit(w.var("mu"))

    if plot:
        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        plot = r.RooStats.LikelihoodIntervalPlot(lInt)
        plot.Draw()
        print
        canvas.Print("intervalPlot.pdf")

    delete(lInt)
    return out


def profilePlots(dataset, modelconfig):
    """from calc"""
    canvas = r.TCanvas()
    canvas.SetTickx()
    canvas.SetTicky()
    pdfFile = "profilePlots.pdf"
    canvas.Print(pdfFile+"[")

    plots = r.RooStats.ProfileInspector().GetListOfProfilePlots(dataset, modelconfig)
    print
    if not plots:
        return
    for i in range(plots.GetSize()):
        graph = plots.At(i)
        graph.Draw("al")
        graph.SetLineWidth(2)
        graph.SetLineColor(r.kBlue)
        h = graph.GetHistogram()
        h.SetMinimum(0.0)
        h.SetMaximum(1.1*h.GetMaximum())
        canvas.SetGridy()
        canvas.Print(pdfFile)
    canvas.Print(pdfFile+"]")


def writeGraphVizTree(wspace, pdfName="model"):
    """from plotting"""
    dotFile = "%s.dot" % pdfName
    wspace.pdf(pdfName).graphVizTree(dotFile, ":", True, False)
    cmd = "dot -Tps %s -o %s" % (dotFile, dotFile.replace(".dot", ".ps"))
    os.system(cmd)


def obsTerms(w=None, injectXs=0.0, lumi=1.0e4, mcStatNuis=True):
    terms = []

    b = (1.0e3, 30.0, 3.0)
    nMcIn = 1.0e4
    wimport(w, r.RooRealVar("nMcInInv", "nMcInInv", 1.0/nMcIn))
    effTrue = tuple([5/nMcIn]*3)
    effMc = effTrue
    #effMc = (4/nMcIn, 6/nMcIn, 3/nMcIn)

    wimport(w, r.RooRealVar("lumi", "lumi", lumi))
    wimport(w, r.RooRealVar("mu", "mu", 1.0, 0.0, 30.0))

    for i in range(len(b)):
        wimport(w, r.RooRealVar("obs%d" % i, "obs%d" % i, b[i] + lumi*injectXs*effTrue[i]))
        wimport(w, r.RooRealVar("b%d" % i, "b%d" % i, b[i]))
        if mcStatNuis:
            n = effMc[i]*nMcIn
            wimport(w, r.RooRealVar("nMcSel%d" % i, "nMcSel%d" % i, n))
            wimport(w, r.RooRealVar("nMcExp%d" % i, "nMcExp%d" % i, n, 0.0, max(10.0, 10.0*n)))
            wimport(w, r.RooPoisson("nMc%d" % i, "nMc%d" % i, w.var("nMcSel%d" % i), w.var("nMcExp%d" % i)))
            wimport(w, r.RooProduct("eff%d" % i, "eff%d" % i, r.RooArgSet(w.var("nMcExp%d" % i), w.var("nMcInInv"))))
            wimport(w, r.RooProduct("s%d" % i, "s%d" % i, r.RooArgSet(w.var("mu"), w.var("lumi"), w.function("eff%d" % i))))
            terms.append("nMc%d" % i)
        else:
            wimport(w, r.RooRealVar("eff%d" % i, "eff%d" % i, effMc[i]))
            wimport(w, r.RooProduct("s%d" % i, "s%d" % i, r.RooArgSet(w.var("mu"), w.var("lumi"), w.var("eff%d" % i))))
        wimport(w, r.RooAddition("exp%d" % i, "exp%d" % i, r.RooArgSet(w.function("b%d" % i), w.function("s%d" % i))))
        wimport(w, r.RooPoisson("pois%d" % i, "pois%d" % i, w.var("obs%d" % i), w.function("exp%d" % i)))
        terms.append("pois%d" % i)

    w.defineSet("obs", argSet(w, ["obs%d" % i for i in range(len(b))]))
    w.defineSet("poi", argSet(w, ["mu"]))
    w.factory("PROD::obsTerms(%s)" % (",".join(terms)))


def argSet(w=None, vars=[]):
    out = r.RooArgSet("out")
    for item in vars:
        out.add(w.var(item))
    return out


def dataset(obsSet):
    out = r.RooDataSet("dataName", "dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out


def setup():
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = r.kWarning
    r.gPrintViaErrorHandler = True
    r.RooRandom.randomGenerator().SetSeed(1)


def workspace(injectXs=0.0):
    w = r.RooWorkspace("Workspace")
    obsTerms(w, injectXs=injectXs)
    w.factory("PROD::model(obsTerms)")
    #w.factory("PROD::model(obsTerms,)")
    return w


def modelConfiguration(w):
    out = r.RooStats.ModelConfig("modelConfig", w)
    out.SetPdf("model")
    out.SetObservables(w.set("obs"))
    out.SetParametersOfInterest(w.set("poi"))
    return out


def go(trace=False, debug=True, profile=False, cl=None, bestFit=False, injectXs=0.0):
    w = workspace(injectXs=injectXs)
    modelConfig = modelConfiguration(w)
    data = dataset(modelConfig.GetObservables())

    if trace:
        #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
        #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
        r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    if debug:
        w.Print("v")
        w.set("obs").Print("v")
        w.set("poi").Print("v")
        writeGraphVizTree(w)

    if profile:
        profilePlots(data, modelConfig)

    if bestFit:
        results = rooFitResults(modelConfig.GetPdf(), data)
        results.Print("v")

    if cl:
        return plInterval(w=w, dataset=data, modelconfig=modelConfig, cl=cl)


def scan(xss=[i/2.0 for i in range(21)]):
    lower = r.TGraph()
    upper = r.TGraph()
    for i, xs in enumerate(xss):
        d = go(cl=0.68, injectXs=xs)
        lower.SetPoint(i, xs, d["lowerLimit"])
        upper.SetPoint(i, xs, d["upperLimit"])


    c = r.TCanvas("canvas", "canvas", 2)
    c.SetTickx()
    c.SetTicky()

    
    null = r.TH2D("null", ";injected xs; fit xs (68%)", 1, 0.0, 10.0, 1, 0.0, 10.0)
    null.SetStats(False)
    null.Draw()

    axis = null.GetXaxis()
    yx = r.TF1("yx", "x", axis.GetXmin(), axis.GetXmax())
    yx.SetLineColor(r.kBlue)
    yx.Draw("same")

    lower.Draw("lps")
    upper.Draw("lps")
    
    r.gPad.Print("foo.pdf")


setup()
scan()
