import collections,socket

batchHost = [ "FNAL", "IC" ][1]

def locations() :
    dct = {
        "ic.ac.uk"   : "/vols/cms02/samr",
        "phosphorus" : "/home/elaird/71_stats_files/",
        "kinitos"    : "/home/hyper/Documents/02_ra1stats_files/",
        "fnal.gov"   : "/uscms_data/d1/samr/",
    }
    lst = filter(lambda x: socket.gethostname().endswith(x), dct.keys())
    assert len(lst) == 1, lst
    s = dct[ lst[0] ]

    return {"eff": "%s/20_yieldHistograms/2011/"%s,
            "xs" : "%s/25_sms_reference_xs_from_mariarosaria"%s}

def method() :
    return {"CL": [0.95, 0.90][:1],
            "nToys": 1000,
            "testStatistic": 3,
            "calculatorType": ["frequentist", "asymptotic", "asymptoticNom"][1],
            "method": ["", "profileLikelihood", "feldmanCousins", "CLs", "CLsCustom"][3],
            "binaryExclusionRatherThanUpperLimit": False,
            "fiftyGeVStepsOnly": False,
            }

def signal() :
    overwriteInput = collections.defaultdict(list)
    overwriteOutput = collections.defaultdict(list)
    overwriteOutput.update({"T1": [],
                            "T2": [(9,2,1)],
                            "T2tt": [],
                            "T2bb":   [
                                (16, 9, 1), (18, 2, 1), (20, 3, 1), (20, 14, 1), (21, 1, 1),
                                (22, 5, 1), (22, 15, 1), (23, 12, 1), (25, 17, 1), (26, 14, 1),
                                (27, 13, 1), (28, 13, 1), (28, 19, 1), (29, 7, 1), (29, 9, 1),
                                (29, 18, 1), (30, 4, 1), (31, 4, 1), (31, 6, 1), (31, 20, 1),
                                (31, 23, 1), (33, 4, 1), (33, 5, 1), (33, 16, 1), (33, 20, 1),
                                (33, 21, 1), (33, 22, 1), (33, 25, 1), (33, 26, 1), (35, 17, 1),
                                (36, 13, 1), (36, 26, 1), (39, 9, 1), (39, 32, 1), (40, 5, 1),
                                (40, 34, 1), (41, 11, 1), (41, 16, 1), (41, 20, 1), (41, 23, 1),
                                (41, 27, 1), (42, 21, 1), (42, 29, 1), (42, 31, 1), (42, 33, 1),
                                (43, 13, 1), (44, 6, 1), (44, 9, 1), (44, 17, 1), (44, 26, 1),
                                (44, 31, 1), (44, 33, 1), (20, 12, 1), (31,2,1)
                                ],
                            "T1bbbb": [ (36, 29, 1) ],
                            "T1tttt": [
                                (37, 2, 1), (37, 3, 1), (37, 4, 1), (37, 5, 1), (37, 6, 1),
                                (37, 7, 1), (29, 13, 1), (40, 24, 1), (44, 28, 1),
                                (27, 11, 1)
                                ],
                            "T5zz": [],
                            })
    models = ["tanBeta10", "tanBeta40", "T5zz", "T1", "T1tttt", "T1bbbb", "T2",
              "T2tt", "T2bb", "TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8",
              "T1tttt_2012"]

    graphBlackLists = {}
    for key in [ "UpperLimit", "ExpectedUpperLimit" ] + [ "ExpectedUpperLimit_%+d_Sigma" % i for i in [-1,1] ] :
        graphBlackLists[key] = collections.defaultdict(list)

    graphBlackLists["UpperLimit"].update({"T1" : [ (1000,125), (1000,175) ]})

    graphBlackLists["UpperLimit"].update({"T2" : [ (800,200) ]})
    graphBlackLists["ExpectedUpperLimit_-1_Sigma"].update({"T2" : [ (875,150) ]})

    graphBlackLists["UpperLimit"].update({"T2bb" : [ (500,100), (500,250),
        (575,125), (500, 150), (525,200), (500,200) ]})
    graphBlackLists["ExpectedUpperLimit_-1_Sigma"].update({"T2bb" : [ (500,250),
        (525,225), (525,100), (525,200)]})
    graphBlackLists["ExpectedUpperLimit_+1_Sigma"].update({"T2bb" : [ (475, 75), ]})

    graphBlackLists["UpperLimit"].update({"T2tt" : [ (550,100), (525,150), (450,50), (475,100) ]})
    graphBlackLists["ExpectedUpperLimit_-1_Sigma"].update({"T2tt" : [ (450,50), (375,50)]})

    graphBlackLists["UpperLimit"].update({"T1bbbb" : [ (1050,200), (1050,250),
        (1075,650), (1050,400), (1025,475), (975,650), (1050,450), (950,625),
        (975,550), (1000,525), (1025,525), (1050,475), (1000,575), (1000,625),
        (1025,625), (1050,600)]})
    graphBlackLists["ExpectedUpperLimit_-1_Sigma"].update({"T1bbbb" :
        [(1050,75), (1100,200), (975,625), (875, 625), (925,575), (900,575),
        (875,575), (850,575), (825,575), (1025,575), (1050,450) ]})
    graphBlackLists["ExpectedUpperLimit"].update({"T1bbbb" : [ (1025,475),
        (1025,450) ]})

    graphBlackLists["UpperLimit"].update({"T1tttt" : [ (550,150), (800,350),
        (750,300), (800,300), (800,250), (825,200), (825,250), (875,300) ]})
    graphBlackLists["ExpectedUpperLimit"].update({"T1tttt" : [(825,175)] })
    graphBlackLists["ExpectedUpperLimit_+1_Sigma"].update({"T1tttt" :
        [(675,175), (750, 125) ]})
    graphBlackLists["ExpectedUpperLimit_-1_Sigma"].update({"T1tttt" :
        [(875,350), (900,150), (900,200), (1000,225), (925,225), (950,275),
        (950,300), (900,325), (850,325)]})

    return {"minSignalXsForConsideration": 1.0e-6,
            "maxSignalXsForConsideration": None,
            "overwriteInput": overwriteInput,
            "overwriteOutput": overwriteOutput,
            "graphBlackLists": graphBlackLists,
            "smsCutFunc": {"T1":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2tt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2bb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T5zz":lambda iX,x,iY,y,iZ,z:(y<(x-200.1) and iZ==1 and x>399.9),
                           "T1bbbb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T1tttt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T1tttt_2012":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           },
            "nEventsIn":{""       :(9900., 10100.),
                         "T1"   :(1, None),
                         "T2"   :(1, None),
                         "T2bb"   :(1, None),
                         "T2tt"   :(1, None),
                         "T1bbbb"   :(1, None),
                         "T1tttt"   :(1, None),
                         "T5zz"   :(5.0e3, None),
                         "TGQ_0p0":(1, None),
                         "TGQ_0p2":(1, None),
                         "TGQ_0p4":(1, None),
                         "TGQ_0p8":(1, None),
                         "T1tttt_2012"   :(1, None),},
            "nlo": True,
            "nloToLoRatios": False,
            "drawBenchmarkPoints": True,
            "effRatioPlots": False,

            "signalModel": dict(zip(models, models))["T2tt"]
            }

def listOfTestPoints() :
    #out = [(181, 29, 1)]
    #out = [(33, 53, 1)]
    #out = [(61, 61, 1)]
    #out = [(13, 3, 1)]
    #out = [(17, 5, 1)]
    #out = [(37, 19, 1)]
    #out = [(19,5,1)]
    #out = [(15,3,1)]
    out = [(13,1,1)]
    return out

def xWhiteList() :
    return []

def other() :
    return {"icfDefaultLumi": 100.0, #/pb
            "icfDefaultNEventsIn": 10000,
            "subCmd": getSubCmds(),
            "envScript": "env.sh",
            "nJobsMax": getMaxJobs()}

def switches() :
    out = {}
    lst = [method(), signal(), other()]
    for func in ["xWhiteList", "listOfTestPoints"] :
        lst.append( {func: eval(func)()} )
    keys = sum([dct.keys() for dct in lst], [])
    assert len(keys)==len(set(keys))
    for dct in lst : out.update(dct)
    checkAndAdjust(out)
    return out

def getMaxJobs() :
    return {
        "IC": 2000,
        "FNAL": 0,
    }[batchHost]

def getSubCmds() :
    return {
        "IC": "qsub -o /dev/null -e /dev/null -q hep{queue}.q".format(queue=["short", "medium", "long"][0]),
        "FNAL": "condor_submit"
    }[batchHost]

def checkAndAdjust(d) :
    d["isSms"] = "tanBeta" not in d["signalModel"]
    if d["isSms"] :
        d["nlo"] = False

    binary = d["binaryExclusionRatherThanUpperLimit"]
    d["rhoSignalMin"] = 0.0 if binary else 0.1
    d["fIniFactor"] = 1.0 if binary else 0.05
    d["extraSigEffUncSources"] = [] if binary else [] #["effHadSumUncRelMcStats"]

    d["plSeedParams"] = {"usePlSeed": False} if binary else \
                        {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 10, "minFactor": 0.0, "maxFactor":3.0}
                        #{"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 7, "minFactor": 0.5, "maxFactor":2.0}

    d["minEventsIn"],d["maxEventsIn"] = d["nEventsIn"][d["signalModel"] if d["signalModel"] in d["nEventsIn"] else ""]
    return

def mergedFileStem(outputDir, switches) :
    out  = "%s/%s"%(outputDir, switches["method"])
    if "CLs" in switches["method"] :
        out += "_%s_TS%d"%(switches["calculatorType"], switches["testStatistic"])
    out += "_%s"%switches["signalModel"]
    out += "_nlo" if switches["nlo"] else "_lo"
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
