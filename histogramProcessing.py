#!/usr/bin/env python
import collections
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
    
def fullPoints() :
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
        return fullPoints()[:4]        
    else :
        return fullPoints()

def points() :
    return _points

_points = cachedPoints()
