def method():
    return {"CL": [0.95, 0.90][:1],
            "nToys": 1000,
            "testStatistic": 3,
            "calculatorType": ["frequentist",
                               "asymptotic",
                               "asymptoticNom"][1],
            "method": ["",
                       "profileLikelihood",
                       "feldmanCousins",
                       "CLs",
                       "CLsCustom"][3],
            "binaryExclusionRatherThanUpperLimit": False,
            "multiplesInGeV": None,
            }


def switches():
    out = {}
    lst = [method()]
    keys = sum([dct.keys() for dct in lst], [])
    assert len(keys) == len(set(keys))
    for dct in lst:
        out.update(dct)
    checkAndAdjust(out)
    return out


def checkAndAdjust(d):
    binary = d["binaryExclusionRatherThanUpperLimit"]
    d["rhoSignalMin"] = 0.0 if binary else 0.1
    d["fIniFactor"] = 1.0 if binary else 0.05
    if binary:
        d["extraSigEffUncSources"] = []
    else:
        d["extraSigEffUncSources"] = []  # ["effHadSumUncRelMcStats"]

    d["plSeedParams"] = {"usePlSeed": False} if binary else \
                        {"usePlSeed": True,
                         "plNIterationsMax": 10,
                         "nPoints": 10,
                         "minFactor": 0.0,
                         "maxFactor": 3.0,
                         }
                        #{"usePlSeed": True,
                        # "plNIterationsMax": 10,
                        # "nPoints": 7,
                        # "minFactor": 0.5,
                        # "maxFactor": 2.0}


def mergedFileStem():
    import signal
    s = switches()
    tags = [s["method"]]
    if "CLs" in s["method"]:
        tags += [s["calculatorType"], "TS%d" % s["testStatistic"]]
    if s["binaryExclusionRatherThanUpperLimit"]:
        tags.append("binaryExcl")
    tags.append(signal.model())
    if not signal.isSms(signal.model()):
        tags.append(signal.xsVariation())
    return "ra1r/scan/"+"_".join(tags)


def directories():
    return {"job": "jobIO",
            "plot": "plots",
            "log": "log",
            "points": "points",
            }


def pickledFileName(xBin, yBin, zBin):
    return "%s/m0_%d_m12_%d_mZ_%d.pickled" % (directories()["job"],
                                              xBin, yBin, zBin)
