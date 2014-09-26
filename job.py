#!/usr/bin/env python
import sys

import configuration.directories
import configuration.limit
import configuration.signal
from driver import driver
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


def onePoint(llkName=None, point=None):
    fileName = configuration.directories.pickledFileName(*point)+".in"
    signal = utils.readNumbers(fileName=fileName)
    print signal
    if configuration.limit.method() and signal.anyEffHad():
        return signal, resultsMultiCL(llkName=llkName,
                                      signal=signal,
                                      )


def resultsMultiCL(llkName=None, signal=None):
    out = {}
    for cl in configuration.limit.CL():
        out.update(resultsOneCL(llkName=llkName,
                                signal=signal,
                                cl=cl)
                   )
    return out


def formattedClsResults(results={}, cl=None, cl2=None, usePlSeed=None):
    assert type(usePlSeed) is bool, usePlSeed
    out = {}
    for key, value in results.iteritems():
        out[key] = (value, description(key))
        if usePlSeed:
            continue
        if key == "CLs" or ("Median" in key):
            threshold = 1.0 - cl
            outKey = "excluded_%s_%g" % (key, cl2)
            out[outKey] = (compare(results[key], threshold),
                           "is %s<%g ?" % (key, threshold))
    return out


def resultsOneCL(llkName=None, signal=None, cl=None):
    out = {}
    cl2 = 100*cl
    f = driver(signalToTest=signal,
               whiteList=signal.categories(),
               llkName=llkName,
               )

    method = configuration.limit.method()
    plSeedParams = configuration.limit.plSeedParams(signal.binaryExclusion)
    fArgs = (cl, cl2, plSeedParams["usePlSeed"])
    if method == "nlls":
        return formattedClsResults(f.nlls(), *fArgs)
    elif "CLs" in method:
        if "Custom" in method:
            results = f.clsCustom(nToys=configuration.limit.nToys(),
                                  testStatType=configuration.limit.testStatistic(),
                                  )
        else:
            results = f.cls(cl=cl,
                            nToys=configuration.limit.nToys(),
                            testStatType=configuration.limit.testStatistic(),
                            calculatorType=configuration.limit.calculatorType(),
                            plSeedParams=plSeedParams,
                            )
        out.update(formattedClsResults(results, *fArgs))
    else:
        results = f.interval(cl=cl,
                             method=method,
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
    llk = {}
    for model in configuration.signal.models():
        llk[model.name] = model.llk

    for point in points():
        name = point[0]
        fileName = configuration.directories.pickledFileName(*point)+".out"
        utils.writeNumbers(fileName,
                           onePoint(llkName=llk[name],
                                    point=point),
                           )

if False:
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else:
    go()
