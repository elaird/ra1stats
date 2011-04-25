import os,array,data2,utils
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

def validationPlot(wspace = None, canvas = None, psFileName = None, note = "", legendX1 = 0.3, obsKey = None, obsLabel = None, otherVars = []) :
    def inputHisto() :
        bins = array.array('d', list(data2.htBinLowerEdges())+[data2.htMaxForPlot()])
        out = r.TH1D(obsKey, "%s;H_{T} (GeV);counts / bin"%note, len(bins)-1, bins)
        out.Sumw2()
        for i,content in enumerate(data2.observations()[obsKey]) :
            for count in range(content) : out.Fill(bins[i])
        return out
    
    def varHisto(inp, wspace, varName, color, style, wspaceMemberFunc = None) :
        out = inp.Clone(varName)
        out.Reset()
        out.SetMarkerStyle(1)
        out.SetLineColor(color)
        out.SetLineStyle(style)
        out.SetMarkerColor(color)
        for i in range(len(data2.htBinLowerEdges())) :
            if wspaceMemberFunc :
                var = getattr(wspace, wspaceMemberFunc)("%s%d"%(varName,i))
                if not var : continue
                out.SetBinContent(i+1, var.getVal())
            else :
                out.SetBinContent(i+1, data2.mcExpectations()[varName][i])
                
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
    
def validationPlots(wspace, results, method) :
    out = []

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
    utils.ps2pdf(psFileName)
    return out

def pValuePlots(pValue = None, lMaxData = None, lMaxs = None, graph = None) :
    print "pValue =",pValue

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
    utils.ps2pdf(ps)

rootSetup()
