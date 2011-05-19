def scaled(t, factor) : return tuple([factor*a for a in t])

class data(object) :
    def htBinLowerEdges(self) : return (250.0, 300.0, 350.0, 450.0)
    def htMaxForPlot(self) :    return 600.0
    def lumi(self) :
        return {"had":     35.0,
                "hadBulk": 35.0,
                
                "muon":    35.0,
                "mcMuon":  35.0,
                "mcTtw":   35.0,
                
                "phot":    101.,
                "mcPhot":  101.,
                "mcZinv":  101.,
                }
    def observations(self) :
        return {"htMean":       ( 265.0,  315.0,  375.0,  475.0),#place-holder values
                "nBulk": scaled((844459, 331948, 225649, 110034), self.lumi()["had"]/self.lumi()["hadBulk"]),
                "nSel":         (    33,     11,      8,      5), #2010
                "nPhot":        (    94,     45,     21,      9),
                "nMuon":        (    13,      5,      5,      2), #2010
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
