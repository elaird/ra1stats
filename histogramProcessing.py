#!/usr/bin/env python
import collections,cPickle,os
import configuration as conf
import data
import ROOT as r

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

def efficiency() :
    print conf.histoSpecs()
