#!/usr/bin/env python
import sys,cPickle,fresh
import configuration as conf
import histogramProcessing as hp

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def writeNumbers(fileName = None, d = None) :
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()

def description(key) :
    if key[:2]=="CL" : return key
    if key[-5:]=="Limit" : return "%g%% C.L. %s limit on XS factor"%(100*conf.switches()["CL"], key[:-5])

def go() :
    s = conf.switches()
    data = conf.data()
    binsInput = data.htBinLowerEdgesInput()
    binsMerged = data.htBinLowerEdges()
    
    for point in points() :
        xsHisto  = getattr(hp,"%sXsHisto"%("nlo" if s["nlo"] else "lo"))
        effHisto = getattr(hp,"%sEffHisto"%("nlo" if s["nlo"] else "lo"))
        
        x = xsHisto().GetBinContent(*point)
        signalEff = {}
        signalEff["had" ] = [effHisto(box = "had", scale = "1", htLower = htLower, htUpper = htUpper).GetBinContent(*point)\
                             for htLower, htUpper in zip(binsInput, list(binsInput[1:])+[None])]
        signalEff["muon"] = [0.0]*len(binsInput)

        for item in ["had","muon"] :
            signalEff[item] = data.mergeEfficiency(signalEff[item])
        #print x,signalEff
        
        f = fresh.foo(inputData = data,
                      REwk = s["REwk"],
                      RQcd = s["RQcd"],
                      signalXs = x, signalEff = signalEff,
                      )
        results = f.upperLimit(cl = s["CL"], method = s["method"])

        out = {}
        for key,value in results.iteritems() :
            out[key] = (value, description(key))

        if "CLs" in out :
            value = 1.0 - s["CL"]
            out["excluded"] = (2.0*(results["CLs"]<value) - 1.0, "is CLs<%g ?"%value)
        else :
            out["excluded"] = (2.0*(results["upperLimit"]<1.0) - 1.0, "is (upper limit on XS factor)<1?")

        out["xs"] = (x, "#sigma (pb)")
        for i,bin in enumerate(binsMerged) :
            for sel in ["had", "muon"] :
                out["eff%s%d"%(sel, bin)] = (signalEff[sel][i], "#epsilon of %s %d selection"%(sel, bin))
        writeNumbers(conf.strings(*point)["pickledFileName"], out)

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
