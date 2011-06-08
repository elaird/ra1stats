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

def description(key, cl = None) :
    if key[:2]=="CL" : return key
    if key[-5:]=="Limit" : return "%g%% C.L. %s limit on XS factor"%(cl, key[:-5])

def signalEff(switches, data, binsInput, binsMerged, point) :
    out = {}
    for item in ["effHad", "effMuon"] :
        box = item.replace("eff","").lower()
        out[item] = [hp.effHisto(box = box, scale = "1", htLower = htLower, htUpper = htUpper).GetBinContent(*point)\
                     for htLower, htUpper in zip(binsInput, list(binsInput[1:])+[None])]
        out[item] = data.mergeEfficiency(out[item])
    #out["muon"] = tuple([0.0]*len(out["muon"])); print "HACK: muon sig eff set to 0"
    return out

def stuffVars(binsMerged, signal) :
    out = {}
    out["xs"] = (signal["xs"], "#sigma (pb)")
    for i,bin in enumerate(binsMerged) :
        for sel in ["effHad", "effMuon"] :
            out["%s%d"%(sel, bin)] = (signal[sel][i], "#epsilon of %s %d selection"%(sel, bin))
    return out

def go() :
    s = conf.switches()
    data = conf.data()
    binsInput = data.htBinLowerEdgesInput()
    binsMerged = data.htBinLowerEdges()
    
    for point in points() :
        signal = {}
        signal["xs"] = hp.xsHisto().GetBinContent(*point)
        for key,value in signalEff(s, data, binsInput, binsMerged, point).iteritems() :
            signal[key] = value

        out = stuffVars(binsMerged, signal)

        if "CLs" in s["method"] :
            f = fresh.foo(inputData = data, REwk = s["REwk"], RQcd = s["RQcd"], signal = signal)
            results = f.cls(method = s["method"], nToys = s["nToys"])
            for key,value in results.iteritems() : out[key] = (value, description(key))
            for cl in s["CL"] :
                value = 1.0 - cl
                out["excluded%g"%(100*cl)] = (2.0*(results["CLs"]<value) - 1.0, "is CLs<%g ?"%value)
        else :
            for cl in s["CL"] :
                f = fresh.foo(inputData = data, REwk = s["REwk"], RQcd = s["RQcd"], signal = signal)
                results = f.interval(cl = cl, method = s["method"])
                cl2 = 100*cl
                for key,value in results.iteritems() : out["%s%g"%(key, cl2)] = (value, description(key, cl2))
                out["excluded%g"%cl2] = (2.0*(results["upperLimit"]<1.0) - 1.0, "is (%g%% upper limit on XS factor)<1?"%cl2)
        writeNumbers(conf.strings(*point)["pickledFileName"], out)

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
