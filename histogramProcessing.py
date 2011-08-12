#!/usr/bin/env python
import collections,cPickle,os,math,utils
import configuration as conf
import histogramSpecs as hs
import refXsProcessing as rxs
import fresh
import ROOT as r

def setupRoot() :
    r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)
    #r.gStyle.SetPadTickX(True)
    #r.gStyle.SetPadTickY(True)

def ratio(file, numDir, numHisto, denDir, denHisto) :
    f = r.TFile(file)
    assert not f.IsZombie(), file
        
    hOld = f.Get("%s/%s"%(numDir, numHisto))
    assert hOld,"%s/%s"%(numDir, numHisto)
    h = hOld.Clone("%s_clone"%hOld.GetName())
    h.SetDirectory(0)
    h.Divide(f.Get("%s/%s"%(denDir, denHisto)))
    f.Close()
    return h

def checkHistoBinning() :
    def axisStuff(axis) :
        return (axis.GetXmin(), axis.GetXmax(), axis.GetNbins())

    def properties(histos) :
        out = collections.defaultdict(list)
        for h in histos :
            try:
                out["type"].append(type(h))
                out["x"].append(axisStuff(h.GetXaxis()))
                out["y"].append(axisStuff(h.GetYaxis()))
                out["z"].append(axisStuff(h.GetZaxis()))
            except AttributeError as ae :
                h.Print()
                raise ae
        return out

    def histos() :
        binsInput = conf.data().htBinLowerEdgesInput()
        out = [xsHisto()]
        for item in ["had"]+([] if conf.switches()["ignoreSignalContaminationInMuonSample"] else ["muon"]) :
            out += [effHisto(box = item, scale = "1", htLower = htLower, htUpper = htUpper) for htLower, htUpper in zip(binsInput, list(binsInput[1:])+[None])]
        return out
    
    for axis,values in properties(histos()).iteritems() :
        #print "Here are the %s binnings: %s"%(axis, str(values))        
        if len(set(values))!=1 :
            print "The %s binnings do not match: %s"%(axis, str(values))
            for h in handles() :
                print h,properties([h])
            assert False

def fillHoles(h, nZeroNeighborsAllowed = 0) :
    def avg(items) :
        out = sum(items)
        n = len(items) - items.count(0.0)
        if n : return out/n
        return None

    for iBinX in range(2, h.GetNbinsX()) :
        for iBinY in range(2, h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :                
                if h.GetBinContent(iBinX, iBinY, iBinZ) : continue
                l = h.GetBinContent(iBinX-1, iBinY  , iBinZ)
                r = h.GetBinContent(iBinX+1, iBinY  , iBinZ)
                u = h.GetBinContent(iBinX  , iBinY+1, iBinZ)
                d = h.GetBinContent(iBinX  , iBinY-1, iBinZ)
                items = [l, r, u, d]
                if items.count(0.0)>nZeroNeighborsAllowed : continue #require at least n neighbors
                value = avg(items)
                if value!=None :
                    h.SetBinContent(iBinX, iBinY, iBinZ, value)
                    print "WARNING: hole in histo %s at bin (%3d, %3d, %3d) has been filled with %g.  (%2d zero neighbors)"%\
                          (h.GetName(), iBinX, iBinY, iBinZ, value, items.count(0.0))
    return h
        
def pdfUncHisto(spec) :
    f = r.TFile(spec["file"])
    assert not f.IsZombie()

    dir = spec["350Dirs"][0]
    hOld = f.Get("%s/%s"%(dir, spec["loYield"]))
    h = hOld.Clone("%s_%s_%s"%(spec["file"], dir, spec["loYield"]))
    h.SetDirectory(0)
    f.Close()

    if conf.switches()["fillHolesInEffUncRelPdf"] :
        return fillHoles(h, 2)
    else :
        return h

def xsHisto() :
    s = conf.switches()
    if "tanBeta" in s["signalModel"] : return nloXsHisto() if conf.switches()["nlo"] else loXsHisto()
    else : return smsXsHisto(s["signalModel"])

def effHisto(**args) :
    s = conf.switches()
    if "tanBeta" in s["signalModel"] : return nloEffHisto(**args) if conf.switches()["nlo"] else loEffHisto(**args)
    else : return smsEffHisto(s["signalModel"], **args)

def loXsHisto() :
    s = hs.histoSpec(box = "had", scale = "1")
    out = ratio(s["file"], s["beforeDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi_noweight")
    out.Scale(conf.switches()["icfDefaultNEventsIn"]/conf.switches()["icfDefaultLumi"])
    #mData = mEv.GetSusyCrossSection()*mDesiredLumi/10000;
    #http://svnweb.cern.ch/world/wsvn/icfsusy/trunk/AnalysisV2/framework/src/common/Compute_Helpers.cc
    #http://svnweb.cern.ch/world/wsvn/icfsusy/trunk/AnalysisV2/hadronic/src/common/mSuGraPlottingOps.cc
    return out

def loEffHisto(box, scale, htLower, htUpper) :
    s = hs.histoSpec(box = box, scale = scale, htLower = htLower, htUpper = htUpper)
    out = ratio(s["file"], s["afterDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi")
    return out

def nloXsHisto(scale = "1") :
    s = hs.histoSpec(box = "had", scale = scale)
    out = None
    for process in conf.processes() :
        h = ratio(s["file"], s["beforeDir"], "m0_m12_%s"%process, s["beforeDir"], "m0_m12_%s_noweight"%process)
        if out is None : out = h.Clone("nloXsHisto")
        else :           out.Add(h)
    out.SetDirectory(0)
    #see links in loXsHisto
    return out

def nloEffHisto(box, scale, htLower, htUpper) :
    s = hs.histoSpec(box = box, scale = scale, htLower = htLower, htUpper = htUpper)
    out = None
    for process in conf.processes() :
        h = ratio(s["file"], s["afterDir"], "m0_m12_%s"%process, s["beforeDir"], "m0_m12_%s_noweight"%process) #eff weighted by xs
        if out is None : out = h.Clone("nloEffHisto")
        else :           out.Add(h)
    out.SetDirectory(0)
    out.Divide(nloXsHisto(scale)) #divide by total xs
    return out

def smsXsHisto(model) :
    h = smsEffHisto(model = model, box = "had", scale = None, htLower = 875, htUpper = None)
    return h

def smsEffHisto(model, box, scale, htLower, htUpper) :
    s = hs.smsHistoSpec(model = model, box = box, htLower = htLower, htUpper = htUpper)
    #out = ratio(s["file"], s["afterDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi")
    out = ratio(s["file"], s["afterDir"], "m0_m12_mChi_noweight", s["beforeDir"], "m0_m12_mChi_noweight")
    return out

def effUncRelMcStatHisto(spec, beforeDirs = None, afterDirs = None) :
    def counts(dirs) :
        out = None
        for dir in dirs :
            name = "%s/m0_m12_mChi_noweight_0"%dir
            if out is None :
                out = f.Get(name)
            else :
                out.Add(f.Get(name))
        return out

    f = r.TFile(spec["file"])
    if f.IsZombie() : return None

    before = counts(beforeDirs)
    after  = counts(afterDirs)
    out = before.Clone("%s_%s"%(spec["file"], beforeDirs[0]))
    out.SetDirectory(0)
    out.Reset()

    for iBinX in range(1, 1+out.GetNbinsX()) :
        for iBinY in range(1, 1+out.GetNbinsY()) :
            for iBinZ in range(1, 1+out.GetNbinsZ()) :
                n = float(before.GetBinContent(iBinX, iBinY, iBinZ))
                m = float(after.GetBinContent(iBinX, iBinY, iBinZ))
                content = 1.0 if not m else 1.0/math.sqrt(m)
                out.SetBinContent(iBinX, iBinY, iBinZ, content)

    f.Close()
    return out

def mergedFile() :
    s = conf.switches()
    d = {}
    for item in fresh.noteArgs()+["ignoreSignalContaminationInMuonSample"] :
        d[item] = s[item]
    return "%s_%s%s"%(conf.stringsNoArgs()["mergedFileStem"], fresh.note(**d), ".root")

def mergePickledFiles() :
    example = xsHisto()
    #print "Here are the example binnings:"
    #print "x:",example.GetNbinsX(), example.GetXaxis().GetXmin(), example.GetXaxis().GetXmax()
    #print "y:",example.GetNbinsY(), example.GetYaxis().GetXmin(), example.GetYaxis().GetXmax()
    #print "z:",example.GetNbinsZ(), example.GetZaxis().GetXmin(), example.GetZaxis().GetXmax()
    histos = {}
    zTitles = {}
    
    for point in points() :
        fileName = conf.strings(*point)["pickledFileName"]
        if not os.path.exists(fileName) :
            print "skipping file",fileName            
        else :
            inFile = open(fileName)
            d = cPickle.load(inFile)
            inFile.close()
            for key,value in d.iteritems() :
                content,zTitle = value
                if key not in histos :
                    histos[key] = example.Clone(key)
                    histos[key].Reset()
                    zTitles[key] = zTitle
                histos[key].SetBinContent(point[0], point[1], point[2], content)
            os.remove(fileName)

    for key,histo in histos.iteritems() :
        histo.GetZaxis().SetTitle(zTitles[key])

    f = r.TFile(mergedFile(), "RECREATE")
    for histo in histos.values() :
        histo.Write()
    f.Close()

def fullPoints() :
    out = []
    s = conf.switches()
    h = xsHisto()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        if "xWhiteList" in s and s["xWhiteList"] and iBinX not in s["xWhiteList"] : continue
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                content = h.GetBinContent(iBinX, iBinY, iBinZ)
                min = s["minSignalXsForConsideration"]
                max = s["maxSignalXsForConsideration"]
                if min!=None and content<min : continue
                if max!=None and content>max : continue
                if s["fiftyGeVStepsOnly"] and ((h.GetXaxis().GetBinLowEdge(iBinX)/50.0)%1 != 0.0) : continue
                out.append( (iBinX, iBinY, iBinZ) )
    return out

def cachedPoints() :
    p = conf.switches()["listOfTestPoints"]
    if p : return p
    return fullPoints()

def points() :
    return _points

_points = cachedPoints()
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

def squareCanvas(margin = 0.18) :
    canvas = r.TCanvas("canvas","canvas",2)
    for side in ["Left", "Right", "Top", "Bottom"] :
        getattr(canvas, "Set%sMargin"%side)(margin)
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

def adjustHisto(h, zTitle = "") :
    h.SetStats(False)
    h.SetTitle("%s;%s"%(hs.histoTitle(), zTitle))
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

def printHoles(h) :
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            hole = h.GetBinContent(iBinX, iBinY)==0.0 and h.GetBinContent(iBinX, iBinY+1)!=0.0 and h.GetBinContent(iBinX, iBinY-1)!=0.0
            if hole : print "found hole: (%d, %d) = (%g, %g)"%(iBinX, iBinY, h.GetXaxis().GetBinCenter(iBinX), h.GetYaxis().GetBinCenter(iBinY))
    return
    
def printMaxes(h) :
    s = conf.switches()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            max = abs(h.GetBinContent(iBinX, iBinY)-s["masterSignalMax"])<2.0
            if max : print "found max: (%d, %d) = (%g, %g)"%(iBinX, iBinY, h.GetXaxis().GetBinCenter(iBinX), h.GetYaxis().GetBinCenter(iBinY))
    return
    
def setRange(var, ranges, histo, axisString) :
    if var not in ranges : return
    nums = ranges[var]
    getattr(histo,"Get%saxis"%axisString)().SetRangeUser(*nums[:2])
    if len(nums)==3 : r.gStyle.SetNumberContours(nums[2])
    if axisString=="Z" :
        maxContent = histo.GetBinContent(histo.GetMaximumBin())
        if maxContent>nums[1] :
            print "ERROR: histo truncated in Z (maxContent = %g, maxSpecified = %g) %s"%(maxContent, nums[1], histo.GetName())

def makeEfficiencyPlots(item = "sig10") :
    s = conf.switches()
    fileName = "%s/%s_eff.eps"%(conf.stringsNoArgs()["outputDir"], s["signalModel"])
    c = squareCanvas()
    spec = hs.histoSpecs()[item]
    num = loYieldHisto(spec, spec["350Dirs"]+spec["450Dirs"], lumi = 1.0)
    den = loYieldHisto(spec, [spec["beforeDir"]], lumi = 1.0)
    num.Divide(den)
    h2 = threeToTwo(num)

    if s["fillHolesInEfficiencyPlots"] : h2 = fillHoles(h2, 0)

    #output a root file
    f = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
    h2.Write("m0_m12_0")
    f.Close()

    #output a pdf
    adjustHisto(h2, zTitle = "analysis efficiency")
    model = s["signalModel"]
    ranges = conf.smsRanges()
    if len(model)==2 :
        setRange("smsXRange", ranges, h2, "X")
        setRange("smsYRange", ranges, h2, "Y")
        setRange("smsEffZRange", ranges, h2, "Z")
    h2.Draw("colz")
    printOnce(c, fileName)
    printHoles(h2)

def makeTopologyXsLimitPlots(logZ = False, name = "UpperLimit") :
    s = conf.switches()
    if not (s["signalModel"] in ["T1","T2"]) : return
    
    inFile = mergedFile()
    f = r.TFile(inFile)
    fileName = inFile.replace(".root","_xsLimit.eps")

    c = squareCanvas()
    h2 = threeToTwo(f.Get(name))
    if s["fillHolesInXsLimitPlot"] : h2 = fillHoles(h2, 1)
    
    adjustHisto(h2, zTitle = "%g%% C.L. upper limit on #sigma (pb)"%(100.0*s["CL"]))

    #output a root file
    g = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
    h2.Write()
    g.Close()
    
    ranges = conf.smsRanges()
    setRange("smsXRange", ranges, h2, "X")
    setRange("smsYRange", ranges, h2, "Y")
        
    h2.Draw("colz")
    graphs = rxs.graphs(h2, s["signalModel"], "LowEdge")

    if not logZ :
        setRange("smsXsZRangeLin", ranges, h2, "Z")
        printOnce(c, fileName)

        stuff = rxs.drawGraphs(graphs)
        printOnce(c, fileName.replace(".eps", "_refXs.eps"))
    else :
        c.SetLogz()
        setRange("smsXsZRangeLog", ranges, h2, "Z")
        printOnce(c, fileName.replace(".eps","_logZ.eps"))

        stuff = rxs.drawGraphs(graphs)
        printOnce(c, fileName.replace(".eps", "_refXs_logZ.eps"))

    printHoles(h2)
    
def makeEfficiencyUncertaintyPlots() :
    s = conf.switches()
    if not (s["signalModel"] in ["T1","T2"]) : return

    inFile = mergedFile()
    f = r.TFile(inFile)
    ranges = conf.smsRanges()

    def go(name, suffix, zTitle, zRangeKey) :
        fileName = "%s/%s_%s.eps"%(conf.stringsNoArgs()["outputDir"], s["signalModel"], suffix)
        c = squareCanvas()
        h2 = threeToTwo(f.Get(name))
        if s["fillHolesInEfficiencyPlots"] : h2 = fillHoles(h2, 0)
        adjustHisto(h2, zTitle = zTitle)
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
    s = conf.switches()
    text = r.TText()
    text.SetNDC()
    text.DrawText(0.1, 0.1, "file created at %s"%r.TDatime().AsString())
    text.DrawText(0.1, 0.30, "RQcd = %s"%(s["RQcd"] if s["RQcd"] else "[no form assumed]"))
    text.DrawText(0.1, 0.35, "REwk = %s"%(s["REwk"] if s["REwk"] else "[no form assumed]"))
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
        
def makeValidationPlots() :
    inFile = mergedFile()
    f = r.TFile(inFile)
    fileName = inFile.replace(".root",".ps")
    outFileName = fileName.replace(".ps",".pdf")
    canvas = utils.numberedCanvas()
    canvas.SetRightMargin(0.15)
    
    canvas.Print(fileName+"[")

    text1 = printTimeStamp()
    text2 = printLumis()
    canvas.Print(fileName)
    canvas.Clear()

    logZ = ["xs"]
    special = ["excluded", "upperLimit", "lowerLimit", "CLs", "CLb", "xs"]
    suppressed = []
    
    first = []
    names = sorted([key.GetName() for key in f.GetListOfKeys()])
    for item in special :
        for name in names :
            if item==name[:len(item)] :
                first.append(name)

    for item in first :
        names.remove(item)

    for name in first+names :
        h2 = threeToTwo(f.Get(name))
        if name=="UpperLimit" :
            printHoles(h2)
            printMaxes(h2)
        h2.SetStats(False)
        h2.SetTitle("%s%s"%(name, hs.histoTitle()))
        h2.Draw("colz")
        if not h2.Integral() :
            suppressed.append(name)
            continue
        canvas.SetLogz(name in logZ)
        if name=="xs" and name in logZ : h2.SetMinimum(1.0e-2)
        if "NLO_over_LO" in name :
            h2.SetMinimum(0.5)
            h2.SetMaximum(3.0)
        stuff = drawBenchmarks()

        if "excluded" in name :
            title = h2.GetTitle()
            h2.SetTitle("")
            eps = fileName.replace(".ps","_%s.eps"%name)
            super(utils.numberedCanvas, canvas).Print(eps)
            utils.epsToPdf(eps)
            h2.SetTitle(title)
        canvas.SetTickx()
        canvas.SetTicky()
        canvas.Print(fileName)

    #effMu/effHad
    if conf.switches()["effRatioPlots"] :
        for name in names :
            num = threeToTwo(f.Get(name))
            if name[:7]!="effmuon" : continue
            denName = name.replace("muon", "had")
            den = threeToTwo(f.Get(denName))
            num.Divide(den)
            num.SetStats(False)
            num.SetTitle("%s/%s%s;"%(name, denName, hs.histoTitle()))
            num.Draw("colz")
            if not num.Integral() : continue
            num.SetMinimum(0.0)
            num.SetMaximum(0.5)
            stuff = drawBenchmarks()
            canvas.Print(fileName)

    canvas.Clear()
    text3 = printSuppressed(suppressed)
    canvas.Print(fileName)
    
    canvas.Print(fileName+"]")
    os.system("ps2pdf %s %s"%(fileName, outFileName))
    os.remove(fileName)
    print "%s has been written."%outFileName

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
