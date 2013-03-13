def directories():
    return {"job": "jobIO",
            "plot": "plots",
            "log": "log",
            "points": "points",
            "mergedFile": "ra1r/scan/",
            }


def pickledFileName(xBin, yBin, zBin):
    return "%s/m0_%d_m12_%d_mZ_%d.pickled" % (directories()["job"],
                                              xBin, yBin, zBin)


def switches():
    d = {"CL": [0.95, 0.90][:1],
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
                         #"nPoints": 7,
                         #"minFactor": 0.5,
                         #"maxFactor": 2.0,
                         }
    return d
