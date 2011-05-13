def htBinLowerEdges() :
    return (250.0, 300.0, 350.0, 450.0)

def htMaxForPlot() :
    return 600.0

def scaled(t, factor) :
    return tuple([factor*a for a in t])

def lumi() :
    return {"had":     35.0,
            "hadBulk": 35.0,

            "muon":    35.0,
            "mcMuon":  35.0,
            "mcTtw":   35.0,

            "phot":    101.,
            "mcPhot":  101.,
            "mcZinv":  101.,
            }

def observations() :
    return {"htMean":       ( 265.0,  315.0,  375.0,  475.0),#place-holder values
            "nBulk": scaled((844459, 331948, 225649, 110034), lumi()["had"]/lumi()["hadBulk"]),
            "nSel":         (    33,     11,      8,      5), #2010
            "nPhot":        (    94,     45,     21,      9),
            "nMuon":        (    13,      5,      5,      2), #2010
            }

def mcExpectations() :
    return {"mcMuon":scaled((  12.2,    5.2,    4.1,    1.9  ), lumi()["muon"]/lumi()["mcMuon"]), #2010
            "mcTtw": scaled((  10.5,    4.47,   3.415,  1.692), lumi()["had" ]/lumi()["mcTtw"] ), #2010
            "mcPhot":scaled(( 100.,    30.,    15.,     8.   ), lumi()["phot"]/lumi()["mcPhot"]),
            "mcZinv":scaled((  33.,    14.,     7.,     7.   ), lumi()["had"] /lumi()["mcZinv"]),
            }

def fixedParameters() :
    return {"sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }
