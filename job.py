#!/usr/bin/env python
import sys
import configuration as conf
import pickling,fresh

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def description(key, cl = None) :
    if key[:2]=="CL" : return key
    if key[-5:]=="Limit" and cl : return "%g%% C.L. %s limit on XS factor"%(cl, key[:-5])
    else : return ""

def printDict(d) :
    print "{"
    for key,value in d.iteritems() :
        out = '"%s":'%key
        if type(value)!=tuple and type(value)!=list :
            out+=str(value)
        else :
            out += "[%s]"%(", ".join(["%s"%str(item) for item in value]))
        print out+","
    print "}"

def onePoint(switches = None, data = None, likelihoodSpec = None, point = None) :
    signal = pickling.readNumbers(fileName = conf.strings(*point)["pickledFileName"]+".in")
    printDict(signal)
    out = {}
    eventsInRange = True
    if switches["minEventsIn"]!=None : eventsInRange &= switches["minEventsIn"]<=signal["nEventsIn"]
    if switches["maxEventsIn"]!=None : eventsInRange &= signal["nEventsIn"]<=switches["maxEventsIn"]
    if eventsInRange :
        out.update(pickling.stuffVars(switches, binsMerged = data.htBinLowerEdges(), signal = signal))
        if switches["method"] and bool(signal["effHadSum"])  : out.update(results(switches = switches, data = data, likelihoodSpec = likelihoodSpec, signal = signal))
    return out

def results(switches = None, data = None, likelihoodSpec = None, signal = None) :
    out = {}
    for cl in switches["CL"] :
        cl2 = 100*cl
        f = fresh.foo(inputData = data, signal = signal, likelihoodSpec = likelihoodSpec,
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
    data = conf.data()
    likelihoodSpec = conf.likelihood()
    for point in points() :
        pickling.writeNumbers(fileName = conf.strings(*point)["pickledFileName"]+".out", d = onePoint(switches = s, data = data, likelihoodSpec = likelihoodSpec, point = point))

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
