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

    def loYields(specs, dirs) :
        out = {}
        for key,spec in specs.iteritems() :
            out[key] = loYield(spec, dirs)
        return out

    out = collections.defaultdict(dict)

    specs = conf.histoSpecs()

    yields = {}
    for edge in [250, 300, 350, 450] :
        yields[edge] = loYields(specs, "%dDirs"%edge)

    norm = data.numbers()["lumi"]/100.0 #100/pb is the default normalization

    h = yields[350]["sig10"]
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                content = h.GetBinContent(iBinX, iBinY, iBinZ)
                if content==0.0 : continue
                bins = (iBinX, iBinY, iBinZ)
                for key in specs :
                    for binEdge,histoDict in yields.iteritems() :
                        out[bins]["%s_%d"%(key, binEdge)] = histoDict[key].GetBinContent(*bins)*norm if histoDict[key] else None
    return out

def cachedPoints() :
    if conf.switches()["testPointsOnly"] :
        small = {}
        for key,value in fullPoints().iteritems() :
            small[key] = value
            if len(small)>=4 : break
        return small
    else :
        return fullPoints()

def points() :
    return _points

_points = cachedPoints()
