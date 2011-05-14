#!/usr/bin/env python

def switches() :
    d = {}

    d["CL"] = 0.95
    d["method"] = ["profileLikelihood", "feldmanCousins"][0]

    d["nlo"] = True
    d["signalModel"] = ["tanBeta3", "tanBeta10", "tanBeta50", "T1", "T2"][0]
    d["listOfTestPoints"] = [(14, 9, 1)]
    
    d["computeExpectedLimit"] = False
    d["expectedPlusMinus"] = {"OneSigma": 1.0, "TwoSigma": 2.0}
    d["nToys"] = 1000
    d["debugMedianHisto"] = False

    d["fillHolesInEffUncRelPdf"] = True
    d["fillHolesInEfficiencyPlots"] = True
    d["fillHolesInXsLimitPlot"] = True
    
    d["fcAdditionalNToysFactor"] = 4
    d["fcSetNBins"] = 40
    d["fcUseProof"] = False

    d["debugOutput"] = False
    d["sourceFiles"] = []
    
    d["subCmd"] = "qsub -q hep%s.q"%(["short", "medium", "long"][0])
    d["envScript"] = "icJob.sh"

    checkAndAdjust(d)
    return d

def checkAndAdjust(d) :
    assert d["signalModel"] in ["T1", "T2", "tanBeta3", "tanBeta10", "tanBeta50"]
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

