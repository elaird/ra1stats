import os,array,math,copy,collections
import utils
import ROOT as r

def rootSetup() :
    #r.gROOT.SetStyle("Plain")
    r.gErrorIgnoreLevel = 2000

def writeGraphVizTree(wspace, pdfName = "model") :
    dotFile = "%s.dot"%pdfName
    wspace.pdf(pdfName).graphVizTree(dotFile, ":", True, False)
    cmd = "dot -Tps %s -o %s"%(dotFile, dotFile.replace(".dot", ".ps"))
    os.system(cmd)
    
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
    q["Observed"] = obs

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

def expectedLimitPlots(quantiles = {}, hist = None, obsLimit = None, note = "") :
    ps = "limits_%s.ps"%note
    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(ps+"[")

    l = drawDecoratedHisto(quantiles, hist, obsLimit)

    canvas.Print(ps)
    canvas.Print(ps+"]")
    utils.ps2pdf(ps)

def pValuePlots(pValue = None, lMaxData = None, lMaxs = None, graph = None, note = "") :
    print "pValue =",pValue

    ps = "pValue_%s.ps"%note
    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(ps+"[")

    graph.SetMarkerStyle(20)
    graph.SetTitle(";toy number;p-value")
    graph.Draw("ap")
    canvas.Print(ps)
    
    totalList = lMaxs+[lMaxData]
    histo = r.TH1D("lMaxHisto",";log(L_{max});pseudo experiments / bin", 100, 0.0, max(totalList)*1.1)
    for item in lMaxs :
        histo.Fill(item)
    histo.SetStats(False)
    histo.SetMinimum(0.0)
    histo.Draw()
    
    line = r.TLine()
    line.SetLineColor(r.kBlue)
    line.SetLineWidth(2)
    line = line.DrawLine(lMaxData, histo.GetMinimum(), lMaxData, histo.GetMaximum())
    
    legend = r.TLegend(0.1, 0.7, 0.5, 0.9)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.AddEntry(histo, "log(L_{max}) in pseudo-experiments", "l")
    legend.AddEntry(line, "log(L_{max}) observed", "l")
    legend.Draw()
    
    canvas.Print(ps)
    canvas.Print(ps+"]")
    utils.ps2pdf(ps)

def clsCustomPlots(obs = None, valuesDict = {}, note = "") :
    ps = "clsCustom_%s.ps"%note

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
    utils.ps2pdf(ps)

def pretty(l) :
    out = "("
    for i,item in enumerate(l) :
        out += "%6.2f"%item
        if i!=len(l)-1 : out += ", "
    return out+")"

def inDict(d, key, default) :
    return d[key] if key in d else default

def drawOne(hist, goptions, errorBand, bandFillStyle = 1001) :
    if not errorBand :
        hist.Draw(goptions)
        return

    goptions = "he2"+goptions
    errors   = hist.Clone(hist.GetName()+"_errors")
    noerrors = hist.Clone(hist.GetName()+"_noerrors")
    for i in range(1, 1+noerrors.GetNbinsX()) : noerrors.SetBinError(i, 0.0)
    errors.SetFillColor(errorBand)
    errors.SetFillStyle(bandFillStyle)
    errors.Draw("e2same")
    noerrors.Draw("h"+goptions)
    return [errors, noerrors]

def printOnePage(canvas, fileName) :
    fileName = fileName+".eps"
    super(utils.numberedCanvas, canvas).Print(fileName)
    utils.epsToPdf(fileName)

def legSpec(goptions) :
    out = ""
    if "p" in goptions : out += "p"
    if "hist" in goptions : out += "l"
    return out

def histoMax(h, factor = 1.1) :
    i = h.GetMaximumBin()
    return factor*(h.GetBinContent(i)+h.GetBinError(i))

def akDesc(wspace, var1 = "", var2 = "", errors = True) :
    varA = wspace.var("%s"%var1)
    vark = wspace.var("%s"%var2)
    out = ""
    if varA : out += "%s = %4.2e%s; "%(var1[0], varA.getVal(), " #pm %4.2e"%varA.getError() if errors else "")
    if vark : out += "%s = %4.2e%s"  %(var2[0], vark.getVal(), " #pm %4.2e"%vark.getError() if errors else "")
    return out

def lumi(lumiInInvPb) :
    return "[%4.2f/fb]"%(lumiInInvPb/1000.)

class validationPlotter(object) :
    def __init__(self, args) :
        for key,value in args.iteritems() :
            setattr(self,key,value)
        if any(self.signalExampleToStack) : assert self.smOnly

        self.toPrint = []
        self.ewkType = "function" if self.REwk else "var"

        if not self.smOnly :
            self.signalDesc = "signal"
            self.signalDesc2 = "xs/xs^{nom} = %4.2e #pm %4.2e; #rho = %4.2f"%(self.wspace.var("f").getVal(), self.wspace.var("f").getError(), self.wspace.var("rhoSignal").getVal())

    def go(self) :
        self.canvas = utils.numberedCanvas()
        self.psFileName = "bestFit_%s%s.ps"%(self.note, "_smOnly" if self.smOnly else "")
        self.canvas.Print(self.psFileName+"[")        

        self.hadPlots()
        self.hadDataMcPlots()
        self.hadControlPlots()
        self.muonPlots()
        self.photPlots()
        self.mumuPlots()
        self.ewkPlots()
        self.mcFactorPlots()
        self.alphaTRatioPlots()
        self.printPars()
        self.correlationHist()
        self.propagatedErrorsPlots()

	if self.printPages :
            for item in sorted(list(set(self.toPrint))) :
                print " ".join(item)
            #self.hadronicSummaryTable()

        self.canvas.Print(self.psFileName+"]")
        utils.ps2pdf(self.psFileName)
        
    def hadPlots(self) :
        vars = [
            {"var":"hadB", "type":"function", "desc":"expected total background",
             "color":r.kBlue, "style":1, "width":3, "stack":"total"},
            {"var":"ewk",  "type":self.ewkType, "desc":"EWK", "desc2":akDesc(self.wspace, "A_ewk", "k_ewk", errors = True) if self.REwk else "[floating]",
             "color":r.kCyan, "style":2, "width":2, "stack":"background"},
            {"var":"qcd",  "type":"function", "desc":"QCD", "desc2":akDesc(self.wspace, "A_qcd", "k_qcd", errors = True),
             "color":r.kMagenta, "style":3, "width":2, "stack":"background"},
            ]

        desc2 = "#rho_{ph} = %4.2f #pm %4.2f"%(self.wspace.var("rhoPhotZ").getVal(), self.wspace.var("rhoPhotZ").getError()) if self.wspace.var("rhoPhotZ") else ""
        if self.mumuTerms : desc2 += "; #rho_{#mu#mu} = %4.2f #pm %4.2f"%(self.wspace.var("rhoMumuZ").getVal(), self.wspace.var("rhoMumuZ").getError())
        vars += [
            {"var":"zInv", "type":"function", "desc":"Z->inv", "desc2": desc2,  "color":r.kRed, "style":2, "width":2, "stack":"ewk"},
            {"var":"ttw",  "type":"function", "desc":"t#bar{t} + W",
             "desc2": "#rho_{#mu} = %4.2f #pm %4.2f"%(self.wspace.var("rhoMuonW").getVal(), self.wspace.var("rhoMuonW").getError()) if self.wspace.var("rhoMuonW") else "",
             "color":r.kGreen, "style":2, "width":2, "stack":"ewk"},
            ]
        if not self.smOnly :
            vars += [{"var":"hadS", "type":"function", "desc":self.signalDesc, "desc2":self.signalDesc2, "color":r.kOrange, "style":1, "width":2, "stack":"total"}]
        elif any(self.signalExampleToStack) :
            vars += [{"example":self.signalExampleToStack[1], "box":"had", "desc":self.signalExampleToStack[0], "color":r.kOrange, "style":1, "width":2, "stack":"total"}]

        for logY in [False, True] :
            thisNote = "Hadronic Signal Sample%s"%(" (logY)" if logY else "")
            fileName = "hadronic_signal_fit%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.63), legend1 = (0.85, 0.88),
                                obsKey = "nHad", obsLabel = "hadronic data %s"%lumi(self.lumi["had"]), otherVars = vars, logY = logY)

    def hadDataMcPlots(self) :
        for logY in [False, True] :
            thisNote = "Hadronic Signal Sample%s"%(" (logY)" if logY else "")
            fileName = "hadronic_signal_data_mc%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True, logY = logY,
                                obsKey = "nHad", obsLabel = "hadronic data %s"%lumi(self.lumi["had"]), otherVars = [
                {"var":"mcHad", "type":None, "color":r.kGray+2, "style":2, "width":2, "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray},
                {"var":"ewk",  "type":self.ewkType, "desc":"EWK", "desc2":akDesc(self.wspace, "A_ewk", "k_ewk", errors = True) if self.REwk else "[floating]",
                 "color":r.kCyan, "style":2, "width":2, "stack":"background"},
                {"var":"hadB", "type":"function", "desc":"expected total background",
                 "color":r.kBlue, "style":1, "width":3, "stack":"total"},
                ])

    def hadControlPlots(self) :
        for labelRaw in self.hadControlLabels :
            label = "_"+labelRaw+"_"
            label1 = label[:-1]
            for logY in [False, True] :
                thisNote = "Hadronic Control Sample %s %s"%(labelRaw, " (logY)" if logY else "")
                fileName = "hadronic_control_fit_%s%s"%(labelRaw, "_logy" if logY else "")
                self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72),
                                    obsKey = "nHadControl%s"%label, obsLabel = "hadronic control data (%s) %s"%(labelRaw, lumi(self.lumi["had"])),
                                    logY = logY, otherVars = [
                    {"var":"hadControlB%s"%label, "type":"function", "color":r.kBlue, "style":1, "width":3, "desc":"expected SM yield", "stack":None},
                    {"var":"ewkControl%s"%label,  "type":"function", "desc":"EWK", "desc2":akDesc(self.wspace, "A_ewkControl%s"%label1, "d_ewkControl%s"%label1, errors = True),
                     "color":r.kCyan,    "style":2, "width":2, "stack":"background"},
                    {"var":"qcdControl%s"%label,  "type":"function", "desc":"QCD", "desc2":akDesc(self.wspace, "A_qcdControl%s"%label1, "k_qcd", errors = True),
                     "color":r.kMagenta, "style":3, "width":2, "stack":"background"},
                    ])

    def muonPlots(self) :
        vars = [
            {"var":"muonB",   "type":"function", "color":r.kBlue,   "style":1, "width":3, "desc":"expected SM yield", "stack":"total"},
            {"var":"mcMuon",  "type":None,       "color":r.kGray+2, "style":2, "width":2,
             "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray} if not self.printPages else {},
            ]
        if not self.smOnly :
            vars += [{"var":"muonS",   "type":"function", "color":r.kOrange, "style":1, "width":2, "desc":self.signalDesc, "desc2":self.signalDesc2, "stack":"total"}]
        elif any(self.signalExampleToStack) :
            vars += [{"example":self.signalExampleToStack[1], "box":"muon", "desc":self.signalExampleToStack[0], "color":r.kOrange, "style":1, "width":2, "stack":"total"}]

        for logY in [False, True] :
            thisNote = "Muon Control Sample%s"%(" (logY)" if logY else "")
            fileName = "muon_control_fit%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.7),
                                obsKey = "nMuon", obsLabel = "muon data %s"%lumi(self.lumi["muon"]), otherVars = vars, logY = logY)

    def photPlots(self) :
        for logY in [False, True] :
            thisNote = "Photon Control Sample%s"%(" (logY)" if logY else "")
            fileName = "photon_control_fit%s"%("_logy" if logY else "")            
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True, logY = logY,
                                obsKey = "nPhot", obsLabel = "photon data %s"%lumi(self.lumi["phot"]), otherVars = [
                {"var":"mcGjets", "type":None, "purityKey": "phot", "color":r.kGray+2, "style":2, "width":2,
                 "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray}  if not self.printPages else {},
                {"var":"photExp", "type":"function", "color":r.kBlue,   "style":1, "width":3, "desc":"expected SM yield", "stack":None},
                ])

    def mumuPlots(self) :
        for logY in [False, True] :
            thisNote = "Mu-Mu Control Sample%s"%(" (logY)" if logY else "")
            fileName = "mumu_control_fit%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True,
                                obsKey = "nMumu", obsLabel = "mumu data %s"%lumi(self.lumi["mumu"]), logY = logY, otherVars = [
                {"var":"mcZmumu", "type":None, "purityKey": "mumu", "color":r.kGray+2, "style":2, "width":2, "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray},
                {"var":"mumuExp", "type":"function", "color":r.kBlue,   "style":1, "width":3, "desc":"expected SM yield", "stack":None},
                ])

    def ewkPlots(self) :
        self.ratioPlot(note = "ttW scale factor (result of fit)", legend0 = (0.5, 0.8), maximum = 3.0, specs = [
            {"num":"ttw",   "numType":"function", "dens":["mcTtw"],  "denTypes":[None], "desc":"ML ttW / MC ttW",       "color":r.kGreen}], goptions = "hist")
        self.ratioPlot(note = "Zinv scale factor (result of fit)", legend0 = (0.5, 0.8), maximum = 3.0, specs = [
            {"num":"zInv",  "numType":"function", "dens":["mcZinv"], "denTypes":[None], "desc":"ML Z->inv / MC Z->inv", "color":r.kRed}], goptions = "hist")
        
        self.validationPlot(note = "fraction of EWK background which is Zinv (result of fit)",
                            legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", minimum = 0.0, maximum = 1.0,
                            otherVars = [{"var":"fZinv", "type":"var", "color":r.kBlue, "style":1, "desc":"fit Z->inv / fit EWK", "stack":None}], yLabel = "")
        
    def mcFactorPlots(self) :
        self.validationPlot(note = "muon translation factor (from MC)",
                       legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", maximum = 2.0,
                       otherVars = [{"var":"rMuon", "type":"var", "color":r.kBlue, "style":1, "desc":"MC muon / MC ttW", "stack":None}],
                       yLabel = "", scale = self.lumi["had"]/self.lumi["muon"])
        self.validationPlot(note = "photon translation factor (from MC)",
                       legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", maximum = 4.0,
                       otherVars = [{"var":"rPhot", "type":"var", "color":r.kBlue, "style":1, "desc":"MC #gamma / MC Z#rightarrow#nu#bar{#nu} / P", "stack":None}],
                       yLabel = "", scale = self.lumi["had"]/self.lumi["phot"])
        self.validationPlot(note = "muon-muon translation factor (from MC)",
                       legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", maximum = 1.0,
                       otherVars = [{"var":"rMumu", "type":"var", "color":r.kBlue, "style":1, "desc":"MC Z#rightarrow#mu#bar{#mu} / MC Z#rightarrow#nu#bar{#nu} / P", "stack":None}],
                       yLabel = "", scale = self.lumi["had"]/self.lumi["mumu"])

    def alphaTRatioPlots(self) :
        ewk = {"num":"ewk",   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML EWK / nHadBulk",  "color":r.kCyan, "numErrorsFrom":"A_ewk"}
        if self.ewkType=="var" :
            {  "num":"ewk",   "numType":"var",      "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML EWK / nHadBulk",  "color":r.kCyan},
            
        self.ratioPlot(note = "hadronic signal", fileName = "hadronic_signal_alphaT_ratio", legend0 = (0.12, 0.7), legend1 = (0.52, 0.88), specs = [
            {"num":"qcd",   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML QCD / nHadBulk",  "color":r.kMagenta, "numErrorsFrom":"A_qcd"},
            ewk,
            {"num":"hadB",  "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML hadB / nHadBulk", "color":r.kBlue},
            {"num":"nHad",  "numType":"data",     "dens":["nHadBulk"], "denTypes":["var"], "desc":"nHad / nHadBulk",    "color":r.kBlack},
            ], yLabel = "R_{#alpha_{T}}", customMaxFactor = 1.5, reverseLegend = True)

        for labelRaw in self.hadControlLabels :
            label = "_"+labelRaw+"_"
            label1 = label[:-1]
            self.ratioPlot(note = "hadronic control %s"%labelRaw,
                      legend0 = (0.12, 0.7), legend1 = (0.52, 0.88), specs = [
                {"num":"qcdControl%s"%label,   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML QCD / nHadBulk", "color":r.kMagenta},
                {"num":"ewkControl%s"%label,   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML EWK / nHadBulk", "color":r.kCyan},
                {"num":"hadControlB%s"%label,  "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML hadControlB / nHadBulk", "color":r.kBlue},
                {"num":"nHadControl%s"%label1, "numType":"data",     "dens":["nHadBulk"], "denTypes":["var"], "desc":"nHadControl / nHadBulk",    "color":r.kBlack},
                ], yLabel = "R_{#alpha_{T}}", customMaxFactor = 1.5, reverseLegend = True)

        self.ratioPlot(note = "muon to tt+W", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), specs = [
            {"num":"nMuon", "numType":"data",     "dens":["nHadBulk", "rMuon"], "denTypes":["data", "var"], "desc":"nMuon * (MC ttW / MC mu) / nHadBulk", "color":r.kBlack},
            {"num":"ttw",   "numType":"function", "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"ML ttW / nHadBulk",             "color":r.kGreen},        
            ], yLabel = "R_{#alpha_{T}}")
        self.ratioPlot(note = "photon to Zinv", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), specs = [
            {"num":"nPhot", "numType":"data",     "dens":["nHadBulk", "rPhot"], "denTypes":["data", "var"], "desc":"nPhot * P * (MC Zinv / MC #gamma) / nHadBulk", "color":r.kBlack},
            {"num":"zInv",  "numType":"function", "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"ML Zinv / nHadBulk",          "color":r.kRed},
            ], yLabel = "R_{#alpha_{T}}")
        self.ratioPlot(note = "mumu to Zinv", legend0 = (0.12, 0.7), legend1 = (0.62, 0.88), specs = [
            {"num":"nMumu", "numType":"data",     "dens":["nHadBulk", "rMumu"], "denTypes":["data", "var"], "desc":"nMumu * P * (MC Zinv / MC Zmumu) / nHadBulk", "color":r.kBlack},
            {"num":"zInv",  "numType":"function", "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"ML Zinv / nHadBulk",            "color":r.kRed},
            ], yLabel = "R_{#alpha_{T}}")

    def printPars(self) :
        def printText(x, y, s, color = r.kBlack) :
            #print s
            text.SetTextColor(color)
            text.DrawText(x, y, s)
            y -= slope
            return y
        
        text = r.TText()
        text.SetNDC()
        text.SetTextFont(102)
        text.SetTextSize(0.45*text.GetTextSize())
        x = 0.1
        y = 0.9
        slope = 0.03
        
        self.canvas.Clear()
        y = printText(x, y, "%20s:    %6s   +/-   %6s       [ %6s    -  %6s   ]"%("par name", "value", "error", "min", "max"))
        y = printText(x, y, "-"*78)
        vars = self.wspace.allVars()
        it = vars.createIterator()    
        while it.Next() :
            if it.getMax()==r.RooNumber.infinity() : continue
            if it.getMin()==-r.RooNumber.infinity() : continue
            if not it.hasError() : continue
            s = "%20s:  %10.3e +/- %10.3e     [%10.3e - %10.3e]"%(it.GetName(), it.getVal(), it.getError(), it.getMin(), it.getMax())
            factor = 2.0
            close = (it.getVal() + factor*it.getError() > it.getMax()) or (it.getVal() - factor*it.getError() < it.getMin())
            y = printText(x, y, s, color = r.kRed if close else r.kBlack)
        self.canvas.Print(self.psFileName)
        return

    def correlationHist(self) :
        h = self.results.correlationHist()
        h.SetStats(False)
        h.Draw("colz")
        self.canvas.Print(self.psFileName)
        
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
    
    def funcCollect(self) :
        funcs = self.wspace.allFunctions()
        func = funcs.createIterator()

        funcBestFit = {}
        funcLinPropError = {}
        while func.Next() :
            key = func.GetName()
            funcBestFit[key] = func.getVal()
            funcLinPropError[key] = func.getPropagatedError(self.results)
        return funcBestFit,funcLinPropError

    def parCollect(self) :
        vars = self.wspace.allVars()
        it = vars.createIterator()

        parBestFit = {}
        parError = {}
        parMin = {}
        parMax = {}
        while it.Next() :
            if it.getMax()==r.RooNumber.infinity() : continue
            if it.getMin()==-r.RooNumber.infinity() : continue
            if not it.hasError() : continue
            key = it.GetName()
            parBestFit[key] = it.getVal()
            parError[key] = it.getError()
            parMin[key] = it.getMin()
            parMax[key] = it.getMax()
        return parBestFit,parError,parMin,parMax
    
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

    def histoLines(self, args = {}, key = None, histo = None) :
        hLine = r.TLine(); hLine.SetLineColor(args["meanColor"])
        bestLine = r.TLine(); bestLine.SetLineColor(args["bestColor"])
        errorLine = r.TLine(); errorLine.SetLineColor(args["errorColor"])


        q = utils.quantiles(histo, sigmaList = [-1.0, 0.0, 1.0])
        min  = histo.GetMinimum()
        max  = histo.GetMaximum()

        best = args["bestDict"][key]
        error = args["errorDict"][key]
        out = []
        out.append(hLine.DrawLine(q[1], min, q[1], max))
        out.append(hLine.DrawLine(q[0], min, q[0], max))
        out.append(hLine.DrawLine(q[2], min, q[2], max))
        
        out.append(bestLine.DrawLine(best, min, best, max))
        out.append(errorLine.DrawLine(best - error, max/2.0, best + error, max/2.0))

        print "%20s: %g + %g - %g"%(histo.GetName(), best, q[2]-best, best-q[0])
        return out
        
    def dummy(self, args = {}, key = None, histo = None) :
        pass
    
    def cyclePlot(self, d = {}, f = None, args = {}, optStat = 1110) :
        if optStat!=None :
            oldOptStat = r.gStyle.GetOptStat()
            r.gStyle.SetOptStat(optStat)

        stuff = []
        for i,key in enumerate(sorted(d.keys())) :
            j = i%4
            if not j :
                self.canvas.cd(0)
                self.canvas.Clear()
                self.canvas.Divide(2, 2)
                
            self.canvas.cd(1+j)
            d[key].Draw()
            stuff.append( f(args = args, key = key, histo = d[key]) )
            needPrint = True

            #move stat box
            r.gPad.Update()
            tps = d[key].FindObject("stats")
            if tps :
                tps.SetX1NDC(0.78)
                tps.SetX2NDC(0.98)
                tps.SetY1NDC(0.90)
                tps.SetY2NDC(1.00)

            if j==3 :
                self.canvas.cd(0)                
                self.canvas.Print(self.psFileName)
                needPrint = False

        if needPrint :
            self.canvas.cd(0)
            self.canvas.Print(self.psFileName)
        if optStat!=None : r.gStyle.SetOptStat(oldOptStat)
        return

    def propPlotSet(self, randPars = [], suffix = "", pars = []) :
        return self.funcHistos(randPars, suffix = suffix),\
               self.parHistos1D(pars = pars, randPars = randPars, suffix = suffix),\
               self.parHistos2D(pairs = [("A_qcd","k_qcd"), ("A_ewk","A_qcd"), ("A_ewk","k_qcd"), ("A_ewk","fZinv0")], randPars = randPars, suffix = suffix)

    def cyclePlotSet(self, funcHistos = None, parHistos1D = None, parHistos2D = None,
                     funcBestFit = None, funcLinPropError = None,
                     parBestFit = None, parError = None) :
        
        self.cyclePlot(d = parHistos1D, f = self.histoLines, args = {"bestColor":r.kGreen, "meanColor":r.kRed,
                                                                     "bestDict":parBestFit, "errorDict":parError, "errorColor":r.kGreen})
        self.cyclePlot(d = parHistos2D, f = self.dummy, args = {})
        self.cyclePlot(d = funcHistos, f = self.histoLines, args = {"bestColor":r.kGreen, "meanColor":r.kRed,
                                                                    "bestDict":funcBestFit, "errorDict":funcLinPropError, "errorColor":r.kCyan})
        return
        
    def propagatedErrorsPlots(self, nValues = 1000, pdfName = "model") :
        #http://root.cern.ch/phpBB3/viewtopic.php?f=15&t=8892&p=37735

        funcBestFit,funcLinPropError = self.funcCollect()
        parBestFit,parError,parMin,parMax = self.parCollect()

        minNll = self.results.minNll()
        print "minNll =",minNll
        maxPdfValue = self.wspace.pdf(pdfName).getVal()
        print "nLMaxPdfValue =",-math.log(maxPdfValue)
        ndf = 13
        print "ndf =",ndf

        randPars = self.randomizedPars(nValues)

        llHisto = self.llHisto(randPars, pdfName = pdfName, maxPdfValue = maxPdfValue, minNll = minNll, ndf = ndf)

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
        print "MC EWK  :",pretty(self.inputData.mcExtra()["mcHad"])
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
        return out

    def signalExampleHisto(self, d = {}) :
        box = d["box"]
        
        out = self.htHisto(name = box + d["extraName"])
        out.SetLineColor(d["color"])
        out.SetLineStyle(inDict(d, "style", 1))
        out.SetLineWidth(inDict(d, "width", 1))
        
        out.SetMarkerColor(d["color"])
        out.SetMarkerStyle(inDict(d, "style", 1))
        
        for i in range(len(self.htBinLowerEdges)) :
            l = self.lumi[box]
            xs = d["example"]["xs"]
            eff = d["example"]["eff%s"%box.capitalize()][i]
            out.SetBinContent(i+1, l*xs*eff)
        return out
    
    def varHisto(self, varName = None, extraName = "", wspaceMemberFunc = None, purityKey = None, yLabel = "", note = "",
                 color = r.kBlack, lineStyle = 1, lineWidth = 1, markerStyle = 1, lumiString = "", errorsFrom = "") :
	d = {}
	d["value"] = self.htHisto(name = varName+extraName, note = note, yLabel = yLabel)
	d["value"].Reset()
	
	d["value"].SetLineColor(color)
	d["value"].SetLineStyle(lineStyle)
	d["value"].SetLineWidth(lineWidth)
	
	if wspaceMemberFunc=="var" :
	    for item in ["min", "max"] :
	        d[item] = d["value"].Clone(d["value"].GetName()+item)
	        d[item].SetLineColor(color)
	        d[item].SetLineStyle(lineStyle+1)
	        d[item].SetLineWidth(lineWidth)
	          
	d["value"].SetMarkerColor(color)
	d["value"].SetMarkerStyle(markerStyle)

	toPrint = []
	for i in range(len(self.htBinLowerEdges)) :
	    if wspaceMemberFunc :
	        var  = self.wspace.var("%s%d"%(varName, i))
	        func = self.wspace.function("%s%d"%(varName, i))
	        if (not var) and (not func) : continue
	        value = (var if var else func).getVal()
	        d["value"].SetBinContent(i+1, value)
	        if var :
                    if varName[0]=="n" :
                        d["value"].SetBinError(i+1, math.sqrt(value))
                    else :
                        d["value"].SetBinError(i+1, var.getError())
                    
	            for item in ["min", "max"] :
	                x = getattr(var, "get%s"%item.capitalize())()
	                if abs(x)==1.0e30 : continue
	                d[item].SetBinContent(i+1, x)
                elif errorsFrom :
                    errorsVar = self.wspace.var(errorsFrom) if self.wspace.var(errorsFrom) else self.wspace.var(errorsFrom+"%d"%i)
                    if errorsVar and errorsVar.getVal() : d["value"].SetBinError(i+1, value*errorsVar.getError()/errorsVar.getVal())
	    else :
	        value = self.inputData.mcExpectations()[varName][i] if varName in self.inputData.mcExpectations() else self.inputData.mcExtra()[varName][i]
	        purity = 1.0 if not purityKey else self.inputData.purities()[purityKey][i]
	        d["value"].SetBinContent(i+1, value/purity)
	        key = varName+"Err"
	        if key in self.inputData.mcStatError() :
	            d["value"].SetBinError(i+1, self.inputData.mcStatError()[key][i]/purity)
	    toPrint.append(value)
        self.toPrint.append( (varName.rjust(10), lumiString.rjust(10), pretty(toPrint)) )
	return d

    def validationPlot(self, note = "", fileName = "", legend0 = (0.3, 0.6), legend1 = (0.85, 0.85), reverseLegend = False, minimum = 0.0, maximum = None,
                       logY = False, obsKey = None, obsLabel = None, otherVars = [], yLabel = "counts / bin", scale = 1.0) :
        stuff = []
        leg = r.TLegend(legend0[0], legend0[1], legend1[0], legend1[1], "ML values" if (otherVars and obsKey) else "")
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        extraName = str(logY)+"_".join([inDict(o, "var", "") for o in otherVars])
        lumiString = obsLabel[obsLabel.find("["):]
        obs = self.varHisto(varName = obsKey, extraName = extraName, wspaceMemberFunc = "var",
                            yLabel = yLabel, note = note, lumiString = lumiString)["value"]
                            
        obs.SetMarkerStyle(20)
        obs.SetStats(False)
        obs.Draw("p")
        if obsLabel : leg.AddEntry(obs, obsLabel, "lp")
        if minimum!=None : obs.SetMinimum(minimum)
        if maximum!=None : obs.SetMaximum(maximum)
	
        if logY :
            obs.SetMinimum(0.1)
            r.gPad.SetLogy()
        else :
            r.gPad.SetLogy(False)
	    
	goptions = "same"
	stacks = {}
	stuff += [leg,obs,stacks]
	legEntries = []
	for d in otherVars :
	    if "example" not in d :
                if "var" not in d : continue
	        histos = self.varHisto(varName = d["var"], extraName = extraName, wspaceMemberFunc = d["type"],
                                       purityKey = inDict(d, "purityKey", None), color = d["color"], lineStyle = d["style"],
                                       lineWidth = inDict(d, "width", 1), lumiString = lumiString, errorsFrom = inDict(d, "errorsFrom", ""))
	        hist = histos["value"]
	    else :
                d2 = copy.deepcopy(d)
                d2["extraName"] = extraName
	        hist = self.signalExampleHisto(d2)
	    if not hist.GetEntries() : continue
	    stuff.append(hist)
	    legEntries.append( (hist, "%s %s"%(d["desc"], inDict(d, "desc2", "")), "l") )
	    if d["stack"] :
	        if d["stack"] not in stacks :
	            stacks[d["stack"]] = utils.thstack(name = d["stack"])
	        stacks[d["stack"]].Add(hist, inDict(d, "stackOptions", ""))
	    else :
	        hist.Scale(scale)
	        stuff.append( drawOne(hist, goptions, inDict(d, "errorBand", False)) )
	        for item in ["min", "max"] :
	            if item not in histos : continue
	            histos[item].Draw(goptions)

        stuff.append(stacks)
	for stack in stacks.values() :
	    stack.Draw(goptions, reverse = True)
            
	obs.Draw("psame")#redraw data

	for item in reversed(legEntries) if reverseLegend else legEntries :
	    leg.AddEntry(*item)
	leg.Draw()
	r.gPad.SetTickx()
	r.gPad.SetTicky()
	r.gPad.Update()

	if self.printPages and fileName :
	    obs.SetTitle("")
	    printOnePage(self.canvas, fileName)
	self.canvas.Print(self.psFileName)

	return stuff

    def ratioPlot(self, note = "", fileName = "", legend0 = (0.3, 0.6), legend1 = (0.85, 0.88), specs = [], yLabel = "",
                  customMaxFactor = None, maximum = None, goptions = "p", reverseLegend = False) :
    	stuff = []
    	leg = r.TLegend(legend0[0], legend0[1], legend1[0], legend1[1])
    	leg.SetBorderSize(0)
    	leg.SetFillStyle(0)
    	
    	legEntries = []
    	histos = []
    	for spec in specs :
            num = self.varHisto(spec["num"], extraName = spec["num"]+"_".join(spec["dens"]), errorsFrom = inDict(spec, "numErrorsFrom", ""),
                                wspaceMemberFunc = spec["numType"], yLabel = yLabel, note = note)["value"]
    	
    	    for den,denType in zip(spec["dens"], spec["denTypes"]) :
                num.Divide( self.varHisto(den, wspaceMemberFunc = denType)["value"] )
    	
    	    num.SetMarkerStyle(20)
    	    num.SetStats(False)
    	    num.SetLineColor(spec["color"])
    	    num.SetMarkerColor(spec["color"])
    	    legEntries.append( (num, spec["desc"], legSpec(goptions)) )
    	    histos.append(num)
    	
    	for i,h in enumerate(histos) :
    	    if not i :
    	        h.Draw(goptions)
    	        r.gPad.SetLogy(False)
    	        h.SetMinimum(0.0)
    	        if customMaxFactor : h.SetMaximum(max([histoMax(histo, customMaxFactor) for histo in histos]))
    	        if maximum :  h.SetMaximum(maximum)
    	    else :
    	        h.Draw("%ssame"%goptions)
    	
    	for item in reversed(legEntries) if reverseLegend else legEntries :
    	    leg.AddEntry(*item)
    	
    	leg.Draw()
    	stuff.append(leg)
    	stuff.append(histos)
    	r.gPad.SetTickx()
    	r.gPad.SetTicky()
    	r.gPad.Update()
    	
    	if self.printPages and fileName :
    	    histos[0].SetTitle("")
    	    printOnePage(self.canvas, fileName)
    	self.canvas.Print(self.psFileName)

rootSetup()
