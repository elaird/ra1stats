#!/usr/bin/env python
import sys
import configuration as conf
import pickling,workspace,likelihoodSpec

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def description(key, cl = None) :
    if key[:2]=="CL" : return key
    if key[-5:]=="Limit" and cl : return "%g%% C.L. %s limit on XS factor"%(cl, key[:-5])
    else : return ""

def printDict(d, space = "") :
    print "%s{"%space
    for key in sorted(d.keys()) :
        value = d[key]
        out = '%s"%s":'%(space, key)
        if type(value)==dict :
            print out
            printDict(value, space = "  ")
            continue
        elif type(value)!=tuple and type(value)!=list :
            out+=str(value)
        else :
            out += "[%s]"%(", ".join(["%s"%str(item) for item in value]))
        print out+","
    print "%s}"%space

def onePoint(switches = None, likelihoodSpec = None, point = None) :
    signal = pickling.readNumbers(fileName = conf.strings(*point)["pickledFileName"]+".in")
    printDict(signal)
    out = {}
    if signal["eventsInRange"] :
        #out.update(pickling.stuffVars(switches, binsMerged = data.htBinLowerEdges(), signal = signal))
        out.update(signal)
        eff = False
        for key,dct in signal.iteritems() :
            if type(dct)!=dict : continue
            if "effHadSum" in dct and dct["effHadSum"] :
                eff = True
                break
        if switches["method"] and eff : out.update(results(switches = switches, likelihoodSpec = likelihoodSpec, signal = signal))
    else :
        print "WARNING nEventsIn = %d not in allowed range[ %d, %d ] " % ( signal["nEventsIn"], switches["minEventsIn"], switches["maxEventsIn"] )
    return out

def results(switches = None, likelihoodSpec = None, signal = None) :
    out = {}
    for cl in switches["CL"] :
        cl2 = 100*cl
        f = workspace.foo(signal = signal, likelihoodSpec = likelihoodSpec,
                          extraSigEffUncSources = switches["extraSigEffUncSources"], rhoSignalMin = switches["rhoSignalMin"])

        if switches["method"]=="CLs" :
            results = f.cls(cl = cl, nToys = switches["nToys"], plusMinus = switches["expectedPlusMinus"], testStatType = switches["testStatistic"],
                            plSeed = switches["plSeedForCLs"], plNIterationsMax = switches["nIterationsMax"])
            for key,value in results.iteritems() :
                out[key] = (value, description(key))
                if switches["plSeedForCLs"] : continue
                if key=="CLs" or ("Median" in key) :
                    threshold = 1.0 - cl
                    out["excluded_%s_%g"%(key, cl2)] = (compare(results[key], threshold), "is %s<%g ?"%(key, threshold))
        elif switches["method"]=="CLsCustom" :
            results = f.clsCustom(nToys = switches["nToys"], testStatType = switches["testStatistic"])
            for key,value in results.iteritems() :
                out[key] = (value, description(key))
                if key=="CLs" or ("Median" in key) :
                    threshold = 1.0 - cl
                    out["excluded_%s_%g"%(key, cl2)] = (compare(results[key], threshold), "is %s<%g ?"%(key, threshold))
        elif not switches["computeExpectedLimit"] :
            results = f.interval(cl = cl, method = switches["method"], nIterationsMax = switches["nIterationsMax"])
            for key,value in results.iteritems() : out["%s%g"%(key, cl2)] = (value, description(key, cl2))
            out["excluded%g"%cl2] = (compare(results["upperLimit"], 1.0), "is (%g%% upper limit on XS factor)<1?"%cl2)
        else :
            d,nSuccesses = f.expectedLimit(cl = cl, nToys = switches["nToys"], plusMinus = switches["expectedPlusMinus"], makePlots = False)
            for key,value in d.iteritems() :
                out["%s%g"%(key, cl2)] = (value, description(key, cl2))
                out["excluded%s%g"%(key, cl2)] = (compare(value, 1.0), "is (%s %g%% upper limit on XS factor)<1?"%(key, cl2))
            out["nSuccesses%g"%cl2] = (nSuccesses, "# of successfully fit toys")
    return out

def compare(item, threshold) :
    return 2.0*(item<threshold)-1.0

def go() :
    s = conf.switches()
    for point in points() :
        pickling.writeNumbers(fileName = conf.strings(*point)["pickledFileName"]+".out",
                              d = onePoint(switches = s, likelihoodSpec = likelihoodSpec.spec(), point = point))

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
