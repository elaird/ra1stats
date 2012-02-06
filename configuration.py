import collections,socket

def locations() :
    s = "/vols/cms02/elaird1/" if "ic.ac.uk" in socket.gethostname() else "/home/elaird/71_stats_files/"
    return {"eff": "%s/20_yieldHistograms/2011/"%s,
            "xs" : "%s/25_sms_reference_xs_from_mariarosaria"%s}

def method() :
    return {"CL": [0.95, 0.90][:1],
            "nToys": 500,
            "testStatistic": 3,
            "calculatorType": ["frequentist", "asymptotic"][1],
            "method": ["", "profileLikelihood", "feldmanCousins", "CLs", "CLsCustom"][3],
            "computeExpectedLimit": False,
            "expectedPlusMinus": {"OneSigma": 1.0},#, "TwoSigma": 2.0}
            }

def signal() :
    overwriteInput = collections.defaultdict(list)
    overwriteOutput = collections.defaultdict(list)
    overwriteOutput.update({"T1": [(22, 4, 1), (26, 5, 1), (34, 16, 1), (40, 10, 1)],
                            "T2tt": [(22, 2, 1), (31, 17, 1), (9, 2, 1), (36, 23, 1)],
                            "T5zz": [(20, 9, 1), (21, 4, 1), (28, 6, 1), (35, 25, 1), (42, 22, 1), (37, 3, 1)],
                            })
    
    return {"minSignalXsForConsideration": 1.0e-6,
            "maxSignalXsForConsideration": None,
            "overwriteInput": overwriteInput,
            "overwriteOutput": overwriteOutput,
            "smsCutFunc": {"T1":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2tt":lambda iX,x,iY,y,iZ,z:True,
                           "T5zz":lambda iX,x,iY,y,iZ,z:(y<(x-200.1) and iZ==1 and x>399.9),
                           },
            "nEventsIn":{""       :(9900., 10100.),
                         "T2tt"   :(1, None),
                         "T5zz"   :(5.0e3, None),
                         "TGQ_0p0":(1, None),
                         "TGQ_0p2":(1, None),
                         "TGQ_0p4":(1, None),
                         "TGQ_0p8":(1, None)},
            "nlo": True,
            "nloToLoRatios": False,
            "drawBenchmarkPoints": True,
            "effRatioPlots": False,

            "signalModel": ["tanBeta10", "tanBeta40", "T1", "T2", "T2tt", "T5zz", "TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8"][0],
            }

def points() :
    return {#"listOfTestPoints": [[(29, 55, 1)], [(29, 25, 1)], [(181, 19, 1)], [(21, 1, 1)], [(39, 7, 1)], [(10, 3, 1), (10, 7, 1)], [(12, 3, 1), (12, 4, 1), (22, 5, 1)]][0],
            #"listOfTestPoints": [(29, 55, 1), (29, 25, 1), (181, 19, 1), (181, 29, 1), (33, 53, 1)][-1:]
            "listOfTestPoints": [],
            #"listOfTestPoints": [(32, 8, 1), (42, 2, 1)][-1:],
            #"listOfTestPoints": [(21, 61, 1), (51, 51, 1), (101, 33, 1), (181, 21, 1)],
            #"xWhiteList": [ [29, 181], [16, 32]],
            }

def other() :
    return {"icfDefaultLumi": 100.0, #/pb
            "icfDefaultNEventsIn": 10000,
            "subCmd": "qsub -q hep%s.q"%(["short", "medium", "long"][0]),
            "envScript": ["icJob.sh", "env.sh"][1],
            "nJobsMax": 2000}

def switches() :
    out = {}
    dicts = [method(), signal(), points(), other()]
    keys = sum([d.keys() for d in dicts], [])
    assert len(keys)==len(set(keys))
    for d in dicts : out.update(d)
    checkAndAdjust(out)
    return out

def checkAndAdjust(d) :
    if d["computeExpectedLimit"] : assert d["method"]=="profileLikelihood"

    d["rhoSignalMin"] = 0.0
    d["nIterationsMax"] = 1
    d["plSeedForCLs"] = False
    d["minEventsIn"],d["maxEventsIn"] = d["nEventsIn"][d["signalModel"] if d["signalModel"] in d["nEventsIn"] else ""]
    d["extraSigEffUncSources"] = []

    d["fIni"] = 1.0
    d["isSms"] = "tanBeta" not in d["signalModel"]
    if d["isSms"] :
        d["fIni"] = 0.1
        d["nlo"] = False
        d["rhoSignalMin"] = 0.1
        d["nIterationsMax"] = 10
        if d["method"]=="profileLikelihood" : print "WARNING: nIterationsMax=%d; PL limit is suspect"%d["nIterationsMax"]
        d["plSeedForCLs"] = True
        d["extraSigEffUncSources"] = ["effHadSumUncRelMcStats"]
    if d["method"]=="feldmanCousins" :
        d["fiftyGeVStepsOnly"] = True
    else :
        d["fiftyGeVStepsOnly"] = False
    return

def mergedFileStem(outputDir, switches) :
    out  = "%s/%s"%(outputDir, switches["method"])
    if "CLs" in switches["method"] :
        out += "_%s_TS%d"%(switches["calculatorType"], switches["testStatistic"])
    out += "_%s"%switches["signalModel"]
    out += "_nlo" if switches["nlo"] else "_lo"
    for item in ["computeExpectedLimit"] :
        if switches[item] : out += "_%s"%item
    return out

def stringsNoArgs() :
    d = {}
    #output name options
    d["outputDir"]      = "output"
    d["logDir"]         = "log"
    d["logStem"]        = "%s/job"%d["logDir"]
    d["mergedFileStem"] = mergedFileStem(d["outputDir"], switches())
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
    #out["LM0" ] = dict(zip(fields, [   200,    160,  -400,        10,         1]))
    #out["LM1" ] = dict(zip(fields, [    60,    250,     0,        10,         1]))
    out["LM2" ] = dict(zip(fields, [   185,    350,     0,        35,         1]))
    out["LM3" ] = dict(zip(fields, [   330,    240,     0,        20,         1]))
    #out["LM4" ] = dict(zip(fields, [   210,    285,     0,        10,         1]))
    #out["LM5" ] = dict(zip(fields, [   230,    360,     0,        10,         1]))
    #out["LM6" ] = dict(zip(fields, [    85,    400,     0,        10,         1]))
    out["LM7" ] = dict(zip(fields, [  3000,    230,     0,        10,         1]))
    out["LM8" ] = dict(zip(fields, [   500,    300,  -300,        10,         1]))
    out["LM9" ] = dict(zip(fields, [  1450,    175,     0,        50,         1]))
    out["LM10"] = dict(zip(fields, [  3000,    500,     0,        10,         1]))
    out["LM11"] = dict(zip(fields, [   250,    325,     0,        35,         1]))
    out["LM12"] = dict(zip(fields, [  2545,    247,  -866,        48,         1]))
    out["LM13"] = dict(zip(fields, [   270,    218,  -553,        40,         1]))
    
    #out["IM1" ] = dict(zip(fields, [   100,    510,     0,        10,         1]))
    #out["IM2" ] = dict(zip(fields, [   180,    510,     0,        10,         1]))
    #out["IM3" ] = dict(zip(fields, [   260,    450,     0,        10,         1]))
    out["IM4" ] = dict(zip(fields, [   820,    390,     0,        10,         1]))

    out["RM1" ] = dict(zip(fields, [   320,    520,     0,        10,         1]))
    out["RM2" ] = dict(zip(fields, [  1800,    280,     0,        10,         1]))
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
