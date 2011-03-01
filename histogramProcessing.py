#!/usr/bin/env python
import collections,cPickle,os
import configuration as conf
import data
import ROOT as r

def setupRoot() :
    r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)
    #r.gStyle.SetPadTickX(True)
    #r.gStyle.SetPadTickY(True)
    
def checkHistoBinning() :
    def axisStuff(axis) :
        return (axis.GetXmin(), axis.GetXmax(), axis.GetNbins())

    def properties(handles) :
        out = collections.defaultdict(list)
        for handle in handles :
            try:
                f = r.TFile(handle[0])
                h = f.Get("%s/%s"%(handle[1], handle[2]))
                out["x"].append(axisStuff(h.GetXaxis()))
                out["y"].append(axisStuff(h.GetYaxis()))
                f.Close()
            except AttributeError as ae :
                print handle
                raise ae
                
        return out
    
    def handles() :
        d = conf.histoSpecs()
        return [(value["file"], value["350Dirs"][0], value["loYield"]) for value in d.values()]

    for axis,values in properties(handles()).iteritems() :
        if len(set(values))!=1 :
            print "The %s binnings do not match: %s"%(axis, str(values))
            for h in handles() :
                print h,properties([h])
            assert False

def pdfUncHisto(spec) :
    f = r.TFile(spec["file"])
    assert not f.IsZombie()

    dir = spec["350Dirs"][0]
    hOld = f.Get("%s/%s"%(dir, spec["loYield"]))
    h = hOld.Clone("%s_%s_%s"%(spec["file"], dir, spec["loYield"]))
    h.SetDirectory(0)
    f.Close()
    return h

def loYieldHisto(spec, dirs, lumi, beforeSpec = None) :
    f = r.TFile(spec["file"])
    assert not f.IsZombie()

    h = None
    for dir in dirs :
        hOld = f.Get("%s/%s"%(dir, spec["loYield"]))
        if not h :
            h = hOld.Clone("%s_%s_%s"%(spec["file"], dir, hOld.GetName()))
        else :
            h.Add(hOld)
            
    h.SetDirectory(0)
    h.Scale(lumi/data.numbers()["icfDefaultLumi"])
    f.Close()
    return h

def nloYieldHisto(spec, dirs, lumi, beforeSpec = None) :
    def numerator(name) :
        out = None
        for dir in dirs :
            if out is None :
                out = f.Get("%s/m0_m12_%s_0"%(dir, name))
            else :
                out.Add(f.Get("%s/m0_m12_%s_0"%(dir, name)))
        return out

    f = r.TFile(spec["file"])
    beforeFile = f if not beforeSpec else r.TFile(beforeSpec["file"])
    beforeDir = spec["beforeDir"] if not beforeSpec else beforeSpec["beforeDir"]
    if f.IsZombie() : return None

    all = None
    #l = ["gg", "sb", "ss", "sg", "ll", "nn", "ng", "bb", "tb", "ns"]
    l = ["gg", "sb", "ss", "sg", "ll", "nn", "bb", "tb", "ns"]
    for name in l :
        num = numerator(name)
        num.Divide(beforeFile.Get("%s/m0_m12_%s_5"%(beforeDir, name)))
        
        if all is None :
            all = num.Clone("%s_%s_%s"%(spec["file"], dirs[0], name))
        else :
            all.Add(num)

    all.SetDirectory(0)
    all.Scale(lumi)
    f.Close()
    if beforeSpec : beforeFile.Close()
    return all

def exampleHisto() :
    func = nloYieldHisto if conf.switches()["nlo"] else loYieldHisto
    s = conf.histoSpecs()["sig10"]
    return func(s, s["350Dirs"]+s["450Dirs"], data.numbers()["lumi"])

def mergePickledFiles() :
    example = exampleHisto()
    histos = {}

    for point in points() :
        fileName = conf.strings(*point)["pickledFileName"]
        if not os.path.exists(fileName) :
            print "skipping file",fileName            
        else :
            inFile = open(fileName)
            stuff = cPickle.load(inFile)
            inFile.close()
            bin = tuple(stuff[:3])
            d = stuff[3]
            for key,value in d.iteritems() :
                if key not in histos :
                    histos[key] = example.Clone(key)
                    histos[key].Reset()
                histos[key].SetBinContent(bin[0], bin[1], bin[2], value)
            os.remove(fileName)

    f = r.TFile(conf.stringsNoArgs()["mergedFile"], "RECREATE")
    for histo in histos.values() :
        histo.Write()
    f.Close()

def fullPoints() :
    out = []
    s = conf.switches()
    h = exampleHisto()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                content = h.GetBinContent(iBinX, iBinY, iBinZ)
                min = s["minSignalEventsForConsideration"]
                max = s["maxSignalEventsForConsideration"]
                if min!=None and content<min : continue
                if max!=None and content>max : continue
                if s["fiftyGeVStepsOnly"] and ((h.GetXaxis().GetBinLowEdge(iBinX)/50.0)%1 != 0.0) : continue
                out.append( (iBinX, iBinY, iBinZ) )
    return out

def cachedPoints() :
    if conf.switches()["testPointsOnly"] :
        return conf.switches()["listOfTestPoints"]
    else :
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
    return h2

def squareCanvas() :
    canvas = r.TCanvas("canvas","canvas",2)
    for side in ["Left", "Right", "Top", "Bottom"] :
        getattr(canvas, "Set%sMargin"%side)(0.18)
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
    h.SetTitle("%s;%s"%(conf.histoTitle(), zTitle))
    h.GetYaxis().SetTitleOffset(1.5)
    h.GetZaxis().SetTitleOffset(1.5)

def printOnce(canvas, fileName) :
    canvas.Print(fileName)
    epsToPdf(fileName)

def printHoles(h) :
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            hole = h.GetBinContent(iBinX, iBinY)==0.0 and h.GetBinContent(iBinX, iBinY+1)!=0.0 and h.GetBinContent(iBinX, iBinY-1)!=0.0
            if hole : print "found hole: (%d, %d) = (%g, %g)"%(iBinX, iBinY, h.GetXaxis().GetBinCenter(iBinX), h.GetYaxis().GetBinCenter(iBinY))
    return
    
def setRange(var, ranges, histo, axisString) :
    if var not in ranges : return
    nums = ranges[var]
    getattr(histo,"Get%saxis"%axisString)().SetRangeUser(*nums[:2])
    if len(nums)==3 : r.gStyle.SetNumberContours(nums[2])
    if axisString=="Z" :
        maxContent = histo.GetBinContent(histo.GetMaximumBin())
        if maxContent>nums[1] :
            print "WARNING: histo truncated in Z (maxContent = %g, maxSpecified = %g) %s"%(maxContent, nums[1], histo.GetName())

def makeEfficiencyPlots(item = "sig10") :
    fileName = "%s/%s_eff.eps"%(conf.stringsNoArgs()["outputDir"], conf.switches()["signalModel"])
    c = squareCanvas()
    spec = conf.histoSpecs()[item]
    num = loYieldHisto(spec, spec["350Dirs"]+spec["450Dirs"], lumi = 1.0)
    den = loYieldHisto(spec, [spec["beforeDir"]], lumi = 1.0)
    num.Divide(den)
    h2 = threeToTwo(num)

    #output a root file
    f = r.TFile(fileName.replace(".eps",".root"), "RECREATE")
    h2.Write("m0_m12_0")
    f.Close()

    #output a pdf
    adjustHisto(h2, zTitle = "analysis efficiency")
    model = conf.switches()["signalModel"]
    ranges = conf.smsRanges()
    if len(model)==2 :
        setRange("smsXRange", ranges, h2, "X")
        setRange("smsYRange", ranges, h2, "Y")
        setRange("smsEffZRange", ranges, h2, "Z")
    h2.Draw("colz")
    printOnce(c, fileName)
    printHoles(h2)

def excludedGraph(h) :
    refXs = conf.referenceXsHistogram()
    f = r.TFile(refXs["file"])
    refHisto = f.Get(refXs["histo"]).Clone("%s_clone"%refXs["histo"])
    refHisto.SetDirectory(0)
    f.Close()

    out = r.TGraph()
    index = 0
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinLowEdge(iBinX)
        xs = refHisto.GetBinContent(refHisto.FindBin(x))
        for iBinY in range(1+h.GetNbinsY(), 1, -1) :
            y = h.GetYaxis().GetBinLowEdge(iBinY)
            xsLimit     = h.GetBinContent(iBinX, iBinY)
            xsLimitPrev = h.GetBinContent(iBinX, iBinY-1)
            if xs>xsLimit and xs<=xsLimitPrev :
                out.SetPoint(index, x, y)
                index +=1
    return out

def excludedHisto(h) :
    refXs = conf.referenceXsHistogram()
    f = r.TFile(refXs["file"])
    refHisto = f.Get(refXs["histo"]).Clone("%s_clone"%refXs["histo"])
    refHisto.SetDirectory(0)
    f.Close()

    out = h.Clone("%s_clone"%h.GetName())
    out.Reset()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinLowEdge(iBinX)
        xs = refHisto.GetBinContent(refHisto.FindBin(x))
        for iBinY in range(1+h.GetNbinsY(), 1, -1) :
            y = h.GetYaxis().GetBinLowEdge(iBinY)
            xsLimit = h.GetBinContent(iBinX, iBinY)
            #out.SetBinContent(iBinX, iBinY, 2.0*(xs>xsLimit)-1.0)
            out.SetBinContent(iBinX, iBinY, xs)
    return out

def makeTopologyXsLimitPlots(logZ = False, name = "UpperLimit") :
    s = conf.switches()
    if not (s["signalModel"] in ["T1","T2"]) : return
    
    inFile = conf.stringsNoArgs()["mergedFile"]
    f = r.TFile(inFile)
    fileName = inFile.replace(".root","_xsLimit.eps")

    c = squareCanvas()
    h2 = threeToTwo(f.Get(name))
    adjustHisto(h2, zTitle = "%g%% C.L. upper limit on #sigma (pb)"%(100.0*s["CL"]))

    ranges = conf.smsRanges()
    setRange("smsXRange", ranges, h2, "X")
    setRange("smsYRange", ranges, h2, "Y")
        
    h2.Draw("colz")
    g = excludedGraph(h2)
    hExcl = excludedHisto(h2)
    
    if not logZ :
        setRange("smsXsZRangeLin", ranges, h2, "Z")
        printOnce(c, fileName)

        hExcl.Draw("colz")
        printOnce(c, fileName.replace(".eps", "_refXs.eps"))
    else :
        c.SetLogz()
        setRange("smsXsZRangeLog", ranges, h2, "Z")
        printOnce(c, fileName.replace(".eps","_logZ.eps"))

        g.Draw("same")
        printOnce(c, fileName.replace(".eps", "_refXs_logZ.eps"))

    printHoles(h2)
    
def makeValidationPlots() :
    inFile = conf.stringsNoArgs()["mergedFile"]
    f = r.TFile(inFile)
    fileName = inFile.replace(".root",".ps")
    outFileName = fileName.replace(".ps",".pdf")
    canvas = r.TCanvas()
    canvas.SetRightMargin(0.15)
    
    canvas.Print(fileName+"[")
    special = ["ExclusionLimit", "UpperLimit"]
    first = []
    names = sorted([key.GetName() for key in f.GetListOfKeys()])
    for item in special :
        if item in names :
            names.remove(item)
            first.append(item)
            
    for name in first+names :
        h2 = threeToTwo(f.Get(name))
        h2.SetStats(False)
        h2.SetTitle("%s%s"%(name, conf.histoTitle()))
        h2.Draw("colz")
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

    psFileName = expFile.replace(".root", "_results.ps")
    rootFileName = psFileName.replace(".ps", ".root")
    outFile = r.TFile(rootFileName, "RECREATE")
    canvas = r.TCanvas()
    canvas.SetRightMargin(0.15)
    canvas.Print(psFileName+"[")
    ds = histo(obsFile, "ds")
    for item in ["Median", "MedianPlusOneSigma", "MedianMinusOneSigma"] :
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
