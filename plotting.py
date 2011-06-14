import os,array,math,copy
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

def inputHisto(inputData, obsKey, note, extraName = "", yLabel = "") :
    bins = array.array('d', list(inputData.htBinLowerEdges())+[inputData.htMaxForPlot()])
    out = r.TH1D(obsKey+extraName, "%s;H_{T} (GeV);%s"%(note, yLabel), len(bins)-1, bins)
    out.Sumw2()
    obs = inputData.observations()
    for i,content in enumerate(obs[obsKey] if obsKey in obs else []) :
        out.SetBinContent(1+i, content)
        out.SetBinError(1+i, math.sqrt(content))
    return out
    
def varHisto(exampleHisto = None, inputData = None, wspace = None, varName = None,
             color = r.kBlack, lineStyle = 1, lineWidth = 1, markerStyle = 1,
             wspaceMemberFunc = None, extraName = "") :
    d = {}
    d["value"] = exampleHisto.Clone(varName+extraName)
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

    for i in range(len(inputData.htBinLowerEdges())) :
        if wspaceMemberFunc :
            var = getattr(wspace, wspaceMemberFunc)("%s%d"%(varName,i))
            if not var : continue
            d["value"].SetBinContent(i+1, var.getVal())
            if wspaceMemberFunc=="var" :
                for item in ["min", "max"] :
                    x = getattr(var, "get%s"%item.capitalize())()
                    if abs(x)==1.0e30 : continue
                    d[item].SetBinContent(i+1, x)
        else :
            d["value"].SetBinContent(i+1, inputData.mcExpectations()[varName][i])
    return d

def signalExampleHisto(exampleHisto = None, inputData = None, d = {}) :
    out = exampleHisto.Clone(exampleHisto.GetName()+d["desc"])
    out.Reset()

    out.SetLineColor(d["color"])
    out.SetLineStyle(d["style"] if "style" in d else 1)
    out.SetLineWidth(d["width"] if "width" in d else 1)

    out.SetMarkerColor(d["color"])
    out.SetMarkerStyle(d["style"] if "style" in d else 1)

    for i in range(len(inputData.htBinLowerEdges())) :
        box = d["box"]
        l = inputData.lumi()[box]
        xs = d["example"]["xs"]
        eff = d["example"]["eff%s"%box.capitalize()][i]
        out.SetBinContent(i+1, l*xs*eff)
    return out

def validationPlot(wspace = None, canvas = None, psFileName = None, inputData = None, note = "", legend0 = (0.3, 0.6), legend1 = (0.85, 0.85),
                   minimum = 0.0, maximum = None, logY = False, obsKey = None, obsLabel = None, otherVars = [], yLabel = "counts / bin", scale = 1.0) :
    stuff = []
    leg = r.TLegend(legend0[0], legend0[1], legend1[0], legend1[1], "ML values" if (otherVars and obsKey) else "")
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    inp = inputHisto(inputData, obsKey, note, yLabel = yLabel)
    inp.SetMarkerStyle(20)
    inp.SetStats(False)
    inp.Draw("p")
    if obsLabel : leg.AddEntry(inp, obsLabel, "lp")
    if minimum!=None : inp.SetMinimum(minimum)
    if maximum!=None : inp.SetMaximum(maximum)

    if logY :
        inp.SetMinimum(0.1)
        r.gPad.SetLogy()
    else :
        r.gPad.SetLogy(False)
    
    goptions = "same"
    stacks = {}
    stuff += [leg,inp,stacks]
    for d in otherVars :
        if "example" not in d :
            histos = varHisto(inp, inputData, wspace, d["var"], d["color"], lineStyle = d["style"], lineWidth = d["width"] if "width" in d else 1, wspaceMemberFunc = d["type"])
            hist = histos["value"]
        else :
            hist = signalExampleHisto(inp, inputData, d)
        if not hist.GetEntries() : continue
        stuff.append(hist)
        leg.AddEntry(hist, "%s %s %s"%(d["desc"],("(%s stack)"%d["stack"]) if d["stack"] else "", d["desc2"] if "desc2" in d else ""), "l")
        if d["stack"] :
            if d["stack"] not in stacks :
                stacks[d["stack"]] = r.THStack(d["stack"], d["stack"])
            stacks[d["stack"]].Add(hist)
        else :
            hist.Scale(scale)
            hist.Draw(goptions)
            for item in ["min", "max"] :
                if item not in histos : continue
                histos[item].Draw(goptions)

    for stack in stacks.values() :
        stack.Draw(goptions)

    inp.Draw("psame")#redraw data
    leg.Draw()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Update()

    canvas.Print(psFileName)
    return stuff

def legSpec(goptions) :
    out = ""
    if "p" in goptions : out += "p"
    if "hist" in goptions : out += "l"
    return out

def ratioPlot(wspace = None, canvas = None, psFileName = None, inputData = None, note = "", legend0 = (0.3, 0.6), specs = [], yLabel = "",
              customMax = False, maximum = None, goptions = "p") :
    stuff = []
    leg = r.TLegend(legend0[0], legend0[1], 0.85, 0.85)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    histos = []
    for spec in specs :
        extraName = spec["num"]+"_".join(spec["dens"])
        if spec["numType"]=="data" :
            num = inputHisto(inputData, spec["num"], note, yLabel = yLabel)
        else :
            example = inputHisto(inputData, "nHad", note, extraName = extraName, yLabel = yLabel)
            num = varHisto(example, inputData, wspace, spec["num"], wspaceMemberFunc = spec["numType"])["value"]

        for den,denType in zip(spec["dens"], spec["denTypes"]) :
            if denType=="data" :
                num.Divide( inputHisto(inputData, den, note, extraName = extraName+den) )
            else :
                example = inputHisto(inputData, "nHad", note, extraName = extraName+den)
                num.Divide( varHisto(example, inputData, wspace, den, wspaceMemberFunc = denType)["value"] )

        num.SetMarkerStyle(20)
        num.SetStats(False)
        num.SetLineColor(spec["color"])
        num.SetMarkerColor(spec["color"])
        leg.AddEntry(num, spec["desc"], legSpec(goptions))
        histos.append(num)

    m = 1.1*max(map(lambda x:x.GetMaximum(), histos))
    for i,h in enumerate(histos) :
        if not i :
            h.Draw(goptions)
            r.gPad.SetLogy(False)
            h.SetMinimum(0.0)
            if customMax : h.SetMaximum(m)
            if maximum :  h.SetMaximum(maximum)
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

def validationPlots(wspace, results, inputData, REwk, RQcd, smOnly, signalExampleToStack = ("", {})) :
    if any(signalExampleToStack) : assert smOnly
    
    out = []

    canvas = utils.numberedCanvas()
    psFileName = "bestFit_%s%s.ps"%(note(REwk, RQcd), "_smOnly" if smOnly else "")
    canvas.Print(psFileName+"[")
    
    if not smOnly :
        signalDesc  = "signal"
        signalDesc2 = "xs = %5.2f xs^{nom}; #rho = %4.2f"%(wspace.var("f").getVal(), wspace.var("rhoSignal").getVal())

    #hadronic sample
    hadVars = [
        {"var":"hadB", "type":"function", "desc":"expected total background",
         "color":r.kBlue, "style":1, "width":3, "stack":"total"},
        {"var":"ewk",  "type":"function", "desc":"EWK", "desc2":akDesc(wspace, "ewk") if REwk else "[floating]",
         "color":r.kCyan, "style":2, "width":2, "stack":"background"},
        {"var":"qcd",  "type":"function", "desc":"QCD", "desc2":akDesc(wspace, "qcd"),
         "color":r.kMagenta, "style":3, "width":2, "stack":"background"},
        ]

    hadVars += [
        {"var":"zInv", "type":"function", "desc":"Z->inv", "desc2": "#rho = %4.2f"%wspace.var("rhoPhotZ").getVal(),
         "color":r.kRed, "style":2, "width":2, "stack":"ewk"},
        {"var":"ttw",  "type":"function", "desc":"t#bar{t} + W", "desc2": "#rho = %4.2f"%wspace.var("rhoMuonW").getVal(),
         "color":r.kGreen, "style":2, "width":2, "stack":"ewk"},
        ]
    if not smOnly :
        hadVars += [{"var":"hadS", "type":"function", "desc":signalDesc, "desc2":signalDesc2, "color":r.kOrange, "style":1, "width":2, "stack":"total"}]
    elif any(signalExampleToStack) :
        hadVars += [{"example":signalExampleToStack[1], "box":"had", "desc":signalExampleToStack[0], "color":r.kOrange, "style":1, "width":2, "stack":"total"}]

    for logY in [False, True] :
        thisNote = "Hadronic Sample%s"%(" (logY)" if logY else "")
        validationPlot(wspace, canvas, psFileName, inputData = inputData, note = thisNote, legend0 = (0.35, 0.63), legend1 = (0.85, 0.88),
                       obsKey = "nHad", obsLabel = "hadronic data [%g/pb]"%inputData.lumi()["had"], otherVars = hadVars, logY = logY)

    #muon control sample
    muonVars = [
        {"var":"muonB",   "type":"function", "color":r.kBlue,   "style":1, "width":3, "desc":"expected SM yield", "stack":"total"},
        {"var":"mcMuon",  "type":None,       "color":r.kGray+2, "style":2, "width":2, "desc":"SM MC",             "stack":None},
        ]
    if not smOnly :
        muonVars += [{"var":"muonS",   "type":"function", "color":r.kOrange, "style":1, "width":2, "desc":signalDesc, "desc2":signalDesc2, "stack":"total"}]
    elif any(signalExampleToStack) :
        muonVars += [{"example":signalExampleToStack[1], "box":"muon", "desc":signalExampleToStack[0], "color":r.kOrange, "style":1, "width":2, "stack":"total"}]

    for logY in [False, True] :
        thisNote = "Muon Control Sample%s"%(" (logY)" if logY else "")
        validationPlot(wspace, canvas, psFileName, inputData = inputData, note = thisNote, legend0 = (0.35, 0.7),
                       obsKey = "nMuon", obsLabel = "muon data [%g/pb]"%inputData.lumi()["muon"], otherVars = muonVars, logY = logY)

    #photon control sample
    for logY in [False, True] :
        thisNote = "Photon Control Sample%s"%(" (logY)" if logY else "")        
        validationPlot(wspace, canvas, psFileName, inputData = inputData, note = thisNote, legend0 = (0.35, 0.72),
                       obsKey = "nPhot", obsLabel = "photon data [%g/pb]"%inputData.lumi()["phot"], logY = logY, otherVars = [
            {"var":"photExp", "type":"function", "color":r.kBlue,   "style":1, "width":3, "desc":"expected SM yield", "stack":None},
            {"var":"mcPhot",  "type":None,       "color":r.kGray+2, "style":2, "width":2, "desc":"SM MC",             "stack":None},
            ])

    #EWK background scale factors
    ratioPlot(wspace, canvas, psFileName, inputData = inputData, note = "ttW scale factor (result of fit)", legend0 = (0.5, 0.8), maximum = 3.0, specs = [
        {"num":"ttw",   "numType":"function", "dens":["mcTtw"],  "denTypes":[None], "desc":"ML ttW / MC ttW",       "color":r.kGreen}], goptions = "hist")
    ratioPlot(wspace, canvas, psFileName, inputData = inputData, note = "Z->inv scale factor (result of fit)", legend0 = (0.5, 0.8), maximum = 3.0, specs = [
        {"num":"zInv",  "numType":"function", "dens":["mcZinv"], "denTypes":[None], "desc":"ML Z->inv / MC Z->inv", "color":r.kRed}], goptions = "hist")

    #fZinv
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = "fraction of EWK background which is Z->inv (result of fit)",
                   legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", minimum = 0.0, maximum = 1.0,
                   otherVars = [{"var":"fZinv", "type":"var", "color":r.kBlue, "style":1, "desc":"fit Z->inv / fit EWK", "stack":None}], yLabel = "")

    #MC translation factors
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = "muon translation factor (from MC)",
                   legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", maximum = 4.0,
                   otherVars = [{"var":"rMuon", "type":"var", "color":r.kBlue, "style":1, "desc":"MC muon / MC ttW", "stack":None}],
                   yLabel = "", scale = inputData.lumi()["had"]/inputData.lumi()["muon"])
    validationPlot(wspace, canvas, psFileName, inputData = inputData, note = "photon translation factor (from MC)",
                   legend0 = (0.5, 0.8), obsKey = "", obsLabel = "", maximum = 4.0,
                   otherVars = [{"var":"rPhot", "type":"var", "color":r.kBlue, "style":1, "desc":"MC phot / MC Z->inv", "stack":None}],
                   yLabel = "", scale = inputData.lumi()["had"]/inputData.lumi()["phot"])

    #alphaT ratios
    ratioPlot(wspace, canvas, psFileName, inputData = inputData, note = "", legend0 = (0.5, 0.7), specs = [
        {"num":"nHad",  "numType":"data",     "dens":["nHadBulk"], "denTypes":["data"], "desc":"nHad / nHadBulk",    "color":r.kBlack},
        {"num":"hadB",  "numType":"function", "dens":["nHadBulk"], "denTypes":["data"], "desc":"ML hadB / nHadBulk", "color":r.kBlue},
        ], yLabel = "R_{#alpha_{T}}")
    ratioPlot(wspace, canvas, psFileName, inputData = inputData, note = "", legend0 = (0.5, 0.7), specs = [
       #{"num":"nPhot", "numType":"data",     "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"nPhot / nHadBulk",            "color":r.kGray+2},
        {"num":"nPhot", "numType":"data",     "dens":["nHadBulk", "rPhot"], "denTypes":["data", "var"], "desc":"nPhot * MCZ/MCph / nHadBulk", "color":r.kBlack},
        {"num":"zInv",  "numType":"function", "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"ML Zinv / nHadBulk",          "color":r.kRed},
        ], yLabel = "R_{#alpha_{T}}")
    ratioPlot(wspace, canvas, psFileName, inputData = inputData, note = "", legend0 = (0.5, 0.7), specs = [
       #{"num":"nMuon", "numType":"data",     "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"nMuon / nHadBulk",              "color":r.kGray+2},
        {"num":"nMuon", "numType":"data",     "dens":["nHadBulk", "rMuon"], "denTypes":["data", "var"], "desc":"nMuon * MCttW/MCmu / nHadBulk", "color":r.kBlack},
        {"num":"ttw",   "numType":"function", "dens":["nHadBulk"],          "denTypes":["data"],        "desc":"ML ttW / nHadBulk",             "color":r.kGreen},        
        ], yLabel = "R_{#alpha_{T}}")
    canvas.Print(psFileName+"]")
    utils.ps2pdf(psFileName)
    return out

def expectedLimitPlots(quantiles = {}, obsLimit = None, note = "") :
    ps = "limits_%s.ps"%note
    canvas = r.TCanvas("canvas")
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(ps+"[")

    h = quantiles["hist"]
    h.Draw()
    h.SetStats(False)

    q = copy.deepcopy(quantiles)
    q["Observed Limit"] = obsLimit

    legend = r.TLegend(0.1, 0.7, 0.5, 0.9)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    
    line = r.TLine()
    line.SetLineWidth(2)
    keys = sorted(q.keys())
    keys.remove("hist")
    for i,key in enumerate(keys) :
        line.SetLineColor(2+i)
        line2 = line.DrawLine(q[key], h.GetMinimum(), q[key], h.GetMaximum())
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

rootSetup()
