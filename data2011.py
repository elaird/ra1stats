def scaled(t, factor) : return tuple([factor*a for a in t])

class data(object) :
    def htBinLowerEdges(self) : return (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
    def htMaxForPlot(self) :    return 975.0
    def lumi(self) :
        return {"had":     189.,
                "hadBulk": 189.,
                
                "muon":     35.,
                "mcMuon":   35.,
                "mcTtw":    35.,
                
                "phot":    101.,
                "mcPhot":  101.,
                "mcZinv":  101.,
                }
    def observations(self) :
        return {"htMean": (     297.51,      347.25,      415.57,   516.2 , 617.17, 717.72, 818.33, 919.08),
                "nBulk":  (9.04799e+06, 3.79382e+06, 2.62383e+06,   823968, 289401, 112899,  48118,  65098),
                "nHad":   (        130,          68,          47,       12,      5,      1,      0,      0),
                "nPhot":       (    94,     45,     21,      9),
                "nMuon":       (    13,      5,      5,      2), #2010
                }
    def mcExpectations(self) :
        return {"mcMuon":scaled((  12.2,    5.2,    4.1,    1.9  ), self.lumi()["muon"]/self.lumi()["mcMuon"]), #2010
                "mcTtw": scaled((  10.5,    4.47,   3.415,  1.692), self.lumi()["had" ]/self.lumi()["mcTtw"] ), #2010
                "mcPhot":scaled(( 100.,    30.,    15.,     8.   ), self.lumi()["phot"]/self.lumi()["mcPhot"]),
                "mcZinv":scaled((  33.,    14.,     7.,     7.   ), self.lumi()["had"] /self.lumi()["mcZinv"]),
                }
    def fixedParameters(self) :
        return {"sigmaLumi":  0.04,
                "sigmaPhotZ": 0.40,
                "sigmaMuonW": 0.30,
                }
