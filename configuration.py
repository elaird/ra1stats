import socket,patches
import likelihoodSpec as ls

batchHost = [ "FNAL", "IC" ][1]

def locations() :
    dct = {
        "ic.ac.uk"   : "/vols/cms02/elaird1",
        "phosphorus" : "/home/elaird/71_stats_files/",
        "kinitos"    : "/home/hyper/Documents/02_ra1stats_files/",
        "fnal.gov"   : "/uscms_data/d2/elaird/",
        "brown02"    : "/vols/cms02/elaird1"
    }
    lst = filter(lambda x: socket.gethostname().endswith(x), dct.keys())
    assert len(lst) == 1, lst
    s = dct[ lst[0] ]

    return {"eff": "%s/20_yieldHistograms/2012/"%s,
            "xs" : "%s/25_sms_reference_xs_from_mariarosaria"%s}

def method() :
    return {"CL": [0.95, 0.90][:1],
            "nToys": 1000,
            "testStatistic": 3,
            "calculatorType": ["frequentist", "asymptotic", "asymptoticNom"][0],
            "method": ["", "profileLikelihood", "feldmanCousins", "CLs", "CLsCustom"][1],
            "binaryExclusionRatherThanUpperLimit": False,
            "multiplesInGeV": None,
            }

def ignoreEff() :
    return {"ignoreEff":{"T1":["muon"], "T2":["muon"], "T2bb":["muon"]}}

def effUncRel() :
    return {"effUncRel":{"T1":0.140,
                         "T2":0.134,
                         "T2bb":0.131,
                         "T2tt":0.139,
                         "T1bbbb":0.160,
                         "T1tttt":0.230,
                         }}

def signal() :
    models = ["tanBeta10", "tanBeta40", "T5zz", "T1", "T1tttt", "T1bbbb", "T2",
              "T2tt", "T2bb", "TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8",
              "T1tttt_ichep", "T2bw"]

    variations = ["default", "up", "down"]
    out = {}
    for item in ["overwriteInput", "overwriteOutput",
                 "graphBlackLists", "graphReplacePoints", "graphAdditionalPoints",
                 "cutFunc", "nEventsIn", "curves"] :
        out[item] = getattr(patches, item)()
    out["drawBenchmarkPoints"] = True
    out["effRatioPlots"] = False
    out["xsVariation"] = dict(zip(variations, variations))["default"]
    out["signalModel"] = dict(zip(models, models))["T1bbbb"]
    return out

def likelihoodSpec() :
    dct = {"T1"          : {"whiteList":["0b_ge4j"]},
           "T2"          : {"whiteList":["0b_le3j"]},
           "T2bb"        : {"whiteList":["1b_le3j", "2b_le3j"]},
           "T2tt"        : {"whiteList":["1b_ge4j", "2b_ge4j"]},
           "T1bbbb"      : {"whiteList":["2b_ge4j", "3b_ge4j", "ge4b_ge4j"]},
           "T1tttt"      : {"whiteList":["2b_ge4j", "3b_ge4j", "ge4b_ge4j"]},
           "T1tttt_ichep": {"whiteList":["2b", "ge3b"], "dataset":"2012ichep"},
           }
    return ls.spec(**dct[signal()["signalModel"]])

def whiteListOfPoints() : #GeV
    out = []
    #out += [(700.0, 300.0)]  #T1
    out += [(900.0, 500.0)]  #T1bbbb
    #out += [(850.0, 250.0)]  #T1tttt
    #out += [( 450.0,  20.0)]  #T2tt
    #out += [( 550.0,  20.0)]  #T2tt
    #out += [( 400.0,  0.0)]  #T2tt
    #out += [( 420.0,  20.0)]  #T2tt
    #out += [( 500.0, 150.0)]  #T2bb
    #out += [( 600.0, 250.0)]  #T2
    return out

def other() :
    return {"icfDefaultLumi": 100.0, #/pb
            "icfDefaultNEventsIn": 10000,
            "subCmd": getSubCmds(),
            "subCmdFormat": "qsub -o /dev/null -e /dev/null -q hep%s.q",
            "queueSelection" : ["short", "medium", "long"][0:1],
            "envScript": "env.sh",
            "nJobsMax": getMaxJobs()}

def switches() :
    out = {}
    lst = [method(), signal(), ignoreEff(), effUncRel(), other()]
    for func in ["whiteListOfPoints"] :
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
        "IC": "qsub -o /dev/null -e /dev/null -q hep{queue}.q".format(queue=["short", "medium", "long"][1]),
        "FNAL": "condor_submit"
    }[batchHost]

def checkAndAdjust(d) :
    d["isSms"] = "tanBeta" not in d["signalModel"]
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
    if switches["binaryExclusionRatherThanUpperLimit"] :
        out += "_binaryExcl"
    out += "_%s"%switches["signalModel"]
    if not switches["isSms"] :
        out += "_%s"%switches["xsVariation"]
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

def processStamp(key = "") :
    chi = "#tilde{#chi}^{0}_{1}"
    dct = {
        ''     : {
        'text': "",
        'xpos': 0.4250,
        },
        'T2'     : {
        'text': "pp #rightarrow #tilde{q} #tilde{q}, #tilde{q} #rightarrow q %s; m(#tilde{g})>>m(#tilde{q})"%chi,
        'xpos': 0.4250,
        },
        'T2bb'   : {
        'text': "pp #rightarrow #tilde{b} #tilde{b}, #tilde{b} #rightarrow b %s; m(#tilde{g})>>m(#tilde{b})"%chi,
        'xpos': 0.425,
        },
        'T2tt'   : {
        'text': "pp #rightarrow #tilde{t} #tilde{t}, #tilde{t} #rightarrow t %s; m(#tilde{g})>>m(#tilde{t})"%chi,
        'xpos': 0.41,
        },
        'T1'     : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow q #bar{q} %s; m(#tilde{q})>>m(#tilde{g})"%chi,
        'xpos': 0.4325,
        },
        'T1bbbb' : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow b #bar{b} %s; m(#tilde{b})>>m(#tilde{g})"%chi,
        'xpos': 0.43,
        },
        'T1tttt' : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow t #bar{t} %s; m(#tilde{t})>>m(#tilde{g})"%chi,
        'xpos': 0.425,
        },
        }
    return dct.get(key, dct[""])
