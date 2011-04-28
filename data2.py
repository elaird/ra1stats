def lumi() : #recorded lumi for analyzed sample
    return 35.0 #/pb

def htBinLowerEdges() :
    return (250.0, 300.0, 350.0, 450.0)

def htMaxForPlot() :
    return 600.0

def observations() :
    return {"htMean":( 265.0,  315.0,  375.0,  475.0),#place-holder values
            "nBulk": (844459, 331948, 225649, 110034),
            "nSel":  (    33,     11,      8,      5),
            "nPhot": (    24,      4,      6,      1),
            "nMuon": (    13,      5,      5,      2),
            }

def mcExpectations() : #events / lumi
    return {"mcMuon":(  12.2,    5.2,    4.1,    1.9  ),
            "mcTtw": (  10.5,    4.47,   3.415,  1.692),
            "mcPhot":(  22.4,    7.0,    4.4,    2.1  ),
            "mcZinv":(    -1,     -1,    2.586,  1.492),
            }

def fixedParameters() :
    return {"sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }

def signalXs() :
    return 4.9 #pb

def signalEff() :
    return {"had":(0.0,    0.0,    0.02,   0.10),
            "mu": (0.0,    0.0,    0.0,    0.0 ),
            }
