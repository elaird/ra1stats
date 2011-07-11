import os,array,math,copy
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

def expectedLimitPlots(quantiles = {}, hist = None, obsLimit = None, note = "") :
    ps = "limits_%s.ps"%note
    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(ps+"[")

    hist
    hist.Draw()
    hist.SetStats(False)

    q = copy.deepcopy(quantiles)
    q["Observed Limit"] = obsLimit

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
    out = []
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
    out += "%s = %4.2e%s; "%(var1[0], varA.getVal(), " #pm %4.2e"%varA.getError() if errors else "")
    out += "%s = %4.2e%s"  %(var2[0], vark.getVal(), " #pm %4.2e"%vark.getError() if errors else "")
    return out

class validationPlotter(object) :
    def __init__(self, args) :
        for key,value in args.iteritems() :
            setattr(self,key,value)
        if any(self.signalExampleToStack) : assert self.smOnly

        self.toPrint = []
        self.ewkType = "function" if self.REwk else "var"
        if not self.smOnly :
            self.signalDesc = "signal"
            self.signalDesc2 = "xs = %5.2f xs^{nom}; #rho = %4.2f"%(self.wspace.var("f").getVal(), self.wspace.var("rhoSignal").getVal())

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
            {"var":"ewk",  "type":self.ewkType, "desc":"EWK", "desc2":akDesc(self.wspace, "A_ewk", "d_ewk", errors = True) if self.REwk else "[floating]",
             "color":r.kCyan, "style":2, "width":2, "stack":"background"},
            {"var":"qcd",  "type":"function", "desc":"QCD", "desc2":akDesc(self.wspace, "A_qcd", "k_qcd", errors = True),
             "color":r.kMagenta, "style":3, "width":2, "stack":"background"},
            ]

        desc2 = "#rho_{ph} = %4.2f #pm %4.2f"%(self.wspace.var("rhoPhotZ").getVal(), self.wspace.var("rhoPhotZ").getError())
        if self.mumuTerms : desc2 += "; #rho_{#mu#mu} = %4.2f #pm %4.2f"%(self.wspace.var("rhoMumuZ").getVal(), self.wspace.var("rhoMumuZ").getError())
        vars += [
            {"var":"zInv", "type":"function", "desc":"Z->inv", "desc2": desc2,  "color":r.kRed, "style":2, "width":2, "stack":"ewk"},
            {"var":"ttw",  "type":"function", "desc":"t#bar{t} + W", "desc2": "#rho_{#mu} = %4.2f #pm %4.2f"%(self.wspace.var("rhoMuonW").getVal(), self.wspace.var("rhoMuonW").getError()),
             "color":r.kGreen, "style":2, "width":2, "stack":"ewk"},
            ]
        if not self.smOnly :
            vars += [{"var":"hadS", "type":"function", "desc":signalDesc, "desc2":signalDesc2, "color":r.kOrange, "style":1, "width":2, "stack":"total"}]
        elif any(self.signalExampleToStack) :
            vars += [{"example":self.signalExampleToStack[1], "box":"had", "desc":self.signalExampleToStack[0], "color":r.kOrange, "style":1, "width":2, "stack":"total"}]

        for logY in [False, True] :
            thisNote = "Hadronic Signal Sample%s"%(" (logY)" if logY else "")
            fileName = "hadronic_signal_fit%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.63), legend1 = (0.85, 0.88),
                                obsKey = "nHad", obsLabel = "hadronic data [%g/pb]"%self.lumi["had"], otherVars = vars, logY = logY)

    def hadDataMcPlots(self) :
        for logY in [False, True] :
            thisNote = "Hadronic Signal Sample%s"%(" (logY)" if logY else "")
            fileName = "hadronic_signal_data_mc%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True, logY = logY,
                                obsKey = "nHad", obsLabel = "hadronic data [%g/pb]"%self.lumi["had"], otherVars = [
                {"var":"mcHad", "type":None, "color":r.kGray+2, "style":2, "width":2, "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray},
                {"var":"ewk",  "type":self.ewkType, "desc":"EWK", "desc2":akDesc(self.wspace, "A_ewk", "d_ewk", errors = True) if self.REwk else "[floating]",
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
                                    obsKey = "nHadControl%s"%label, obsLabel = "hadronic control data (%s) [%g/pb]"%(labelRaw, self.lumi["had"]),
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
            vars += [{"var":"muonS",   "type":"function", "color":r.kOrange, "style":1, "width":2, "desc":signalDesc, "desc2":signalDesc2, "stack":"total"}]
        elif any(self.signalExampleToStack) :
            vars += [{"example":self.signalExampleToStack[1], "box":"muon", "desc":self.signalExampleToStack[0], "color":r.kOrange, "style":1, "width":2, "stack":"total"}]

        for logY in [False, True] :
            thisNote = "Muon Control Sample%s"%(" (logY)" if logY else "")
            fileName = "muon_control_fit%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.7),
                                obsKey = "nMuon", obsLabel = "muon data [%g/pb]"%self.lumi["muon"], otherVars = vars, logY = logY)

    def photPlots(self) :
        for logY in [False, True] :
            thisNote = "Photon Control Sample%s"%(" (logY)" if logY else "")
            fileName = "photon_control_fit%s"%("_logy" if logY else "")            
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True, logY = logY,
                                obsKey = "nPhot", obsLabel = "photon data [%g/pb]"%self.lumi["phot"], otherVars = [
                {"var":"mcGjets", "type":None, "purityKey": "phot", "color":r.kGray+2, "style":2, "width":2,
                 "desc":"SM MC #pm stat. error", "stack":None, "errorBand":r.kGray}  if not self.printPages else {},
                {"var":"photExp", "type":"function", "color":r.kBlue,   "style":1, "width":3, "desc":"expected SM yield", "stack":None},
                ])

    def mumuPlots(self) :
        for logY in [False, True] :
            thisNote = "Mu-Mu Control Sample%s"%(" (logY)" if logY else "")
            fileName = "mumu_control_fit%s"%("_logy" if logY else "")
            self.validationPlot(note = thisNote, fileName = fileName, legend0 = (0.35, 0.72), reverseLegend = True,
                                obsKey = "nMumu", obsLabel = "mumu data [%g/pb]"%self.lumi["mumu"], logY = logY, otherVars = [
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
        self.ratioPlot(note = "hadronic signal", fileName = "hadronic_signal_alphaT_ratio", legend0 = (0.12, 0.7), legend1 = (0.52, 0.88), specs = [
            {"num":"qcd",   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML QCD / nHadBulk", "color":r.kMagenta},
            {"num":"ewk",   "numType":self.ewkType,    "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML EWK / nHadBulk", "color":r.kCyan},
            {"num":"hadB",  "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML hadB / nHadBulk", "color":r.kBlue},
            {"num":"nHad",  "numType":"data",     "dens":["nHadBulk"], "denTypes":["var"], "desc":"nHad / nHadBulk",    "color":r.kBlack},
            ], yLabel = "R_{#alpha_{T}}", customMax = True, reverseLegend = True)

        for labelRaw in self.hadControlLabels :
            label = "_"+labelRaw+"_"
            label1 = label[:-1]
            self.ratioPlot(note = "hadronic control %s"%labelRaw,
                      legend0 = (0.12, 0.7), legend1 = (0.52, 0.88), specs = [
                {"num":"qcdControl%s"%label,   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML QCD / nHadBulk", "color":r.kMagenta},
                {"num":"ewkControl%s"%label,   "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML EWK / nHadBulk", "color":r.kCyan},
                {"num":"hadControlB%s"%label,  "numType":"function", "dens":["nHadBulk"], "denTypes":["var"], "desc":"ML hadControlB / nHadBulk", "color":r.kBlue},
                {"num":"nHadControl%s"%label1, "numType":"data",     "dens":["nHadBulk"], "denTypes":["var"], "desc":"nHadControl / nHadBulk",    "color":r.kBlack},
                ], yLabel = "R_{#alpha_{T}}", customMax = True, reverseLegend = True)

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
        def printText(x, y, s) :
            #print s
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
            y = printText(x, y, s)
        self.canvas.Print(self.psFileName)
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
                 color = r.kBlack, lineStyle = 1, lineWidth = 1, markerStyle = 1, lumiString = "") :
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
                                       lineWidth = inDict(d, "width", 1), lumiString = lumiString)
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
	            stacks[d["stack"]] = r.THStack(d["stack"], d["stack"])
	        stacks[d["stack"]].Add(hist)
	    else :
	        hist.Scale(scale)
	        stuff.append( drawOne(hist, goptions, inDict(d, "errorBand", False)) )
	        for item in ["min", "max"] :
	            if item not in histos : continue
	            histos[item].Draw(goptions)

        stuff.append(stacks)
	for stack in stacks.values() :
	    stack.Draw(goptions)
            
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
                  customMax = False, maximum = None, goptions = "p", reverseLegend = False) :
    	stuff = []
    	leg = r.TLegend(legend0[0], legend0[1], legend1[0], legend1[1])
    	leg.SetBorderSize(0)
    	leg.SetFillStyle(0)
    	
    	legEntries = []
    	histos = []
    	for spec in specs :
            num = self.varHisto(spec["num"], extraName = spec["num"]+"_".join(spec["dens"]),
                                wspaceMemberFunc = spec["numType"], yLabel = yLabel, note = note)["value"]
    	
    	    for den,denType in zip(spec["dens"], spec["denTypes"]) :
                num.Divide( self.varHisto(den, wspaceMemberFunc = denType)["value"] )
    	
    	    num.SetMarkerStyle(20)
    	    num.SetStats(False)
    	    num.SetLineColor(spec["color"])
    	    num.SetMarkerColor(spec["color"])
    	    legEntries.append( (num, spec["desc"], legSpec(goptions)) )
    	    histos.append(num)
    	
    	m = max(map(histoMax, histos))
    	for i,h in enumerate(histos) :
    	    if not i :
    	        h.Draw(goptions)
    	        r.gPad.SetLogy(False)
    	        h.SetMinimum(0.0)
    	        if customMax : h.SetMaximum(m)
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
