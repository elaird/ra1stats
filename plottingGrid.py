import os
import sys
import math

import histogramProcessing as hp
import configuration as conf
import likelihoodSpec
import patches
import pickling
import refXsProcessing as rxs
import utils

import ROOT as r

sa = conf.signal  # compatibility

def setupRoot() :
    #r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)
    #r.gStyle.SetPadTickX(True)
    #r.gStyle.SetPadTickY(True)

setupRoot()

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
    h.GetYaxis().SetTitleOffset(1.6)
    h.GetZaxis().SetTitleOffset(1.5)

def printOnce(canvas, fileName, alsoC = False) :
    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(22)
    #text.DrawText(0.5, 0.85, "CMS")

    if True :
        latex = r.TLatex()
        latex.SetNDC()
        latex.SetTextAlign(22)
        current_stamp = sa.processStamp(conf.switches()['signalModel'])

        latex.SetTextSize(0.6*latex.GetTextSize())
        if current_stamp:
            latex.DrawLatex(current_stamp['xpos'], 0.78, current_stamp['text'])

    canvas.Print(fileName)
    utils.epsToPdf(fileName)
    if alsoC :
        canvas.Print(fileName.replace(".eps",".C"))

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

def pruneGraph(graph, lst = [], debug = False, breakLink = False) :
    if debug: graph.Print()
    nRemoved = 0
    for p in lst:
        x = graph.GetX()
        y = graph.GetY()
        bad = []
        for i in range(graph.GetN()):
            if abs(p[0]-x[i]) < 1.0e-6 and abs(p[1]-y[i]) < 1.0e-6:
                bad.append(i-len(bad))
        nRemoved += len(bad)
        for i in bad:
            if debug :
                print "WARN: Removing point %d = (%g,%g) from %s"%(i, x[i], y[i], graph.GetName())
            graph.RemovePoint(i)
    if breakLink:
        graph.RemovePoint(graph.GetN()-1)
    if debug: graph.Print()
    if nRemoved :
        print "WARN: Removing %d points from graph %s"%(nRemoved, graph.GetName())

def modifyGraph(graph, dct = {}, debug = True) :
    if debug: graph.Print()
    for old,new in dct.iteritems() :
        x = graph.GetX()
        y = graph.GetY()
        for i in range(graph.GetN()):
            if abs(old[0]-x[i]) < 1.0e-6 and abs(old[1]-y[i]) < 1.0e-6:
                graph.SetPoint(i,new[0],new[1])
                print "WARN: Replacing point %d: (%g,%g) --> (%g,%g) from graph %s" % (i, old[0], old[1], new[0], new[1], graph.GetName())
    if debug: graph.Print()

def insertPoints( graph, lst=[], mode="prepend" ) :
    if not lst : return
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

def exclusionGraphs(histos={}, interBin="", pruneYMin=False, debug=False, printXs=None):
    switches = conf.switches()
    model = switches["signalModel"]
    cutFunc = patches.cutFunc()[model]
    curves = patches.curves()[model]

    graphReplacePoints = patches.graphReplacePoints()
    graphAdditionalPoints = patches.graphAdditionalPoints()

    graphs = {}
    simpleExclHistos = {}
    for histoName,xsVariation in [("ExpectedUpperLimit_m1_Sigma", 0.0),
                                  ("ExpectedUpperLimit_p1_Sigma", 0.0),
                                  ("ExpectedUpperLimit",          0.0),
                                  ("UpperLimit",                  0.0),
                                  ("UpperLimit",                 -1.0),
                                  ("UpperLimit",                  1.0),
                                  ] :
        graphName = histoName
        if xsVariation==1.0 :
            graphName += "_p1_Sigma"
        if xsVariation==-1.0 :
            graphName += "_m1_Sigma"
        graphName += "_graph"

        if curves :
            assert False,"fix me"
            key = (spec["name"], switches["xsVariation"])
            if key in curves :
                spec["curve"] = spline(points = curves[key])

        graph = rxs.graph(h = histos[histoName], model = model, interBin = interBin,
                          printXs = printXs, spec = {"variation":xsVariation})
        graph["graph"].SetName(graphName)
        graph["histo"].SetName(graphName.replace("_graph","_simpleExcl"))
        key = graphName.replace("m1","-1").replace("p1","+1").replace("_graph","")
        pruneGraph(graph['graph'], debug = False, breakLink = pruneYMin,
                   lst = patches.graphBlackLists()[key][model]+(pointsAtYMin(graph['graph']) if pruneYMin else []))
        modifyGraph(graph['graph'], dct = patches.graphReplacePoints()[key][model], debug = False)
        insertPoints(graph['graph'], lst = patches.graphAdditionalPoints()[key][model])
        graphs[graphName] = graph["graph"]
        simpleExclHistos[graphName] = graph["histo"]
    return graphs,simpleExclHistos

def upperLimitHistos(inFileName = "", shiftX = False, shiftY = False) :
    switches = conf.switches()
    assert len(switches["CL"])==1
    cl = switches["CL"][0]
    model = switches["signalModel"]
    ranges = sa.ranges(model)

    #read and adjust histos
    f = r.TFile(inFileName)
    histos = {}
    for name,pretty in [("UpperLimit" if switches["method"]=="CLs" else "upperLimit95", "upper limit"),
                        ("ExpectedUpperLimit", "expected upper limit"),
                        ("ExpectedUpperLimit_-1_Sigma", "title"),
                        ("ExpectedUpperLimit_+1_Sigma", "title")] :
        h3 = f.Get(name)
        if not h3 : continue
        h = utils.shifted(utils.threeToTwo(h3), shift = (shiftX, shiftY))
        hp.modifyHisto(h, model)
        title = sa.histoTitle(model = model)
        title += ";%g%% CL %s on  #sigma (pb)"%(100.0*cl, pretty)
        adjustHisto(h, title = title)
        setRange("xRange", ranges, h, "X")
        setRange("yRange", ranges, h, "Y")
        if ranges["xDivisions"] : h.GetXaxis().SetNdivisions(*ranges["xDivisions"])
        if ranges["yDivisions"] : h.GetYaxis().SetNdivisions(*ranges["yDivisions"])
        rename(h)
        hp.printHoles(h)
        histos[h.GetName()] = h
    f.Close()
    return histos

def rename(h) :
    name = h.GetName()
    for old,new in [("+","p"), ("-","m"), ("upper", "Upper"), ("95",""),
                    ("_shifted",""), ("_2D","")] :
        name = name.replace(old,new)
    h.SetName(name)

def writeList(fileName = "", objects = []) :
    f = r.TFile(fileName, "RECREATE")
    for obj in objects :
        obj.Write()
    f.Close()

def outFileName(tag = "") :
    base = pickling.mergedFile().split("/")[-1]
    root = conf.directories()["plot"]+"/"+base.replace(".root", "_%s.root"%tag)
    return {"root":root,
            "eps" :root.replace(".root",".eps"),
            "pdf" :root.replace(".root",".pdf"),
            }

def makeRootFiles(limitFileName="", simpleFileName="", shiftX=None, shiftY=None,
                  interBin="", pruneYMin=None, printXs=None):
    for item in ["shiftX", "shiftY", "interBin", "pruneYMin"] :
        assert eval(item)!=None,item
    histos = upperLimitHistos(inFileName=pickling.mergedFile(), shiftX=shiftX, shiftY=shiftY)
    graphs, simple = exclusionGraphs(histos, interBin=interBin, pruneYMin=pruneYMin, printXs=printXs)
    writeList(fileName = limitFileName, objects = histos.values()+graphs.values())
    writeList(fileName = simpleFileName, objects = simple.values())

def makeXsUpperLimitPlots(logZ=False, curveGopts="", mDeltaFuncs={},
                          diagonalLine=False, printXs=False, pruneYMin=False,
                          debug=False):

    limitFileName = outFileName(tag = "xsLimit")["root"]
    simpleFileName = outFileName(tag = "xsLimit_simpleExcl")["root"]

    shift = sa.interBin(model=conf.switches()["signalModel"])=="LowEdge"
    makeRootFiles(limitFileName=limitFileName, simpleFileName=simpleFileName,
                  shiftX=shift, shiftY=shift, interBin="Center",
                  pruneYMin=pruneYMin, printXs=printXs)

    specs = [{"name":"ExpectedUpperLimit_m1_Sigma", "label":"",
               "lineStyle":2, "lineWidth":2, "color":r.kViolet},
              {"name":"ExpectedUpperLimit_p1_Sigma", "label":"",
               "lineStyle":2, "lineWidth":2, "color":r.kViolet},
              {"name":"ExpectedUpperLimit",          "label":"Expected Limit #pm1 #sigma exp.",
               "lineStyle":7, "lineWidth":3, "color":r.kViolet},
              {"name":"UpperLimit",                  "label":"#sigma^{NLO+NLL} #pm1 #sigma theory",
               "lineStyle":1, "lineWidth":3, "color":r.kBlack},
              {"name":"UpperLimit_m1_Sigma",         "label":"",
               "lineStyle":1, "lineWidth":1, "color":r.kBlack},
              {"name":"UpperLimit_p1_Sigma",         "label":"",
               "lineStyle":1, "lineWidth":1, "color":r.kBlack},
              ]

    makeLimitPdf(rootFileName = limitFileName, specs = specs, diagonalLine = diagonalLine,
                 logZ = logZ, curveGopts = curveGopts, mDeltaFuncs = mDeltaFuncs)
    makeSimpleExclPdf(histoFileName = simpleFileName, graphFileName = limitFileName, specs = specs,
                      curveGopts = curveGopts)

def makeLimitPdf(rootFileName = "", diagonalLine = False, logZ = False,
                 curveGopts = "", mDeltaFuncs = False, specs = []) :

    s = conf.switches()
    model = s["signalModel"]
    ranges = sa.ranges(model)

    epsFile = rootFileName.replace(".root", ".eps")
    f = r.TFile(rootFileName)

    c = squareCanvas()

    if s["method"]=="CLs":
        hName = "excluded_CLs_95" if s["binaryExclusionRatherThanUpperLimit"] else "UpperLimit"
    else:
        hName = "upperLimit95"
    h = f.Get(hName)
    h.Draw("colz")

    if logZ :
        c.SetLogz()
        setRange("xsZRangeLog", ranges, h, "Z")
    else :
        setRange("xsZRangeLin", ranges, h, "Z")
        epsFile = epsFile.replace(".eps", "_linZ.eps")

    graphs = []
    for d in specs :
        graph = f.Get(d["name"]+"_graph")
        if not graph : continue
        graph.SetLineColor(d["color"])
        graph.SetLineWidth(d["lineWidth"])
        graph.SetLineStyle(d["lineStyle"])
        graphs.append({"graph":graph, "label":d["label"]})

    if curveGopts :
        stuff = rxs.drawGraphs(graphs, gopts = curveGopts)
    else :
        epsFile = epsFile.replace(".eps", "_noRef.eps")

    if diagonalLine :
        yx = r.TF1("yx", "x", ranges["xRange"][0], ranges["xMaxDiag"])
        yx.SetLineColor(1)
        yx.SetLineStyle(3)
        yx.SetLineWidth(2)
        yx.Draw("same")

    if mDeltaFuncs :
        epsFile = epsFile.replace(".eps", "_mDelta.eps")
        funcs = rxs.mDeltaFuncs(**mDeltaFuncs)
        for func in funcs :
            func.Draw("same")

    s3 = stamp(text = likelihoodSpec.likelihoodSpec(model).legendTitle(), x = 0.2075, y = 0.64, factor = 0.65)
    printOnce(c, epsFile, alsoC = True)
    f.Close()

def makeSimpleExclPdf(histoFileName = "", graphFileName = "", specs = [], curveGopts = "") :
    ranges = sa.ranges(conf.switches()["signalModel"])

    c = squareCanvas()
    pdf = histoFileName.replace(".root",".pdf")

    hFile = r.TFile(histoFileName)
    gFile = r.TFile(graphFileName)

    c.Print(pdf+"[")
    for d in specs :
        foo = {'color': 880, 'lineWidth': 2, 'lineStyle': 2, 'name': 'ExpectedUpperLimit_m1_Sigma', 'label': ''}
        h = hFile.Get(d["name"]+"_simpleExcl")
        if not h : continue
        h.Draw("colz")
        h.SetMinimum(-1.0)
        h.SetMaximum(1.0)
        h.SetTitle(d["name"])
        r.gPad.SetGridx()
        r.gPad.SetGridy()

        g = gFile.Get(d["name"]+"_graph")
        if g and curveGopts :
            g.SetMarkerColor(r.kBlack)
            g.SetMarkerStyle(20)
            g.SetMarkerSize(0.3*g.GetMarkerSize())
            g.SetLineColor(r.kYellow)
            g.SetLineStyle(1)
            g.Draw("%spsame"%curveGopts)
        if d.get("curve") and d["curve"].GetNp() :
            d["curve"].SetMarkerStyle(20)
            d["curve"].SetMarkerSize(0.3*d["curve"].GetMarkerSize())
            d["curve"].Draw("lpsame")
        c.Print(pdf)

    c.Print(pdf+"]")
    print "INFO: %s has been written."%pdf
    hFile.Close()
    gFile.Close()

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

        h2 = utils.threeToTwo(h)
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

    h2 = utils.threeToTwo(h3)

    assert h2
    hp.modifyHisto(h2, s["signalModel"])

    title = sa.histoTitle(model = s["signalModel"])
    title += ";A #times #epsilon"
    adjustHisto(h2, title = title)

    #output a root file
    g = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
    h2.Write()
    g.Close()

    ranges = sa.ranges(s["signalModel"])
    setRange("xRange", ranges, h2, "X")
    setRange("yRange", ranges, h2, "Y")

    h2.Draw("colz")

    printName = fileName
    setRange("effZRange", ranges, h2, "Z")

    s2 = stamp(text = "#alpha_{T}", x = 0.22, y = 0.55, factor = 1.3)

    printOnce(c, printName)
    hp.printHoles(h2)

def makeEfficiencyUncertaintyPlots() :
    s = conf.switches()
    if not s["isSms"] : return

    inFile = pickling.mergedFile()
    f = r.TFile(inFile)
    ranges = sa.ranges(s["signalModel"])

    def go(name, suffix, zTitle, zRangeKey) :
        fileName = outFileName(tag = "%s_%s"%(s["signalModel"], suffix))["eps"]
        c = squareCanvas()
        h2 = utils.threeToTwo(f.Get(name))
        xyTitle = sa.histoTitle(model = s["signalModel"])
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
    parameters =  sa.scanParameters()
    if not (switches["signalModel"] in parameters) : return
    params = parameters[switches["signalModel"]]

    text = r.TText()
    out = []
    for label,coords in sa.benchmarkPoints().iteritems() :
        drawIt = True
        for key,value in coords.iteritems() :
            if key in params and value!=params[key] : drawIt = False
        if not drawIt : continue
        marker = r.TMarker(coords["m0"], coords["m12"], 20)
        marker.Draw()
        out.append(marker)
        out.append(text.DrawText(10+coords["m0"], 10+coords["m12"], label))
    return out

def printOneHisto(h2=None, name="", canvas=None, fileName="",
                  effRatioPlots=False, drawBenchmarkPoints=False,
                  logZ=[], switches={}, suppressed=[]):
    model = switches["signalModel"]
    if "upper" in name :
        hp.printHoles(h2)
    h2.SetStats(False)
    h2.SetTitle("%s%s"%(name, sa.histoTitle(model = model)))
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

    if drawBenchmarkPoints:
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
    minEventsIn, maxEventsIn = sa.nEventsIn(model)
    if "nEventsIn" in name and (minEventsIn or maxEventsIn):
        if minEventsIn : h2.SetMinimum(minEventsIn)
        if maxEventsIn : h2.SetMaximum(maxEventsIn)
        canvas.Print(fileName)

    #effMu/effHad
    if effRatioPlots:
        for name in names :
            num = utils.threeToTwo(f.Get(name))
            if name[:7]!="effmuon" : continue
            denName = name.replace("muon", "had")
            den = utils.threeToTwo(f.Get(denName))
            num.Divide(den)
            num.SetStats(False)
            num.SetTitle("%s/%s%s;"%(name, denName, sa.histoTitle(model = model)))
            num.Draw("colz")
            if not num.Integral() : continue
            num.SetMinimum(0.0)
            num.SetMaximum(0.5)
            if drawBenchmarkPoints:
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

def multiPlots(tag="", first=[], last=[], whiteListMatch=[], blackListMatch=[],
               outputRootFile=False, modify=False, square=False):
    assert tag

    inFile = pickling.mergedFile()
    f = r.TFile(inFile)
    r.gROOT.cd()

    fileNames = outFileName(tag = tag)
    fileName = fileNames["pdf"]

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
        outFile = r.TFile(fileNames["root"], "RECREATE")
        r.gROOT.cd()

    suppressed = []
    for name in names :
        if whiteListMatch and not any([item in name for item in whiteListMatch]) : continue
        if any([item in name for item in blackListMatch]) : continue

        h2 = utils.threeToTwo(f.Get(name))
        if modify : hp.modifyHisto(h2, s["signalModel"])
        printOneHisto(h2=h2, name=name, canvas=canvas, fileName=fileName,
                      logZ=["xs", "nEventsHad"], switches=s,
                      suppressed=suppressed)
        if outputRootFile :
            outFile.cd()
            h2.Write()
            r.gROOT.cd()

    if outputRootFile :
        print "%s has been written."%fileNames["root"]
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
            out[name] = utils.threeToTwo(f.Get(name))
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

    fileName = outFileName(tag = tag+"_"+str(cl).replace("0.",""))["pdf"]
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
    multiPlots(tag = "validation", first = ["excluded", "upperLimit", "CLs", "CLb", "xs"], last = ["lowerLimit"],
               blackListMatch = ["eff", "_nEvents"], square = square)
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
