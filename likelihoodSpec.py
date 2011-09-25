#!/usr/bin/env python

def spec(simpleOneBin = False, qcdSearch = False, nHtBins = 8) :
    d = {}

    d["alphaT"] = {0.52: {"controlSamples": False, "htBinMask": [1]*nHtBins},
                   0.53: {"controlSamples": False, "htBinMask": [1]*nHtBins},
                   0.55: {"controlSamples": True,  "htBinMask": [1]*nHtBins},
                   }

    if simpleOneBin :
        d["simpleOneBin"] = {"b":3.0}
        key = max(d["alphaT"].keys())
        d["alphaT"] = {key: {"controlSamples": False, "htBinMask": [0]*(nHtBins-1)+[1]} }
    else :
        d["simpleOneBin"] = {}
        d["hadTerms"]  = True
        d["muonTerms"] = True
        d["mumuTerms"] = False
        d["photTerms"] = True

    d["hadControlSamples"] = []
    
    d["REwk"] = ["", "Linear", "Constant"][2]
    d["RQcd"] = ["Zero", "FallingExp", "FallingExpA"][1]
    d["nFZinv"] = ["All", "One", "Two"][0]
    d["qcdSearch"] = qcdSearch

    return d
