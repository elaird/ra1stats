import configuration.directories
import configuration.limit
import configuration.signal
import histogramProcessing as hp
import likelihood
import patches
import refXsProcessing as rxs
import utils

import ROOT as r


def setupRoot():
    #r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)
    #r.gStyle.SetPadTickX(True)
    #r.gStyle.SetPadTickY(True)

setupRoot()


def squareCanvas(margin=0.18, ticks=True, name="canvas", numbered=False):
    canvas = (utils.numberedCanvas if numbered else r.TCanvas)(name, name, 2)
    for side in ["Left", "Right", "Top", "Bottom"]:
        getattr(canvas, "Set%sMargin" % side)(margin)
    canvas.SetTickx(ticks)
    canvas.SetTicky(ticks)
    return canvas


def adjustHisto(h, title=""):
    h.SetStats(False)
    h.SetTitle(title)
    h.GetYaxis().SetTitleOffset(1.6)
    h.GetZaxis().SetTitleOffset(1.5)


def printOnce(model=None, canvas=None, fileName="", alsoC=False, factor=0.6, align=22):
    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(align)

    if model:
        latex = r.TLatex()
        latex.SetNDC()
        latex.SetTextAlign(align)
        stamp = configuration.signal.processStamp(model.name)
        latex.SetTextSize(factor*latex.GetTextSize())
        if stamp:
            latex.DrawLatex(stamp['xpos'], stamp['ypos'], stamp['text'])

    canvas.Print(fileName)
    utils.epsToPdf(fileName)
    if alsoC:
        canvas.Print(fileName.replace(".eps", ".C"))


def stamp(text="#alpha_{T}, P.L., 1.1 fb^{-1}", x=0.25, y=0.55, factor=1.3):
    latex = r.TLatex()
    latex.SetTextSize(factor*latex.GetTextSize())
    latex.SetNDC()
    latex.DrawLatex(x, y, text)
    return latex


def pointsAtYMin(graph):
    out = []
    x = graph.GetX()
    y = graph.GetY()
    if not graph.GetN():
        return out
    yMin = min([y[i] for i in range(graph.GetN())])
    xsAtYMin = []
    for i in range(graph.GetN()):
        if y[i] == yMin:
            out.append((x[i], y[i]))
    if len(out):
        xMax = max([coords[0] for coords in out])
        xMin = min([coords[0] for coords in out])
        while (xMax, yMin) in out:
            out.remove((xMax, yMin))
        while (xMin, yMin) in out:
            out.remove((xMin, yMin))
    return out


def pruneGraph(graph, lst=[], debug=False, breakLink=False, info=None):
    if debug:
        graph.Print()
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
            if debug:
                print "DEBUG: Removing point %d = (%g,%g) from %s" % (i, x[i], y[i], graph.GetName())
            graph.RemovePoint(i)
    if breakLink:
        graph.RemovePoint(graph.GetN()-1)
    if debug:
        graph.Print()
    if nRemoved and info:
        print "INFO: Removing %d points from graph %s" % (nRemoved, graph.GetName())


def modifyGraph(graph, dct={}, debug=False, info=False):
    if debug:
        graph.Print()
    for old, new in dct.iteritems():
        x = graph.GetX()
        y = graph.GetY()
        for i in range(graph.GetN()):
            if abs(old[0]-x[i]) < 1.0e-6 and abs(old[1]-y[i]) < 1.0e-6:
                graph.SetPoint(i, new[0], new[1])
                if info:
                    print "INFO: Replacing point %d: (%g,%g) --> (%g,%g) from graph %s" % (i, old[0], old[1], new[0], new[1], graph.GetName())
    if debug:
        graph.Print()


def insertPoints(graph, lst=[], mode="prepend"):
    if not lst:
        return
    npoints = len(lst)
    ngraph = graph.GetN()

    total_points = npoints + ngraph
    graph.Expand(total_points)

    print "expanding graph", graph.GetName(), "with", graph.GetN(),
    print "points to have", total_points
    if mode == "prepend":
        for p in reversed(range(total_points)):
            if p < npoints:
                graph.SetPoint(p, lst[p][0], lst[p][1])
            else:
                x = r.Double(0.)
                y = r.Double(0.)
                graph.GetPoint(p-npoints, x, y)
                graph.SetPoint(p, x, y)
    elif mode == "append":
        for p in range(total_points):
            if p < ngraph:
                x = r.Double(0.)
                y = r.Double(0.)
                graph.GetPoint(p, x, y)
                graph.SetPoint(p, x, y)
            else:
                graph.SetPoint(p, *lst[p-ngraph])


def spline(points=[], title=""):
    graph = r.TGraph()
    for i, (x, y) in enumerate(points):
        graph.SetPoint(i, x, y)
    return r.TSpline3(title, graph)


def factorString(xsFactor=None):
    if xsFactor == 1.0:
        return ""
    return ("_xs%3.1f" % xsFactor).replace(".", "p")


def exclusionGraphs(model=None, expectedMapsOnly=None, histos={}, interBin="",
                    pruneYMin=False, debug=None, info=None):
    cutFunc = patches.cutFunc()[model.name]
    curves = patches.curves().get(model.name)

    graphs = {}
    simpleExclHistos = {}
    relativeHistos = {}

    items = [("ExpectedUpperLimit_m2_Sigma", 0.0),
             ("ExpectedUpperLimit_p2_Sigma", 0.0),
             ("ExpectedUpperLimit_m1_Sigma", 0.0),
             ("ExpectedUpperLimit_p1_Sigma", 0.0),
             ("ExpectedUpperLimit",          0.0),
             ]
    if not expectedMapsOnly:
        items += [("UpperLimit",  0.0),
                  ("UpperLimit", -1.0),
                  ("UpperLimit",  1.0),
                  ]

    for histoName, xsVariation in items:
        for xsFactor in model.xsFactors:
            graphName = histoName
            if xsVariation == 1.0:
                graphName += "_p1_Sigma"
            if xsVariation == -1.0:
                graphName += "_m1_Sigma"

            if curves:
                assert False, "FIXME"
                key = (spec["name"], model.xsVariation)
                if key in curves:
                    spec["curve"] = spline(points=curves[key])

            h = histos["%s_%s" % (model.name, histoName)]
            kargs = {"variation": xsVariation,
                     "xsFactor": xsFactor,
                     "model": model,
                     "interBin": interBin}

            graph = rxs.excludedGraph(h,
                                      info=info,
                                      whiteList=configuration.signal.whiteListOfPoints(model.name),
                                      **kargs)

            simpleHisto = rxs.exclHisto(h,
                                        tag="_excludedHistoSimple",
                                        zTitle="bin excluded or not",
                                        func=lambda xsLimit, xs: 2*(xsLimit < xs)-1,
                                        **kargs)
            relativeHisto = rxs.exclHisto(h,
                                          tag="_relative",
                                          zTitle="xs upper limit / nominal xs",
                                          func=lambda xsLimit, xs: xsLimit/xs,
                                          **kargs)

            patchesFunc = graphName
            graphName += factorString(xsFactor)
            graph.SetName(graphName)
            simpleHisto.SetName(graphName+"_simpleExcl")
            relativeHisto.SetName(graphName+"_relative")

            dct = getattr(patches, patchesFunc)(model.name+factorString(xsFactor))
            pruneGraph(graph, debug=debug, breakLink=pruneYMin,
                       lst=dct["blackList"]+(pointsAtYMin(graph) if pruneYMin else []))
            modifyGraph(graph, dct=dct["replace"], debug=debug, info=info)
            #insertPoints(graph, lst=insertList)
            graphs[graphName] = graph
            simpleExclHistos[graphName] = simpleHisto
            relativeHistos[graphName] = relativeHisto
    return graphs, simpleExclHistos, relativeHistos


def upperLimitHistos(model=None, expectedMapsOnly=None, inFileName="", shiftX=None, shiftY=None, info=None):
    assert len(configuration.limit.CL()) == 1
    cl = configuration.limit.CL()[0]

    items = [("ExpectedUpperLimit", "expected upper limit"),
             ("ExpectedUpperLimit_-1_Sigma", "title"),
             ("ExpectedUpperLimit_+1_Sigma", "title"),
             ("ExpectedUpperLimit_-2_Sigma", "title"),
             ("ExpectedUpperLimit_+2_Sigma", "title")]

    if not expectedMapsOnly:
        items = [("UpperLimit" if configuration.limit.method() == "CLs" else "upperLimit95", "upper limit")] + items

    histos = {}
    for name, pretty in items:
        nameReplace = []
        try:
            keyName = "%s_%s" % (model.name, name)
            h3 = hp.oneHisto(file=inFileName, name=keyName)
        except AssertionError:
            h3 = hp.oneHisto(file=inFileName, name=name)
            if h3:
                print "WARNING: histo %s not found (using %s)" % (keyName, name)
                nameReplace = [(name, keyName)]
            else:
                print "ERROR: histo %s (nor %s) not found." % (keyName, name)
                continue

        h = hp.modifiedHisto(h3=h3,
                             model=model,
                             shiftX=shiftX,
                             shiftY=shiftY,
                             range=True,
                             info=info)

        zTitle = "%g%% CL %s on  #sigma (pb)" % (100.0*cl, pretty)
        adjustHisto(h, title=";".join([configuration.signal.histoTitle(model=model.name), zTitle]))

        if info:
            hp.printHoles(h)
        rename(h, nameReplace=nameReplace)
        histos[h.GetName()] = h
    return histos


def rename(h, nameReplace=[]):
    name = h.GetName()
    for old, new in nameReplace + [("+", "p"),
                                   ("-", "m"),
                                   ("upper", "Upper"),
                                   ("95", ""),  # hard-coded
                                   ("_shifted", ""),
                                   ("_2D", ""),
                                   ("_clone", "")]:
        name = name.replace(old, new)
    h.SetName(name)


def writeList(fileName="", objects=[]):
    f = r.TFile(fileName, "RECREATE")
    for obj in objects:
        obj.Write()
    f.Close()


def outFileName(model=None, tag="", simple=False):
    if simple:
        base = model.name+".root"
    else:
        base = configuration.limit.mergedFile(model=model).split("/")[-1]

    root = configuration.directories.plot()+"/"+base.replace(".root", "_%s.root" % tag)
    return {"root": root,
            "eps": root.replace(".root", ".eps"),
            "pdf": root.replace(".root", ".pdf"),
            }


def makeLimitRootFiles(model=None, expectedMapsOnly=None, limitFileName="", simpleFileName="",
                       relativeFileName="", interBinOut=None, pruneYMin=None,
                       debug=None, info=None):
    assert pruneYMin is not None
    assert interBinOut

    shiftX = shiftY = (model.interBin == "LowEdge" and interBinOut == "Center")

    histos = upperLimitHistos(model=model,
                              expectedMapsOnly=expectedMapsOnly,
                              inFileName=configuration.limit.mergedFile(model=model),
                              shiftX=shiftX,
                              shiftY=shiftY,
                              info=info)
    graphs, simple, relative = exclusionGraphs(model=model,
                                               expectedMapsOnly=expectedMapsOnly,
                                               histos=histos,
                                               interBin=interBinOut,
                                               pruneYMin=pruneYMin,
                                               debug=debug,
                                               info=info)

    writeList(fileName=limitFileName, objects=histos.values()+graphs.values())
    writeList(fileName=simpleFileName, objects=simple.values())
    writeList(fileName=relativeFileName, objects=relative.values())


def makeEfficiencyPlots(model=None, key="",
                        interBinOut=None,
                        separateCategories=None,
                        includeNonUsedCategories=None,
                        debug=False,
                        info=False,
                        ):
    assert interBinOut
    effHistos = efficiencyHistos(model=model,
                                 key=key,
                                 shift=(model.interBin == "LowEdge" and interBinOut == "Center"),
                                 separateCategories=separateCategories,
                                 includeNonUsedCategories=includeNonUsedCategories,
                                 info=info,
                                 )

    effFileName = outFileName(model=model, tag=key, simple=True)["root"]
    writeList(fileName=effFileName, objects=effHistos.values())
    del effHistos

    makeEfficiencyPdfSum(model=model, rootFileName=effFileName, key=key)
    if separateCategories:
        makeEfficiencyPdfBinned(model=model, rootFileName=effFileName, key=key)


def makeXsUpperLimitPlots(model=None, logZ=False, curveGopts="", interBinOut="",
                          mDeltaFuncs={}, diagonalLine=False, pruneYMin=False,
                          expectedMapsOnly=False, observedCurves=True, debug=False, info=False):

    if expectedMapsOnly:
        assert not observedCuves

    limitFileName = outFileName(model=model,
                                tag="xsLimit")["root"]
    simpleFileName = outFileName(model=model,
                                 tag="xsLimit_simpleExcl")["root"]
    relativeFileName = outFileName(model=model,
                                   tag="xsLimit_relative")["root"]

    makeLimitRootFiles(model=model,
                       expectedMapsOnly=expectedMapsOnly,
                       limitFileName=limitFileName,
                       simpleFileName=simpleFileName,
                       relativeFileName=relativeFileName,
                       interBinOut=interBinOut,
                       pruneYMin=pruneYMin,
                       debug=debug,
                       info=info)

    r.gStyle.SetLineStyleString(19, "50 20")
    curveSpecs = [{"name": "ExpectedUpperLimit", "label": "Expected Limit #pm1 #sigma exp.",
                   "lineStyle": 7, "lineWidth": 3, "color": r.kViolet},
                  {"name": "ExpectedUpperLimit_m1_Sigma", "label": "",
                   "lineStyle": 2, "lineWidth": 2, "color": r.kViolet},
                  {"name": "ExpectedUpperLimit_p1_Sigma", "label": "",
                   "lineStyle": 2, "lineWidth": 2, "color": r.kViolet},
                  {"name": "ExpectedUpperLimit_m2_Sigma", "label": "Expected Limit #m2 #sigma exp.",
                   "lineStyle": 2, "lineWidth": 2, "color": r.kViolet},
                  {"name": "ExpectedUpperLimit_p2_Sigma", "label": "Expected Limit #p2 #sigma exp.",
                   "lineStyle": 2, "lineWidth": 2, "color": r.kViolet},
                  ]
    if observedCurves:
        curveSpecs += [{"name": "UpperLimit",
                        "label": "#sigma^{NLO+NLL} #pm1 #sigma theory",
                        "lineStyle": 1, "lineWidth": 3, "color": r.kBlack},
                       {"name": "UpperLimit_m1_Sigma",         "label": "",
                        "lineStyle": 1, "lineWidth": 1, "color": r.kBlack},
                       {"name": "UpperLimit_p1_Sigma",         "label": "",
                        "lineStyle": 1, "lineWidth": 1, "color": r.kBlack},
                       ]

    makeLimitPdf(model=model,
                 expectedMapsOnly=expectedMapsOnly,
                 rootFileName=limitFileName,
                 curveSpecs=curveSpecs,
                 diagonalLine=diagonalLine,
                 logZ=logZ,
                 curveGopts=curveGopts,
                 mDeltaFuncs=mDeltaFuncs,
                 )

    makeHistoPdf(model=model,
                 histoFileName=simpleFileName,
                 graphFileName=limitFileName,
                 curveSpecs=curveSpecs,
                 curveGopts=curveGopts,
                 tag="_simpleExcl",
                 min=-1.0,
                 max=1.0,
                 )

    makeHistoPdf(model=model,
                 histoFileName=relativeFileName,
                 graphFileName=limitFileName,
                 curveSpecs=curveSpecs,
                 curveGopts=curveGopts,
                 tag="_relative",
                 min=0.8,
                 max=1.2,
                 nContour=100,
                 )


def legendTitle(model=None):
    return likelihood.spec(name=model.llk).legendTitle()


def makeLimitPdf(model=None, expectedMapsOnly=None,
                 rootFileName="", diagonalLine=False, logZ=False,
                 curveGopts="", mDeltaFuncs=False, curveSpecs=[]):

    epsFile = rootFileName.replace(".root", ".eps")
    f = r.TFile(rootFileName)

    canvas = squareCanvas()

    if configuration.limit.method() == "CLs":
        if model.binaryExclusion:
            # FIXME: handle expected
            print "ERROR: handle expected"
            hName = "excluded_CLs_95"
        elif expectedMapsOnly:
            hName = "ExpectedUpperLimit"
        else:
            hName = "UpperLimit"
    else:
        # FIXME: handle expected
        print "ERROR: handle expected"
        hName = "UpperLimit"  # 95 was removed in rename()
    h = f.Get("%s_%s" % (model.name, hName))
    h.Draw("colz")

    if logZ:
        canvas.SetLogz()
        hp.setRange("xsZRangeLog", model, h, "Z")
    else:
        hp.setRange("xsZRangeLin", model, h, "Z")
        epsFile = epsFile.replace(".eps", "_linZ.eps")

    #extra = ", 4 flavours"
    #extra = " (u+d+s+c)"
    #extra = "; u+d+s+c"
    #extra = ", u+d+s+c"
    extra = ", #tilde{u}+#tilde{d}+#tilde{s}+#tilde{c}"
    p8 = "#tilde{q}_{L}%s+ #tilde{q}_{R}%s" % ("^{#color[0]{L}}" if len(model.xsFactors) == 1 else "",
                                               extra)
    p1 = p8.replace("q", "u")[:p8.find("+")]+" only"
    if len(model.xsFactors) >= 2:
        p1 = "#lower[0.1]{%s}" % p1
        p8 = "#lower[-0.05]{%s}" % p8

    stuff = []
    graphs = []
    for xsFactor in sorted(model.xsFactors):
        for d in curveSpecs:
            graph = f.Get(d["name"]+factorString(xsFactor))
            if not graph:
                continue
            graph.SetLineColor(d["color"])
            graph.SetLineWidth(d["lineWidth"])
            lineStyle = d["lineStyle"]
            label = d["label"]
            goption = "l"
            legend = "top"

            if xsFactor == 0.8:
                if d["name"] == "UpperLimit":
                    if len(model.xsFactors) >= 2:
                        label = p8
                        legend = "bottom"
                        # now in legend title
                        # graphs.append({"graph": graph, "label": d["label"], "goption": "", "legend": legend})
                    else:
                        label = d["label"].replace("theory", "th. (%s)" % p8)

            elif xsFactor == 0.1:
                if len(model.xsFactors) == 1:
                    label = d["label"].replace("theory", "th. (%s)" % p1)
                else:
                    lineStyle = {"ExpectedUpperLimit": 7,
                                 "ExpectedUpperLimit_m1_Sigma": 2,
                                 "ExpectedUpperLimit_p1_Sigma": 2,
                                 "ExpectedUpperLimit_m2_Sigma": 2,
                                 "ExpectedUpperLimit_p2_Sigma": 2,
                                 "UpperLimit": 19,  # 9,#3,#1,#5,
                                 "UpperLimit_m1_Sigma": 19,
                                 "UpperLimit_p1_Sigma": 19
                                 }[d["name"]]
                    if d["name"] == "UpperLimit":
                        label = p1
                        legend = "bottom"
                    else:
                        label = ""

            graph.SetLineStyle(lineStyle)
            graphs.append({"graph": graph, "label": label, "goption": goption, "legend": legend})

    if curveGopts:
        if len(model.xsFactors) >= 2:
            xMax = 0.69
        elif model.xsFactors[0] == 0.8:
            xMax = 0.8
        elif model.xsFactors[0] == 0.1:
            xMax = 0.69
        else:
            xMax = 0.69
        stuff += drawGraphs(graphs, gopts=curveGopts, xMaxTop=xMax)
    else:
        epsFile = epsFile.replace(".eps", "_noRef.eps")

    if diagonalLine:
        ranges = configuration.signal.ranges(model.name)
        yx = r.TF1("yx", "x", ranges["xRange"][0], ranges["xMaxDiag"])
        yx.SetLineColor(1)
        yx.SetLineStyle(3)
        yx.SetLineWidth(2)
        yx.Draw("same")

    if mDeltaFuncs:
        epsFile = epsFile.replace(".eps", "_mDelta.eps")
        funcs = rxs.mDeltaFuncs(**mDeltaFuncs)
        for func in funcs:
            func.Draw("same")

    if len(model.xsFactors) == 1:
        s3 = stamp(text=legendTitle(model),
                   x=0.2075, y=0.64, factor=0.65)
    else:
        yStamp = 0.50
        c = ", "
        text = legendTitle(model).split(c)
        s3 = stamp(text=c.join(text[:-1]), x=0.2075, y=yStamp, factor=0.65)
        s4 = stamp(text=text[-1], x=0.2075, y=yStamp-0.04, factor=0.65)

    printOnce(model=model, canvas=canvas, fileName=epsFile, alsoC=True)
    if len(model.xsFactors) >= 2:
        print 'WARNING: must add gStyle->SetLineStyleString(19, "50 20"); to .C file'
    f.Close()


def drawGraphs(graphs, legendTitle="", gopts="", xMin=0.19, xMaxTop=0.69, xMaxBot=0.59):
    countTop = len(filter(lambda x: x["label"] and x["legend"] == "top", graphs))
    countBot = len(filter(lambda x: x["label"] and x["legend"] == "bottom", graphs))
    yMaxTop = 0.755
    yMinTop = yMaxTop-0.04*countTop

    yMaxBot = yMinTop - 0.04*0.75
    yMinBot = yMaxBot - 0.04*(1.2+countBot)  # include title+space

    legendTop = r.TLegend(xMin, yMinTop, xMaxTop, yMaxTop, legendTitle)
    legendTop.SetBorderSize(0)
    legendTop.SetFillStyle(0)

    legendBot = r.TLegend(xMin, yMinBot, xMaxBot, yMaxBot, " #sigma^{NLO+NLL} #pm1 #sigma theory")
    legendBot.SetBorderSize(0)
    legendBot.SetFillStyle(0)

    entriesTop = []
    entriesBot = []
    for d in graphs:
        g = d["graph"]
        if d['label']:
            entry = (g, d["label"], d["goption"])
            legend = None
            if d["legend"] == "bottom":
                entriesBot.append(entry)
            if d["legend"] == "top":
                entriesTop.append(entry)
        if g.GetN():
            g.Draw("%ssame" % gopts)

    for entry in entriesTop:
        legendTop.AddEntry(*entry)

    for entry in reversed(entriesBot):
        legendBot.AddEntry(*entry)

    if countTop:
        legendTop.Draw("same")
    if countBot:
        legendBot.Draw("same")
    return legendTop, legendBot, graphs


def makeHistoPdf(model=None, histoFileName="", graphFileName="",
                 curveSpecs=[], curveGopts="",
                 min=None, max=None, tag="", nContour=None):

    c = squareCanvas()
    pdf = histoFileName.replace(".root", ".pdf")

    hFile = r.TFile(histoFileName)
    gFile = r.TFile(graphFileName)

    c.Print(pdf+"[")
    for xsFactor in model.xsFactors:
        for d in curveSpecs:
            name = d["name"]+factorString(xsFactor)
            h = hFile.Get(name+tag)
            if not h:
                continue
            if nContour:
                h.SetContour(nContour)
            h.Draw("colz")
            h.SetMinimum(min)
            h.SetMaximum(max)
            h.SetTitle(name)
            r.gPad.SetGridx()
            r.gPad.SetGridy()

            g = gFile.Get(name)
            if g and curveGopts:
                g.SetMarkerColor(r.kBlack)
                g.SetMarkerStyle(20)
                g.SetMarkerSize(0.3*g.GetMarkerSize())
                g.SetLineColor(r.kYellow)
                g.SetLineStyle(1)
                g.Draw("%spsame" % curveGopts)
            if d.get("curve") and d["curve"].GetNp():
                d["curve"].SetMarkerStyle(20)
                d["curve"].SetMarkerSize(0.3*d["curve"].GetMarkerSize())
                d["curve"].Draw("lpsame")
            c.Print(pdf)

    c.Print(pdf+"]")
    print "INFO: %s has been written." % pdf
    hFile.Close()
    gFile.Close()


def efficiencyHistos(model=None,
                     key="",
                     shift=None,
                     separateCategories=None,
                     includeNonUsedCategories=None,
                     info=True,
                     ):
    assert key
    for var in ["shift", "separateCategories", "includeNonUsedCategories"]:
        assert eval(var) is not None, var

    globalSum = None
    perCategory = {}

    effHistos = hp.effHistos(model, allCategories=includeNonUsedCategories)
    for cat, dct in effHistos.iteritems():
        sum1Cat = None
        for histo in dct[key]:
            if not sum1Cat:
                sum1Cat = histo.Clone("_".join([model.name, key, cat]))
            else:
                sum1Cat.Add(histo)

            if not globalSum:
                globalSum = histo.Clone("_".join([model.name, key]))
            else:
                globalSum.Add(histo)

        perCategory[cat] = sum1Cat

    out = {key: globalSum}
    if separateCategories:
        out.update(perCategory)

    for key, h3 in out.iteritems():
        h = hp.modifiedHisto(h3=h3,
                             model=model,
                             shiftX=shift,
                             shiftY=shift,
                             range=True,
                             info=info,
                             )

        zTitle = "A #times #epsilon"
        adjustHisto(h, title=";".join([configuration.signal.histoTitle(model=model.name), zTitle]))
        rename(h)
        out[key] = h

    return out


def effPad(cat=""):
    pads = {"0b_le3j": 1,
            "0b_ge4j": 2,
            "1b_le3j": 3,
            "1b_ge4j": 4,
            "2b_le3j": 5,
            "2b_ge4j": 6,
            "3b_le3j": 7,
            "3b_ge4j": 8,
            "effHad": 9,
            "ge4b_ge4j": 10,
            }
    for key, value in pads.iteritems():
        if cat.endswith(key):
            return value
    print "ERROR: %s will clobber pad 1" % cat
    return 1


def makeEfficiencyPdfBinned(model=None, rootFileName="", key=""):
    def prep(p):
        p.SetTopMargin(0.15)
        p.SetBottomMargin(0.15)
        p.SetLeftMargin(0.15)
        p.SetRightMargin(0.15)
        p.SetTickx()
        p.SetTicky()

    can = r.TCanvas("canvas", "canvas", 400, 1000)
    can.Divide(2, 5)

    dct = allHistos(rootFileName)
    maximum = max([h.GetMaximum() for h in dct.values()])

    for i, (cat, h) in enumerate(sorted(dct.iteritems())):
        can.cd(effPad(cat))
        prep(r.gPad)

        h.SetTitle(cat)
        h.SetStats(False)
        h.SetMinimum(0.0)
        h.SetMaximum(maximum)
        h.Draw("colz")
        #h.GetListOfFunctions().FindObject("palette").GetAxis().SetTitle("")

    can.cd(0)
    printOnce(model=None,  # suppress stamp
              canvas=can,
              fileName=rootFileName.replace(".root", "Binned.eps"),
              )


def makeEfficiencyPdfSum(model=None, rootFileName="", key=""):
    canvas = squareCanvas()

    h = hp.oneHisto(file=rootFileName,
                    name="%s_%s" % (model.name, key),
                    )
    h.Draw("colz")
    hp.setRange("effZRange", model, h, "Z")

    coords = configuration.signal.processStamp(model.name)

    factor = 0.6
    s3 = stamp(text=legendTitle(model),
               x=0.23,
               y=0.70,
               factor=factor,
               )

    printOnce(model=model,
              canvas=canvas,
              fileName=rootFileName.replace(".root", ".eps"),
              factor=factor,
              )
    hp.printHoles(h)


def printTimeStamp():
    text = r.TText()
    text.SetNDC()
    text.DrawText(0.1, 0.1, "file created at %s" % r.TDatime().AsString())
    text.DrawText(0.1, 0.35, "[restore useful info here]")
    #text.DrawText(0.1, 0.35, "REwk = %s"%(l["REwk"] if l["REwk"] else "[no form assumed]"))
    #text.DrawText(0.1, 0.30, "RQcd = %s"%(l["RQcd"] if l["RQcd"] else "[no form assumed]"))
    #text.DrawText(0.1, 0.25, "nFZinv = %s"%(l["nFZinv"].replace("fZinv","")))
    return text


def printSuppressed(l):
    text = r.TText()
    text.SetTextSize(0.3*text.GetTextSize())
    text.SetNDC()
    text.DrawText(0.1, 0.9, "empty histograms: %s" % str(l))
    return text


def printLumis():
    text = r.TText()
    text.SetNDC()
    text.SetTextFont(102)
    text.SetTextSize(0.5*text.GetTextSize())

    x = 0.1
    y = 0.9
    s = 0.035
    text.DrawText(x, y, "restore useful info here")
    return text

    text.DrawText(x, y,   "sample     lumi (/pb)")
    text.DrawText(x, y-s, "---------------------")
    inputData = configuration.data()
    i = 1
    d = inputData.lumi()
    for key in sorted(d.keys()):
        i += 1
        text.DrawText(x, y-i*s, "%8s       %6.0f" % (key, d[key]))
    text.DrawText(x, y-(i+1)*s, "HT bins: %s" % str(inputData.htBinLowerEdges()))
    return text


def drawBenchmarks(model=None):
    parameters = configuration.signal.scanParameters()
    if not (model in parameters):
        return

    params = parameters[model.name]

    text = r.TText()
    out = []
    for label, coords in configuration.signal.benchmarkPoints().iteritems():
        drawIt = True
        for key, value in coords.iteritems():
            if key in params and value != params[key]:
                drawIt = False
        if not drawIt:
            continue
        marker = r.TMarker(coords["m0"], coords["m12"], 20)
        marker.Draw()
        out.append(marker)
        out.append(text.DrawText(10+coords["m0"], 10+coords["m12"], label))
    return out


def printOneHisto(h2=None, name="", canvas=None, fileName="",
                  effRatioPlots=False, drawBenchmarkPoints=False,
                  logZ=[], model=None, suppressed=[], alsoC=False):
    if "upper" in name:
        hp.printHoles(h2)
    h2.SetStats(False)
    h2.SetTitle("%s%s" % (name, configuration.signal.histoTitle(model=model.name)))
    h2.Draw("colz")
    if not h2.Integral():
        suppressed.append(name)
        return

    canvas.SetLogz(name in logZ)
    if name == "xs" and name in logZ:
        h2.SetMinimum(1.0e-2)
    if name == "nEventsSigMcHad" and name in logZ:
        h2.SetMinimum(0.9)
    if "NLO_over_LO" in name:
        h2.SetMinimum(0.5)
        h2.SetMaximum(3.0)

    if drawBenchmarkPoints:
        stuff = drawBenchmarks(model)

    if "excluded" in name and model.isSms:
        return

    printSinglePage = (not model.isSms) and "excluded" in name
    printSinglePage |= model.isSms and "upperLimit" in name

    if printSinglePage:
        title = h2.GetTitle()
        h2.SetTitle("")
#        eps = fileName.replace(".ps","_%s.eps"%name)
#        super(utils.numberedCanvas, canvas).Print(eps)
#        utils.epsToPdf(eps)
        pdf_fileName = fileName.replace(".pdf", "_%s.pdf" % name)
        super(utils.numberedCanvas, canvas).Print(pdf_fileName)
        h2.SetTitle(title)

    canvas.Print(fileName)
    if alsoC:
        canvas.Print(fileName.replace(".pdf","_%s.C"%name))
    #effMu/effHad
    if effRatioPlots:
        for name in names:
            num = utils.threeToTwo(f.Get(name))
            if name[:7] != "effmuon":
                continue
            denName = name.replace("muon", "had")
            den = utils.threeToTwo(f.Get(denName))
            num.Divide(den)
            num.SetStats(False)
            num.SetTitle("%s/%s%s;" % (name, denName, configuration.signal.histoTitle(model=model.name)))
            num.Draw("colz")
            if not num.Integral():
                continue
            num.SetMinimum(0.0)
            num.SetMaximum(0.5)
            if drawBenchmarkPoints:
                stuff = drawBenchmarks(model)
            canvas.Print(fileName)


def sortedNames(histos=[], first=[], last=[]):
    start = []
    end = []
    names = sorted([histo.GetName() for histo in histos])
    for name in names:
        for item in first:
            if item == name[:len(item)]:
                start.append(name)
        for item in last:
            if item == name[:len(item)]:
                end.append(name)

    for item in list(set(start+end)):
        names.remove(item)
    return start+names+end


def multiPlots(model=None, tag="", first=[], last=[], whiteListMatch=[], blackListMatch=[],
               outputRootFile=False, modify=False, square=False):
    assert tag

    inFile = configuration.limit.mergedFile(model=model)
    f = r.TFile(inFile)
    r.gROOT.cd()

    fileNames = outFileName(model=model, tag=tag)
    fileName = fileNames["pdf"]

    if square:
        canvas = squareCanvas(numbered=True)
    else:
        canvas = utils.numberedCanvas()
        canvas.SetRightMargin(0.15)

    canvas.Print(fileName+"[")
    canvas.SetTickx()
    canvas.SetTicky()

    text1 = printTimeStamp()
    text2 = printLumis()
    canvas.Print(fileName)
    canvas.Clear()

    names = sortedNames(histos=f.GetListOfKeys(), first=first, last=last)

    if outputRootFile:
        outFile = r.TFile(fileNames["root"], "RECREATE")
        r.gROOT.cd()

    suppressed = []
    for name in names:
        if whiteListMatch and not any([item in name for item in whiteListMatch]):
            continue
        if any([item in name for item in blackListMatch]):
            continue

        h2 = utils.threeToTwo(f.Get(name))
        if modify:
            hp.modifyHisto(h2, model)
        printOneHisto(h2=h2, name=name, canvas=canvas, fileName=fileName,
                      logZ=["xs", "nEventsHad"], model=model,
                      suppressed=suppressed)
        if outputRootFile:
            outFile.cd()
            h2.Write()
            r.gROOT.cd()

    if outputRootFile:
        print "%s has been written." % fileNames["root"]
        outFile.Close()

    canvas.Clear()
    text3 = printSuppressed(suppressed)
    canvas.Print(fileName)

    canvas.Print(fileName+"]")

    print "%s has been written." % fileName


def allHistos(fileName="", collapse=False):
    f = r.TFile(fileName)
    r.gROOT.cd()
    out = {}
    for key in f.GetListOfKeys():
        name = key.GetName()
        h = f.Get(name)
        out[name] = utils.threeToTwo(h) if collapse else h
        out[name].SetDirectory(0)
    f.Close()
    return out


def clsValidation(model=None, cl=None, tag="", masterKey="",
                  yMin=0.0, yMax=1.0, lineHeight=0.5,
                  divide=(4, 3), whiteList=[], stampTitle=True):

    def name(s=""):
        #return s
        return "%s_%s" % (model.name, s)

    assert tag
    assert masterKey
    assert cl
    if whiteList:
        assert len(whiteList) == divide[0]*divide[1], "%d != %d" % (len(whiteList), divide[0]*divide[1])

    histos = allHistos(fileName=configuration.limit.mergedFile(model=model), collapse=True)
    master = histos.get(name(masterKey))
    assert master, "%s not found.  Available keys: %s" % (masterKey, str(histos.keys()))

    graphs = {}
    for iBinX in range(1, 1 + master.GetNbinsX()):
        for iBinY in range(1, 1 + master.GetNbinsY()):
            if whiteList and (iBinX, iBinY) not in whiteList:
                continue
            if not master.GetBinContent(iBinX, iBinY):
                continue

            specialKey = name("CLb")
            if specialKey not in histos or not histos[specialKey]:
                continue
            if not histos[specialKey].GetBinContent(iBinX, iBinY):
                continue

            binX = master.GetXaxis().GetBinLowEdge(iBinX)
            binY = master.GetYaxis().GetBinLowEdge(iBinY)
            graphName = name("CLs_%d_%d" % (iBinX, iBinY))
            graphTitle = "%d_%d: (%g, %g)" % (iBinX, iBinY, binX, binY)
            graph = r.TGraphErrors()
            graph.SetName(graphName)
            graph.SetTitle("%s;#sigma (pb);CL_{s}" % (graphTitle if stampTitle else ""))
            graph.SetMarkerStyle(20)
            graph.SetMarkerSize(0.5)
            graph.SetMinimum(yMin)
            graph.SetMaximum(yMax)
            iPoint = 0
            while True:
                s = "" if not iPoint else "_%d" % iPoint
                if name("CLs%s" % s) not in histos:
                    break
                x = histos[name("PoiValue%s" % s)].GetBinContent(iBinX, iBinY)
                if not iPoint:
                    xMin = x
                xMax = x
                graph.SetPoint(iPoint, x, histos[name("CLs%s" % s)].GetBinContent(iBinX, iBinY))
                graph.SetPointError(iPoint, 0.0, histos[name("CLsError%s" % s)].GetBinContent(iBinX, iBinY))
                iPoint += 1

            e = 0.1*(xMax-xMin)
            y = 1.0 - cl
            clLine = r.TLine(xMin-e, y, xMax+e, y)
            clLine.SetLineColor(r.kRed)

            xLim = histos[name("UpperLimit")].GetBinContent(iBinX, iBinY)
            limLine = r.TLine(xLim, yMin, xLim, yMax*lineHeight)
            limLine.SetLineColor(r.kBlue)
            graphs[graphName] = [graph, clLine, limLine]

            if not whiteList:
                xLimPl = histos[name("PlUpperLimit")].GetBinContent(iBinX, iBinY)
                plLimLine = r.TLine(xLimPl, yMin, xLimPl, yMax*lineHeight)
                plLimLine.SetLineColor(r.kGreen)
                graphs[graphName].append(plLimLine)

    fileName = outFileName(model=model,
                           tag=tag+"_"+str(cl).replace("0.", ""))["pdf"]
    if whiteList:
        fileName = fileName.replace(".pdf", ".eps")
        canvas = r.TCanvas("canvas", "", 500*divide[0], 500*divide[1])
    else:
        canvas = utils.numberedCanvas()
        canvas.Print(fileName+"[")
        text1 = printTimeStamp()
        text2 = printLumis()
        canvas.Print(fileName)
        canvas.Clear()

    canvas.SetRightMargin(0.15)
    utils.cyclePlot(d=graphs, f=None, args={}, optStat=1110, canvas=canvas,
                    fileName=fileName, divide=divide, goptions="alp")

    if whiteList:
        utils.epsToPdf(fileName, sameDir=True)
        print "%s has been written." % fileName.replace(".eps", ".pdf")
    else:
        canvas.Print(fileName+"]")
        print "%s has been written." % fileName


def makePlots(square=False):
    for model in configuration.signal.models():
        multiPlots(model=model,
                   tag="validation",
                   first=["excluded", "upperLimit", "CLs", "CLb", "xs"],
                   last=["lowerLimit"],
                   blackListMatch=["eff", "_nEvents"],
                   square=square)

        #multiPlots(model=model,
        #           tag="nEvents",
        #           whiteListMatch=["nEvents"],
        #           square=square)
        #
        #multiPlots(model=model,
        #           tag="effHad",
        #           whiteListMatch=["effHad"],
        #           blackListMatch=["UncRel"],
        #           outputRootFile=True,
        #           modify=True,
        #           square=square)
        #
        #multiPlots(model=model,
        #           tag="effMu",
        #           whiteListMatch=["effMu"],
        #           blackListMatch=["UncRel"],
        #           outputRootFile=True,
        #           modify=True,
        #           square=square)
        #
        #multiPlots(model=model,
        #           tag="xs",
        #           whiteListMatch=["xs"],
        #           outputRootFile=True,
        #           modify=True,
        #           square=square)

        if model.isSms and configuration.limit.method() == "CLs":
            for cl in configuration.limit.CL():
                clsValidation(model=model,
                              tag="clsValidation",
                              cl=cl,
                              masterKey="xs")
