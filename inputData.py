from data import data,scaled,excl

class data2011_3(data) :
    """default data"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    1,     0,     0,     0,     0,     0,     0,     0)
        
        #self._mergeBins =                (    0,     1,     2,     3,     4,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    1,     0,     0,     0,     0)

        #self._mergeBins =                (    0,     1,     2,     3,     3,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    1,     0,     0,     0,     0)

        self._lumi = {
            "had":     769.,
            "hadBulk": 769.,

            "muon":    769.,
            "mcMuon":  769.,
            "mcTtw":   769.,

            "phot":    771.2,
            "mcGjets": 771.2,
            "mcZinv":  468.8,

            "mumu":    697.,
            "mcZmumu": 697.,
            }
        self._htMeans =       (   297.51,    347.25,     415.57,     516.2,    617.17,    717.72,    818.33,    919.08)
        self._observations = {
            "nHadBulk":scaled(( 4.118e+07, 1.693e+07, 1.158e+07, 3.664e+06, 1.273e+06, 4.934e+05, 2.072e+05, 1.861e+05), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           ( 5.720e+02, 2.370e+02, 1.400e+02, 4.500e+01, 1.800e+01, 3.000e+00, 2.000e+00, 1.000e+00),
            "nHad53":         ( 1.809e+03, 4.000e+02, 2.230e+02, 6.900e+01, 3.200e+01, 1.000e+01, 4.000e+00, 2.000e+00),
            "nPhot":     excl((       630,       227,       233,        81,        33,        15,         6,         3), isExcl),
           #"nPhot2Jet": excl((       255,        94,        99,        31,        11,         3,         1,         0), isExcl),
            "nMuon":          (       262,       100,        78,        31,        12,         4,         0,         0),
           #"nMuon2Jet":      (        86,        23,        25,        10,         2,         0,         0,         0),
            "nMumu":     excl((        22,         5,        11,         6,         3,         0,         0,         0), isExcl),
            }
        self._observations["nHadControl"] = tuple([n53-n55 for n53,n55 in zip(self._observations["nHad53"], self._observations["nHad"])])
        self._mcExpectations = {
            "mcMuon":          scaled((252.07,  104.36,   67.61,  24.04,   9.39,   4.37,   0.32, 0.22), self.lumi()["muon"]/self.lumi()["mcMuon"]),
           #"mcMuon2Jet":      scaled(( 86.03,   28.51,   25.63,   2.02,   4.78,   3.29,  0.107,    0), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":           scaled((274.87,  104.11,   66.67,  24.58,   4.18,   3.94,   1.92, 0.54), self.lumi()["had" ]/self.lumi()["mcTtw"] ),
            "mcGjets":    excl(scaled((   440,     190,     181,     62,     22,      5,      4,  1.5), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
           #"mcPhot2Jet": excl(scaled((   210,      91,      71,     20,      8,    0.4,    0.4,  0.4), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcZinv":     excl(scaled((    90,      41,      51,     24,      4,      1,      1,    0), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
            "mcZmumu":    excl(scaled((    15,       9,      11,      7,      3,    0.9,      0,    0), self.lumi()["mumu"]/self.lumi()["mcZmumu"]), isExcl),
            }
        self._mcStatError = {
            "mcMuonErr":             ( 14.79,   10.39,    8.91,   5.39,  3.244,  2.286,  0.186, 0.152),
           #"mcMuon2JetErr":         ( 11.59,    7.23,    6.92,   2.84,   2.83,   2.31,   0.11,   0.1),
            "mcTtwErr":              ( 17.58,   10.41,    8.47,   5.40,   2.32,   2.28,   1.60,  0.24),
            "mcGjetsErr":     scaled((    20,      10,      10,      6,      4,      2,      1,   0.9), self.lumi()["phot"]/self.lumi()["mcGjets"]),
           #"mcPhot2JetErr":  scaled((    20,      10,       6,      3,      2,    0.4,    0.4,   0.4), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErr":      scaled((    10,       7,       8,      5,      2,      1,      1,     1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            "mcZmumuErr":     scaled((     4,       3,       3,      3,      2,      1,      1,     1), self.lumi()["mumu"]/self.lumi()["mcZmumu"]),
            }
        self._purities = {
            "phot":                  (  0.92,    0.97,    0.99,   0.99,   0.99,   0.99,   0.99, 0.99),
            "mumu":                  (  0.89,    0.94,    0.97,   0.97,   0.97,   0.97,   0.97, 0.97),
            }
        self._fixedParameters = {
            "sigmaLumi":  0.06,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,
            }
        # (3% ECAL, 2.5% vetoes, 2.5% JES and JER + the lumi uncert.) PDF uncertainties we used 10%.
        
class data2011_2(data) :
    """data used for pre-approval talk"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0

        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0,     0,     0,     0)
        
        #self._mergeBins =                (    0,     1,     2,     2,     2,     2,     2,     2)
        #self._constantMcRatioAfterHere = (    0,     0,     1)

        #self._mergeBins =                (    0,     1,     2,     3,     3,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0)

        self._lumi = {
            "had":     602.,
            "hadBulk": 602.,
            
            "muon":    448.,
            "mcMuon":  441.,
            "mcTtw":   441.,

            "phot":    468.8,
            "mcPhot":  468.8,
            "mcZinv":  468.8,
            }
        self._htMeans =       (    297.51,      347.25,      415.57,     516.2 , 617.17, 717.72, 818.33, 919.08)
        self._observations = {
            "nHadBulk":scaled(( 3.234e+07,   1.328e+07,   9.086e+06,  2.870e+06, 998416, 387024, 162452, 145889), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           (       458,         189,         109,         37,     18,      2,      2,      1),
            "nPhot":     excl((       402,         149,         139,         55,     21,      9,      4,      1), isExcl),
            "nMuon":          (       146,          53,          39,         17,      7,      1,      0,      0),
            }

        self._mcExpectations = {
            "mcMuon":         scaled((152.05,   57.80,   39.77,  12.93,   4.53,   2.63,   0.19, 0.06), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":          scaled((157.63,   59.71,   38.23,  14.09,   2.40,   2.26,   1.10, 0.31), self.lumi()["had" ]/self.lumi()["mcTtw"] ),
            "mcPhot":    excl(scaled((   290,     112,     109,     37,     14,      3,    2.1,  0.9), self.lumi()["phot"]/self.lumi()["mcPhot"]), isExcl),
            "mcZinv":    excl(scaled((    90,      41,      51,     24,      4,      1,      1,    0), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
            }
        self._mcStatError = {
            "mcMuonErr":      scaled((  9.55,    5.62,    5.03,   2.95,   1.62,   1.31,   0.11, 0.06), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtwErr":       scaled(( 10.08,    5.97,    4.86,   3.10,   1.33,   1.31,   0.92, 0.14), self.lumi()["had"] /self.lumi()["mcTtw"]),
            "mcPhotErr":      scaled((    20,       6,       6,      3,      2,      1,    0.8,  0.5), self.lumi()["phot"]/self.lumi()["mcPhot"]),
            "mcZinvErr":      scaled((    10,       7,       8,      5,      2,      1,      1,    1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            }
        self._fixedParameters = {
            "sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }
        # (3% ECAL, 2.5% vetoes, 2.5% JES and JER + the lumi uncert.) PDF uncertainties we used 10%.
        
def addLists(l1, l2) :
    out = []
    for a,b in zip(l1,l2) :
        out.append(a+b)
    return out
        
class data2011(data2011_3) :
    pass

class data2010(data) :
    def _fill(self) :
        self._htBinLowerEdges =          (250.0, 300.0, 350.0, 450.0)
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0)
        self._htMaxForPlot = 600.0
        self._lumi = {
            "had":     35.0,
            "hadBulk": 35.0,
            
            "muon":    35.0,
            "mcMuon":  35.0,
            "mcTtw":   35.0,
            
            "phot":    35.0,
            "mcPhot":  35.0,
            "mcZinv":  35.0,
            }
        self._htMeans = ( 265.0,  315.0,  375.0,  475.0) #place-holder values
        self._observations = {
            "nHadBulk": (844459, 331948, 225649, 110034),
            "nHad":     (    33,     11,      8,      5),
            "nPhot":    (    24,      4,      6,      1),
            "nMuon":    (    13,      5,      5,      2),
            }
        self._mcExpectations = {
            "mcMuon": (  12.2,    5.2,    4.1,    1.9  ),
            "mcTtw":  (  10.5,    4.47,   3.415,  1.692),
            "mcPhot": (  22.4,    7.0,    4.4,    2.1  ),
            "mcZinv": (   8.1,    3.9,    2.586,  1.492),
            }
        self._mcStatError = {}

        self._fixedParameters = {
            "sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }
