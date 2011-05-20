def scaled(t, factor) :
    return tuple([factor*a for a in t])

def excl(counts, isExclusive) :
    out = []
    for i,count,isExcl in zip(range(len(counts)), counts, isExclusive) :
        out.append(count if isExcl else (count-counts[i+1]))
    return tuple(out)

class data(object) :
    def photIsExcl(self) :      return (    1,     1,     0,     0,     0,     0,     0,     1)
    def htBinLowerEdges(self) : return (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
    def htMaxForPlot(self) :    return 975.0
    def lumi(self) :
        return {"had":     189.,
                "hadBulk": 189.,
                
                "muon":     35.,
                "mcMuon":   35.,
                "mcTtw":    35.,
                
                "phot":    164.6,
                "mcPhot":  164.6,
                "mcZinv":  164.6,
                }
    def observations(self) :
        return {"htMean":    (    297.51,      347.25,      415.57,  516.2 , 617.17, 717.72, 818.33, 919.08),
                "nBulk":     ( 9.047e+06,   3.793e+06,   2.623e+06,  823968, 289401, 112899,  48118,  65098),
                "nHad":      (       130,          68,          47,      12,      5,      1,      0,      0),
                "nPhot":excl((       142,          57,          43,      12,      2,      2,      2,      0), self.photIsExcl()),
                "nMuon":     (   13,   5,     5,    2), #2010
                }
    def mcExpectations(self) :
        return {"mcMuon":         scaled((  12.2,     5.2,     4.1,    1.9), self.lumi()["muon"]/self.lumi()["mcMuon"]), #2010
                "mcTtw":          scaled((  10.5,    4.47,   3.415,  1.692), self.lumi()["had" ]/self.lumi()["mcTtw"] ), #2010
                "mcPhot":    excl(scaled((   110,      37,      28,      9,    4,    0.8,    0.5,    0), self.lumi()["phot"]/self.lumi()["mcPhot"]), self.photIsExcl()),
                "mcPhotErr":      scaled((    10,       3,       3,      1,    1,    0.5,    0.4,    1), self.lumi()["phot"]/self.lumi()["mcPhot"]),
                "mcZinv":    excl(scaled((    39,      16,      18,      9,  1.7,    0.4,    0.4,    0), self.lumi()["had"] /self.lumi()["mcZinv"]), self.photIsExcl()),
                "mcZinvErr":      scaled((     4,       3,       3,      2,  0.9,    0.4,    0.4,    1), self.lumi()["had"] /self.lumi()["mcZinv"]),
                }
    def fixedParameters(self) :
        return {"sigmaLumi":  0.04,
                "sigmaPhotZ": 0.40,
                "sigmaMuonW": 0.30,
                }
