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
            "profileLikelihood",
            "feldmanCousins",
            "CLs",
            "CLsCustom"][3]


def binaryExclusion():
    return False


def multiplesInGeV():
    return None


def plSeedParams():
    if binaryExclusion():
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


def rhoSignalMin():
    return 0.0 if binaryExclusion() else 0.1


def fIniFactor():
    return 1.0 if binaryExclusion() else 0.05
