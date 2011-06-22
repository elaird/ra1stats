from data import data,scaled,excl

class data2011_2(data) :
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0

        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0,     0,     0,     0)
        
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

        ep = 0.01        
        self._mcExpectations = {
            "mcMuon":         scaled((152.05,   57.80,   39.77,  12.93,   4.53,   2.63,   0.19, 0.06), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":          scaled((157.63,   59.71,   38.23,  14.09,   2.40,   2.26,   1.10, 0.31), self.lumi()["had" ]/self.lumi()["mcTtw"] ),
            "mcPhot":    excl(scaled((   290,     112,     109,     37,     14,      3,    2.1,  0.9), self.lumi()["phot"]/self.lumi()["mcPhot"]), isExcl),
            "mcZinv":    excl(scaled((    90,      41,      51,     24,      4,   ep+1,      1,   ep), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
            }
        self._mcStatError = {
            "mcPhotErr":      scaled((    20,       6,       6,      3,      2,      1,    0.8,  0.5), self.lumi()["phot"]/self.lumi()["mcPhot"]),
            "mcZinvErr":      scaled((    10,       7,       8,      5,      2,      1,      1,    1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            }
        self._fixedParameters = {
            "sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }
        # (3% ECAL, 2.5% vetoes, 2.5% JES and JER + the lumi uncert.) PDF uncertainties we used 10%.
        
class data2011_2_mb_dphi_cut(data) :
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0

        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0,     0,     0,     0)
        
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
            "nHad":           (       384,         159,          91,         30,     14,      2,      1,      1),
            "nPhot":     excl((       402,         149,         139,         55,     21,      9,      4,      1), isExcl),
            "nMuon":          (       146,          53,          39,         17,      7,      1,      0,      0),
            }
        ep = 0.01        
        self._mcExpectations = {
            "mcMuon":         scaled((152.05,   57.80,   39.77,  12.93,   4.53,   2.63,   0.19, 0.06), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw": addLists([117., 39.6, 25.1, 7.98, 1.48, 3.97, 0, 0], [55.4, 23.2, 13.6, 4.46, 0.42, 0.01, 0, 0.09]),
            "mcPhot":    excl(scaled((   290,     112,     109,     37,     14,      3,    2.1,  0.9), self.lumi()["phot"]/self.lumi()["mcPhot"]), isExcl),
            "mcZinv":                (  101.,    49.3,    33.7,   26.1,   4.46,      0,   1.73,    0),
            }
        self._mcStatError = {
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
        
class data2011_2_no_cleaning_cuts(data) :
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0

        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0,     0,     0,     0)
        
        self._lumi = {
            "had":     602.,
            "hadBulk": 602.,
            
            "muon":    448.,
            "mcMuon":  441.,

            "phot":    468.8,
            "mcPhot":  468.8,
            }
        self._htMeans =       (    297.51,      347.25,      415.57,     516.2 , 617.17, 717.72, 818.33, 919.08)
        self._observations = {
            "nHadBulk":       ( 3.234e+07,   1.328e+07,   9.086e+06,  2.870e+06, 998415, 387023, 162452, 145889),
            "nHad":           (      2398,         633,         260,         56,     19,      3,      2,      1),
            "nPhot":     excl((       402,         149,         139,         55,     21,      9,      4,      1), isExcl),
            "nMuon":          (       146,          53,          39,         17,      7,      1,      0,      0),            
            }

        ep = 0.01        
        self._mcExpectations = {
            "mcMuon":         scaled((121.78,   46.29,   31.85,  10.36,   3.63,   2.11,   0.15, 0.05), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw": addLists([137.,  47.5,  32.8,  12.7,  0.91,  1.82,  0.91,  0.91], [79.1,  37.9,  27.4,  9.51,  3.08,  1.11,  0.37,  0.43]),
            "mcPhot":    excl(scaled((   290,     112,     109,     37,     14,      3,    2.1,  0.9), self.lumi()["phot"]/self.lumi()["mcPhot"]), isExcl),
            "mcZinv":                (  102.,    44.2,    32.5,   19.7,   3.49,      0,   1.16,    0),
            }
        self._mcStatError = {
            "mcPhotErr":      scaled((    20,       6,       6,      3,      2,      1,    0.8,  0.5), self.lumi()["phot"]/self.lumi()["mcPhot"]),
           #"mcZinvErr":      scaled((    10,       7,       8,      5,      2,      1,      1,    1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            }
        self._fixedParameters = {
            "sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }
        # (3% ECAL, 2.5% vetoes, 2.5% JES and JER + the lumi uncert.) PDF uncertainties we used 10%.
        
class data2011_1(data) :
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0

        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0,     0,     0,     0)
        
        #self._mergeBins =                (    0,     1,     2,     3,     3,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0)

        self._lumi = {
            "had":     353.,
            "hadBulk": 353.,
            
            "muon":    361.,
            "mcMuon":  353.,
            "mcTtw":   353.,

            "phot":    468.8,
            "mcPhot":  468.8,
            "mcZinv":  468.8,
            }
        self._htMeans =       (    297.51,      347.25,      415.57,     516.2 , 617.17, 717.72, 818.33, 919.08)
        self._observations = {
            "nHadBulk":scaled(( 1.918e+07,   7.867e+06,   5.389e+06,  1.701e+06, 589724, 227972,  96054,  86017), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           (       254,         118,          66,         19,     11,      1,      2,      1),
            "nPhot":     excl((       402,         149,         139,         55,     21,      9,      4,      1), isExcl),
            "nMuon":          (       114,          42,          35,         13,      6,      1,      0,      0),
            }

        ep = 0.01        
        self._mcExpectations = {
            "mcMuon":         scaled((121.78,   46.29,   31.85,  10.36,   3.63,   2.11,   0.15, 0.05), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":          scaled((126.25,   47.82,   30.62,  11.29,   1.92,   1.81,   0.88, 0.25), self.lumi()["had" ]/self.lumi()["mcTtw"] ),
            "mcPhot":    excl(scaled((   290,     112,     109,     37,     14,      3,    2.1,  0.9), self.lumi()["phot"]/self.lumi()["mcPhot"]), isExcl),
            "mcZinv":    excl(scaled((    90,      41,      51,     24,      4,   ep+1,      1,   ep), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
            }
        self._mcStatError = {
            "mcPhotErr":      scaled((    20,       6,       6,      3,      2,      1,    0.8,  0.5), self.lumi()["phot"]/self.lumi()["mcPhot"]),
            "mcZinvErr":      scaled((    10,       7,       8,      5,      2,      1,      1,    1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            }
        self._fixedParameters = {
            "sigmaLumi":  0.04,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            }
        # (3% ECAL, 2.5% vetoes, 2.5% JES and JER + the lumi uncert.) PDF uncertainties we used 10%.
        
class data2011(data2011_2) :
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
