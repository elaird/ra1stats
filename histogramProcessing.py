#!/usr/bin/env python
import configuration as conf
import ROOT as r

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
