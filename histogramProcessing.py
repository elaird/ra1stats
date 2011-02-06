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
            f = r.TFile(handle[0])
            h = f.Get("%s/%s"%(handle[1], handle[2]))
            out["x"].append(axisStuff(h.GetXaxis()))
            out["y"].append(axisStuff(h.GetYaxis()))
            f.Close()
        return out
    
    def handles() :
        d = conf.histoSpecs()
        return [(value["file"], value["350Dirs"][0], value["loYield"]) for value in d.values()]

    for axis,values in properties(handles()).iteritems() :
        assert len(set(values))==1,"The %s binnings do not match: %s"%(axis, str(values))
    
def loYield(spec, dirs) :
    out = None
    f = r.TFile(spec["file"])
    for iDir,dir in enumerate(spec[dirs]) :
        name = "%s_%s_%s"%(spec["file"], dir, spec["loYield"])
        h = f.Get("%s/%s"%(dir, spec["loYield"]))
        if not iDir :
            out = h.Clone(name)
            out.SetDirectory(0)
        else :
            out.Add(h)
    f.Close()
    return out

def mergePickledFiles() :
    example = loYield(conf.histoSpecs()["sig10"], "350Dirs")
    histos = {}

    for point in points() :
        fileName = conf.strings(*point)["plotFileName"]
        if os.path.exists(fileName) :
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
        else :
            print "skipping file",fileName

    f = r.TFile(conf.stringsNoArgs()["mergedFile"], "RECREATE")
    for histo in histos.values() :
        histo.Write()
    f.Close()

def fullPoints() :
    out = []
    h = loYield(conf.histoSpecs()["sig10"], "350Dirs")
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
        return [(20, 20, 1), (20, 30, 1), (30, 20, 1), (30, 30, 1)]
    else :
        return fullPoints()

def points() :
    return _points

_points = cachedPoints()
