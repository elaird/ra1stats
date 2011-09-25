#!/usr/bin/env python

def spec(simpleOneBin = False, qcdSearch = False, nHtBins = 8) :
    d = {}

    d["alphaT"] = {#"52": {"htBinMask": [1]*nHtBins, "samples": ["had"]},
                   #"53": {"htBinMask": [1]*nHtBins, "samples": ["had"]},
                   "55": {"htBinMask": [1]*nHtBins, "samples": ["had", "muon", "phot", "mumu"][:-1]},
                   }

    if simpleOneBin :
        d["simpleOneBin"] = {"b":3.0}
        key = max(d["alphaT"].keys())
        d["alphaT"] = {key: {"samples": ["had"], "htBinMask": [0]*(nHtBins-1)+[1]} }
    else :
        d["simpleOneBin"] = {}
    
    d["REwk"] = ["", "Linear", "Constant"][2]
    d["RQcd"] = ["Zero", "FallingExp", "FallingExpA"][1]
    d["nFZinv"] = ["All", "One", "Two"][0]
    d["qcdSearch"] = qcdSearch

    return d
