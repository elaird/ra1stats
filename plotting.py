import array
import collections
import copy
import math
import os

import configuration as conf
import common
import ensemble
import utils
import ROOT as r

# compatibility
ni = common.ni
inDict = utils.inDict

def rootSetup() :
    #r.gROOT.SetStyle("Plain")
    r.gErrorIgnoreLevel = 2000

def writeGraphVizTree(wspace, pdfName = "model") :
    dotFile = "%s.dot"%pdfName
    wspace.pdf(pdfName).graphVizTree(dotFile, ":", True, False)
    cmd = "dot -Tps %s -o %s"%(dotFile, dotFile.replace(".dot", ".ps"))
    os.system(cmd)

def magnify(h = None) :
    for axis in ["X","Y"] :
        h.SetLabelSize(2.0*h.GetLabelSize(axis), axis)
    h.GetXaxis().SetTitleSize(1.4*h.GetXaxis().GetTitleSize())
    h.GetYaxis().SetTitleSize(1.4*h.GetYaxis().GetTitleSize())

def pValueCategoryPlots(hMap = None, logYMinMax = None) :
    can = r.TCanvas("canvas", "", 700, 500)
    can.Divide(2,2)

    can.cd(1)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.SetGridy()

    pValues = [{"key":"chi2ProbSimple", "latex":"#chi^{2} prob.",        "color":602     },
               {"key":"chi2Prob",       "latex":"#chi^{2} prob. (toys)", "color":r.kBlack},
               {"key":"lMax",           "latex":"L_{max} (toys)",        "color":r.kCyan },
               ]

    leg = r.TLegend(0.60, 0.65, 0.85, 0.85)
    for i,d in enumerate(pValues) :
        key = d["key"]
        hMap[key].SetMarkerStyle(20)
        hMap[key].SetMarkerColor(d["color"])
        if not i :
            hMap[key].SetStats(False)
            hMap[key].Draw("p")
            hMap[key].SetMinimum(logYMinMax[0] if logYMinMax else 0.0)
            hMap[key].SetMaximum(logYMinMax[1] if logYMinMax else 1.5)
            magnify(hMap[key])
        else :
            hMap[key].Draw("psame")
        leg.AddEntry(hMap[key], d["latex"], "p")
    leg.Draw()
    if logYMinMax :
        r.gPad.SetLogy()

    keep = []
    for i,d in enumerate(pValues) :
        key = d["key"]

        hDist = r.TH1D("pValueDist"+key, ";p-value;categories / bin", 55, 0.0, 1.1)
        hDist.SetStats(False)
        hDist.SetLineColor(d["color"])
        magnify(hDist)
        for iBin in range(1, 1+hMap[key].GetNbinsX()) :
            hDist.Fill(hMap[key].GetBinContent(iBin))

        can.cd(i+2)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        hDist.Draw()
        keep.append(hDist)

    can.Print("plots/pValues.pdf")

def errorsPlot(wspace, results) :
    results.Print("v")
    k = wspace.var("k_qcd")
    A = wspace.var("A_qcd")
    plot = r.RooPlot(k, A, 0.0, 2.0e-2, 0.0, 0.5e-4)
    results.plotOn(plot, k, A, "ME12VHB")
    plot.Draw()
    r.gPad.Print("Ak.png")
    return plot

def drawDecoratedHisto(quantiles = {}, hist = None, obs = None) :
    hist.Draw()
    hist.SetStats(False)

    q = copy.deepcopy(quantiles)
    if obs!=None : q["Observed"] = obs

    legend = r.TLegend(0.1, 0.7, 0.5, 0.9)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    line = r.TLine()
    line.SetLineWidth(2)
    for i,key in enumerate(sorted(q.keys())) :
        line.SetLineColor(2+i)
        line2 = line.DrawLine(q[key], hist.GetMinimum(), q[key], hist.GetMaximum())
        legend.AddEntry(line2, key, "l")
    legend.Draw()
    return legend

def histoLines(args = {}, key = None, histo = None) :
    hLine = r.TLine(); hLine.SetLineColor(args["quantileColor"])
    bestLine = r.TLine(); bestLine.SetLineColor(args["bestColor"])
    errorLine = r.TLine(); errorLine.SetLineColor(args["errorColor"])

    q = args["quantileDict"][key]
    min  = histo.GetMinimum()
    max  = histo.GetMaximum()

    best = args["bestDict"][key]
    error = args["errorDict"][key] if "errorDict" in args else None
    out = []
    out.append(hLine.DrawLine(q[1], min, q[1], max))
    out.append(hLine.DrawLine(q[0], min, q[0], max))
    out.append(hLine.DrawLine(q[2], min, q[2], max))

    out.append(bestLine.DrawLine(best, min, best, max))
    if error!=None : out.append(errorLine.DrawLine(best - error, max/2.0, best + error, max/2.0))
    return out

def expectedLimitPlots(quantiles = {}, hist = None, obsLimit = None, note = "", plotsDir = "plots") :
    ps = "%s/limits_%s.ps"%(plotsDir, note)
    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(ps+"[")

    l = drawDecoratedHisto(quantiles, hist, obsLimit)

    canvas.Print(ps)
    canvas.Print(ps+"]")
    utils.ps2pdf(ps, sameDir = True)

def pValuePlots(pValue = None, observed = None, pseudo = None, note = "", plotsDir = "", stdout = False,
                key = "", keyLatex = "") :
    finalPValue = utils.ListFromTGraph(pValue)[-1]
    if stdout : print "pValue (TS = %s) = %g"%(key, finalPValue)

    observedList = utils.ListFromTGraph(observed)
    assert len(observedList)==1,len(observedList)
    observedValue = observedList[0]
    toyValues = utils.ListFromTGraph(pseudo)

    fileName = "%s/pValue_%s_%s.pdf"%(plotsDir, key, note)
    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(fileName+"[")

    pValue.SetMarkerStyle(20)
    pValue.SetTitle(";toy number;p-value")
    pValue.Draw("ap")

    Tl = r.TLatex()
    Tl.SetNDC(True)
    Tl.SetTextSize(0.05)
    Tl.DrawLatex(0.05, 0.92, "obs. value of TS = %g"%observedValue)
    Tl.DrawLatex(0.55, 0.92, "quantile of obs. = %g"%finalPValue)
    canvas.Print(fileName)

    histo = r.TH1D("%sHisto"%key,";%s;pseudo experiments / bin"%keyLatex, 100, 0.0, max(toyValues + observedList)*1.1)
    for value in toyValues :
        histo.Fill(value)
    histo.SetStats(False)
    histo.SetMinimum(0.0)
    histo.Draw()

    line = r.TLine()
    line.SetLineColor(r.kBlue)
    line.SetLineWidth(2)
    line = line.DrawLine(observedValue, histo.GetMinimum(), observedValue, histo.GetMaximum())

    legend = r.TLegend(0.1, 0.7, 0.5, 0.9)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.AddEntry(histo, "%s in pseudo-experiments"%keyLatex, "l")
    legend.AddEntry(line, "%s observed"%keyLatex, "l")
    legend.Draw()
    canvas.Print(fileName)

    canvas.Print(fileName+"]")

def ensembleResults(note = "", nToys = None) :
    _,tfile = ensemble.results(note, nToys)

    out = []
    for key,keyLatex in [("lMax", "log(L_{max})"),
                         ("chi2Prob", "#chi^{2} prob."),
                         ] :
        kargs = {}
        for item in ["pValue", "observed", "pseudo"] :
            kargs[item] = tfile.Get("/graphs/%s_%s"%(key, item))
        for item in ["key", "keyLatex"] :
            kargs[item] = eval(item)
        out.append(kargs)
    return out

def ensemblePlotsAndTables(note = "", nToys = None, plotsDir = "", stdout = False, selections = []) :
    #open results
    obs,tfile = ensemble.results(note, nToys)

    #collect histos and quantiles
    fHistos,fQuantiles = ensemble.histosAndQuantiles(tfile, "funcs")
    pHistos,pQuantiles = ensemble.histosAndQuantiles(tfile, "pars")
    oHistos,oQuantiles = ensemble.histosAndQuantiles(tfile, "other")

    #p-value plots
    for kargs in ensembleResults(note, nToys) :
        for item in ["note", "plotsDir", "stdout"] :
            kargs[item] = eval(item)
        pValuePlots(**kargs)

    #latex yield tables
    ensemble.latex(quantiles = fQuantiles, bestDict = obs["funcBestFit"],
                   stdout = stdout, selections = selections, note = note, nToys = nToys)

    #ensemble plots
    canvas = utils.numberedCanvas()
    fileName = "%s/ensemble_%s.pdf"%(plotsDir, note)
    canvas.Print(fileName+"[")

    utils.cyclePlot(d = pHistos, f = histoLines, canvas = canvas, fileName = fileName,
                    args = {"bestDict":obs["parBestFit"], "bestColor":r.kGreen,
                            "quantileDict": pQuantiles, "quantileColor":r.kRed,
                            "errorDict":obs["parError"], "errorColor":r.kGreen,
                            })
    utils.cyclePlot(d = fHistos, f = histoLines, canvas = canvas, fileName = fileName,
                    args = {"bestDict":obs["funcBestFit"], "bestColor":r.kGreen,
                            "quantileDict": fQuantiles, "quantileColor":r.kRed,
                            "errorColor":r.kGreen})
    utils.cyclePlot(d = oHistos, canvas = canvas, fileName = fileName)
    #utils.cyclePlot(d = pHistos2, canvas = canvas, fileName = fileName)
    canvas.Print(fileName+"]")

    tfile.Close()

def clsCustomPlots(obs = None, valuesDict = {}, note = "", plotsDir = "plots") :
    ps = "%s/clsCustom_%s.ps"%(plotsDir, note)

    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(ps+"[")

    totalList = [obs]
    for v in valuesDict.values() :
        totalList += v

    colors = {"b":r.kBlue, "sb":r.kRed, "obs":r.kBlack}
    maxes = []
    histos = {}
    for key,values in valuesDict.iteritems() :
        h = histos[key] = r.TH1D(key,";TS;pseudo experiments / bin", 100, min(totalList), max(totalList))
        map(h.Fill, values)
        h.SetStats(False)
        h.SetMinimum(0.0)
        h.SetLineColor(colors[key])
        maxes.append( (h.GetMaximum(), h) )

    maxes.sort()
    maxes.reverse()
    first = True
    for m,h in maxes :
        h.Draw("" if first else "same")
        first = False

    line = r.TLine()
    line.SetLineColor(colors["obs"])
    line.SetLineWidth(2)
    line.SetLineStyle(3)
    line = line.DrawLine(obs, 0.0, obs, maxes[0][0])

    legend = r.TLegend(0.1, 0.7, 0.5, 0.9)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    for key in valuesDict.keys() :
        legend.AddEntry(histos[key], key, "l")

    legend.AddEntry(line, "observed", "l")
    legend.Draw()

    canvas.Print(ps)
    canvas.Print(ps+"]")
    utils.ps2pdf(ps, sameDir = True)

def pretty(l) :
    out = "("
    for i,item in enumerate(l) :
        out += ("%6.2f"%item) if item else "%6s"%""
        if i!=len(l)-1 : out += ", "
    return out+")"

def drawOne(hist = None, goptions = "", errorBand = False, bandFillStyle = 1001) :
    if not errorBand :
        hist.Draw(goptions)
        return []

    goptions = "he2"+goptions
    errors   = hist.Clone(hist.GetName()+"_errors")
    noerrors = hist.Clone(hist.GetName()+"_noerrors")
    for i in range(1, 1+noerrors.GetNbinsX()) : noerrors.SetBinError(i, 0.0)
    errors.SetFillColor(errorBand)
    errors.SetFillStyle(bandFillStyle)
    errors.Draw("e2same")
    noerrors.Draw("h"+goptions)
    return [errors, noerrors]

def printOnePage(canvas, fileName, ext = ".pdf", plotsDir = "plots") :
    if "_logy" in fileName :
        fileName = fileName.replace("_logy","")+"_logy"
    fileName = "%s/%s%s"%(plotsDir, fileName, ext)
    super(utils.numberedCanvas, canvas).Print(fileName)
    if ext==".eps" : utils.epsToPdf(fileName)

def legSpec(goptions) :
    out = ""
    if "p" in goptions : out += "p"
    if "hist" in goptions : out += "l"
    return out

def akDesc(wspace, var1 = "", var2 = "", errors = True) :
    varA = wspace.var("%s"%var1)
    vark = wspace.var("%s"%var2)
    out = ""
    if varA : out += "%s = %4.2e%s; "%(var1[0], varA.getVal(), " #pm %4.2e"%varA.getError() if errors else "")
    if vark : out += "%s = %4.2e%s"  %(var2[0], vark.getVal(), " #pm %4.2e"%vark.getError() if errors else "")
    return out

def obsString(label = "", other = "", lumi = 0.0) :
    return "%s (%s, %3.1f/fb)"%(label, other, lumi/1.0e3)

class validationPlotter(object) :
    def __init__(self, args) :
        for key,value in args.iteritems() :
            setattr(self,key,value)
        if self.signalExampleToStack : assert self.smOnly
        if not hasattr(self,"drawRatios") : setattr(self,"drawRatios",False)

        if self.printPages :
            print "printing individual pages; drawMc = False"
            self.drawMc = False

        self.quantiles = {}
        if self.errorsFromToys:
            print "using quantiles from previously generated toys"
            self.quantiles = ensemble.functionQuantiles(self.note, nToys=self.errorsFromToys)

        self.toPrint = []
        self.ewkType = "function" if self.REwk else "var"

        self.plotsDir = "plots"
        utils.getCommandOutput("mkdir %s"%self.plotsDir)

        if not self.smOnly :
            iXs = self.signalToTest.label.find("(xs =")
            xs = self.signalToTest.label[6+iXs:-1]
            mlF = "[#sigma_{ML} = (%3.1e #pm %3.1e) #times %s]"%(self.wspace.var("f").getVal(), self.wspace.var("f").getError(), xs)
            self.signalDesc = "#lower[0.35]{#splitline{%s}{%s}}"%(self.signalToTest.label[:iXs], mlF)
            self.signalDesc2 = ""

        self.width1 = 2
        self.width2 = 3

        self.smDesc = "Standard Model" if not self.ignoreHad else "EWK Prediction"
        if self.errorsFromToys :
            self.smDesc += " #pm Expected Unc."
        self.bandInLegend = True
        self.sm = r.kAzure if not self.ignoreHad else r.kSpring
        self.smError = r.kAzure+6 if not self.ignoreHad else r.kGreen-2
        self.smBandStyle = 1001
        self.sig = r.kPink+7
        self.ewk = r.kBlue+1
        self.qcd = r.kGreen+3
        self.qcdError = r.kGreen-3

    def makeLegends(self) :
        x0 = 0.35; x1 = 0.87
        y0 = 0.65; y1 = 0.88
        dx = x1 - x0
        dy = y1 - y0
        f = 3.75/5.0
        self.hadLegend  = {"legend0": (x0,y0     ), "legend1": (x1, y1)}
        self.photLegend = {"legend0": (x0,y1-dy*f), "legend1": (x1, y1)}
        self.mumuLegend = self.photLegend
        y = 1.0
        if self.signalExampleToStack and self.signalExampleToStack.keyPresent("effMuon") :
            f = 1.0
            y = 1.08
        self.muonLegend = {"legend0": (1.0-x1, y-y0), "legend1": (1.0-x1+dx, y-y0-dy*f)} #top left to bottom right

    def go(self) :
        self.canvas = utils.numberedCanvas()
        utils.divideCanvas( self.canvas, self.drawRatios )
        fields = ["%s/bestFit"%self.plotsDir, self.note, "sel%s"%self.label]
        if self.smOnly : fields.append("smOnly")
        self.psFileName = "_".join(fields)+".pdf"
        self.canvas.Print(self.psFileName+"[")

        self.makeLegends()

        self.simplePlots()
        self.hadPlots()
        #self.hadDataMcPlots()
        self.muonPlots()
        self.photPlots()
        self.mumuPlots()
        self.ewkPlots()
        #self.mcFactorPlots()
        self.alphaTRatioPlots()
        self.significancePlots()
        self.rhoPlots()
        self.printPars()
        self.correlationHist()
        #self.propagatedErrorsPlots(printResults = False)

        if self.printPages :
            for item in sorted(list(set(self.toPrint))) :
                print " ".join(item)
            #self.hadronicSummaryTable()

        self.canvas.Print(self.psFileName+"]")
        #utils.ps2pdf(self.psFileName, sameDir = True)

    def simplePlots(self) :
        if "simple" not in self.lumi : return
        vars = [
            {"var":"bSimple", "type":"var", "desc":"b", "color":self.sm, "style":1, "width":self.width2, "stack":"total"},
            ]
        if not self.smOnly :
            vars += [{"var":"sSimple", "type":"function", "desc":self.signalDesc, "desc2":self.signalDesc2, "color":self.sig, "style":1, "width":self.width1, "stack":"total"}]
        elif self.signalExampleToStack :
            vars += [{"example":self.signalExampleToStack, "box":"simple", "desc":self.signalExampleToStack.label,
                      "color":self.signalExampleToStack.lineColor, "style":self.signalExampleToStack.lineStyle,
                      "width":self.width1, "stack":"total"}]

        for logY in [False, True] :
            thisNote = "Simple Sample%s"%(" (logY)" if logY else "")
            fileName = ["simple"]+(["logy"] if logY else [])
            self.plot(fileName = fileName, legend0 = (0.48, 0.65), legend1 = (0.88, 0.85),
                      obs = {"var":"nSimple", "desc": obsString(self.obsLabel, "simple sample", self.lumi["simple"])},
                      otherVars = vars, logY = logY, stampParams = False)

    def hadPlots(self) :
        if "had" not in self.lumi:
            return

        vars = [{"var": "hadB",
                 "type": "function",
                 "desc": "SM (QCD + EWK)" if self.drawComponents else self.smDesc,
                 "color": self.sm,
                 "style": 1,
                 "width": self.width2,
                 "stack": "total",
                 "errorBand": self.smError,
                 "repeatNoBand": True,
                 "bandStyle": self.smBandStyle,
                 "errorsFrom": "",
                },
                {"var":"mcHad",
                 "type":None,
                 "color":r.kGray+2,
                 "style":2,
                 "width":2,
                 "desc":"SM MC #pm stat. error",
                 "stack":None,
                 "errorBand":r.kGray} if self.drawMc else {},
                ]
        if self.drawComponents :
            vars +=[
            {"var":"ewk",  "type":self.ewkType, "desc":"EWK (t#bar{t} + t + W + Z#rightarrow#nu#bar{#nu})",
             "color":self.ewk, "style":2, "width":self.width1, "stack":"background", "suppress":["min","max"]},
            #{"var":"qcd",  "type":"function", "desc":"QCD", "desc2":akDesc(self.wspace, "A_qcd", "k_qcd", errors = True),
            # "color":r.kMagenta, "style":3, "width":2, "stack":"background"},
            {"var":"zInv", "type":"function", "desc":"Z#rightarrow#nu#bar{#nu}",  "color":r.kOrange+7, "style":2, "width":self.width1, "stack":"ewk"},
            #{"var":"ttw",  "type":"function", "desc":"t#bar{t} + W",
            # "desc2": "#rho_{#mu} = %4.2f #pm %4.2f"%(self.wspace.var("rhoMuonW").getVal(), self.wspace.var("rhoMuonW").getError()) if self.wspace.var("rhoMuonW") else "",
            # "color":r.kGreen, "style":2, "width":2, "stack":"ewk"},
            ]
        if not self.smOnly :
            vars += [{"var":"hadS", "type":"function", "desc":self.signalDesc, "desc2":self.signalDesc2, "color":self.sig, "style":1, "width":self.width1, "stack":"total"}]
        elif self.signalExampleToStack :
            vars += [{"example":self.signalExampleToStack, "box":"had", "desc":self.signalExampleToStack.label,
                      "color":self.signalExampleToStack.lineColor, "style":self.signalExampleToStack.lineStyle,
                      "width":self.width1, "stack":"total"}]

        obs = {"var":"nHad",
               #"desc": obsString(self.obsLabel, "hadronic sample", self.lumi["had"]),
               #"desc": "Data (hadronic sample, %s)" % self.selNote,
               "desc": "Data (signal region, %s)" % self.selNote,
               }

        for logY in [False, True] :
            thisNote = "Hadronic Signal Sample%s"%(" (logY)" if logY else "")
            self.plot(fileName=["hadronic"]+(["logy"] if logY else []),
                      obs=obs,
                      otherVars=vars,
                      logY=logY,
                      stampParams=True,
                      ratioDenom="hadB",
                      **self.hadLegend)


        for var in [obs]+vars:
            var.update({"dens": ["hadB"], "denTypes": ["function"]})

        self.plot(note="",
                  fileName=["b_over_b"],
                  legend0=(0.2, 0.75),
                  legend1=(0.6, 0.88),
                  yLabel="Events / b",
                  yAxisMinMax=(0.0, 2.0),
                  obs=obs,
                  otherVars=vars,
                  )

    def hadDataMcPlots(self) :
        for logY in [False, True] :
            thisNote = "Hadronic Signal Sample%s"%(" (logY)" if logY else "")
            fileName = ["hadronic","data","mc"]+(["logy"] if logY else [])
            self.plot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True, logY = logY,
                      obs = {"var":"nHad", "desc": obsString(self.obsLabel, "hadronic sample", self.lumi["had"])}, otherVars = [
                {"var":"mcHad", "type":None, "color":r.kGray+2, "style":2, "width":2, "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray},
                {"var":"ewk",  "type":self.ewkType, "desc":"EWK", "desc2":akDesc(self.wspace, "A_ewk", "k_ewk", errors = True) if self.REwk else "[floating]",
                 "color":r.kCyan, "style":2, "width":2, "stack":"background"},
                {"var":"hadB", "type":"function", "desc":"expected total background",
                 "color":r.kBlue, "style":1, "width":3, "stack":"total"},
                ])

    def muonPlots(self) :
        if "muon" not in self.lumi : return
        vars = [
            {"var":"muonB",   "type":"function", "color":self.sm, "style":1, "width":self.width2, "desc":self.smDesc, "stack":"total",
             "errorBand":self.smError, "repeatNoBand":True, "bandStyle":self.smBandStyle},
            {"var":"mcMuon",  "type":None,       "color":r.kGray+2, "style":2, "width":2,
             "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray} if self.drawMc else {},
            ]
        if not self.smOnly :
            vars += [{"var":"muonS",   "type":"function", "color":self.sig, "style":1, "width":self.width1, "desc":self.signalDesc, "desc2":self.signalDesc2, "stack":"total"}]
        elif self.signalExampleToStack and self.signalExampleToStack.keyPresent("effMuon") :
            vars += [{"example":self.signalExampleToStack, "box":"muon", "desc":self.signalExampleToStack.label,
                      "color":self.signalExampleToStack.lineColor, "style":self.signalExampleToStack.lineStyle,
                      "width":self.width1, "stack":"total"}]

        for logY in [False, True] :
            thisNote = "Muon Control Sample%s"%(" (logY)" if logY else "")
            fileName = ["muon"]+(["logy"] if logY else [])
            legend = self.muonLegend if "ge4b" not in self.note else self.photLegend
            self.plot(fileName = fileName,
                      obs = {"var":"nMuon", #"desc": obsString(self.obsLabel, "muon sample", self.lumi["muon"])},
                             "desc": "Data (#mu + jets sample, %s)"%self.selNote},
                      otherVars = vars, logY = logY, ratioDenom = "muonB", **legend)

    def photPlots(self) :
        if "phot" not in self.lumi : return
        if self.muonForFullEwk : return
        for logY in [False, True] :
            thisNote = "Photon Control Sample%s"%(" (logY)" if logY else "")
            fileName = ["photon"]+(["logy"] if logY else [])
            self.plot(fileName = fileName,
                      reverseLegend = True, logY = logY, ratioDenom = "photExp",
                      obs = {"var":"nPhot", #"desc": obsString(self.obsLabel, "photon sample", self.lumi["phot"])},
                             "desc": "Data (#gamma + jets sample, %s)"%self.selNote},
                      otherVars = [
                {"var":"mcPhot", "type":None, "color":r.kGray+2, "style":2, "width":2,
                 "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray} if self.drawMc else {},
                {"var":"photExp", "type":"function", "color":self.sm,  "style":1, "width":self.width2,
                 "desc":self.smDesc, "stack":None, "errorBand":self.smError, "bandStyle":self.smBandStyle},
                ], **self.photLegend)

    def mumuPlots(self) :
        if "mumu" not in self.lumi : return
        if self.muonForFullEwk : return
        for logY in [False, True] :
            thisNote = "Mu-Mu Control Sample%s"%(" (logY)" if logY else "")
            fileName = ["mumu"]+(["logy"] if logY else [])
            self.plot(fileName = fileName,
                      reverseLegend = True,
                      obs = {"var":"nMumu", #"desc": obsString(self.obsLabel, "mumu sample", self.lumi["mumu"])},
                             "desc": "Data (#mu#mu + jets sample, %s)"%self.selNote},
                      logY = logY, ratioDenom = "mumuExp", otherVars = [
                {"var":"mcMumu", "type":None, "color":r.kGray+2, "style":2, "width":2,
                 "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray} if self.drawMc else {},
                {"var":"mumuExp", "type":"function", "color":self.sm,   "style":1, "width":self.width2, "desc":self.smDesc, "stack":None,
                 "errorBand":self.smError, "bandStyle":self.smBandStyle},
                ], **self.mumuLegend)

    def ewkPlots(self) :
        if "had" not in self.lumi : return

        if not self.muonForFullEwk :
            self.plot(note = "ttW scale factor (result of fit)", legend0 = (0.5, 0.8), yAxisMinMax = (0.0,3.0), yLabel = "",
                      otherVars = [ {"var":"ttw", "type":"function", "dens":["mcTtw"], "denTypes":[None], "desc":"ML ttW / MC ttW",
                                     "stack":None, "color":r.kGreen, "goptions": "hist"} ])

            self.plot(note = "Zinv scale factor (result of fit)", legend0 = (0.5, 0.8), yAxisMinMax = (0.0,3.0), yLabel = "",
                      otherVars = [ {"var":"zInv", "type":"function", "dens":["mcZinv"], "denTypes":[None], "desc":"ML Z->inv / MC Z->inv",
                                     "stack":None, "color":r.kRed, "goptions": "hist"}])

            self.plot(note = "fraction of EWK background which is Zinv (result of fit)" if not self.printPages else "",
                      fileName = ["fZinv"], legend0 = (0.2, 0.8), legend1 = (0.55, 0.85), yAxisMinMax = (0.0,1.0), yLabel = "",
                      otherVars = [{"var":"fZinv", "type":"var", "color":r.kBlue, "style":1, "desc":"fit Z#rightarrow#nu#bar{#nu} / EWK", "stack":None}])
        else :
            self.plot(note = "ewk scale factor (result of fit)", legend0 = (0.5, 0.8), yLabel = "",
                      otherVars = [ {"var":"ewk", "type":("function" if self.REwk else "var"), "dens":["mcHad"], "denTypes":[None], "desc":"ML EWK / MC EWK",
                                     "stack":None, "color":r.kRed, "suppress":["min","max"], "goptions": "hist"}])

    def mcFactorPlots(self) :
        if "muon" in self.lumi :
            self.plot(note = "muon translation factor (from MC)", legend0 = (0.5, 0.8),
                      otherVars = [{"var":"rMuon", "type":"var", "color":r.kBlue, "style":1, "desc":"MC muon / MC %s"%("ewk" if self.muonForFullEwk else "ttW"), "stack":None}],
                      yLabel = "", scale = self.lumi["had"]/self.lumi["muon"])
        if self.muonForFullEwk : return
        if "phot" in self.lumi :
            self.plot(note = "photon translation factor (from MC)", legend0 = (0.5, 0.8),
                      otherVars = [{"var":"rPhot", "type":"var", "color":r.kBlue, "style":1, "desc":"MC #gamma / MC Z#rightarrow#nu#bar{#nu} / P", "stack":None}],
                      yLabel = "", scale = self.lumi["had"]/self.lumi["phot"])

        if "mumu" in self.lumi :
            self.plot(note = "mumu translation factor (from MC)", legend0 = (0.5, 0.8),
                      otherVars = [{"var":"rMumu", "type":"var", "color":r.kBlue, "style":1, "desc":"MC Z#rightarrow#mu#bar{#mu} / MC Z#rightarrow#nu#bar{#nu} / P", "stack":None}],
                      yLabel = "", scale = self.lumi["had"]/self.lumi["mumu"])

    def significancePlots(self):
        if "had" not in self.lumi or not self.signalExampleToStack:
            return

        self.plot(note="",
                  fileName=["s_over_b"],
                  legend0=(0.2, 0.8),
                  legend1=(0.55, 0.85),
                  yLabel="s / b",
                  otherVars=[{"example": self.signalExampleToStack,
                              "box": "had",
                              "desc": self.signalExampleToStack.label+" / b",
                              "color": self.signalExampleToStack.lineColor,
                              "style": self.signalExampleToStack.lineStyle,
                              "width": self.width1,
                              "stack": "total",
                              "dens": ["hadB"],
                              "denTypes": ["function"],
                              }],
                  )

        self.plot(note="",
                  fileName=["s_over_root_b"],
                  legend0=(0.2, 0.8),
                  legend1=(0.55, 0.85),
                  yLabel="s / #sqrt{b}",
                  otherVars=[{"example": self.signalExampleToStack,
                              "box": "had",
                              "desc": self.signalExampleToStack.label+" / b",
                              "color": self.signalExampleToStack.lineColor,
                              "style": self.signalExampleToStack.lineStyle,
                              "width": self.width1,
                              "stack": "total",
                              "dens": ["hadB"],
                              "denTypes": ["function"],
                              "denFuncs": [lambda x:math.sqrt(x)],
                              }],
                  )

        self.plot(note="",
                  fileName=["s_over_func_of_b"],
                  legend0=(0.2, 0.8),
                  legend1=(0.55, 0.85),
                  yLabel="s / #sqrt{b + (0.1b)^{2}}",
                  otherVars=[{"example": self.signalExampleToStack,
                              "box": "had",
                              "desc": self.signalExampleToStack.label+" / b",
                              "color": self.signalExampleToStack.lineColor,
                              "style": self.signalExampleToStack.lineStyle,
                              "width": self.width1,
                              "stack": "total",
                              "dens": ["hadB"],
                              "denTypes": ["function"],
                              "denFuncs": [lambda x:math.sqrt(x + (0.1*x)**2)],
                              }],
                  )

        self.plot(note="",
                  fileName=["s_over_unc_b"],
                  legend0=(0.2, 0.8),
                  legend1=(0.55, 0.85),
                  yLabel="s / #sigma_{b}",
                  otherVars=[{"example": self.signalExampleToStack,
                              "box": "had",
                              "desc": self.signalExampleToStack.label+" / b",
                              "color": self.signalExampleToStack.lineColor,
                              "style": self.signalExampleToStack.lineStyle,
                              "width": self.width1,
                              "stack": "total",
                              "dens": ["hadB"],
                              "denTypes": ["function"],
                              "denKeys": ["uncFromToys"],
                              }],
                  )
        return


    def alphaTRatioPlots(self) :
        if "had" not in self.lumi : return

        specs = [
            {"var":"hadB",  "type":"function", "desc":"SM (QCD + EWK)" if self.drawComponents else self.smDesc,
             "color":self.sm, "style":1, "width":self.width2, "stack":"total",
             "errorBand":self.smError, "repeatNoBand":True, "bandStyle":self.smBandStyle,
             "dens":["nHadBulk"], "denTypes":["var"]},
            ]
        if self.drawComponents :
            specs +=[
                {"var":"ewk", "type":self.ewkType, "desc":"EWK (t#bar{t} + t + W + Z#rightarrow#nu#bar{#nu})",
                 "color":self.ewk, "style":2, "width":self.width1, "stack":"background", "suppress":["min","max"],
                 "dens":["nHadBulk"], "denTypes":["var"]},
                {"var":"qcd", "type":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"QCD",
                 "color":self.qcd, "width":self.width1, "markerStyle":1, "legSpec":"lp", "errorBand":self.qcdError},
                ]

        if not self.smOnly :
            specs += [{"var":"hadS", "type":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":self.signalDesc+" "+self.signalDesc2,
                       "color":self.sig, "style":1, "width":self.width1, "stack":"total"}]
        elif self.signalExampleToStack :
            specs += [{"example":self.signalExampleToStack, "box":"had", "dens":["nHadBulk"], "denTypes":["var"], "desc":self.signalExampleToStack.label,
                       "color":self.signalExampleToStack.lineColor, "style":self.signalExampleToStack.lineStyle,
                       "width":self.width1, "stack":"total"}]

        self.plot(fileName = ["hadronic","alphaT","ratio"], legend0 = (0.48, 0.65), legend1 = (0.85, 0.88),
                  obs = {"var":"nHad", "dens":["nHadBulk"], "denTypes":["var"], "desc": "Data (hadronic sample, %s)"%self.selNote},
                  otherVars = specs, yLabel = "R_{#alpha_{T}}", customMaxFactor = [1.5]*2)

        return

        if self.muonForFullEwk :
            self.plot(note = "muon to ewk", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), yLabel = "R_{#alpha_{T}}", customMaxFactor = [1.5]*2,
                      obs = {"var":"nMuon", "dens":["nHadBulk", "rMuon"], "denTypes":["data", "var"], "desc":"nMuon * (MC ewk / MC mu) / nHadBulk"},
                      otherVars = [{"var":"ewk", "type":("function" if self.REwk else "var"), "dens":["nHadBulk"], "denTypes":["data"],
                                    "desc":"ML ewk / nHadBulk", "suppress":["min","max"], "color":r.kGreen}])

            #self.plot(note = "``naive prediction''", legend0 = (0.12, 0.7), legend1 = (0.82, 0.88), yLabel = "R_{#alpha_{T}}", maximum = 20.0e-6,#customMaxFactor = [1.5]*2,
            #          otherVars = [
            #        {"var":"nMuon", "type":"var",      "dens":["nHadBulk", "rMuon"], "denTypes":["data", "var"], "stack":"pred", "goptions":"pe",
            #         "desc":"nMuon * (MC ewk / MC mu) / nHadBulk", "markerStyle":20, "color":r.kGreen+3, "legSpec":"lpe"},
            #        {"var":"ewk",   "type":"function", "dens":["nHadBulk"], "denTypes":["data"], "desc":"ML ewk / nHadBulk", "color":r.kGreen},
            #        ])

        else :
            self.plot(note = "muon to tt+W", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), yLabel = "R_{#alpha_{T}}", customMaxFactor = [1.5]*2,
                      obs = {"var":"nMuon", "dens":["nHadBulk", "rMuon"], "denTypes":["data", "var"], "desc":"nMuon * (MC ttW / MC mu) / nHadBulk"},
                      otherVars = [{"var":"ttw",   "type":"function", "dens":["nHadBulk"], "denTypes":["data"], "desc":"ML ttW / nHadBulk", "color":r.kGreen}])

            self.plot(note = "photon to Zinv", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), yLabel = "R_{#alpha_{T}}", customMaxFactor = [1.5]*2,
                      obs = {"var":"nPhot", "dens":["nHadBulk", "rPhot"], "denTypes":["data", "var"], "desc":"nPhot * (MC Zinv / MC #gamma) / nHadBulk"},
                      otherVars = [{"var":"zInv",  "type":"function", "dens":["nHadBulk"], "denTypes":["data"], "desc":"ML Zinv / nHadBulk", "color":r.kRed}])

            #self.plot(note = "mumu to Zinv", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), yLabel = "R_{#alpha_{T}}", maximum = 10.0e-6,
            #          obs = {"num":"nMumu", "dens":["nHadBulk", "rMumu"], "denTypes":["data", "var"], "desc":"nMumu * (MC Zinv / MC Mumu) / nHadBulk"},
            #          otherVars = [{"num":"zInv",  "numType":"function", "dens":["nHadBulk"], "denTypes":["data"], "desc":"ML Zinv / nHadBulk", "color":r.kRed}])


            self.plot(note = "``naive prediction''", legend0 = (0.12, 0.7), legend1 = (0.82, 0.88), yLabel = "R_{#alpha_{T}}", maximum = 20.0e-6,#customMaxFactor = [1.5]*2,
                      otherVars = [
                    {"var":"nMuon", "type":"var",      "dens":["nHadBulk", "rMuon"], "denTypes":["data", "var"], "stack":"pred", "goptions":"pe",
                     "desc":"nMuon * (MC ttW / MC mu) / nHadBulk",                       "markerStyle":20, "color":r.kGreen+3, "legSpec":"lpe"},
                    {"var":"nPhot", "type":"var",      "dens":["nHadBulk", "rPhot"], "denTypes":["data", "var"], "stack":"pred", "goptions":"pe",
                     "desc":" + nPhot * (MC Zinv / MC #gamma) / nHadBulk (stacked)", "markerStyle":20, "color":r.kBlue+3,   "legSpec":"lpe"},
                    {"var":"ttw",   "type":"function", "dens":["nHadBulk"],          "denTypes":["data"], "stack":"ml",
                     "desc":"ML ttW / nHadBulk", "color":r.kGreen},
                    {"var":"zInv",  "type":"function", "dens":["nHadBulk"],          "denTypes":["data"], "stack":"ml",
                     "desc":"ML EWK (ttw+zInv) / nHadBulk", "color":self.ewk},
                    ])

    def rhoPlots(self) :
        if "simple" in self.lumi : return
        if self.label!=self.systematicsLabel : return

        if "phot" in self.lumi :
            self.plot(otherVars = [{"var":"rhoPhotZ", "type":"var", "desc":"#rho_{#gammaZ}", "suppress":["min","max"], "color":self.ewk,
                                    "width":self.width1, "markerStyle":1, "legSpec":"lpf", "errorBand":self.ewk-6, "systMap":True}],
                      yAxisMinMax = (0.0,2.0), yLabel = "", legend0 = (0.18, 0.7), legend1 = (0.45, 0.9))

        if "muon" in self.lumi :
            self.plot(otherVars = [{"var":"rhoMuonW", "type":"var", "desc":"#rho_{#muW}", "suppress":["min","max"], "color":self.ewk,
                                    "width":self.width1, "markerStyle":1, "legSpec":"lpf", "errorBand":self.ewk-6, "systMap":True}],
                      yAxisMinMax = (0.0,2.0), yLabel = "", legend0 = (0.18, 0.7), legend1 = (0.45, 0.9))

        if "mumu" in self.lumi :
            self.plot(otherVars = [{"var":"rhoMumuZ", "type":"var", "desc":"#rho_{#mu#muZ}", "suppress":["min","max"], "color":self.ewk,
                                    "width":self.width1, "markerStyle":1, "legSpec":"lpf", "errorBand":self.ewk-6, "systMap":True}],
                      yAxisMinMax = (0.0,2.0), yLabel = "", legend0 = (0.18, 0.7), legend1 = (0.45, 0.9))

    def printPars(self) :
        def ini(x, y) :
            y = printText(x, y, "%20s:  %6s   +/- %6s   [ %4s   -  %4s  ]"%("par name", "value", "error", "min", "max"))
            y = printText(x, y, "-"*64)
            return y

        def printText(x, y, s, color = r.kBlack) :
            text.SetTextColor(color)
            text.DrawText(x, y, s)
            y -= slope
            return y

        def close(name = "", value = None, error = None, min = None, max = None, factor = 2.0) :
            return (value + factor*error > max) or (value - factor*error < min)

        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.4*text.GetTextSize())
        x = -0.5
        y = y0 = 0.95
        slope = 0.02
        nLines = 40

        self.canvas.Clear()

        for i, d in enumerate(common.floatingVars(self.wspace)):
            if not (i%nLines) :
                x += 0.5
                y = y0
                y = ini(x, y)

            s = "%20s: %9.2e +/-%8.1e  [%7.1e - %7.1e]"%(d["name"], d["value"], d["error"], d["min"], d["max"])
            y = printText(x, y, s, color = r.kRed if close(**d) else r.kBlack)
            i += 1

        self.canvas.Print(self.psFileName)
        return

    def correlationHist(self) :
        if self.smOnly and "simple" in self.lumi : return

        name = "correlation_matrix"
        h = self.results.correlationHist(name)
        h.SetStats(False)
        r.gStyle.SetPaintTextFormat("4.1f")
        h.Draw("colz")

        for side in ["Right", "Left", "Top", "Bottom"] :
            getattr(r.gPad,"Set%sMargin"%side)(0.15)

        if self.printPages and name :
            h.SetTitle("")
            printOnePage(self.canvas, "_".join([name, self.label]))
            #printOnePage(self.canvas, name, ext = ".C")
        self.canvas.Print(self.psFileName)
        utils.delete(h)

    def randomizedPars(self, nValues) :
        return [copy.copy(self.results.randomizePars()) for i in range(nValues)]

    def filteredPars(self, randPars = [], maxPdfValue = None, pdfName = "") :
        out = []
        #for parSet in randPars :
        #    func = self.wspace.function("hadB0")
        #    func.getVariables().assignValueOnly(parSet)
        #    if func.getVal()>650.0 : continue
        #    out.append(parSet)

        #for parSet in randPars :
        #    index = parSet.index("k_qcd")
        #    if index<0 : continue
        #    if parSet[index].getVal()<0.003 : continue
        #    out.append(parSet)

        for parSet in randPars :
            self.wspace.allVars().assignValueOnly(parSet)
            value = self.wspace.pdf(pdfName).getVal()
            if -2.0*math.log(value/maxPdfValue)>60.0 : continue
            out.append(parSet)
        return out

    def llHisto(self, randPars = [], pdfName = "", maxPdfValue = None, minNll = None, ndf = None) :
        values = []
        for parSet in randPars :
            self.wspace.allVars().assignValueOnly(parSet)
            value = self.wspace.pdf(pdfName).getVal()
            values.append(-2.0*math.log(value/maxPdfValue))

        h = r.TH1D("logPdfValue", ";-2*log(pdfValue/max.pdfValue);parameter value set / bin", 100, 0.0, 1.1*max(values))
        h.Sumw2()
        map(h.Fill, values)
        h.Draw()

        #chi2 = r.TH1D("chi2","", h.GetNbinsX(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
        #for i in range(1, 1+h.GetNbinsX()) :
        #    xLo = chi2.GetBinLowEdge(  i)
        #    xHi = chi2.GetBinLowEdge(1+i)
        #    chi2.SetBinContent(i, r.TMath.Prob(xLo, ndf) - r.TMath.Prob(xHi, ndf))
        #
        #chi2.SetLineColor(r.kRed)
        #chi2.Scale(h.GetMaximum()/chi2.GetMaximum())
        #chi2.Draw("same")

        self.canvas.Print(self.psFileName)
        return h

    def funcHistos(self, randPars = [], suffix = "") :
        histos = {}

        funcs = self.wspace.allFunctions()
        func = funcs.createIterator()
        while func.Next() :
            name = "%s%s"%(func.GetName(), suffix)
            h = r.TH1D(name, name, 100, 1.0, -1.0)
            h.Sumw2()

            for parSet in randPars :
                func.getVariables().assignValueOnly(parSet)
                value = func.getVal()
                #if value<0.0 : values.Print("v")
                h.Fill(value)

            histos[func.GetName()] = h
        return histos

    def parHistos1D(self, pars = [], randPars = [], suffix = "") :
        histos = {}

        for par in pars :
            name = "%s%s"%(par,suffix)
            h = r.TH1D(name, name, 100, 1.0, -1.0)
            h.Sumw2()

            for parList in randPars :
                index = parList.index(par)
                if index<0 : continue
                h.Fill(parList[index].getVal())

            histos[par] = h
        return histos

    def parHistos2D(self, pairs = [], randPars = [], suffix = "") :
        histos = {}

        for pair in pairs :
            name = "_".join(pair)
            name += suffix
            title = ";".join([""]+list(pair))
            h = r.TH2D(name, title, 100, 1.0, -1.0, 100, 1.0, -1.0)
            h.Sumw2()
            h.SetStats(False)
            h.SetTitleOffset(1.3)

            for parList in randPars :
                indices = map(parList.index, pair)
                if any(map(lambda x:x<0, indices)) : continue
                h.Fill(*tuple(map(lambda i:parList[i].getVal(), indices)))

            histos[h.GetName()] = h
        return histos

    def propPlotSet(self, randPars = [], suffix = "", pars = []) :
        return self.funcHistos(randPars, suffix = suffix),\
               self.parHistos1D(pars = pars, randPars = randPars, suffix = suffix),\
               self.parHistos2D(pairs = [("A_qcd","k_qcd"), ("A_ewk","A_qcd"), ("A_ewk","k_qcd"), ("A_ewk","fZinv0")], randPars = randPars, suffix = suffix)

    def cyclePlotSet(self, funcHistos = None, parHistos1D = None, parHistos2D = None,
                     funcBestFit = None, funcLinPropError = None,
                     parBestFit = None, parError = None) :

        utils.cyclePlot(d = parHistos1D, f = histoLines, canvas = self.canvas, fileName = self.psFileName,
                        args = {"bestColor":r.kGreen, "quantileColor":r.kRed, "bestDict":parBestFit, "errorDict":parError, "errorColor":r.kGreen})

        utils.cyclePlot(d = parHistos2D, canvas = self.canvas, fileName = self.psFileName)
        utils.cyclePlot(d = funcHistos, f = histoLines, canvas = self.canvas, fileName = self.psFileName,
                        args = {"bestColor":r.kGreen, "quantileColor":r.kRed, "bestDict":funcBestFit, "errorDict":funcLinPropError, "errorColor":r.kCyan})

        return

    def propagatedErrorsPlots(self, nValues = 1000, pdfName = "model", printResults = None) :
        #http://root.cern.ch/phpBB3/viewtopic.php?f=15&t=8892&p=37735

        funcBestFit,funcLinPropError = utils.funcCollect(self.wspace, self.results)
        parBestFit,parError,parMin,parMax = utils.parCollect(self.wspace)

        #minNll = self.results.minNll()
        #print "minNll =",minNll
        #maxPdfValue = self.wspace.pdf(pdfName).getVal()
        #print "nLMaxPdfValue =",-math.log(maxPdfValue)
        #ndf = 13
        #print "ndf =",ndf

        randPars = self.randomizedPars(nValues)

        #llHisto = self.llHisto(randPars, pdfName = pdfName, maxPdfValue = maxPdfValue, minNll = minNll, ndf = ndf)

        funcHistos,parHistos1D,parHistos2D = self.propPlotSet(randPars = randPars, suffix = "", pars = parBestFit.keys())
        self.cyclePlotSet(funcHistos = funcHistos, parHistos1D = parHistos1D, parHistos2D = parHistos2D,
                          funcBestFit = funcBestFit, funcLinPropError = funcLinPropError,
                          parBestFit = parBestFit, parError = parError)

        #funcHistos,parHistos1D,parHistos2D = self.propPlotSet(randPars = self.filteredPars(randPars, maxPdfValue = maxPdfValue, pdfName = pdfName),
        #                                                      suffix = "_filtered",
        #                                                      pars = parBestFit.keys())
        #
        #self.cyclePlotSet(funcHistos = funcHistos, parHistos1D = parHistos1D, parHistos2D = parHistos2D,
        #                  funcBestFit = funcBestFit, funcLinPropError = funcLinPropError,
        #                  parBestFit = parBestFit, parError = parError)
        return

    def hadronicSummaryTable(self) :
        N = len(self.htBinLowerEdges)
        print "HT bins :",pretty(self.htBinLowerEdges)
        print "Data    :",pretty([self.wspace.var("nHad%d"%i).getVal() for i in range(N)])
        print "fit SM  :",pretty([self.wspace.function("hadB%d"%i).getVal() for i in range(N)])
        print "fit EWK :",pretty([self.wspace.function("ewk%d"%i).getVal() for i in range(N)])
        print "fit Zinv:",pretty([self.wspace.function("zInv%d"%i).getVal() for i in range(N)])
        print "fit TTw :",pretty([self.wspace.function("ttw%d"%i).getVal() for i in range(N)])
        print "fit QCD :",pretty([self.wspace.function("qcd%d"%i).getVal() for i in range(N)])

    def htHisto(self, name = "example", note = "", yLabel = "counts / bin") :
        bins = array.array('d', list(self.htBinLowerEdges)+[self.htMaxForPlot])
        out = r.TH1D(name, "%s;H_{T} (GeV);%s"%(note, yLabel), len(bins)-1, bins)
        out.Sumw2()
        out.GetXaxis().SetLabelSize(1.5*out.GetXaxis().GetLabelSize())
        out.GetYaxis().SetLabelSize(1.5*out.GetYaxis().GetLabelSize())
        out.GetXaxis().SetTitleOffset(0.88*out.GetXaxis().GetTitleOffset())
        out.GetXaxis().SetTitleSize(1.5*out.GetXaxis().GetTitleSize())
        out.GetYaxis().SetTitleSize(1.5*out.GetYaxis().GetTitleSize())
        return out

    def fillSignalExampleYield(self, spec={}, histo=None):
        box = spec["box"]
        l = self.lumi[box]
        xs = spec["example"].xs
        eff = inDict(spec["example"][self.label],
                     "eff%s" % spec["box"].capitalize(),
                     [0.0]*len(self.htBinLowerEdges))
        activeBins = self.activeBins["n%s" % spec["box"].capitalize()]
        for i in range(len(self.htBinLowerEdges)):
            if not activeBins[i]:
                continue
            histo.SetBinContent(i+1, l*xs*eff[i])


    def varHisto(self, spec={}, extraName="", yLabel="", note="", lumiString=""):
        color       = spec.get("color", r.kBlack)
        lineStyle   = spec.get("style", 1)
        lineWidth   = spec.get("width", 1)
        markerStyle = spec.get("markerStyle", 1)
        fillStyle   = spec.get("fillStyle", 0)
        fillColor   = spec.get("fillColor", color)
        errorsFrom  = spec.get("errorsFrom", "")
        systMap     = spec.get("systMap", False)

        varName = spec["box" if "example" in spec else "var"]
        wspaceMemberFunc = "" if "example" in spec else spec["type"]

        d = {}
        d["value"] = self.htHisto(name=varName + extraName,
                                  note=note,
                                  yLabel=yLabel)
        d["value"].Reset()

        if wspaceMemberFunc == "var":
            for item in ["min", "max"]:
                d[item] = d["value"].Clone(d["value"].GetName()+item)

        for item in ["errors", "noErrors", "errorsLo", "errorsHi", "uncFromToys"]:
            d[item] = d["value"].Clone(d["value"].GetName()+item)

        #style
        for key,histo in d.iteritems():
            histo.SetLineColor(color)
            histo.SetLineWidth(lineWidth)
            histo.SetFillStyle(fillStyle)
            histo.SetFillColor(fillColor)
            if key == "value":
                histo.SetMarkerColor(color)
                histo.SetMarkerStyle(markerStyle)
                histo.SetLineStyle(lineStyle)
            else :
                # FIXME: lineStyle increment
                histo.SetLineStyle(lineStyle+0)

        if "example" in spec:
            assert "func" not in spec, "func will not be applied here"
            self.fillSignalExampleYield(spec=spec, histo=d["value"])
            return d

        toPrint = []
        for i in range(len(self.htBinLowerEdges)) :
            if wspaceMemberFunc :
                iLabel = i if not systMap else self.inputData.systBins()[varName.replace("rho", "sigma")][i]
                item1 = ni(varName, "", iLabel)
                item2 = ni(varName, self.label, iLabel)
                var = self.wspace.var(item1)
                if not var : var = self.wspace.var(item2)
                func = self.wspace.function(item1)
                if not func : func = self.wspace.function(item2)
                if (not var) and (not func) : continue

                value = (var if var else func).getVal()
                if spec.get("func"):
                    value = spec["func"](value)
                d["value"].SetBinContent(i+1, value)
                if var :
                    if varName[0]=="n" :
                        d["value"].SetBinError(i+1, math.sqrt(value))
                    else :
                        d["value"].SetBinError(i+1, var.getError())

                    for item in ["min", "max"] :
                        x = getattr(var, "get%s"%item.capitalize())()
                        if abs(x)==1.0e30 : continue
                        if item in d : d[item].SetBinContent(i+1, x)

                    d["errors"].SetBinContent(i+1, d["value"].GetBinContent(i+1))
                    d["errors"].SetBinError(i+1, d["value"].GetBinError(i+1))
                    d["noErrors"].SetBinContent(i+1, d["value"].GetBinContent(i+1))
                    d["noErrors"].SetBinError(i+1, 0.0)
                elif self.errorsFromToys :
                    q = self.quantiles[ni(varName, self.label, i)]
                    d["errors"].SetBinContent(i+1, (q[2]+q[0])/2.0)
                    d["errors"].SetBinError(i+1, (q[2]-q[0])/2.0)
                    d["uncFromToys"].SetBinContent(i+1, d["errors"].GetBinError(i+1))
                    d["noErrors"].SetBinContent(i+1, value)
                    d["noErrors"].SetBinError(i+1, 0.0)
                    d["errorsLo"].SetBinContent(i+1, d["errors"].GetBinContent(i+1)-d["errors"].GetBinError(i+1)) #used in ratioPlots
                    d["errorsHi"].SetBinContent(i+1, d["errors"].GetBinContent(i+1)+d["errors"].GetBinError(i+1)) #used in ratioPlots
                elif errorsFrom :
                    noI = ni(errorsFrom, self.label)
                    errorsVar = self.wspace.var(noI) if self.wspace.var(noI) else self.wspace.var(ni(errorsFrom, self.label, i))
                    if errorsVar and errorsVar.getVal() :
                        d["value"].SetBinError(i+1, value*errorsVar.getError()/errorsVar.getVal())
                        d["errors"].SetBinContent(i+1, d["value"].GetBinContent(i+1))
                        d["errors"].SetBinError(i+1, d["value"].GetBinError(i+1))
                        d["noErrors"].SetBinContent(i+1, d["value"].GetBinContent(i+1))
                        d["noErrors"].SetBinError(i+1, 0.0)
                #else : d["value"].SetBinError(i+1, func.getPropagatedError(self.results))
            else :
                value = self.inputData.mcExpectations()[varName][i]
                if value!=None :
                    d["value"].SetBinContent(i+1, value)
                    d["errors"].SetBinContent(i+1, value)
                    d["noErrors"].SetBinContent(i+1, value)
                key = varName+"Err"
                if key in self.inputData.mcStatError() :
                    error = self.inputData.mcStatError()[key][i]
                    if error!=None :
                        d["value"].SetBinError(i+1, error)
                        d["errors"].SetBinError(i+1, error)
                        d["noErrors"].SetBinError(i+1, 0.0)

            toPrint.append(value)
        self.toPrint.append( (varName.rjust(10), lumiString.rjust(10), pretty(toPrint)) )
        return d

    def stampMlParameters(self) :
        def sl(s) :
            return set(self.inputData.systBins()[s])

        text = r.TLatex()
        text.SetNDC()
        x = 0.25
        y = 0.85
        s = 0.03
        text.SetTextSize(0.5*text.GetTextSize())
        #text.DrawLatex(x, y + s, "ML fit values")
        l = []
        if self.printValues :
            l += [("A_ewk", "A_{EWK} = %4.2e #pm %4.2e", None),
                  ("k_ewk", "k_{EWK} = %4.2e #pm %4.2e", None),
                  ("A_qcd", "A_{QCD } = %4.2e #pm %4.2e", None),
                  ("k_qcd", "k_{QCD  } = %4.2e #pm %4.2e", None),]

            l += [("rhoPhotZ",  ("#rho (#gammaZ% d)"%i)+" = %4.2f #pm %4.2f", i) for i in sl("sigmaPhotZ")]
            l += [("rhoMuonW",  ("#rho (#muW %d)"%i)+" = %4.2f #pm %4.2f", i) for i in sl("sigmaMuonW")]
            l += [("rhoMumuZ",  ("#rho (#mu#muZ %d)"%i)+" = %4.2f #pm %4.2f", i) for i in sl("sigmaMumuZ")]

        if self.printNom :
            l +=  [("", ""),
                   ("k_qcd_nom", "k nom = %4.2e #pm %4.2e"),
                   ("k_qcd_unc_inp", "#sigma k nom = %4.2e #pm %4.2e"),
                   ]

        for i,t in enumerate(l) :
            var,label,iPar = t
            obj = self.wspace.var(var)
            if not obj : obj = self.wspace.var(ni(var, self.label, iPar))
            if not obj : continue
            text.DrawLatex(x, y-i*s, label%(obj.getVal(), obj.getError()))
        return

    def divide(self, histo=None, spec={}):
        for den, denType, denFunc, denKey in zip(spec["dens"],
                                                 spec["denTypes"],
                                                 spec.get("denFuncs", [lambda x:x]*len(spec["dens"])),
                                                 spec.get("denKeys", ["value"]*len(spec["dens"])),
                                                 ):
            histo.Divide(self.varHisto(spec={"var": den,
                                             "type": denType,
                                             "func": denFunc,
                                             },
                                       )[denKey])

    def stacks(self, specs=[], extraName="", lumiString="", scale=1.0):
        stacks = {}
        histoList = []
        legEntries = []

        for iSpec, spec in enumerate(specs):
            if "dens" in spec:
                extraName += "_".join([""]+spec["dens"])

            if ("var" not in spec) and ("example" not in spec):
                continue

            histos = self.varHisto(spec=spec, extraName=extraName, lumiString=lumiString)
            if not histos["value"].GetEntries():
                continue

            if "dens" in spec:
                for h in histos.values():
                    self.divide(histo=h, spec=spec)

            legHisto = histos["value"]
            legGopts = "l"

            if spec.get("errorBand") and self.bandInLegend:
                legHisto = histos["legend"] = histos["value"].Clone("%s_legendClone"%histos["value"].GetName())
                legHisto.SetFillColor(spec["errorBand"])
                legHisto.SetFillStyle(spec.get("bandStyle", 1001))
                legGopts += "f"
            legEntries.append((legHisto,
                               "%s %s" % (spec["desc"], spec.get("desc2", "")),
                               spec.get("legSpec", legGopts))
                              )

            stack = spec.get("stack", "")
            if not stack:
                stack = "_".join(["NONE","%03d" % iSpec]+[spec["var"]]*3) #hacky default stack name
            if stack not in stacks:
                stacks[stack] = utils.thstackMulti(name=stack, drawErrors=(self.errorsFromToys or spec.get("errorsFrom")))
            stacks[stack].Add(histos, spec)
        return stacks, legEntries


    def plot(self, note = "", fileName = "", legend0 = (0.3, 0.6), legend1 = (0.85, 0.85), reverseLegend = False,
             selNoteCoords = (0.13, 0.85), yAxisMinMax = (0.0, None), customMaxFactor = (1.1, 2.0),
             logY = False, stampParams = False, obs = {"var":"", "desc":""}, otherVars = [],
             yLabel = "Events / bin", scale = 1.0, ratioDenom = "" ) :

        ## assert [CONDITION], would work here, but this seems easier to read
        #if ( self.drawRatios and (None in ratioVars) ) or ( len(ratioVars) != 2 ) :
        #    assert False, "Wrong number of histograms provided to plot() for drawRatios"

        self.canvas.cd(1)

        leg = r.TLegend(legend0[0], legend0[1], legend1[0], legend1[1], self.legendTitle)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        stuff = [leg]
        extraName = str(logY)+"_".join([inDict(o, "var", "") for o in otherVars])
        lumiString = obs["desc"][obs["desc"].find("["):]

        obsHisto = self.varHisto(extraName = extraName, yLabel = yLabel, note = note, lumiString = lumiString,
                                 spec = {"var":obs["var"], "type":"var"})["value"]

        if "dens" in obs:
            self.divide(histo=obsHisto, spec=obs)

        obsHisto.SetMarkerStyle(inDict(obs, "markerStyle", 20))
        obsHisto.SetStats(False)
        obsHisto.Draw(inDict(obs, "goptions", "p"))

        minimum,maximum = self.yAxisLogMinMax if logY else yAxisMinMax
        if minimum!=None : obsHisto.SetMinimum(minimum)
        if maximum!=None : obsHisto.SetMaximum(maximum)

        if obs["desc"] : leg.AddEntry(obsHisto, obs["desc"], inDict(obs, "legSpec", "lpe"))
        stuff += [obs]

        r.gPad.SetLogy(logY)

        args = {}
        for item in ["extraName", "lumiString", "scale"] :
            args[item] = eval(item)

        stackDict, legEntries = self.stacks(specs=otherVars, **args)

        maxes = [utils.histoMax(h) for h in [obsHisto]]+[s.Maximum() for s in stackDict.values()]
        if maxes and not maximum :
            obsHisto.SetMaximum(customMaxFactor[logY]*max(maxes))

        stuff += stackDict

        for key,stack in stackDict.iteritems() :
            stack.Draw(goptions = "histsame" if key[:4]!="NONE" else "same", reverse = False)

        obsHisto.Draw("sameaxis") #redraw axis
        obsHisto.Draw("psame") #redraw data points

        for item in reversed(legEntries) if reverseLegend else legEntries :
            leg.AddEntry(*item)
        leg.Draw()
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        r.gPad.Update()


        if stampParams and not self.printPages : stuff += [self.stampMlParameters()]
        #if selNoteCoords :
        #    latex = r.TLatex()
        #    latex.SetTextSize(0.7*latex.GetTextSize())
        #    latex.SetNDC()
        #    latex.DrawLatex(selNoteCoords[0], selNoteCoords[1], self.selNote)

        denomHisto = self.varHisto(spec = {"var":ratioDenom, "type": "function"})
        denomHisto["errorsHi"].SetFillColor(r.kAzure)
        denomHisto["errorsHi"].SetFillStyle(1001)
        denomHisto["errorsHi"].SetLineStyle(1)
        denomHisto["errorsHi"].SetLineColor(r.kAzure)

        denomHisto["errorsLo"].SetFillColor(10)
        denomHisto["errorsLo"].SetFillStyle(1001)
        denomHisto["errorsLo"].SetLineStyle(1)
        denomHisto["errorsLo"].SetLineColor(r.kAzure)

        numHistos = [ denomHisto["errorsHi"], denomHisto["errorsLo"] ]
        if "total" in stackDict :
            numHistos.append(stackDict["total"].histos[-1][0]["value"])
        numHistos.append( obsHisto )

        #ratios = self.makeRatios(numHistos, denomHisto["value"])

        #foo = self.plotRatio([obsHisto, denomHisto], 1)
        #foo = self.plotRatios( ratios )

        if self.printPages and fileName :
            #obsHisto.SetTitle("")
            printOnePage(self.canvas, "_".join(fileName+[self.label]), ext = ".eps")
            #printOnePage(self.canvas, fileName, ext = ".C")
        self.canvas.Print(self.psFileName)

        return stuff

    def makeRatios( self, numHistos, denomHisto ) :
        ratioHistos = []
        for numHisto in numHistos :
            ratioHistos.append(numHisto.Clone("%sClone"%numHisto.GetName()))
            ratioHistos[-1].SetDirectory(0)
            ratioHistos[-1].Divide(denomHisto)
            ratioHistos[-1].SetMarkerStyle(numHisto.GetMarkerStyle())
            color = numHisto.GetLineColor()
            ratioHistos[-1].SetLineColor(color)
            ratioHistos[-1].SetMarkerColor(color)
        return ratioHistos


    def plotRatios( self, ratios ) :
        numLabel,denomLabel = "Data", "SM"
        numSampleName,denomSampleNames = "Data", "SM"

        same = ""
        self.canvas.cd(2)
        for i,ratio in enumerate(ratios) :
            if same == "" :
                ratio.SetMinimum(0.0)
                ratio.SetMaximum(2.0)
                ratio.GetYaxis().SetTitle(numLabel+" / "+denomLabel)
                ratio.SetStats(False)
                ratio.GetXaxis().SetLabelSize(0.0)
                ratio.GetXaxis().SetTickLength(3.5*ratio.GetXaxis().GetTickLength())
                ratio.GetYaxis().SetLabelSize(0.2)
                ratio.GetYaxis().SetNdivisions(502,True)
                ratio.GetXaxis().SetTitleOffset(0.2)
                ratio.GetYaxis().SetTitleSize(0.2)
                ratio.GetYaxis().SetTitleOffset(0.2)
            ratio.Draw(same)
            if i == 2 :
                xr = [ ratio.GetXaxis().GetXmin(), ratio.GetXaxis().GetXmax() ]
                line = r.TLine(xr[0],1.0,xr[1],1.0)
                line.SetLineWidth(1)
                line.SetLineStyle(1)
                line.SetLineColor(r.kAzure+6)
                line.Draw()
            same = "same"

        r.gPad.SetTickx()
        r.gPad.SetTicky()
        r.gPad.RedrawAxis()
        return line
