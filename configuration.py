import collections,socket

batchHost = [ "FNAL", "IC" ][0]

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
            "nToys": 200,
            "testStatistic": 3,
            "calculatorType": ["frequentist", "asymptotic", "asymptoticNom"][0],
            "method": ["", "profileLikelihood", "feldmanCousins", "CLs", "CLsCustom"][3],
            "computeExpectedLimit": False,
            "expectedPlusMinus": {"OneSigma": 1.0},#, "TwoSigma": 2.0}
            }

def signal() :
    overwriteInput = collections.defaultdict(list)
    overwriteOutput = collections.defaultdict(list)
    overwriteOutput.update({"T1": [],
                            "T2": [ (34, 15, 1), (38, 9, 1), (29, 7, 1), ( 35, 11, 1) ],
                            "T2tt": [],
                            "T2bb":   [(10, 1, 1),  (15, 6, 1),  (16, 2, 1),  (16, 9, 1),  (18, 2, 1),  (20, 3, 1),
                                       (20, 11, 1), (20, 12, 1), (20, 14, 1), (21, 1, 1),  (21, 4, 1),  (22, 5, 1),
                                       (22, 15, 1), (23, 12, 1), (24, 10, 1), (24, 16, 1), (25, 9, 1),  (25, 15, 1),
                                       (25, 17, 1), (25, 19, 1), (26, 4, 1),  (26, 6, 1),  (26, 14, 1), (27, 10, 1),
                                       (28, 1, 1),  (28, 3, 1),  (28, 13, 1), (28, 15, 1), (28, 19, 1), (28, 22, 1),
                                       (29, 3, 1),  (29, 7, 1),  (29, 9, 1),  (29, 11, 1), (29, 15, 1), (29, 18, 1),
                                       (29, 21, 1), (31, 6, 1),  (31, 17, 1), (31, 20, 1), (31, 23, 1), (32, 5, 1),
                                       (32, 22, 1), (32, 26, 1), (33, 4, 1),  (33, 16, 1), (33, 20, 1), (33, 21, 1),
                                       (33, 25, 1), (34, 1, 1),  (34, 6, 1),  (34, 24, 1), (35, 2, 1),  (35, 5, 1),
                                       (35, 17, 1), (35, 22, 1), (36, 13, 1), (36, 19, 1), (36, 26, 1), (37, 1, 1),
                                       (37, 6, 1),  (38, 6, 1),  (38, 30, 1), (39, 5, 1),  (39, 9, 1),  (39, 13, 1),
                                       (39, 32, 1), (40, 3, 1),  (40, 5, 1),  (40, 11, 1), (40, 28, 1), (40, 32, 1),
                                       (40, 34, 1), (41, 11, 1), (41, 16, 1), (41, 20, 1), (41, 22, 1), (41, 23, 1),
                                       (41, 25, 1), (41, 27, 1), (41, 35, 1), (42, 21, 1), (42, 29, 1), (42, 31, 1),
                                       (42, 33, 1), (43, 13, 1), (43, 21, 1), (43, 31, 1), (44, 2, 1),  (44, 9, 1),
                                       (44, 17, 1), (44, 26, 1), (44, 31, 1), (44, 33, 1), (27, 13, 1), (29, 19, 1),
                                       (33, 5, 1),  (33, 22, 1), (33, 26, 1), (41, 28, 1), (26, 11, 1), (27, 11, 1),
                                       (26, 12, 1), (27, 12, 1), (30, 3, 1),  (31, 3, 1),  (30, 4, 1),  (31, 4, 1),
                                       (41, 1, 1),  (42, 1, 1),  (44, 6, 1),  (44, 7, 1),  (44, 12, 1), (44, 13, 1) ],
                            "T1bbbb": [],#(9, 2, 1), (13, 5, 1), (16, 6, 1), (16, 8, 1), (17, 3, 1), (19, 7, 1),
                                      #(21, 1, 1), (21, 4, 1), (21, 6, 1), (21, 11, 1), (21, 12, 1), (22, 4, 1),
                                      #(23, 6, 1), (24, 7, 1), (24, 17, 1), (27, 2, 1), (27, 19, 1), (28, 2, 1),
                                      #(28, 8, 1), (30, 5, 1), (30, 8, 1), (30, 20, 1), (31, 17, 1), (31, 21, 1),
                                      #(32, 9, 1), (32, 13, 1), (32, 22, 1), (33, 25, 1), (35, 2, 1), (35, 16, 1),
                                      #(35, 24, 1), (36, 14, 1), (36, 22, 1), (36, 30, 1), (38, 5, 1), (38, 7, 1),
                                      #(38, 20, 1), (39, 24, 1), (40, 8, 1), (40, 32, 1), (41, 5, 1), (41, 16, 1),
                                      #(41, 35, 1), (42, 7, 1), (42, 11, 1), (43, 23, 1), (44, 4, 1), (44, 10, 1),
                                      #(44, 38, 1), (9, 2, 1), (13, 5, 1), (16, 6, 1), (16, 8, 1), (17, 3, 1),
                                      #(19, 7, 1), (21, 1, 1), (21, 4, 1), (21, 6, 1), (21, 11, 1), (21, 12, 1),
                                      #(22, 4, 1), (23, 6, 1), (24, 7, 1), (24, 17, 1), (27, 2, 1), (27, 19, 1),
                                      #(28, 2, 1), (28, 8, 1), (30, 5, 1), (30, 8, 1), (30, 20, 1), (31, 17, 1),
                                      #(31, 21, 1), (32, 9, 1), (32, 13, 1), (32, 22, 1), (33, 25, 1), (35, 2, 1),
                                      #(35, 16, 1), (35, 24, 1), (36, 14, 1), (36, 22, 1), (36, 30, 1), (38, 5, 1),
                                      #(38, 7, 1), (38, 20, 1), (39, 24, 1), (40, 8, 1), (40, 32, 1), (41, 5, 1),
                                      #(41, 16, 1), (41, 35, 1), (42, 7, 1), (42, 11, 1), (43, 23, 1), (44, 4, 1),
                                      #(44, 10, 1), (44, 38, 1), (32, 21, 1) ],
                            "T1tttt": [(37, 2, 1), (37, 3, 1), (37, 4, 1),
                                       (37, 5, 1), (37, 6, 1), (37, 7, 1), ],
                            "T5zz": [(20, 9, 1), (21, 4, 1), (28, 6, 1), (35, 25, 1), (42, 22, 1), (37, 3, 1)],
                            })

    models = ["tanBeta10", "tanBeta40", "T5zz", "T1", "T1tttt", "T1bbbb", "T2", "T2tt", "T2bb", "TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8"]

    return {"minSignalXsForConsideration": 1.0e-6,
            "maxSignalXsForConsideration": None,
            "overwriteInput": overwriteInput,
            "overwriteOutput": overwriteOutput,
            "smsCutFunc": {"T1":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2tt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T2bb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T5zz":lambda iX,x,iY,y,iZ,z:(y<(x-200.1) and iZ==1 and x>399.9),
                           "T1bbbb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           "T1tttt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
                           },
            "nEventsIn":{""       :(9900., 10100.),
                         "T2tt"   :(1, None),
                         "T5zz"   :(5.0e3, None),
                         "T1bbbb"   :(1, None),
                         "T1tttt"   :(1, None),
                         "TGQ_0p0":(1, None),
                         "TGQ_0p2":(1, None),
                         "TGQ_0p4":(1, None),
                         "TGQ_0p8":(1, None)},
            "nlo": True,
            "nloToLoRatios": False,
            "drawBenchmarkPoints": True,
            "effRatioPlots": False,

            "signalModel": dict(zip(models, models))["T1bbbb"]
            }

def listOfTestPoints() :
    #out = [(181, 29, 1)]
    #out = [(33, 53, 1)]
    #out = [(61, 61, 1)]
    #out = [(13, 1, 1)]
    #out = [(17, 5, 1)]
    #out = [(37, 19, 1)]
    out = []
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
    if d["computeExpectedLimit"] : assert d["method"]=="profileLikelihood"

    d["rhoSignalMin"] = 0.0
    d["plSeedParams"] = {"usePlSeed": False}
    d["minEventsIn"],d["maxEventsIn"] = d["nEventsIn"][d["signalModel"] if d["signalModel"] in d["nEventsIn"] else ""]
    d["extraSigEffUncSources"] = []

    d["fIniFactor"] = 1.0
    d["isSms"] = "tanBeta" not in d["signalModel"]
    if d["isSms"] :
        d["fIniFactor"] = 0.05
        d["nlo"] = False
        d["rhoSignalMin"] = 0.1
        #d["plSeedParams"] = {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 7, "minFactor": 0.5, "maxFactor":2.0}
        d["plSeedParams"] = {"usePlSeed": True, "plNIterationsMax": 10, "nPoints": 10, "minFactor": 0.0, "maxFactor":3.0}
        #d["extraSigEffUncSources"] = ["effHadSumUncRelMcStats"]
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
