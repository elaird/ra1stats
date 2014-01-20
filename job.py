#!/usr/bin/env python
import sys

import configuration as conf
import likelihoodSpec
import workspace
import utils


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


def onePoint(likelihoodSpec=None, point=None):
    fileName = conf.directories.pickledFileName(*point)+".in"
    signal = utils.readNumbers(fileName=fileName)
    print signal
    if conf.limit.method() and signal.anyEffHad():
        return signal, resultsMultiCL(likelihoodSpec=likelihoodSpec,
                                      signal=signal,
                                      )


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
        specs[model.name] = likelihoodSpec.likelihoodSpec(model)

    for point in points():
        name = point[0]
        fileName = conf.directories.pickledFileName(*point)+".out"
        utils.writeNumbers(fileName,
                           onePoint(likelihoodSpec=specs[name],
                                    point=point),
                           )

if False:
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else:
    go()
