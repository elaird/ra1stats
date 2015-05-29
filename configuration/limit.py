import directories


def CL():
    return [0.95, 0.90][:1]


def nToys():
    return 1000


def testStatistic():
    return 3


def calculatorType():
    return ["frequentist",
            "asymptotic",
            "asymptoticNom"][1]


def method():
    return ["",
            "nlls",
            "profileLikelihood",
            "feldmanCousins",
            "CLs",
            "CLsCustom"][4]


def multiplesInGeV():
    return None


def plSeedParams(binaryExclusion):
    if binaryExclusion:
        return {"usePlSeed": False}
    else:
        return {"usePlSeed": True,
                "plNIterationsMax": 10,
                "nPoints": 10,
                "minFactor": 0.0,
                "maxFactor": 3.0,
                #"nPoints": 7,
                #"minFactor": 0.5,
                #"maxFactor": 2.0,
                }


def mergedFile(model=None):
    tags = [method()]
    if "CLs" in method():
        tags += [calculatorType(),
                #"TS%d" % testStatistic()
                ]
    if model.binaryExclusion:
        tags.append("binaryExcl")

    return "".join([directories.mergedFile()+"/",
                    "_".join(tags + model.tags()),
                    ".root"
                    ])

def mergedFiles(model=None,
                expFileNameSuffix=None,
                obsFileNameSuffix=None):
    expFileName = mergedFile(model=model)
    obsFileName = expFileName
    if expFileNameSuffix is not None : expFileName = expFileName.replace('.root',expFileNameSuffix+'.root')
    if obsFileNameSuffix is not None : obsFileName = obsFileName.replace('.root',obsFileNameSuffix+'.root')
    return (expFileName,obsFileName)
    
