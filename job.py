#!/usr/bin/env python
import sys,cPickle,fresh
import configuration as conf
import histogramSpecs as hs
import histogramProcessing as hp

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def writeNumbers(fileName = None, d = None) :
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()

def xs(point) :
    return hp.loXsHisto().GetBinContent(*point)

def xsFail(point) :
    spec = hs.histoSpecs()["sig10"]
    lumi = 1.0
    h = hp.loYieldHisto(spec, [spec["beforeDir"]], lumi = lumi)
    eventYield = h.GetBinContent(*point)
    return eventYield/lumi

def eff(point, label) :
    out = [0.0, 0.0]
    spec = hs.histoSpecs()[label]

    for dir in [spec["350Dirs"], spec["450Dirs"]] :
        num = hp.loYieldHisto(spec, dir, lumi = 1.0)
        den = hp.loYieldHisto(spec, [spec["beforeDir"]], lumi = 1.0)
        num.Divide(den)
        out.append(num.GetBinContent(*point))
    return tuple(out)
    
def go() :
    for point in points() :
        x = xs(point)
        signalEff = {}
        signalEff["had" ] = eff(point, "sig10")
        signalEff["muon"] = eff(point, "muon")
        
        f = fresh.foo(REwk = ["", "FallingExp", "Constant"][0],
                      RQcd = ["FallingExp", "Zero"][0],
                      signalXs = x, signalEff = signalEff,
                      )
        ul = f.upperLimit()

        out = {}
        out["upperLimit"] = ul
        out["xs"] = x
        for i,bin in enumerate([250, 300, 350, 450]) :
            for sel in ["had", "muon"] :
                out["eff%s%d"%(sel, bin)] = signalEff[sel][i]
        writeNumbers(conf.strings(*point)["pickledFileName"], out)

profile = False
if profile :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
