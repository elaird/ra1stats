#!/usr/bin/env python
import sys

import configuration as conf
import likelihoodSpec
import pickling
import workspace

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
            form = "%8.6f" if key[:3]=="eff" else "%f"
            out += "[%s]"%(", ".join([form%item for item in value]))
        print out+","
    print "%s}"%space

def onePoint(likelihoodSpec=None, point=None):
    signal = pickling.readNumbers(fileName=conf.directories.pickledFileName(*point)+".in")
    printDict(signal)
    out = {}
    if signal["eventsInRange"]:
        #out.update(pickling.stuffVars(binsMerged = data.htBinLowerEdges(), signal = signal))
        out.update(signal)
        eff = False
        for key, dct in signal.iteritems():
            if type(dct) != dict:
                continue
            if "effHadSum" in dct and dct["effHadSum"]:
                eff = True
                break
        if conf.limit.method() and eff:
            out.update(results(likelihoodSpec=likelihoodSpec, signal=signal))
    else:
        minEventsIn, maxEventsIn = conf.signal.nEventsIn(conf.signal.model())
        print "WARNING nEventsIn = {0} not in allowed range[ {1}, {2} ] ".format(signal["nEventsIn"],
                                                                                 minEventsIn,
                                                                                 maxEventsIn)
    return out

def results(likelihoodSpec=None, signal=None):
    out = {}
    for cl in conf.limit.CL():
        cl2 = 100*cl
        f = workspace.foo(signalToTest=signal,
                          likelihoodSpec=likelihoodSpec,
                          extraSigEffUncSources=conf.limit.extraSigEffUncSources(),
                          rhoSignalMin=conf.limit.rhoSignalMin(),
                          fIniFactor=conf.limit.fIniFactor(),
                          )

        if conf.limit.method() == "CLs":
            results = f.cls(cl=cl,
                            nToys=conf.limit.nToys(),
                            testStatType=conf.limit.testStatistic(),
                            calculatorType=conf.limit.calculatorType(),
                            plSeedParams=conf.limit.plSeedParams()
                            )
            for key, value in results.iteritems():
                out[key] = (value, description(key))
                if conf.limit.plSeedParams()["usePlSeed"]:
                    continue
                if key == "CLs" or ("Median" in key):
                    threshold = 1.0 - cl
                    out["excluded_%s_%g"%(key, cl2)] = (compare(results[key], threshold),
                                                        "is %s<%g ?"%(key, threshold))
        elif conf.limit.method() == "CLsCustom":
            results = f.clsCustom(nToys=conf.limit.nToys(),
                                  testStatType=conf.limit.testStatistic(),
                                  )
            for key, value in results.iteritems():
                out[key] = (value, description(key))
                if key=="CLs" or ("Median" in key) :
                    threshold = 1.0 - cl
                    out["excluded_%s_%g"%(key, cl2)] = (compare(results[key], threshold),
                                                        "is %s<%g ?"%(key, threshold))
        else:
            results = f.interval(cl=cl,
                                 method=conf.limit.method(),
                                 nIterationsMax=10,
                                 )
            for key, value in results.iteritems():
                out["%s%g"%(key, cl2)] = (value, description(key, cl2))
            out["excluded%g"%cl2] = (compare(results["upperLimit"], 1.0),
                                     "is (%g%% upper limit on XS factor)<1?"%cl2)
    return out


def compare(item, threshold):
    return 2.0*(item<threshold)-1.0


def go():
    spec = likelihoodSpec.likelihoodSpec(conf.signal.model())

    for point in points() :
        pickling.writeNumbers(fileName=conf.directories.pickledFileName(*point)+".out",
                              d=onePoint(likelihoodSpec=spec, point=point),
                              )

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
