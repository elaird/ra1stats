#!/usr/bin/env python

def switches() :
    d = {}

    d["dataYear"] = [2010, 2011][1]
    
    d["CL"] = [0.95, 0.90][:1]
    d["nToys"] = 200
    
    d["method"] = ["profileLikelihood", "feldmanCousins", "CLs", "CLsViaToys"][0]
    d["minSignalXsForConsideration"] = 1.0e-6
    d["maxSignalXsForConsideration"] = None

    d["hadTerms"]        = True
    d["hadControlTerms"] = True
    d["muonTerms"]       = True
    d["photTerms"]       = True
    d["mumuTerms"]       = False
    
    d["REwk"] = ["", "FallingExp", "Constant"][2]
    d["RQcd"] = ["FallingExp", "Zero"][1]
    
    d["nlo"] = False
    d["signalModel"] = ["tanBeta3", "tanBeta10", "tanBeta50", "T1", "T2"][1]
    d["drawBenchmarkPoints"] = True
    d["effRatioPlots"] = False
    #d["listOfTestPoints"] = [(6, 25, 1)]#LM1 (when tb=10)
    #d["listOfTestPoints"] = [(51, 44, 1)] #Filip's request
    #d["listOfTestPoints"] = [(11, 11, 1)] #Sue Ann's request
    d["listOfTestPoints"] = []

    d["computeExpectedLimit"] = False
    d["expectedPlusMinus"] = {"OneSigma": 1.0}#, "TwoSigma": 2.0}

    d["fillHolesInEffUncRelPdf"] = True
    d["fillHolesInEfficiencyPlots"] = True
    d["fillHolesInXsLimitPlot"] = True

    d["icfDefaultLumi"] = 100.0 #/pb
    d["icfDefaultNEventsIn"] = 10000
    
    d["subCmd"] = "qsub -q hep%s.q"%(["short", "medium", "long"][0])
    d["envScript"] = "icJob.sh"

    checkAndAdjust(d)
    return d

def data() :
    exec("from inputData import data%s as data"%str(switches()["dataYear"]))
    return data()

def checkAndAdjust(d) :
    assert d["signalModel"] in ["T1", "T2", "tanBeta3", "tanBeta10", "tanBeta50"]
    d["lateDivision"] = False
    if len(d["signalModel"])==2 :
        d["nlo"] = False
        d["lateDivision"] = True

    if d["method"]=="feldmanCousins" :
        d["fiftyGeVStepsOnly"] = True
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
    if switches["dataYear"]==2010 : out +="_2010"
    out += ".root"
    return out

def stringsNoArgs() :
    d = {}
    #output name options
    d["outputDir"]      = "output"
    d["logDir"]         = "log"
    d["logStem"]        = "%s/job"%d["logDir"]
    d["mergedFile"]     = mergedFile(d["outputDir"], switches())
    return d

def strings(xBin, yBin, zBin) :
    d = stringsNoArgs()
    #output name options
    d["tag"]               = "m0_%d_m12_%d_mZ_%d"%(xBin, yBin, zBin)
    d["pickledFileName"]   = "%s/%s.pickled"%(d["outputDir"], d["tag"])
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

def processes() :
    return ["gg", "sb", "ss", "sg", "ll", "nn", "ng", "bb", "tb", "ns"]
