#!/usr/bin/env python

def switches() :
    d = {}

    d["dataYear"] = [2010, 2011][1]
    
    d["CL"] = 0.95
    d["method"] = ["profileLikelihood", "feldmanCousins"][0]
    d["minSignalEventsForConsideration"] = 1.0e-6
    d["maxSignalEventsForConsideration"] = None

    d["REwk"] = ["", "FallingExp", "Constant"][2]
    d["RQcd"] = ["FallingExp", "Zero"][1]
    
    d["nlo"] = False
    d["signalModel"] = ["tanBeta3", "tanBeta10", "tanBeta50", "T1", "T2"][1]
    #d["listOfTestPoints"] = [(6, 25, 1)]#LM1 (when tb=10)
    d["listOfTestPoints"] = []
    
    d["computeExpectedLimit"] = False
    d["expectedPlusMinus"] = {"OneSigma": 1.0, "TwoSigma": 2.0}
    d["nToys"] = 1000
    d["debugMedianHisto"] = False

    d["fillHolesInEffUncRelPdf"] = True
    d["fillHolesInEfficiencyPlots"] = True
    d["fillHolesInXsLimitPlot"] = True
    d["icfDefaultLumi"] = 100.0 #/pb
    d["icfDefaultNEventsIn"] = 10000
    
    d["fcAdditionalNToysFactor"] = 4
    d["fcSetNBins"] = 40
    d["fcUseProof"] = False

    d["debugOutput"] = False
    d["sourceFiles"] = []
    
    d["subCmd"] = "qsub -q hep%s.q"%(["short", "medium", "long"][0])
    d["envScript"] = "icJob.sh"

    checkAndAdjust(d)
    return d

def data() :
    exec("import data%s as inputData"%str(switches()["dataYear"]))
    return inputData.data()

def checkAndAdjust(d) :
    assert d["signalModel"] in ["T1", "T2", "tanBeta3", "tanBeta10", "tanBeta50"]
    assert not d["nlo"],"NLO is not yet supported."
    d["lateDivision"] = False
    if len(d["signalModel"])==2 :
        d["nlo"] = False
        d["minSignalEventsForConsideration"] = 1.0e-18
        d["maxSignalEventsForConsideration"] = None
        d["lateDivision"] = True

    d["suppressJobOutput"] = d["computeExpectedLimit"] and not d["debugMedianHisto"]
    if d["method"]=="feldmanCousins" :
        d["fiftyGeVStepsOnly"] = True
        d["minSignalEventsForConsideration"] = 10.0
        d["maxSignalEventsForConsideration"] = 26.0
    else :
        d["fiftyGeVStepsOnly"] = False
    return

def mergedFile(outputDir, switches) :
    out  = "%s/"%outputDir
    out += "_".join([switches["method"],
                     "REwk%s"%switches["REwk"],
                     "RQcd%s"%switches["RQcd"],
                     switches["signalModel"],
                     "nlo" if switches["nlo"] else "lo",
                     ])
    for item in ["computeExpectedLimit"] :
        if switches[item] : out += "_%s"%item
    out += ".root"
    return out

def stringsNoArgs() :
    d = {}
    #output name options
    d["outputDir"]      = "output"
    d["logDir"]         = "log"
    d["plotStem"]       = "%s/"%d["outputDir"]
    d["logStem"]        = "%s/job"%d["logDir"]
    d["mergedFile"]     = mergedFile(d["outputDir"], switches())
    return d

def strings(xBin, yBin, zBin) :
    d = stringsNoArgs()
    #output name options
    d["tag"]               = "m0_%d_m12_%d_mZ_%d"%(xBin, yBin, zBin)
    d["pickledFileName"]   = "%s_%s.pickled"%(d["plotStem"], d["tag"])
    return d

def benchmarkPoints() :
    out = {}
    fields =                       [  "m0",  "m12",  "A0", "tanBeta", "sgn(mu)"]
    out["LM0" ] = dict(zip(fields, [   200,    160,  -400,        10,         1]))
    out["LM1" ] = dict(zip(fields, [    60,    250,     0,        10,         1]))
    out["LM2" ] = dict(zip(fields, [   185,    350,     0,        35,         1]))
    out["LM3" ] = dict(zip(fields, [   330,    240,     0,        20,         1]))
    out["LM4" ] = dict(zip(fields, [   210,    285,     0,        10,         1]))
    out["LM5" ] = dict(zip(fields, [   230,    360,     0,        10,         1]))
    out["LM6" ] = dict(zip(fields, [    85,    400,     0,        10,         1]))
    out["LM7" ] = dict(zip(fields, [  3000,    230,     0,        10,         1]))
    out["LM8" ] = dict(zip(fields, [   500,    300,  -300,        10,         1]))
    out["LM9" ] = dict(zip(fields, [  1450,    175,     0,        50,         1]))
    out["LM10"] = dict(zip(fields, [  3000,    500,     0,        10,         1]))
    out["LM11"] = dict(zip(fields, [   250,    325,     0,        35,         1]))
    out["LM12"] = dict(zip(fields, [  2545,    247,  -866,        48,         1]))
    out["LM13"] = dict(zip(fields, [   270,    218,  -553,        40,         1]))
    
    out["IM1" ] = dict(zip(fields, [   100,    510,     0,        10,         1]))
    out["IM2" ] = dict(zip(fields, [   180,    510,     0,        10,         1]))
    out["IM3" ] = dict(zip(fields, [   260,    450,     0,        10,         1]))
    out["IM4" ] = dict(zip(fields, [   820,    390,     0,        10,         1]))

    return out

def scanParameters() :
    out = {}
    fields =                            ["A0", "tanBeta", "sgn(mu)"]
    out["tanBeta3" ] = dict(zip(fields, [   0,         3,         1]))
    out["tanBeta10"] = dict(zip(fields, [   0,        10,         1]))
    out["tanBeta50"] = dict(zip(fields, [   0,        50,         1]))
    return out
