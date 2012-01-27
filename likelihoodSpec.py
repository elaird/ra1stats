import inputData

class selection(object) :
    def __init__(self, name = "", samplesAndSignalEff = {}, data = None,
                 universalSystematics = False, universalKQcd = False) :
        for item in ["name", "samplesAndSignalEff", "data", "universalSystematics", "universalKQcd"] :
            setattr(self, item, eval(item))

def spec(simpleOneBin = False, qcdSearch = False) :
    d = {}

    d["selections"] = []
    d["selections"].append(selection(name = "55",
                                     samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                                     data = inputData.data2011_6(),
                                     universalSystematics = True,
                                     universalKQcd = True,
                                     )
                           )

    d["selections"].append(selection(name = "2010",
                                     samplesAndSignalEff = {"had":True, "muon":True, "phot":False},
                                     data = inputData.data2010(),
                                     )
                           )

    if simpleOneBin :
        assert False
        d["simpleOneBin"] = {"b":3.0}
        key = max(d["alphaT"].keys())
        d["alphaT"] = {key: {"samples": [("had", True)]} }
    else :
        d["simpleOneBin"] = {}
    
    d["REwk"] = ["", "Linear", "FallingExp", "Constant"][0]
    d["RQcd"] = ["Zero", "FallingExp", "FallingExpA"][1]
    d["nFZinv"] = ["All", "One", "Two"][2]
    d["qcdSearch"] = qcdSearch
    d["constrainQcdSlope"] = True

    return d
