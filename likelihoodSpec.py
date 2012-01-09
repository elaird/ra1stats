def spec(simpleOneBin = False, qcdSearch = False) :
    d = {}

    #d["alphaT"] = {"53": {"samples": [("had", True), ("muon", False), ("phot", False), ("mumu", False)][:-1]},
    #               "55": {"samples": [("had", True), ("muon", False), ("phot", False), ("mumu", False)][:-1]},
    #               "70": {"samples": [("had", True), ("muon", False), ("phot", False), ("mumu", False)][:-1]},
    #               }

    d["alphaT"] = {"": {"samples": [("had", True),
                                    ("muon", True),
                                    ("phot", True),
                                    ("mumu", True)
                                    ]}
                   }

    if simpleOneBin :
        d["simpleOneBin"] = {"b":3.0}
        key = max(d["alphaT"].keys())
        d["alphaT"] = {key: {"samples": [("had", True)]} }
    else :
        d["simpleOneBin"] = {}
    
    d["REwk"] = ["", "Linear", "FallingExp", "Constant"][0]
    d["RQcd"] = ["Zero", "FallingExp", "FallingExpA"][1]
    d["nFZinv"] = ["All", "One", "Two"][2]
    d["qcdSearch"] = qcdSearch

    return d
