#!/usr/bin/env python
import collections
import configuration as conf
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
        return [
            (conf.mSuGra_FileSignal(),        conf.mSuGra_Dir2Signal(),     conf.mSuGra_ExampleHistSignal()),
            (conf.mSuGra_FileSys05(),         conf.mSuGra_Dir2Signal(),     conf.mSuGra_ExampleHistSignal()),
            (conf.mSuGra_FileSys2(),          conf.mSuGra_Dir2Signal(),     conf.mSuGra_ExampleHistSignal()),
            (conf.mSuGra_FileMuonControl(),   conf.mSuGra_DirMuonControl(), conf.mSuGra_HistMuonControl()  ),
            ]

    for axis,values in properties(handles()).iteritems() :
        assert len(set(values))==1,"The %s binnings do not match: %s"%(axis, str(values))
    
def fullPoints() :
    #return 
    f = r.TFile(conf.mSuGra_FileMuonControl())
    h = f.Get("%s/%s"%(conf.mSuGra_DirMuonControl(), conf.mSuGra_HistMuonControl()))
    out = []

    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            out.append( (iBinX, iBinY) )

    f.Close()
    return out

def cachedPoints() :
    if conf.testPointsOnly() :
        return [(10, 10), (10, 20), (20, 10), (20, 20)]
    else :
        return fullPoints()

def points() :
    return _points

_points = cachedPoints()
