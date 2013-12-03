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


def plInterval(w=None, dataset=None, modelconfig=None, cl=None, plot=False):
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


def obsTerms(w=None, injectXs=0.0, lumi=1.0e4, bMean=(1.0e3, 30.0, 3.0), bObs=(1.0e3, 30.0, 3.0),
             nMcIn=1.0e4, mcOutMean=5.0, mcOut=(4, 6, 3),
             mcNuis=True):
    terms = []
    wimport(w, r.RooRealVar("nMcInInv", "nMcInInv", 1.0/nMcIn))
    wimport(w, r.RooRealVar("lumi", "lumi", lumi))
    wimport(w, r.RooRealVar("mu", "mu", 1.0, 0.0, 5.0*max(1.0, injectXs)))

    for i in range(len(bMean)):
        wimport(w, r.RooRealVar("obs%d" % i, "obs%d" % i, bObs[i] + lumi*injectXs*mcOutMean/nMcIn))
        wimport(w, r.RooRealVar("b%d" % i, "b%d" % i, bMean[i]))
        if mcNuis:
            n = mcOut[i]
            wimport(w, r.RooRealVar("nMcSel%d" % i, "nMcSel%d" % i, n))
            wimport(w, r.RooRealVar("nMcExp%d" % i, "nMcExp%d" % i, n, 0.0, max(10.0, 10.0*n)))
            wimport(w, r.RooPoisson("nMc%d" % i, "nMc%d" % i, w.var("nMcSel%d" % i), w.var("nMcExp%d" % i)))
            wimport(w, r.RooProduct("eff%d" % i, "eff%d" % i, r.RooArgSet(w.var("nMcExp%d" % i), w.var("nMcInInv"))))
            wimport(w, r.RooProduct("s%d" % i, "s%d" % i, r.RooArgSet(w.var("mu"), w.var("lumi"), w.function("eff%d" % i))))
            terms.append("nMc%d" % i)
        else:
            wimport(w, r.RooRealVar("eff%d" % i, "eff%d" % i, mcOut[i]/nMcIn))
            wimport(w, r.RooProduct("s%d" % i, "s%d" % i, r.RooArgSet(w.var("mu"), w.var("lumi"), w.var("eff%d" % i))))
        wimport(w, r.RooAddition("exp%d" % i, "exp%d" % i, r.RooArgSet(w.function("b%d" % i), w.function("s%d" % i))))
        wimport(w, r.RooPoisson("pois%d" % i, "pois%d" % i, w.var("obs%d" % i), w.function("exp%d" % i)))
        terms.append("pois%d" % i)

    w.defineSet("obs", argSet(w, ["obs%d" % i for i in range(len(bMean))]))
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


def workspace(injectXs=0.0, effcard={}):
    w = r.RooWorkspace("Workspace")
    obsTerms(w, injectXs=injectXs, **effcard)
    w.factory("PROD::model(obsTerms)")
    #w.factory("PROD::model(obsTerms,)")
    return w


def modelConfiguration(w):
    out = r.RooStats.ModelConfig("modelConfig", w)
    out.SetPdf("model")
    out.SetObservables(w.set("obs"))
    out.SetParametersOfInterest(w.set("poi"))
    return out


def go(trace=False, debug=True, profile=False, cl=None, bestFit=False, injectXs=0.0, effcard=None):
    w = workspace(injectXs=injectXs, effcard=effcard)
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


def oneXs(effcard=None, i=None, xs=None,
          gLo=None, gUp=None,
          lowerHistos=None, upperHistos=None,
          lowerEff=None, upperEff=None):

    d = go(cl=0.68, effcard=effcard, injectXs=xs)
    if gLo:
        gLo.SetPoint(i, xs, d["lowerLimit"])
    if gUp:
        gUp.SetPoint(i, xs, d["upperLimit"])

    if lowerHistos.get(xs):
        lowerHistos[xs].Fill(d["lowerLimit"])
    if upperHistos.get(xs):
        upperHistos[xs].Fill(d["upperLimit"])
    if lowerEff:
        lowerEff.Fill(d["lowerLimit"] < xs, xs)
    if upperEff:
        upperEff.Fill(xs < d["upperLimit"], xs)


def scan(effcard=None, xss=[], fileName="", upperHistos={}, lowerHistos={}, upperEff=None, lowerEff=None):
    gLo = r.TGraph()
    gUp = r.TGraph()
    for i, xs in enumerate(xss):
        oneXs(effcard=effcard,
              i=i, xs=xs,
              gLo=gLo, gUp=gUp,
              lowerHistos=lowerHistos,
              upperHistos=upperHistos,
              lowerEff=lowerEff,
              upperEff=upperEff,
              )

    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(21)
    text.SetTextSize(0.3*text.GetTextSize())

    null = r.TH2D("null", ";injected xs; fit xs (68%)", 1, 0.0, 10.0, 1, 0.0, 10.0)
    null.SetStats(False)
    null.Draw()

    axis = null.GetXaxis()
    yx = r.TF1("yx", "x", axis.GetXmin(), axis.GetXmax())
    yx.SetLineColor(r.kBlue)
    yx.Draw("same")

    gLo.Draw("lps")
    gUp.Draw("lps")
    
    foo = text.DrawText(0.5, 0.95, str(effcard))
    r.gPad.Print(fileName)


def examples(fileName="", xss=[]):
    c = r.TCanvas("canvas", "canvas", 2)
    c.SetTickx()
    c.SetTicky()
    c.Print(fileName+"[")

    for effcard in [{"lumi": 1.0e4, "nMcIn": 1.0e6, "mcOutMean":500.0, "mcOut":(500, 500, 500), "mcNuis": False},
                    {"lumi": 1.0e4, "nMcIn": 1.0e6, "mcOutMean":500.0, "mcOut":(500, 500, 500), "mcNuis": True},
                    {"lumi": 1.0e4, "nMcIn": 1.0e4, "mcOutMean":5.0, "mcOut":(5, 5, 5), "mcNuis": False},
                    {"lumi": 1.0e4, "nMcIn": 1.0e4, "mcOutMean":5.0, "mcOut":(5, 5, 5), "mcNuis": True},
                    #{"lumi": 1.0e4, "nMcIn": 1.0e4, "mcOutMean":5.0, "mcOut":(4, 6, 3), "mcNuis": False},
                    #{"lumi": 1.0e4, "nMcIn": 1.0e4, "mcOutMean":5.0, "mcOut":(4, 6, 3), "mcNuis": True},
                    {"lumi": 1.0e4, "nMcIn": 2.0e3, "mcOutMean":1.0, "mcOut":(1, 1, 1), "mcNuis": False},
                    {"lumi": 1.0e4, "nMcIn": 2.0e3, "mcOutMean":1.0, "mcOut":(1, 1, 1), "mcNuis": True},
                    ]:
        scan(effcard=effcard, fileName=fileName, xss=xss)

    c.Print(fileName+"]")


def randomized(rand=None, mcOutMean=None, bMean=None, fluctuateB=False):
    d = {"mcOut": (rand.Poisson(mcOutMean),
                   rand.Poisson(mcOutMean),
                   rand.Poisson(mcOutMean),
                   )}
    if fluctuateB:
        d["bObs"] = tuple([rand.Poisson(b) for b in bMean])
    else:
        d["bObs"] = bMean
    return d


def ensemble(fileName="", mcNuis=None, nToys=None, mcOutMean=None, nMcIn=None, xss=[], shareToys=True, fluctuateB=False):
    fileName = fileName.replace(".pdf", "_%s_%d.pdf" % (str(mcNuis), mcOutMean))

    upperHistos = {}
    lowerHistos = {}
    for xs in xss:
        upperHistos[xs] = r.TH1D("upper%g" % xs, ";upper limit on xs;toys / bin", 100, 0.0, 2.0*max(1.0, xs))
        lowerHistos[xs] = r.TH1D("lower%g" % xs, ";lower limit on xs;toys / bin", 100, 0.0, 2.0*max(1.0, xs))

    lowerEff = r.TEfficiency("lowerEff%s" % str(mcNuis), ";xs;fraction of toys with (lower limit < xs)", 21, -0.25, 10.25)
    upperEff = r.TEfficiency("upperEff%s" % str(mcNuis), ";xs;fraction of toys with (xs < upper limit)", 21, -0.25, 10.25)

    rand = r.TRandom3()
    rand.SetSeed(1)

    c = r.TCanvas("canvas", "canvas", 2)
    c.SetTickx()
    c.SetTicky()
    c.Print(fileName+"[")

    effcard = {"lumi": 1.0e4, "nMcIn": nMcIn, "mcOutMean": mcOutMean, "mcNuis": mcNuis, "bMean": (1.0e3, 30.0, 3.0),}
    if shareToys:
        for iToy in range(nToys):
            effcard.update(randomized(rand=rand,
                                      mcOutMean=mcOutMean,
                                      bMean=effcard["bMean"],
                                      fluctuateB=fluctuateB,
                                      ))
            scan(effcard=effcard, fileName=fileName, xss=xss,
                 upperHistos=upperHistos, lowerHistos=lowerHistos,
                 upperEff=upperEff, lowerEff=lowerEff)
    else:
        for iToy in range(nToys):
            for xs in xss:
                effcard.update(randomized(rand=rand,
                                          mcOutMean=mcOutMean,
                                          bMean=effcard["bMean"],
                                          fluctuateB=fluctuateB,
                                          ))
                oneXs(effcard=effcard, xs=xs,
                      lowerHistos=lowerHistos,
                      upperHistos=upperHistos,
                      lowerEff=lowerEff,
                      upperEff=upperEff,
                      )


    text = r.TLatex()
    text.SetNDC()
    text.SetTextSize(1.5*text.GetTextSize())

    for dct in [lowerHistos, upperHistos]:
        c.cd(0)
        c.Clear()
        c.Divide(4, 3)
        for iKey, key in enumerate(sorted(dct.keys())):
            c.cd(1 + iKey)
            r.gPad.SetTickx()
            r.gPad.SetTicky()
            h = dct[key]
            h.Draw()
            h.SetStats(False)
            text.DrawLatex(0.1, 0.95, "xs=%4.1f    (#mu=%4.2f,  #sigma=%3.1f)" % (key, h.GetMean(), h.GetRMS()))
        c.cd(0)
        c.Print(fileName)

    c.Clear()
    c.Divide(1, 2)

    nullL = r.TH2D("nullL", ";xs;fraction of toys with (lowerlimit < xs)", 1, -0.25, 10.25, 1, 0.0, 1.1)
    nullL.SetStats(False)
    nullU = r.TH2D("nullU", ";xs;fraction of toys with (xs < upperlimit)", 1, -0.25, 10.25, 1, 0.0, 1.1)
    nullU.SetStats(False)

    line = r.TLine()
    line.SetLineColor(r.kBlue)
    keep = []
    for iEff, (eff, null) in enumerate([(lowerEff, nullL), (upperEff, nullU)]):
        c.cd(1 + iEff)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        null.Draw()
        keep.append(line.DrawLine(-0.25, 0.84, 10.25, 0.84))
        eff.Draw("same")
    c.Print(fileName)

    c.Print(fileName+"]")


setup()

kargs = {"xss": [0.0, 0.5, 1.0, 1.5] + range(2, 7) + [8, 10],
         "nToys": 20,
         "shareToys": False,
         "mcOutMean": 500.0,
         "nMcIn": 1.0e6,
         "fileName": "ensemble.pdf",
         "fluctuateB": False,
         }

examples(xss=[i/2.0 for i in range(21)], fileName="examples.pdf")

#ensemble(mcNuis=False, **kargs)
#ensemble(mcNuis=True, **kargs)
