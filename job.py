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

def go() :
    s = conf.switches()
    data = conf.data()
    bins = data.htBinLowerEdges()

    for point in points() :
        xsHisto  = getattr(hp,"%sXsHisto"%("nlo" if s["nlo"] else "lo"))
        effHisto = getattr(hp,"%sEffHisto"%("nlo" if s["nlo"] else "lo"))
        
        x = xsHisto().GetBinContent(*point)
        signalEff = {}
        signalEff["had" ] = [effHisto(box = "had", scale = "1", htLower = htLower, htUpper = htUpper).GetBinContent(*point)\
                             for htLower, htUpper in zip(bins, list(bins[1:])+[None])]
        signalEff["muon"] = [0.0]*len(bins)
        #print x,signalEff
        
        f = fresh.foo(inputData = data,
                      REwk = s["REwk"],
                      RQcd = s["RQcd"],
                      signalXs = x, signalEff = signalEff,
                      )
        ul = f.upperLimit()
        
        out = {}
        out["upperLimit"] = (ul, "95% C.L. upper limit on XS factor")
        out["excluded"] = (2.0*(ul<1.0) - 1.0, "is (upper limit on XS factor)<1?")

        out["xs"] = (x, "#sigma (pb)")
        for i,bin in enumerate(bins) :
            for sel in ["had", "muon"] :
                out["eff%s%d"%(sel, bin)] = (signalEff[sel][i], "#epsilon of %s %d selection"%(sel, bin))
        writeNumbers(conf.strings(*point)["pickledFileName"], out)

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
