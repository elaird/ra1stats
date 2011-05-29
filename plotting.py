import os,array,math
import utils
import ROOT as r

def rootSetup() :
    r.gROOT.SetStyle("Plain")
    r.gErrorIgnoreLevel = 2000

def writeGraphVizTree(wspace, pdfName = "model") :
    dotFile = "%s.dot"%pdfName
    wspace.pdf(pdfName).graphVizTree(dotFile, ":", True, False)
    cmd = "dot -Tps %s -o %s"%(dotFile, dotFile.replace(".dot", ".ps"))
    os.system(cmd)
    
def errorsPlot(wspace, results) :
    results.Print("v")
    k = wspace.var("k")
    A = wspace.var("A")
    plot = r.RooPlot(k, A, 0.0, 1.0e-5, 0.0, 1.0e-4)
    results.plotOn(plot, k, A, "ME12VHB")
    plot.Draw()
    return plot

def inputHisto(inputData, obsKey, note, extraName = "") :
    bins = array.array('d', list(inputData.htBinLowerEdges())+[inputData.htMaxForPlot()])
    out = r.TH1D(obsKey+extraName, "%s;H_{T} (GeV);counts / bin"%note, len(bins)-1, bins)
    out.Sumw2()
    obs = inputData.observations()
    for i,content in enumerate(obs[obsKey] if obsKey in obs else []) :
        out.SetBinContent(1+i, content)
        out.SetBinError(1+i, math.sqrt(content))
    return out
    
def varHisto(exampleHisto = None, inputData = None, wspace = None, varName = None,
             color = r.kBlack, lineStyle = 1, lineWidth = 1, markerStyle = 1,
             wspaceMemberFunc = None, extraName = "") :
    out = exampleHisto.Clone(varName+extraName)
    out.Reset()

    out.SetLineColor(color)
    out.SetLineStyle(lineStyle)
    out.SetLineWidth(lineWidth)

    out.SetMarkerColor(color)
    out.SetMarkerStyle(markerStyle)

    for i in range(len(inputData.htBinLowerEdges())) :
        if wspaceMemberFunc :
            var = getattr(wspace, wspaceMemberFunc)("%s%d"%(varName,i))
            if not var : continue
            out.SetBinContent(i+1, var.getVal())
        else :
            out.SetBinContent(i+1, inputData.mcExpectations()[varName][i])
    return out

def validationPlot(wspace = None, canvas = None, psFileName = None, inputData = None, note = "", legendX1 = 0.3, obsKey = None, obsLabel = None, maximum = None, otherVars = []) :
    stuff = []
    leg = r.TLegend(legendX1, 0.6, 0.85, 0.85, "ML values" if (otherVars and obsKey) else "")
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    inp = inputHisto(inputData, obsKey, note)
    inp.SetMarkerStyle(20)
    inp.SetStats(False)
    inp.Draw("p")
    inp.SetMinimum(0.0)
    if obsLabel : leg.AddEntry(inp, obsLabel, "lp")
    if maximum!=None : inp.SetMaximum(maximum)

    goptions = "same"
    stacks = {}
    stuff += [leg,inp,stacks]
    for d in otherVars :
        hist = varHisto(inp, inputData, wspace, d["var"], d["color"], lineStyle = d["style"], lineWidth = d["width"] if "width" in d else 1, wspaceMemberFunc = d["type"])
        if not hist.GetEntries() : continue
        stuff.append(hist)
        leg.AddEntry(hist, "%s %s %s"%(d["desc"],("(%s stack)"%d["stack"]) if d["stack"] else "", d["desc2"] if "desc2" in d else ""), "l")
        if d["stack"] :
            if d["stack"] not in stacks :
                stacks[d["stack"]] = r.THStack(d["stack"], d["stack"])
            stacks[d["stack"]].Add(hist)
        else : hist.Draw(goptions)

    for stack in stacks.values() :
        stack.Draw(goptions)

    leg.Draw()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Update()

    canvas.Print(psFileName)
    return stuff


def ratioPlot(wspace = None, canvas = None, psFileName = None, inputData = None, note = "", legendX1 = 0.3, specs = []) :
    stuff = []
    leg = r.TLegend(legendX1, 0.6, 0.85, 0.85)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    histos = []
    for spec in specs :
        if spec["numType"]=="data" :
            num = inputHisto(inputData, spec["num"], note)
        else :
            example = inputHisto(inputData, "nHad", note, extraName = spec["num"]+spec["den"])
            num = varHisto(example, inputData, wspace, spec["num"], wspaceMemberFunc = spec["numType"])

        if spec["denType"]=="data" :            
            den = inputHisto(inputData, spec["den"], note, extraName = spec["num"]+spec["den"])
        else :
            example = inputHisto(inputData, "nHad", note, extraName = spec["num"]+spec["den"])            
            den = varHisto(example, inputData, wspace, spec["den"], wspaceMemberFunc = spec["denType"])

        num.Divide(den)
        num.SetMarkerStyle(20)
        num.SetStats(False)
        num.SetLineColor(spec["color"])
        num.SetMarkerColor(spec["color"])
        leg.AddEntry(num, spec["desc"], "lp")
        histos.append(num)

    m = 1.1*max(map(lambda x:x.GetMaximum(), histos))
    for i,h in enumerate(histos) :
        goptions = "p"
        if not i :
            h.Draw(goptions)
            h.SetMinimum(0.0)
            h.SetMaximum(m)
        else :
            h.Draw("%ssame"%goptions)

    leg.Draw()
    stuff.append(leg)
    stuff.append(histos)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Update()

    canvas.Print(psFileName)
    return stuff

def akDesc(wspace, var) :
    return "A = %4.2e; k = %4.2e"%(wspace.var("A_%s"%var).getVal(), wspace.var("k_%s"%var).getVal())

def note(REwk, RQcd): 
    return "%sRQcd%s"%("REwk%s_"%REwk if REwk else "", RQcd)

def validationPlots(wspace, results, inputData, REwk, RQcd, smOnly) :
    out = []

    canvas = r.TCanvas()
    psFileName = "bestFit_%s%s.ps"%(note(REwk, RQcd), "_smOnly" if smOnly else "")
    canvas.Print(psFileName+"[")
    
    if not smOnly :
        signalDesc  = "signal"
        signalDesc2 = "xs = %5.2f xs^{nom}; #rho = %4.2f"%(wspace.var("f").getVal(), wspace.var("rhoSignal").getVal())

    hadVars = [
        {"var":"hadB", "type":"function", "desc":"expected total background",
         "color":r.kBlue, "style":1, "width":2, "stack":"total"},
        {"var":"ewk",  "type":"function", "desc":"EWK", "desc2":akDesc(wspace, "ewk") if REwk else "[floating]",
         "color":r.kCyan, "style":2, "stack":"background"},
        {"var":"qcd",  "type":"function", "desc":"QCD", "desc2":akDesc(wspace, "qcd"),
         "color":r.kMagenta, "style":3, "stack":"background"},
        ]

    hadVars += [
        {"var":"zInv", "type":"function", "desc":"Z->inv", "desc2": "#rho = %4.2f"%wspace.var("rhoPhotZ").getVal(),
         "color":r.kRed, "style":2, "stack":"ewk"},
        {"var":"ttw",  "type":"function", "desc":"t#bar{t} + W", "desc2": "#rho = %4.2f"%wspace.var("rhoMuonW").getVal(),
         "color":r.kGreen, "style":2, "stack":"ewk"},
        ]
    if not smOnly :
        hadVars += [{"var":"hadS", "type":"function", "desc":signalDesc, "desc2":signalDesc2, "color":r.kOrange,  "style":1,  "stack":"total"}]

    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.3, obsKey = "nHad", obsLabel = "hadronic data [%g/pb]"%inputData.lumi()["had"], otherVars = hadVars)
    
    muonVars = [
        {"var":"muonB",   "type":"function", "color":r.kBlue,   "style":1, "desc":"expected SM yield", "stack":"total"},
        {"var":"mcMuon",  "type":None,       "color":r.kGray+2, "style":2, "desc":"SM MC",             "stack":None},
        ]
    if not smOnly :
        muonVars += [{"var":"muonS",   "type":"function", "color":r.kOrange, "style":1, "desc":signalDesc, "desc2":signalDesc2, "stack":"total"}]
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.4, obsKey = "nMuon", obsLabel = "muon data [%g/pb]"%inputData.lumi()["muon"], otherVars = muonVars)
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.4, obsKey = "nPhot", obsLabel = "photon data [%g/pb]"%inputData.lumi()["phot"], otherVars = [
            {"var":"photExp", "type":"function", "color":r.kBlue,   "style":1, "desc":"expected SM yield", "stack":None},
            {"var":"mcPhot",  "type":None,       "color":r.kGray+2, "style":2, "desc":"SM MC",             "stack":None},
            ])

    #plot fZinv
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.4, obsKey = "", obsLabel = "", maximum = 1.0,
                   otherVars = [{"var":"fZinv", "type":"var", "color":r.kBlue, "style":1, "desc":"fit Z->inv / fit EWK", "stack":None}])
    #plot MC translation factors
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.4, obsKey = "", obsLabel = "", maximum = 4.0,
                   otherVars = [{"var":"rMuon", "type":"var", "color":r.kBlue, "style":1, "desc":"MC muon / MC ttW", "stack":None}])
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.4, obsKey = "", obsLabel = "", maximum = 4.0,
                   otherVars = [{"var":"rPhot", "type":"var", "color":r.kBlue, "style":1, "desc":"MC phot / MC Z->inv", "stack":None}])

    #plot alphaT ratios
    ratioPlot(wspace, canvas, psFileName, inputData = inputData, note = note(REwk, RQcd), legendX1 = 0.5, specs = [
        {"num":"nHad",  "numType":"data",     "den":"nHadBulk", "denType":"data", "desc":"nHad / nHadBulk",    "color":r.kBlack},
        {"num":"hadB",  "numType":"function", "den":"nHadBulk", "denType":"data", "desc":"ML hadB / nHadBulk", "color":r.kBlue},
        {"num":"nPhot", "numType":"data",     "den":"nHadBulk", "denType":"data", "desc":"nPhot / nHadBulk",   "color":r.kRed},
        {"num":"nMuon", "numType":"data",     "den":"nHadBulk", "denType":"data", "desc":"nMuon / nHadBulk",   "color":r.kGreen},
        ])
    canvas.Print(psFileName+"]")
    utils.ps2pdf(psFileName)
    return out

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
    utils.ps2pdf(ps)

rootSetup()
