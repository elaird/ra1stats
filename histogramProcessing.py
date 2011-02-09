#!/usr/bin/env python
import collections,cPickle,os
import configuration as conf
import data
import ROOT as r

def setupRoot() :
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)
    r.gErrorIgnoreLevel = 2000
    r.gROOT.SetBatch(True)
    
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
    h.Scale(lumi/100.0) #100/pb is the default normalization
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
    return func(conf.histoSpecs()["sig10"], conf.histoSpecs()["sig10"]["350Dirs"], data.numbers()["lumi"])

def mergePickledFiles() :
    example = exampleHisto()
    histos = {}

    for point in points() :
        fileName = conf.strings(*point)["plotFileName"]
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
    h = exampleHisto()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                content = h.GetBinContent(iBinX, iBinY, iBinZ)
                if content==0.0 : continue
                out.append( (iBinX, iBinY, iBinZ) )
    return out

def cachedPoints() :
    if conf.switches()["testPointsOnly"] :
        #return fullPoints()[:4]
        l = 20
        u = 30
        return [(l, l, 1), (l, u, 1), (u, l, 1), (u, u, 1)]
    else :
        return fullPoints()

def points() :
    return _points

_points = cachedPoints()

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

def efficiency(tight = True) :
    setupRoot()
    fileName = "%s/%s_eff.eps"%(conf.stringsNoArgs()["outputDir"], conf.switches()["signalModel"])
    canvas = r.TCanvas("canvas","canvas",2)
    for side in ["Left", "Right", "Top", "Bottom"] :
        getattr(canvas, "Set%sMargin"%side)(0.18)
    for item,spec in conf.histoSpecs().iteritems() :
        if item!="sig10" : continue
        num = loYieldHisto(spec, spec["350Dirs"]+spec["450Dirs"], lumi = 1.0)
        den = loYieldHisto(spec, [spec["beforeDir"]], lumi = 1.0)
        num.Divide(den)
        h2 = threeToTwo(num)
        h2.SetTitle("%s; selection efficiency"%spec["title"])
        h2.SetStats(False)
        h2.GetYaxis().SetTitleOffset(1.5)
        h2.GetZaxis().SetTitleOffset(1.5)
        h2.Draw("colz")
        canvas.Print(fileName)

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
