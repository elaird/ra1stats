def method() :
    return {"CL": [0.95, 0.90][:1],
            "nToys": 1000,
            "testStatistic": 3,
            "calculatorType": ["frequentist", "asymptotic", "asymptoticNom"][1],
            "method": ["", "profileLikelihood", "feldmanCousins", "CLs", "CLsCustom"][3],
            "binaryExclusionRatherThanUpperLimit": False,
            "multiplesInGeV": None,
            }

def signal() :
    models = ["tanBeta10", "tanBeta40", "T5zz", "T1", "T1tttt", "T1bbbb", "T2",
              "T2tt", "T2bb", "T2cc", "TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8",
              "T1tttt_ichep", "T2bw"]
    variations = ["default", "up", "down"]

    out = {}
    out["nEventsIn"] = {""         :(1,     None),
                        "T5zz"     :(5.0e3, None),
                        "tanBeta10":(9.0e3, 11.0e3),
                        }

    out["drawBenchmarkPoints"] = True
    out["effRatioPlots"] = False
    out["xsVariation"] = dict(zip(variations, variations))["default"]
    out["signalModel"] = dict(zip(models, models))["T2cc"]
    return out

def whiteListOfPoints() : #GeV
    out = []
    #out += [( 700.0, 300.0)]  #T1
    #out += [( 900.0, 500.0)]  #T1bbbb
    #out += [( 850.0, 250.0)]  #T1tttt
    #out += [( 450.0,  20.0)]  #T2tt
    #out += [( 550.0,  20.0)]  #T2tt
    #out += [( 400.0,   0.0)]  #T2tt
    #out += [( 410.0,  20.0)]  #T2tt
    #out += [( 420.0,  20.0)]  #T2tt
    #out += [( 500.0, 150.0)]  #T2bb
    #out += [( 600.0, 250.0)]  #T2
    #out += [( 175.0, 95.0)]    #T2cc
    return out

def switches() :
    out = {}
    lst = [method(), signal()]
    for func in ["whiteListOfPoints"] :
        lst.append( {func: eval(func)()} )
    keys = sum([dct.keys() for dct in lst], [])
    assert len(keys)==len(set(keys))
    for dct in lst : out.update(dct)
    checkAndAdjust(out)
    return out

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

def mergedFileStem() :
    s = switches()
    tags = [s["method"]]
    if "CLs" in s["method"] : tags += [s["calculatorType"], "TS%d"%s["testStatistic"]]
    if s["binaryExclusionRatherThanUpperLimit"] : tags.append("binaryExcl")
    tags.append(s["signalModel"])
    if not s["isSms"] : tags.append(s["xsVariation"])
    return "ra1r/scan/"+"_".join(tags)

def directories() :
    return {"job"   : "jobIO",
            "plot"  : "plots",
            "log"   : "log",
            "points": "points",
            }

def pickledFileName(xBin, yBin, zBin) :
    return "%s/m0_%d_m12_%d_mZ_%d.pickled"%(directories()["job"], xBin, yBin, zBin)
