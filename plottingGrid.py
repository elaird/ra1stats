import os,math,utils
import configuration as conf
import histogramSpecs as hs
import refXsProcessing as rxs
from histogramProcessing import printHoles,fillPoints,killPoints
from pickling import mergedFile
import ROOT as r

def setupRoot() :
    #r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)
    #r.gStyle.SetPadTickX(True)
    #r.gStyle.SetPadTickY(True)

setupRoot()

def threeToTwo(h3) :
    name = h3.GetName()
    h2 = r.TH2D(name+"_2D",h3.GetTitle(),
                h3.GetNbinsX(), h3.GetXaxis().GetXmin(), h3.GetXaxis().GetXmax(),
                h3.GetNbinsY(), h3.GetYaxis().GetXmin(), h3.GetYaxis().GetXmax(),
                )

    for iX in range(1, 1+h3.GetNbinsX()) :
        for iY in range(1, 1+h3.GetNbinsY()) :
            content = h3.GetBinContent(iX, iY, 1)
            h2.SetBinContent(iX, iY, content)
    h2.GetZaxis().SetTitle(h3.GetZaxis().GetTitle())
    return h2

def modifyHisto(h, s) :
    fillPoints(h, points = s["overwriteOutput"][s["signalModel"]])
    killPoints(h, cutFunc = s["smsCutFunc"][s["signalModel"]] if s["signalModel"] in s["smsCutFunc"] else None)

def squareCanvas(margin = 0.18, ticks = True) :
    canvas = r.TCanvas("canvas","canvas",2)
    for side in ["Left", "Right", "Top", "Bottom"] :
        getattr(canvas, "Set%sMargin"%side)(margin)
    canvas.SetTickx(ticks)
    canvas.SetTicky(ticks)
    return canvas

def epsToPdf(fileName, tight = True) :
    if not tight : #make pdf
        os.system("epstopdf "+fileName)
        os.system("rm       "+fileName)
    else : #make pdf with tight bounding box
        epsiFile = fileName.replace(".eps",".epsi")
        os.system("ps2epsi "+fileName+" "+epsiFile)
        os.system("epstopdf "+epsiFile)
        os.system("rm       "+epsiFile)
        os.system("rm       "+fileName)
    print "%s has been written."%fileName.replace(".eps",".pdf")

def adjustHisto(h, title = "") :
    h.SetStats(False)
    h.SetTitle(title)
    h.GetYaxis().SetTitleOffset(1.5)
    h.GetZaxis().SetTitleOffset(1.5)

def printOnce(canvas, fileName) :
    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(22)
    text.DrawText(0.5, 0.85, "CMS Preliminary")
    canvas.Print(fileName)
    canvas.Print(fileName.replace(".eps",".C"))
    epsToPdf(fileName)

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

def makeTopologyXsLimitPlots(logZ = False, names = [], drawGraphs = True, mDeltaFuncs = {}, simpleExcl = False, printXs = False) :
    s = conf.switches()
    if not s["isSms"] : return
    
    inFile = mergedFile()
    f = r.TFile(inFile)
    fileName = inFile.replace(".root","_xsLimit.eps")

    c = squareCanvas()
    h2 = None
    for iName,name in enumerate(names) :
        h3 = f.Get(name)
        if not h3 : continue
        h2 = threeToTwo(h3)
        if iName :
            print "WARNING: used name %d (%s)"%(iName, name)
        break

    assert h2,names
    modifyHisto(h2, s)
    
    assert len(s["CL"])==1
    title = hs.histoTitle(model = s["signalModel"])
    title += ";%g%% C.L. upper limit on #sigma (pb)"%(100.0*s["CL"][0])
    adjustHisto(h2, title = title)

    #output a root file
    g = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
    h2.Write()
    g.Close()
    
    ranges = hs.smsRanges(s["signalModel"])
    setRange("smsXRange", ranges, h2, "X")
    setRange("smsYRange", ranges, h2, "Y")
    
    h2.Draw("colz")
    graphs = rxs.graphs(h2, s["signalModel"], "LowEdge", printXs = printXs)

    if simpleExcl :
        ps = fileName.replace(".eps","_simpleExcl.ps")
        c.Print(ps+"[")
        for d in graphs :
            d["histo"].Draw("colz")
            d["histo"].SetMaximum(1.0)
            d["histo"].SetMinimum(-1.0)
            d["histo"].SetTitle(d["label"])
            d["graph"].Draw("psame")
            c.Print(ps)
        c.Print(ps+"]")
        utils.ps2pdf(ps, sameDir = True)
        return

    printName = fileName
    if not logZ :
        setRange("smsXsZRangeLin", ranges, h2, "Z")
        if drawGraphs : stuff = rxs.drawGraphs(graphs)
        printName = fileName.replace(".eps", "_refXs.eps")
    else :
        c.SetLogz()
        setRange("smsXsZRangeLog", ranges, h2, "Z")
        if drawGraphs :
            stuff = rxs.drawGraphs(graphs)
            fileName = fileName.replace(".eps", "_refXs.eps")
        if mDeltaFuncs :
            fileName = fileName.replace(".eps", "_mDelta.eps")
            funcs = rxs.mDeltaFuncs(**mDeltaFuncs)
            for func in funcs :
                func.Draw("same")
        printName = fileName.replace(".eps", "_logZ.eps")

    s2 = stamp(text = "#alpha_{T}", x = 0.22, y = 0.55, factor = 1.3)
    textMap = {"profileLikelihood":"PL", "CLs":"CL_{s}"}
    s3 = stamp(text = "%s, 4.6 fb^{-1}"%textMap[conf.switches()["method"]], x = 0.22, y = 0.62, factor = 0.7)
    
    printOnce(c, printName)
    printHoles(h2)
    
def makeEfficiencyUncertaintyPlots() :
    s = conf.switches()
    if not s["isSms"] : return

    inFile = mergedFile()
    f = r.TFile(inFile)
    ranges = hs.smsRanges(s["signalModel"])

    def go(name, suffix, zTitle, zRangeKey) :
        fileName = "%s/%s_%s.eps"%(conf.stringsNoArgs()["outputDir"], s["signalModel"], suffix)
        c = squareCanvas()
        h2 = threeToTwo(f.Get(name))
        xyTitle = hs.histoTitle(model = s["signalModel"])
        adjustHisto(h2, title = "%s;%s"%(xyTitle, zTitle))
        setRange("smsXRange", ranges, h2, "X")
        setRange("smsYRange", ranges, h2, "Y")
        h2.Draw("colz")
        setRange(zRangeKey, ranges, h2, "Z")

        #output a root file
        g = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
        h2.Write()
        g.Close()
        
        printOnce(c, fileName)

    go(name = "effUncRelExperimental", suffix = "effUncRelExp", zTitle = "#sigma^{exp}_{#epsilon} / #epsilon", zRangeKey = "smsEffUncExpZRange")
    go(name = "effUncRelTheoretical", suffix = "effUncRelTh", zTitle = "#sigma^{theo}_{#epsilon} / #epsilon", zRangeKey = "smsEffUncThZRange")
    go(name = "effUncRelIsr", suffix = "effUncRelIsr", zTitle = "#sigma^{ISR}_{#epsilon} / #epsilon", zRangeKey = "smsEffUncRelIsrZRange")
    go(name = "effUncRelPdf", suffix = "effUncRelPdf", zTitle = "#sigma^{PDF}_{#epsilon} / #epsilon", zRangeKey = "smsEffUncRelPdfZRange")
    go(name = "effUncRelJes", suffix = "effUncRelJes", zTitle = "#sigma^{JES}_{#epsilon} / #epsilon", zRangeKey = "smsEffUncRelJesZRange")
    go(name = "effUncRelMcStats", suffix = "effUncRelMcStats", zTitle = "#sigma^{MC stats}_{#epsilon} / #epsilon", zRangeKey = "smsEffUncRelMcStatsZRange")

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
        eps = fileName.replace(".ps","_%s.eps"%name)
        super(utils.numberedCanvas, canvas).Print(eps)
        utils.epsToPdf(eps)
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

def multiPlots(tag = "", first = [], last = [], whiteListMatch = [], blackListMatch = [], outputRootFile = False, modify = False) :
    assert tag
    
    inFile = mergedFile()
    f = r.TFile(inFile)
    r.gROOT.cd()
    
    fileName = inFile.replace(".root","_%s.pdf"%tag)
    rootFileName = fileName.replace(".pdf", ".root")
    
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

    histos = allHistos(fileName = mergedFile())
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

    fileName = mergedFile().replace(".root","_%s_%s.pdf"%(tag, str(cl).replace("0.","")))
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
    utils.cyclePlot(d = graphs, f = None, args = {}, optStat = 1110, canvas = canvas, psFileName = fileName, divide = divide, goptions = "alp")

    if whiteList :
        utils.epsToPdf(fileName, sameDir = True)
        print "%s has been written."%fileName.replace(".eps", ".pdf")
    else :
        canvas.Print(fileName+"]")
        print "%s has been written."%fileName
    
def makePlots() :
    multiPlots(tag = "validation", first = ["excluded", "upperLimit", "CLs", "CLb", "xs"], last = ["lowerLimit"])
    multiPlots(tag = "effHad", whiteListMatch = ["effHad"], blackListMatch = ["UncRel"], outputRootFile = True, modify = True)
    multiPlots(tag = "effMu", whiteListMatch = ["effMu"], blackListMatch = ["UncRel"], outputRootFile = True, modify = True)
    multiPlots(tag = "xs", whiteListMatch = ["xs"], outputRootFile = True, modify = True)

    s = conf.switches()
    if s["isSms"] and s["method"]=="CLs" :
        for cl in s["CL"] :
            clsValidation(tag = "clsValidation", cl = cl, masterKey = "xs")
    
    #pg.makeEfficiencyUncertaintyPlots()
    #pg.makeTopologyXsLimitPlots()

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
