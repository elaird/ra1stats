import os,sys,math,utils,pickling

from histogramProcessing import printHoles,fillPoints,killPoints
from utils import threeToTwo, shifted

import configuration as conf
import histogramSpecs as hs
import refXsProcessing as rxs
import ROOT as r

def setupRoot() :
    #r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)
    #r.gStyle.SetPadTickX(True)
    #r.gStyle.SetPadTickY(True)

setupRoot()


def modifyHisto(h, s) :
    fillPoints(h, points = s["overwriteOutput"][s["signalModel"]])
    killPoints(h, cutFunc = s["cutFunc"][s["signalModel"]] if s["signalModel"] in s["cutFunc"] else None)

def squareCanvas(margin = 0.18, ticks = True, name = "canvas", numbered = False) :
    canvas = (utils.numberedCanvas if numbered else r.TCanvas)(name, name, 2)
    for side in ["Left", "Right", "Top", "Bottom"] :
        getattr(canvas, "Set%sMargin"%side)(margin)
    canvas.SetTickx(ticks)
    canvas.SetTicky(ticks)
    return canvas

def adjustHisto(h, title = "") :
    h.SetStats(False)
    h.SetTitle(title)
    h.GetYaxis().SetTitleOffset(1.5)
    h.GetZaxis().SetTitleOffset(1.5)

def printOnce(canvas, fileName) :
    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(22)
    #text.DrawText(0.5, 0.85, "CMS")

    if True :
        latex = r.TLatex()
        latex.SetNDC()
        latex.SetTextAlign(22)

        # should this go somewhere else (refXsProcessing?)
        # i.e. modelSpec = { 'T2': { 'histo': 'squark', 'factor': 1.0, 'file':
        # seven, 'process': 'pp ....' } }
        process_stamps =  {
            'T2'     : {
                'text': "pp #rightarrow #tilde{q} #tilde{q}, #tilde{q} #rightarrow q + LSP; m(#tilde{g})>>m(#tilde{q})",
                'xpos': 0.4250,
                },
            'T2bb'   : {
                'text': "pp #rightarrow #tilde{b} #tilde{b}, #tilde{b} #rightarrow b + LSP; m(#tilde{g})>>m(#tilde{b})",
                'xpos': 0.425,
                },
            'T2tt'   : {
                'text': "pp #rightarrow #tilde{t} #tilde{t}, #tilde{t} #rightarrow t + LSP; m(#tilde{g})>>m(#tilde{t})",
                'xpos': 0.41,
                },
            'T1'     : {
                'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow 2q + LSP; m(#tilde{q})>>m(#tilde{g})",
                'xpos': 0.4325,
                },
            'T1bbbb' : {
                'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow 2b + LSP; m(#tilde{b})>>m(#tilde{g})",
                'xpos': 0.43,
                },
            'T1tttt' : {
                'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow 2t + LSP; m(#tilde{t})>>m(#tilde{g})",
                'xpos': 0.425,
                },
            }
        current_stamp = process_stamps.get(conf.switches()['signalModel'],None)

        latex.SetTextSize(0.6*latex.GetTextSize())
        if current_stamp:
            latex.DrawLatex(current_stamp['xpos'], 0.78, current_stamp['text'])

    canvas.Print(fileName)
    utils.epsToPdf(fileName)
    #canvas.Print(fileName.replace(".eps",".C"))

def setRange(var, ranges, histo, axisString) :
    if var not in ranges : return
    nums = ranges[var]
    getattr(histo,"Get%saxis"%axisString)().SetRangeUser(*nums[:2])
    if len(nums)==3 : r.gStyle.SetNumberContours(nums[2])
    if axisString=="Z" :
        maxContent = histo.GetBinContent(histo.GetMaximumBin())
        if maxContent>nums[1] :
            print "ERROR: histo truncated in Z (maxContent = %g, maxSpecified = %g) %s"%(maxContent, nums[1], histo.GetName())

def stamp(text = "#alpha_{T}, P.L., 1.1 fb^{-1}", x = 0.25, y = 0.55, factor = 1.3) :
    latex = r.TLatex()
    latex.SetTextSize(factor*latex.GetTextSize())
    latex.SetNDC()
    latex.DrawLatex(x, y, text)
    return latex

def pointsAtYMin(graph) :
    out = []
    x = graph.GetX()
    y = graph.GetY()
    if not graph.GetN() : return out
    yMin = min([y[i] for i in range(graph.GetN())])
    xsAtYMin = []
    for i in range(graph.GetN()) :
        if y[i]==yMin :
            out.append((x[i], y[i]))
    if len(out) :
        xMax = max([coords[0] for coords in out])
        xMin = min([coords[0] for coords in out])
        while (xMax,yMin) in out:
            out.remove((xMax,yMin))
        while (xMin,yMin) in out:
            out.remove((xMin,yMin))
    return out

def pruneGraph( graph, lst=[], debug=False, breakLink=False ):
    if debug: graph.Print()
    for p in lst:
        x = graph.GetX()
        y = graph.GetY()
        bad = []
        for i in range(graph.GetN()):
            if abs(p[0]-x[i]) < 1.0e-6 and abs(p[1]-y[i]) < 1.0e-6:
                bad.append(i-len(bad))
        for i in bad:
            print "WARNING: Removing point %d = (%g,%g) from graph %s" % (i, x[i], y[i], graph.GetName())
            graph.RemovePoint(i)
    if breakLink:
        graph.RemovePoint(graph.GetN()-1)
    if debug: graph.Print()

def insertPoints( graph, lst=[], mode="prepend" ) :
    npoints = len(lst)
    ngraph = graph.GetN()

    total_points = npoints + ngraph
    graph.Expand(total_points)

    print "expanding graph", graph.GetName(), "with", graph.GetN(),
    print "points to have", total_points
    if mode=="prepend":
        for p in reversed(range(total_points)):
            if p < npoints:
                graph.SetPoint(p, lst[p][0], lst[p][1])
            else:
                x = r.Double(0.)
                y = r.Double(0.)
                graph.GetPoint(p-npoints,x,y)
                graph.SetPoint(p,x,y)
    elif mode=="append":
        for p in range(total_points):
            if p < ngraph:
                x = r.Double(0.)
                y = r.Double(0.)
                graph.GetPoint(p,x,y)
                graph.SetPoint(p,x,y)
            else:
                graph.SetPoint(p, *lst[p-ngraph])

def spline(points = [], title = "") :
    graph = r.TGraph()
    for i,(x,y) in enumerate(points) :
        graph.SetPoint(i, x, y)
    return r.TSpline3(title, graph)

def exclusions(histos = {}, switches = {}, graphBlackLists = None,
        printXs = None, writeDir = None, interBin = "LowEdge", debug = False,
        pruneYMin = False, graphAdditionalPoints=None, upperLimitName = "UpperLimit") :
    graphs = []

    isCLs = upperLimitName=="UpperLimit"
    specs = []
    if switches["xsVariation"]=="default" and isCLs :
        specs += [
            {"name":"ExpectedUpperLimit",          "lineStyle":7, "lineWidth":3, "label":"Expected Limit #pm1 #sigma exp.",
             "color": r.kViolet,                                           "simpleLabel":"Expected Limit"},

            {"name":"ExpectedUpperLimit_-1_Sigma", "lineStyle":2, "lineWidth":2, "label":"",
             "color": r.kViolet,                                           "simpleLabel":"Expected Limit - 1 #sigma"},

            {"name":"ExpectedUpperLimit_+1_Sigma", "lineStyle":2, "lineWidth":2, "label":"",
             "color": r.kViolet,                                           "simpleLabel":"Expected Limit + 1 #sigma"},
            ]

    specs += [
        {"name":upperLimitName,                    "lineStyle":1, "lineWidth":3, "label":"#sigma^{NLO+NLL} #pm1 #sigma theory",
         "color": r.kBlack,                                            "simpleLabel":'Observed Limit ("%s" cross section)'%switches["xsVariation"]},
        ]

    curves = switches["curves"].get(switches["signalModel"])
    if switches["isSms"] :
        specs += [
            {"name":upperLimitName,                  "lineStyle":1, "lineWidth":1, "label":"", "variation":-1.0,
             "color": r.kBlue if debug else r.kBlack,                      "simpleLabel":"Observed Limit - 1 #sigma (theory)"},

            {"name":upperLimitName,                  "lineStyle":1, "lineWidth":1, "label":"", "variation": 1.0,
             "color": r.kYellow if debug else r.kBlack,                    "simpleLabel":"Observed Limit + 1 #sigma (theory)"},
            ]
    elif curves :
        for spec in specs :
            key = (spec["name"], switches["xsVariation"])
            if key in curves :
                spec["curve"] = spline(points = curves[key])

    signalModel = switches["signalModel"]
    for i,spec in enumerate(specs) :
        h = histos[spec["name"]]
        graph = rxs.graph(h = h, model = signalModel, interBin = interBin, printXs = printXs, spec = spec)

        name = spec["name"]+("_%+1d_Sigma"%spec["variation"] if ("variation" in spec and spec["variation"]) else "")
        if name in graphBlackLists :
            lst = graphBlackLists[name][signalModel]
            if pruneYMin :
                lst += pointsAtYMin(graph['graph'])
            pruneGraph(graph['graph'], lst = lst, debug = False, breakLink=pruneYMin)
        if name in graphAdditionalPoints :
            lst = graphAdditionalPoints[name][signalModel]
            insertPoints(graph['graph'], lst = lst)
        graphs.append(graph)

    if writeDir :
        writeDir.cd()
        for dct in graphs :
            dct["graph"].Write()#dct["graph"].GetName()+str(dct.get("variation","")))
        writeDir.Close()
    return graphs

def xsUpperLimitHistograms(fileName = "", switches = {}, ranges = {}, shiftX = False, shiftY = False, upperLimitName = "UpperLimit") :
    assert len(switches["CL"])==1
    cl = switches["CL"][0]
    model = switches["signalModel"]

    f = r.TFile(fileName)
    histos = {}

    for name,pretty in [(upperLimitName, "upper limit"),
                        ("ExpectedUpperLimit", "expected upper limit"),
                        ("ExpectedUpperLimit_-1_Sigma", "title"),
                        ("ExpectedUpperLimit_+1_Sigma", "title")] :
        h3 = f.Get(name)
        if not h3 : continue
        h = shifted(threeToTwo(h3), shift = (shiftX, shiftY))
        modifyHisto(h, switches)
        title = hs.histoTitle(model = model)
        title += ";%g%% C.L. %s on #sigma (pb)"%(100.0*cl, pretty)
        adjustHisto(h, title = title)
        setRange("xRange", ranges, h, "X")
        setRange("yRange", ranges, h, "Y")
        if ranges["xDivisions"] : h.GetXaxis().SetNdivisions(*ranges["xDivisions"])
        if ranges["yDivisions"] : h.GetYaxis().SetNdivisions(*ranges["yDivisions"])
        histos[name] = h

    f.Close()
    return histos

def makeSimpleExclPdf(graphs = [], outFileEps = "", drawGraphs = True) :
    c = squareCanvas(name = "canvas_simpleExcl")
    pdf = outFileEps.replace(".eps","_simpleExcl.pdf")
    root = pdf.replace(".pdf",".root")
    tfile = r.TFile(root, "RECREATE")
    c.Print(pdf+"[")
    for d in graphs :
        d["histo"].Draw("colz")
        d["histo"].SetMaximum(1.0)
        d["histo"].SetMinimum(-1.0)
        d["histo"].SetTitle(d.get("simpleLabel"))
        d["histo"].Write()
        if drawGraphs : d["graph"].Draw("psame")
        if d.get("curve") and d["curve"].GetNp() :
            d["curve"].SetMarkerStyle(20)
            d["curve"].SetMarkerSize(0.3*d["curve"].GetMarkerSize())
            d["curve"].Draw("lpsame")
        c.Print(pdf)
    c.Print(pdf+"]")
    tfile.Close()
    print "INFO: %s has been written."%pdf
    print "INFO: %s has been written."%root

def makeXsUpperLimitPlots(logZ = False, exclusionCurves = True, mDeltaFuncs = {}, printXs = False, name = "UpperLimit",
                          shiftX = False, shiftY = False, interBin = "LowEdge",
                          pruneYMin = False, debug = False, stampPrelim = True) :

    s = conf.switches()
    ranges = hs.ranges(s["signalModel"])

    inFile = pickling.mergedFile()
    outFileRoot = inFile.replace(".root", "_xsLimit.root")
    outFileEps  = inFile.replace(".root", "_xsLimit.eps")
    histos = xsUpperLimitHistograms(fileName = inFile, switches = s, ranges = ranges, shiftX = shiftX, shiftY = shiftY,
                                    upperLimitName = name)
    #output a root file
    g = r.TFile(outFileRoot, "RECREATE")
    for h in histos.values() :
        h.Write()

    #draw observed limit
    c = squareCanvas()
    histos[name].Draw("colz")
    if logZ :
        c.SetLogz()
        setRange("xsZRangeLog", ranges, histos[name], "Z")
        outFileEps = outFileEps.replace(".eps", "_logZ.eps")
    else :
        setRange("xsZRangeLin", ranges, histos[name], "Z")


    #make exclusion histograms and curves
    try:
        graphs = exclusions(histos = histos, writeDir = g, switches = s,
                graphBlackLists = s["graphBlackLists"], interBin = interBin,
                printXs = printXs, pruneYMin = pruneYMin, debug = debug,
                graphAdditionalPoints = s["graphAdditionalPoints"], upperLimitName = name)
    except:
        print "ERROR: creation of exclusions has failed."
        sys.excepthook(*sys.exc_info())
        graphs = []

    #draw exclusion curves
    if exclusionCurves :
        outFileEps = outFileEps.replace(".eps", "_refXs.eps")
        stuff = rxs.drawGraphs(graphs)

    if graphs :
        makeSimpleExclPdf(graphs = graphs, outFileEps = outFileEps, drawGraphs = exclusionCurves)

    #draw curves of iso-mDelta
    if mDeltaFuncs :
        outFileEps = outFileEps.replace(".eps", "_mDelta.eps")
        funcs = rxs.mDeltaFuncs(**mDeltaFuncs)
        for func in funcs :
            func.Draw("same")

    #stamp plot
    stamp_text = conf.likelihoodSpec().legendTitle()

    #s2 = stamp(text = "#alpha_{T}", x = 0.2075, y = 0.55, factor = 1.3)
    textMap = {"profileLikelihood":"PL", "CLs":"CL_{s}"}
    s3 = stamp(text = stamp_text, x = 0.2075, y = 0.64, factor = 0.65)
    if stampPrelim:
        s4 = stamp(text = "Preliminary", x = 0.2075, y = 0.595, factor = 0.7)

    printOnce(c, outFileEps)
    printHoles(histos[name])

def efficiencyHistos(key = "") :
    out = {}
    for cat,dct in pickling.effHistos().iteritems() :
        total = None
        for histo in dct[key] :
            if not total :
                total = histo.Clone("%s_%s"%(cat,key))
            else :
                total.Add(histo)
        out[cat] = total
    return out

def makeEfficiencyPlotBinned(key = "effHad") :
    def prep(p) :
        p.SetTopMargin(0.15)
        p.SetBottomMargin(0.15)
        p.SetLeftMargin(0.15)
        p.SetRightMargin(0.15)

    can = r.TCanvas("canvas", "canvas", 400, 1000)
    can.Divide(2, 5)
    dct = efficiencyHistos(key = key)
    maximum = max([h.GetMaximum() for h in dct.values()])
    keep = []
    pad = {0:2, 1:1, 2:4, 3:3, 4:6, 5:5, 6:8, 7:7, 8:10}

    model = conf.switches()["signalModel"]
    label = "%s_%s"%(model, key)
    total = None
    for i,(cat,h) in enumerate(sorted(dct.iteritems())) :
        can.cd(pad[i])
        prep(r.gPad)

        h2 = threeToTwo(h)
        keep.append(h2)
        h2.SetTitle(cat)
        h2.SetStats(False)
        h2.SetMinimum(0.0)
        h2.SetMaximum(maximum)
        h2.Draw("colz")

        if not total :
            total = h2.Clone(label)
        else :
            total.Add(h2)
        #h2.GetListOfFunctions().FindObject("palette").GetAxis().SetTitle("")

    can.cd(9)
    prep(r.gPad)

    total.Draw("colz")
    total.SetTitle("%s#semicolon max = %4.2f"%(label, total.GetMaximum()))

    can.cd(0)
    can.Print("%s.pdf"%label)

def makeEfficiencyPlot() :
    s = conf.switches()
    if not s["isSms"] : return

    inFile = pickling.mergedFile()
    f = r.TFile(inFile)
    fileName = inFile.replace(".root","_efficiency.eps")

    c = squareCanvas()

    h3 = None
    for item in f.GetListOfKeys() :
        h = f.Get(item.GetName())
        if "effHadSum" not in h.GetName() : continue

        if not h3 :
            h3 = h.Clone("eff")
            h3.SetDirectory(0)
        else :
            h3.Add(h)
    f.Close()

    h2 = threeToTwo(h3)

    assert h2
    modifyHisto(h2, s)

    title = hs.histoTitle(model = s["signalModel"])
    title += ";A #times #epsilon"
    adjustHisto(h2, title = title)

    #output a root file
    g = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
    h2.Write()
    g.Close()

    ranges = hs.ranges(s["signalModel"])
    setRange("xRange", ranges, h2, "X")
    setRange("yRange", ranges, h2, "Y")

    h2.Draw("colz")

    printName = fileName
    setRange("effZRange", ranges, h2, "Z")

    s2 = stamp(text = "#alpha_{T}", x = 0.22, y = 0.55, factor = 1.3)

    printOnce(c, printName)
    printHoles(h2)

def makeEfficiencyUncertaintyPlots() :
    s = conf.switches()
    if not s["isSms"] : return

    inFile = pickling.mergedFile()
    f = r.TFile(inFile)
    ranges = hs.ranges(s["signalModel"])

    def go(name, suffix, zTitle, zRangeKey) :
        fileName = "%s/%s_%s.eps"%(conf.stringsNoArgs()["outputDir"], s["signalModel"], suffix)
        c = squareCanvas()
        h2 = threeToTwo(f.Get(name))
        xyTitle = hs.histoTitle(model = s["signalModel"])
        adjustHisto(h2, title = "%s;%s"%(xyTitle, zTitle))
        setRange("xRange", ranges, h2, "X")
        setRange("yRange", ranges, h2, "Y")
        h2.Draw("colz")
        setRange(zRangeKey, ranges, h2, "Z")

        #output a root file
        g = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
        h2.Write()
        g.Close()

        printOnce(c, fileName)

    go(name = "effUncRelExperimental", suffix = "effUncRelExp", zTitle = "#sigma^{exp}_{#epsilon} / #epsilon", zRangeKey = "effUncExpZRange")
    go(name = "effUncRelTheoretical", suffix = "effUncRelTh", zTitle = "#sigma^{theo}_{#epsilon} / #epsilon", zRangeKey = "effUncThZRange")
    go(name = "effUncRelIsr", suffix = "effUncRelIsr", zTitle = "#sigma^{ISR}_{#epsilon} / #epsilon", zRangeKey = "effUncRelIsrZRange")
    go(name = "effUncRelPdf", suffix = "effUncRelPdf", zTitle = "#sigma^{PDF}_{#epsilon} / #epsilon", zRangeKey = "effUncRelPdfZRange")
    go(name = "effUncRelJes", suffix = "effUncRelJes", zTitle = "#sigma^{JES}_{#epsilon} / #epsilon", zRangeKey = "effUncRelJesZRange")
    go(name = "effUncRelMcStats", suffix = "effUncRelMcStats", zTitle = "#sigma^{MC stats}_{#epsilon} / #epsilon", zRangeKey = "effUncRelMcStatsZRange")

def printTimeStamp() :
    #l = conf.likelihood()
    text = r.TText()
    text.SetNDC()
    text.DrawText(0.1, 0.1, "file created at %s"%r.TDatime().AsString())
    text.DrawText(0.1, 0.35, "[restore useful info here]")
    #text.DrawText(0.1, 0.35, "REwk = %s"%(l["REwk"] if l["REwk"] else "[no form assumed]"))
    #text.DrawText(0.1, 0.30, "RQcd = %s"%(l["RQcd"] if l["RQcd"] else "[no form assumed]"))
    #text.DrawText(0.1, 0.25, "nFZinv = %s"%(l["nFZinv"].replace("fZinv","")))
    return text

def printSuppressed(l) :
    text = r.TText()
    text.SetTextSize(0.3*text.GetTextSize())
    text.SetNDC()
    text.DrawText(0.1, 0.9, "empty histograms: %s"%str(l))
    return text

def printLumis() :
    text = r.TText()
    text.SetNDC()
    text.SetTextFont(102)
    text.SetTextSize(0.5*text.GetTextSize())

    x = 0.1
    y = 0.9
    s = 0.035
    text.DrawText(x, y  , "restore useful info here")
    return text

    text.DrawText(x, y  , "sample     lumi (/pb)")
    text.DrawText(x, y-s, "---------------------")
    inputData = conf.data()
    i = 1
    d = inputData.lumi()
    for key in sorted(d.keys()) :
        i += 1
        text.DrawText(x, y-i*s, "%8s       %6.0f"%(key, d[key]))
    text.DrawText(x, y-(i+1)*s, "HT bins: %s"%str(inputData.htBinLowerEdges()))
    return text

def drawBenchmarks() :
    switches = conf.switches()
    parameters =  conf.scanParameters()
    if not switches["drawBenchmarkPoints"] : return
    if not (switches["signalModel"] in parameters) : return
    params = parameters[switches["signalModel"]]

    text = r.TText()
    out = []
    for label,coords in conf.benchmarkPoints().iteritems() :
        drawIt = True
        for key,value in coords.iteritems() :
            if key in params and value!=params[key] : drawIt = False
        if not drawIt : continue
        marker = r.TMarker(coords["m0"], coords["m12"], 20)
        marker.Draw()
        out.append(marker)
        out.append(text.DrawText(10+coords["m0"], 10+coords["m12"], label))
    return out

def printOneHisto(h2 = None, name = "", canvas = None, fileName = "", logZ = [], switches = {}, suppressed = []) :
    if "upper" in name :
        printHoles(h2)
        #printMaxes(h2)
    h2.SetStats(False)
    h2.SetTitle("%s%s"%(name, hs.histoTitle(model = switches["signalModel"])))
    h2.Draw("colz")
    if not h2.Integral() :
        suppressed.append(name)
        return

    canvas.SetLogz(name in logZ)
    if name=="xs" and name in logZ : h2.SetMinimum(1.0e-2)
    if name=="nEventsHad" and name in logZ : h2.SetMinimum(0.9)
    if "NLO_over_LO" in name :
        h2.SetMinimum(0.5)
        h2.SetMaximum(3.0)

    stuff = drawBenchmarks()

    if "excluded" in name and switches["isSms"] : return

    printSinglePage  = (not switches["isSms"]) and "excluded" in name
    printSinglePage |= switches["isSms"] and "upperLimit" in name

    if printSinglePage :
        title = h2.GetTitle()
        h2.SetTitle("")
#        eps = fileName.replace(".ps","_%s.eps"%name)
#        super(utils.numberedCanvas, canvas).Print(eps)
#        utils.epsToPdf(eps)
        pdf_fileName = fileName.replace(".pdf","_%s.pdf"%name)
        super(utils.numberedCanvas, canvas).Print(pdf_fileName)
        h2.SetTitle(title)

    canvas.Print(fileName)
    if "nEventsIn" in name and (switches["minEventsIn"] or switches["maxEventsIn"]):
        if switches["minEventsIn"] : h2.SetMinimum(switches["minEventsIn"])
        if switches["maxEventsIn"] : h2.SetMaximum(switches["maxEventsIn"])
        canvas.Print(fileName)

    #effMu/effHad
    if switches["effRatioPlots"] :
        for name in names :
            num = threeToTwo(f.Get(name))
            if name[:7]!="effmuon" : continue
            denName = name.replace("muon", "had")
            den = threeToTwo(f.Get(denName))
            num.Divide(den)
            num.SetStats(False)
            num.SetTitle("%s/%s%s;"%(name, denName, hs.histoTitle(model = switches["signalModel"])))
            num.Draw("colz")
            if not num.Integral() : continue
            num.SetMinimum(0.0)
            num.SetMaximum(0.5)
            stuff = drawBenchmarks()
            canvas.Print(fileName)

def sortedNames(histos = [], first = [], last = []) :
    start = []
    end = []
    names = sorted([histo.GetName() for histo in histos])
    for name in names :
        for item in first :
	        if item==name[:len(item)] :
	            start.append(name)
        for item in last :
	        if item==name[:len(item)] :
	            end.append(name)

    for item in list(set(start+end)) :
        names.remove(item)
    return start+names+end

def multiPlots(tag = "", first = [], last = [], whiteListMatch = [], blackListMatch = [], outputRootFile = False, modify = False, square = False) :
    assert tag

    inFile = pickling.mergedFile()
    f = r.TFile(inFile)
    r.gROOT.cd()

    fileName = inFile.replace(".root","_%s.pdf"%tag)
    rootFileName = fileName.replace(".pdf", ".root")

    if square :
        canvas = squareCanvas(numbered = True)
    else :
        canvas = utils.numberedCanvas()
        canvas.SetRightMargin(0.15)

    canvas.Print(fileName+"[")
    canvas.SetTickx()
    canvas.SetTicky()

    text1 = printTimeStamp()
    text2 = printLumis()
    canvas.Print(fileName)
    canvas.Clear()

    names = sortedNames(histos = f.GetListOfKeys(), first = first, last = last)

    s = conf.switches()

    if outputRootFile :
        outFile = r.TFile(rootFileName, "RECREATE")
        r.gROOT.cd()

    suppressed = []
    for name in names :
        if whiteListMatch and not any([item in name for item in whiteListMatch]) : continue
        if any([item in name for item in blackListMatch]) : continue

        h2 = threeToTwo(f.Get(name))
        if modify : modifyHisto(h2, s)
        printOneHisto(h2 = h2, name = name, canvas = canvas, fileName = fileName,
                      logZ = ["xs", "nEventsHad"], switches = s, suppressed = suppressed)
        if outputRootFile :
            outFile.cd()
            h2.Write()
            r.gROOT.cd()

    if outputRootFile :
        print "%s has been written."%rootFileName
        outFile.Close()

    canvas.Clear()
    text3 = printSuppressed(suppressed)
    canvas.Print(fileName)

    canvas.Print(fileName+"]")

    print "%s has been written."%fileName

def clsValidation(cl = None, tag = "", masterKey = "", yMin = 0.0, yMax = 1.0, lineHeight = 0.5, divide = (4,3), whiteList = [], stampTitle = True) :
    def allHistos(fileName = "") :
        f = r.TFile(fileName)
        r.gROOT.cd()
        out = {}
        for key in f.GetListOfKeys() :
            name = key.GetName()
            out[name] = threeToTwo(f.Get(name))
            out[name].SetDirectory(0)
        f.Close()
        return out

    assert tag
    assert masterKey
    assert cl
    if whiteList :
        assert len(whiteList)==divide[0]*divide[1], "%d != %d"%(len(whiteList), divide[0]*divide[1])

    histos = allHistos(fileName = pickling.mergedFile())
    master = histos[masterKey]
    graphs = {}
    for iBinX in range(1, 1 + master.GetNbinsX()) :
        for iBinY in range(1, 1 + master.GetNbinsY()) :
            if whiteList and (iBinX, iBinY) not in whiteList : continue
            if not master.GetBinContent(iBinX, iBinY) : continue
            if "CLb_2" not in histos or not histos["CLb_2"] : continue
            if not histos["CLb_2"].GetBinContent(iBinX, iBinY) : continue

            name = "CLs_%d_%d"%(iBinX, iBinY)
            graph = r.TGraphErrors()
            graph.SetName(name)
            graph.SetTitle("%s;#sigma (pb);CL_{s}"%(name.replace("CLs_","") if stampTitle else ""))
            graph.SetMarkerStyle(20)
            graph.SetMinimum(yMin)
            graph.SetMaximum(yMax)
            iPoint = 0
            while True :
                s = "" if not iPoint else "_%d"%iPoint
                if "CLs%s"%s not in histos : break
                x = histos["PoiValue%s"%s].GetBinContent(iBinX, iBinY)
                if not iPoint : xMin = x
                xMax = x
                graph.SetPoint(iPoint, x, histos["CLs%s"%s].GetBinContent(iBinX, iBinY))
                graph.SetPointError(iPoint, 0.0, histos["CLsError%s"%s].GetBinContent(iBinX, iBinY))
                iPoint += 1

            e = 0.1*(xMax-xMin)
            y = 1.0 - cl
            clLine = r.TLine(xMin-e, y, xMax+e, y)
            clLine.SetLineColor(r.kRed)

            xLim = histos["UpperLimit"].GetBinContent(iBinX, iBinY)
            limLine = r.TLine(xLim, yMin, xLim, yMax*lineHeight)
            limLine.SetLineColor(r.kBlue)
            graphs[name] = [graph, clLine, limLine]

            if not whiteList :
                xLimPl = histos["PlUpperLimit"].GetBinContent(iBinX, iBinY)
                plLimLine = r.TLine(xLimPl, yMin, xLimPl, yMax*lineHeight)
                plLimLine.SetLineColor(r.kGreen)
                graphs[name].append(plLimLine)

    fileName = pickling.mergedFile().replace(".root","_%s_%s.pdf"%(tag, str(cl).replace("0.","")))
    if whiteList :
        fileName = fileName.replace(".pdf", ".eps")
        canvas = r.TCanvas("canvas", "", 500*divide[0], 500*divide[1])
    else :
        canvas = utils.numberedCanvas()
        canvas.Print(fileName+"[")
        text1 = printTimeStamp()
        text2 = printLumis()
        canvas.Print(fileName)
        canvas.Clear()

    canvas.SetRightMargin(0.15)
    utils.cyclePlot(d = graphs, f = None, args = {}, optStat = 1110, canvas = canvas, fileName = fileName, divide = divide, goptions = "alp")

    if whiteList :
        utils.epsToPdf(fileName, sameDir = True)
        print "%s has been written."%fileName.replace(".eps", ".pdf")
    else :
        canvas.Print(fileName+"]")
        print "%s has been written."%fileName

def makePlots(square = False) :
    multiPlots(tag = "validation", first = ["excluded", "upperLimit", "CLs", "CLb", "xs"], last = ["lowerLimit"], square = square)
    #multiPlots(tag = "nEvents", whiteListMatch = ["nEvents"], square = square)
    #multiPlots(tag = "effHad", whiteListMatch = ["effHad"], blackListMatch = ["UncRel"], outputRootFile = True, modify = True, square = square)
    #multiPlots(tag = "effMu", whiteListMatch = ["effMu"], blackListMatch = ["UncRel"], outputRootFile = True, modify = True, square = square)
    #multiPlots(tag = "xs", whiteListMatch = ["xs"], outputRootFile = True, modify = True, square = square)

    s = conf.switches()
    if s["isSms"] and s["method"]=="CLs" :
        for cl in s["CL"] :
            clsValidation(tag = "clsValidation", cl = cl, masterKey = "xs")

def expectedLimit(obsFile, expFile) :
    def histo(file, name) :
        f = r.TFile(file)
        out = f.Get(name).Clone(name+"2")
        out.SetDirectory(0)
        out.SetName(name)
        f.Close()
        return out

    def check(h1, h2) :
        def a(h, x) :
            return getattr(h, "Get%saxis"%x)
        for x in ["X", "Y"] :
            for attr in ["GetXmin", "GetXmax", "GetNbins"] :
                assert getattr(a(h1, x)(), attr)()==getattr(a(h2, x)(), attr)()

    def compare(h1, h2) :
        check(h1, h2)
        out = h2.Clone(h1.GetName()+h2.GetName())
        out.SetTitle(h2.GetName())
        out.Reset()
        for iX in range(1, 1+h1.GetNbinsX()) :
            for iY in range(1, 1+h1.GetNbinsY()) :
                c1 = h1.GetBinContent(iX, iY)
                c2 = h2.GetBinContent(iX, iY)
                if (not c1) or (not c2) :
                    out.SetBinContent(iX, iY, 0.0)
                else :
                    out.SetBinContent(iX, iY, 2.0*(c1<c2)-1.0)
        return out

    def items() :
        keys = conf.switches()["expectedPlusMinus"].keys()
        out = ["Median"]
        for key in keys :
            out += ["MedianPlus%s"%key, "MedianMinus%s"%key]
        return out

    psFileName = expFile.replace(".root", "_results.ps")
    rootFileName = psFileName.replace(".ps", ".root")
    outFile = r.TFile(rootFileName, "RECREATE")
    canvas = r.TCanvas()
    canvas.SetRightMargin(0.15)
    canvas.Print(psFileName+"[")
    ds = histo(obsFile, "ds")
    for item in items() :
        h = compare(ds, histo(expFile, item))
        outFile.cd()
        h.Write()
        h.Draw("colz")
        h.SetStats(False)
        canvas.Print(psFileName)

    outFile.Close()
    canvas.Print(psFileName+"]")
    pdfFileName = psFileName.replace(".ps", ".pdf")
    os.system("ps2pdf %s %s"%(psFileName, pdfFileName))
    os.remove(psFileName)
    print "%s has been written."%pdfFileName
    print "%s has been written."%rootFileName
