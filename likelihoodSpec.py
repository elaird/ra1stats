def spec(simpleOneBin = False, qcdSearch = False, nHtBins = 8) :
    d = {}

    #d["alphaT"] = {"53": {"htBinMask": [1]*nHtBins, "samples": [("had", True), ("muon", False), ("phot", False), ("mumu", False)][:-1]},
    #               "55": {"htBinMask": [1]*nHtBins, "samples": [("had", True), ("muon", False), ("phot", False), ("mumu", False)][:-1]},
    #               "70": {"htBinMask": [1]*nHtBins, "samples": [("had", True), ("muon", False), ("phot", False), ("mumu", False)][:-1]},
    #               }

    d["alphaT"] = {"": {"htBinMask": [1]*nHtBins, "samples": [("had", True),
                                                              ("muon", False),
                                                              ("phot", False),
                                                              #("mumu", False)
                                                              ]}
                   }

    if simpleOneBin :
        d["simpleOneBin"] = {"b":3.0}
        key = max(d["alphaT"].keys())
        d["alphaT"] = {key: {"samples": [("had", True)], "htBinMask": [0]*(nHtBins-1)+[1]} }
    else :
        d["simpleOneBin"] = {}
    
    d["REwk"] = ["", "Linear", "FallingExp", "Constant"][3]
    d["RQcd"] = ["Zero", "FallingExp", "FallingExpA"][1]
    d["nFZinv"] = ["All", "One", "Two"][0]
    d["qcdSearch"] = qcdSearch

    return d
