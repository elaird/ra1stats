#!/usr/bin/env python
import sys

import configuration as conf
import likelihoodSpec
import pickling
import workspace


def points():
    return [(sys.argv[i],
             int(sys.argv[i+1]),
             int(sys.argv[i+2]),
             int(sys.argv[i+3])) for i in range(4, len(sys.argv), 4)]


def description(key, cl=None):
    if key[:2] == "CL":
        return key
    if key[-5:] == "Limit" and cl:
        return "%g%% C.L. %s limit on XS factor" % (cl, key[:-5])
    else:
        return ""


def printDict(d, space=""):
    print "%s{" % space
    for key in sorted(d.keys()):
        value = d[key]
        out = '%s"%s":' % (space, key)
        if type(value) == dict:
            print out
            printDict(value, space="  ")
            continue
        elif (type(value) != tuple) and (type(value) != list):
            out += str(value)
        else:
            form = "%8.6f" if (key[:3] == "eff") else "%f"
            out += "[%s]" % (", ".join([form % item for item in value]))
        print out+","
    print "%s}" % space


def onePoint(likelihoodSpec=None, point=None):
    fileName = conf.directories.pickledFileName(*point)+".in"
    signal = pickling.readNumbers(fileName=fileName)
    printDict(signal)
    out = {}
    if signal["sumWeightInRange"]:
        #out.update(pickling.stuffVars(binsMerged=data.htBinLowerEdges(),
        #                              signal=signal))
        out.update(signal)
        eff = False
        for key, dct in signal.iteritems():
            if type(dct) != dict:
                continue
            if "effHadSum" in dct and dct["effHadSum"]:
                eff = True
                break
        if conf.limit.method() and eff:
            out.update(resultsMultiCL(likelihoodSpec=likelihoodSpec,
                                      signal=signal,
                                      )
                       )
    else:
        minSumWeightIn, maxSumWeightIn = conf.signal.sumWeightIn(model=point[0])
        warning = "WARNING: sumWeightIn = %g not in" % signal["sumWeightIn"]
        warning += " allowed range[ %s, %s ] " % (str(minSumWeightIn),
                                                  str(maxSumWeightIn))
        print warning
    return out


def resultsMultiCL(likelihoodSpec=None, signal=None):
    out = {}
    for cl in conf.limit.CL():
        out.update(resultsOneCL(likelihoodSpec=likelihoodSpec,
                                signal=signal,
                                cl=cl)
                   )
    return out


def formattedClsResults(results={}, cl=None, cl2=None):
    out = {}
    for key, value in results.iteritems():
        out[key] = (value, description(key))
        if conf.limit.plSeedParams()["usePlSeed"]:
            continue
        if key == "CLs" or ("Median" in key):
            threshold = 1.0 - cl
            outKey = "excluded_%s_%g" % (key, cl2)
            out[outKey] = (compare(results[key], threshold),
                           "is %s<%g ?" % (key, threshold))
    return out


def resultsOneCL(likelihoodSpec=None, signal=None, cl=None):
    out = {}
    cl2 = 100*cl
    f = workspace.foo(signalToTest=signal,
                      likelihoodSpec=likelihoodSpec,
                      rhoSignalMin=conf.limit.rhoSignalMin(),
                      fIniFactor=conf.limit.fIniFactor(),
                      )

    if "CLs" in conf.limit.method():
        if "Custom" in conf.limit.method():
            results = f.clsCustom(nToys=conf.limit.nToys(),
                                  testStatType=conf.limit.testStatistic(),
                                  )
        else:
            results = f.cls(cl=cl,
                            nToys=conf.limit.nToys(),
                            testStatType=conf.limit.testStatistic(),
                            calculatorType=conf.limit.calculatorType(),
                            plSeedParams=conf.limit.plSeedParams()
                            )
        out.update(formattedClsResults(results, cl, cl2))
    else:
        results = f.interval(cl=cl,
                             method=conf.limit.method(),
                             nIterationsMax=10,
                             )
        for key, value in results.iteritems():
            out["%s%g" % (key, cl2)] = (value, description(key, cl2))
        outKey = "excluded%g" % cl2
        out[outKey] = (compare(results["upperLimit"], 1.0),
                       "is (%g%% upper limit on XS factor)<1?" % cl2)
    return out


def compare(item, threshold):
    return 2.0*(item < threshold)-1.0


def go():
    specs = {}
    for model in conf.signal.models():
        specs[model.name] = likelihoodSpec.likelihoodSpec(model.name)

    for point in points():
        name = point[0]
        fileName = conf.directories.pickledFileName(*point)+".out"
        pickling.writeNumbers(fileName=fileName,
                              d=onePoint(likelihoodSpec=specs[name],
                                         point=point),
                              )

if False:
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else:
    go()
