import utils
from data import data,scaled,excl,trig

class data2011_55_v6(data) :
    """no odd-muon-veto"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)
        
        self._lumi = {
            "had":     4650.,
            "hadBulk": 4650.,

            "muon":    4650.,
            "mcMuon":  4650.,
            "mcTtw":   4650.,

            "phot":    4529.,
            "mcGjets": 4529.,
            "mcZinv":  4529.,

            "mumu":    4650.,
            "mcZmumu": 4650.,
            }
        print "the 2jet numbers are old"
        print "the mumu purities are old"
        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02) #old
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           ( 3.703e+03, 1.536e+03, 1.043e+03, 3.460e+02, 1.220e+02, 4.400e+01, 1.400e+01, 6.000e+00),
            "nPhot":     excl((      None,      None,      1642,       596,       221,        91,        32,        14), isExcl),
            "nPhot2Jet": excl((      None,      None,       601,       174,        47,        13,         3,         1), isExcl),
            "nMuon":          (      1421,       644,       517,       169,        52,        18,         8,         1),
            "nMuon2Jet":      (       436,       192,       164,        37,         6,         1,         0,         0),#old
            "nMumu":          (       114,        65,        42,        15,         7,         1,         0,         2)
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (  0.921536,  0.977216,  0.995232,  0.987821,  1.000000,  1.000000,  1.000000,  1.000000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectations = {
            "mcMuon":     trig(     scaled((1472.37, 728.81,  501.10, 173.76,  67.80,  21.68,   7.31, 4.99), self.lumi()["muon"]/self.lumi()["mcMuon"]),
                                    self._triggerEfficiencies["had"]),
            "mcMuon2Jet": trig(     scaled(( 407.87, 230.78,  157.66,  39.43,  13.58,   5.00,   1.25, 1.00), self.lumi()["muon"]/self.lumi()["mcTtw"]),#old
                                    self._triggerEfficiencies["had"]),
            "mcTtw":      trig(     scaled((1935.06, 829.26,  545.16, 198.59,  67.73,  30.08,   8.26, 5.63), self.lumi()["muon"]/self.lumi()["mcTtw"]),
                                    self._triggerEfficiencies["had"]),
            "mcGjets":         excl(scaled((  None,    None, 2.00e+3, 7.1e+2, 2.7e+2,     92,     34,   14), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcPhot2Jet":      excl(scaled((  None,    None,  8.3e+2, 2.3e+2,     80,     23,      7,    3), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcZinv01":   trig(            (1579.47, 698.43,     0.0,    0.0,    0.0,    0.0,    0.0,  0.0),
                                    self._triggerEfficiencies["had"]),
            "mcZinv27":   trig(excl(scaled((    0.0,    0.0,  8.9e+2, 3.3e+2,    121,     44,     17,    7), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
                                    self._triggerEfficiencies["had"]),
            "mcZmumu":    trig(     scaled(( 118.61,  75.94,   45.80,  17.54,   9.23,   3.02,   0.14, 1.92), self.lumi()["mumu"]/self.lumi()["mcZmumu"]),
                                    self._triggerEfficiencies["had"]),
            }
        self._mcExpectations["mcZinv"] = [a+b for a,b in zip(self._mcExpectations["mcZinv01"], self._mcExpectations["mcZinv27"])]

        self._mcStatError = {
            "mcMuonErr":                   (  56.3,    40.0,     6.9,    4.1,    2.7,    1.4,    0.7,   0.6),
            "mcMuon2JetErr":               (  34.35,   26.15,    2.97,   1.48,   0.85,   0.49,   0.25,  0.22),#old
            "mcTtwErr":                    (  67.4,    43.9,     7.3,    4.5,    2.5,    1.9,    0.8,   0.7),
            "mcGjetsErr":           scaled((  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,      8,      5,     3), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcPhot2JetErr":        scaled((  None,    None,  0.2e+2, 0.1e+2,      7,      4,      2,     1), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErrTM":          scaled(( 10.39,    6.71,  0.2e+2, 0.1e+2,      6,      4,      2,     1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            "mcZinvErrDB":                 ( 10.17,    6.69,    5.79,   3.46,    2.1,    1.2,    0.8,   0.7),
            "mcZmumuErr":                  (  6.76,    5.46,    4.22,   2.57,    1.9,   1.09,   0.16,  0.78),
            }
        self._mcStatError["mcZinvErr"] = self._mcStatError["mcZinvErrDB"]
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])
        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            "mumu":                  (  0.89,    0.94,    0.97,   0.97,   0.97,   0.97,   0.97, 0.97),#old
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        self._mcExtra["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectations["mcGjets"], self._purities["phot"])])
        self._mcExtra["mcMumu"] = tuple([(zMumu/purity if (zMumu and purity) else None) for zMumu,purity in zip(self._mcExpectations["mcZmumu"], self._purities["mumu"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            #"sigmaLumiLike": 0.0001,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,
            "k_qcd_nom"     : 3.3e-2,
            "k_qcd_unc_inp" : 0.66e-2,
            }

class data2011_5(data) :
    """in progress"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)
        
        self._lumi = {
            "had":     4650.,
            "hadBulk": 4650.,

            "muon":    4650.,
            "mcMuon":  4650.,
            "mcTtw":   4650.,

            "phot":    4529.,
            "mcGjets": 4529.,
            "mcZinv":  4529.,

            "mumu":    4650.,
            "mcZmumu": 4650.,
            }

        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02)
        self._sigEffCorr =    (  9.88e-01,  9.84e-01,  9.96e-01,  9.71e-01,  9.60e-01,  9.58e-01,  9.52e-01,  9.35e-01); print "sigEffCorr ignored"
        self._observations = {
            "nHadBulk":scaled(( 2.724e+08, 1.174e+08, 8.163e+07, 2.526e+07, 8.642e+06, 3.536e+06, 1.480e+06, 1.314e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           ( 3.534e+03, 1.426e+03, 9.440e+02, 3.090e+02, 1.080e+02, 3.200e+01, 1.300e+01, 6.000e+00),
            "nPhot":     excl((      None,      None,      1506,       535,       195,        79,        26,        12), isExcl),
            "nMuon":          (      1428,       660,       504,       182,        52,        17,         8,         1),
            "nMumu":          (    124.55,     67.98,     43.35,     15.32,      7.00,      1.00,      0.00,      2.00),
            }
        print "WARNING: nMumu numbers need to be updated"

        self._triggerEfficiencies = {
            "hadBulk":       (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            #"had":           (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (  0.921536,  0.977216,  0.995232,  0.987821,  1.000000,  1.000000,  1.000000,  1.000000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectations = {
            "mcMuon":     trig(     scaled((1672.52, 737.68,  522.85, 180.61,  66.33,  22.22,   7.67, 5.21), self.lumi()["muon"]/self.lumi()["mcMuon"]),
                                    self._triggerEfficiencies["had"]),
            "mcTtw":      trig(     scaled((2008.69, 733.84,  502.97, 173.22,  57.86,  23.08,   6.77, 5.48), self.lumi()["muon"]/self.lumi()["mcTtw"]),
                                    self._triggerEfficiencies["had"]),
            "mcGjets":         excl(scaled((  None,    None, 1.86e+3, 6.4e+2, 2.4e+2,     82,     30,   13), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            #"mcZinv":     trig(excl(scaled((  None,    None,  8.3e+2,    302,    111,     39,     14,    5), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
            #                   self._triggerEfficiencies["had"]),
            "mcZinv01":                    (1663.76, 702.96,     0.0,    0.0,    0.0,    0.0,    0.0,  0.0),
            "mcZinv27":   trig(excl(scaled((    0.0,    0.0,  8.3e+2,    302,    111,     39,     14,    5), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
                               self._triggerEfficiencies["had"]),
            "mcZmumu":              scaled(( 125.21,  76.95,   45.27,  16.12,   9.04,   3.02,   0.00, 1.21), self.lumi()["mumu"]/self.lumi()["mcZmumu"]),
            }
        self._mcExpectations["mcZinv"] = [a+b for a,b in zip(self._mcExpectations["mcZinv01"], self._mcExpectations["mcZinv27"])]

        print "WARNING: mcZinv  needs to be updated"
        print "WARNING: mcZmumu needs to be updated"

        self._mcStatError = {
            "mcMuonErr":                    (  60.4,    40.2,     7.0,    4.2,    2.5,    1.4,    0.8,   0.6),
            "mcTtwErr":                     (  68.8,    40.7,     6.9,    4.1,    2.4,    1.6,    0.7,   0.7),
            "mcGjetsErr":           scaled((  None,    None, 0.03e+3, 0.2e+2, 0.1e+2,      7,      4,     3), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            #"mcZinvErr":            scaled((  None,    None,  0.2e+2,     10,      6,      4,      2,     1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            "mcZinvErr":            scaled(( 10.39,    6.71,  0.2e+2,     10,      6,      4,      2,     1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            "mcZmumuErr":           scaled((  7.03,    5.51,    4.23,   2.52,   1.89,   1.09,   1.00,  0.69), self.lumi()["mumu"]/self.lumi()["mcZmumu"]),
            }
        print "WARNING: mcZinvErr  needs to be updated"
        print "WARNING: mcZmumuErr needs to be updated"

        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])
        print "put in 2Jet numbers"
        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            "mumu":                  (  0.89,    0.94,    0.97,   0.97,   0.97,   0.97,   0.97, 0.97),
            }
        print "WARNING: mumu purity needs to be updated"

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        self._mcExtra["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectations["mcGjets"], self._purities["phot"])])
        self._mcExtra["mcMumu"] = tuple([(zMumu/purity if (zMumu and purity) else None) for zMumu,purity in zip(self._mcExpectations["mcZmumu"], self._purities["mumu"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            #"sigmaLumiLike": 0.0001,
            "sigmaPhotZ"    : 0.40,
            "sigmaMuonW"    : 0.30,
            "sigmaMumuZ"    : 0.20,
            "k_qcd_nom"     : 3.3e-2,
            "k_qcd_unc_inp" : 0.66e-2,
            }

class data2011_4(data) :
    """EPS"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0,     0,     0,     0)
        
        #self._mergeBins =                (    0,     1,     2,     2,     2,     2,     2,     2)
        #self._constantMcRatioAfterHere = (    0,     0,     0)

        #self._mergeBins =                (    0,     1,     2,     3,     3,     3,     3,     3)
        #self._constantMcRatioAfterHere = (    0,     0,     0,     0)

        #self._mergeBins =                (    0,     1,     2,     3,     4,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0)

        #self._mergeBins =                (    0,     1,     2,     3,     3,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0)

        #self._mergeBins =                (    0,     1,     2,     3,     4,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    0,     0,     1,     0,     0)

        self._lumi = {
            "had":     1080.,
            "hadBulk": 1080.,

            "muon":    1080.,
            "mcMuon":  1080.,
            "mcTtw":   1080.,

            "phot":    1057.,
            "mcGjets": 1057.,
            "mcZinv":  1057.,

            "mumu":    697.,
            "mcZmumu": 697.,
            }

        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02)
        self._sigEffCorr =    (  9.88e-01,  9.84e-01,  9.96e-01,  9.71e-01,  9.60e-01,  9.58e-01,  9.52e-01,  9.35e-01); print "sigEffCorr ignored"
        self._observations = {
            "nHadBulk":scaled(( 5.733e+07, 2.358e+07, 1.619e+07, 5.116e+06, 1.777e+06, 6.888e+05, 2.900e+05, 2.599e+05), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           ( 7.820e+02, 3.210e+02, 1.960e+02, 6.200e+01, 2.100e+01, 6.000e+00, 3.000e+00, 1.000e+00),
            "nPhot":     excl((       849,       307,       321,       111,        44,        20,         8,         4), isExcl),
            "nPhot2Jet": excl((       336,       127,       136,        40,        13,         4,         2,         0), isExcl),
            "nMuon":          (       389,       156,       113,        39,        17,         5,         0,         0),
            "nMuon2Jet":      (       128,        37,        36,        12,         2,         0,         0,         0),
            "nMumu":     excl((        22,         5,        11,         6,         3,         0,         0,         0), isExcl),
            }

        self._observations["nHad_55"] = self._observations["nHad"]

        self._triggerEfficiencies = {
            "hadBulk":       (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
           #"had":           (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.991,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }
        for item in  ["hadControl_51_52", "hadControl_52_53", "hadControl_53_55"] :
            self._triggerEfficiencies[item] = self._triggerEfficiencies["had"]

        self._mcExpectations = {
            "mcMuon":     trig(     scaled((411.20,  179.11,  131.59,  48.68,  13.32,   7.95,   3.20, 0.90), self.lumi()["muon"]/self.lumi()["mcMuon"]),
                                    self._triggerEfficiencies["had"]),
            "mcMuon2Jet":           scaled((121.83,   54.43,   45.06,  14.89,   3.69,   0.72,   0.72, 0.00), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcMuon2JetSpring11":   scaled((139.39,   53.17,   40.62,   2.84,   6.71,   4.63,   0.15, 0.00), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcMuon2JetSpring11Re": scaled((113.86,   48.99,   39.57,   3.75,   3.13,   6.61,  0.166, 0.0 ), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":      trig(     scaled((467.25,  171.16,  116.33,  43.68,  17.50,   5.08,   1.09, 1.81), self.lumi()["had" ]/self.lumi()["mcTtw"] ),
                                    self._triggerEfficiencies["had"]),
            "mcGjets":         excl(scaled((   600,     260,     250,     85,     31,      8,      5,    2), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcPhot2Jet":      excl(scaled((   290,     124,      98,     26,     10,    0.5,    0.5,  0.5), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcZinv":     trig(excl(scaled((   210,      90,     110,     50,      8,      3,      3,    0), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
                               self._triggerEfficiencies["had"]),
            "mcZmumu":         excl(scaled((    15,       9,      11,      7,      3,    0.9,      0,    0), self.lumi()["mumu"]/self.lumi()["mcZmumu"]), isExcl),
            }

        self._mcStatError = {
            "mcMuonErr":                   ( 14.51,    9.57,    8.78,   5.54,   2.92,   2.29,   1.44,  0.73),
            "mcMuon2JetErr":               (  9.01,    6.07,    5.54,   3.22,   1.61,   0.72,   0.72,  0.00),
            "mcMuon2JetSpring11Err":       ( 17.06,   10.50,    9.25,   2.26,   3.88,   3.17,   0.15,  0.00),
            "mcMuon2JetSpring11ReErr":     ( 14.54,   10.34,    9.42,   3.93,   2.45,   3.51,  0.166,  0.00),
            "mcTtwErr":                    ( 16.00,    9.47,    8.26,   5.06,   3.17,   1.80,   0.73,  1.03),
            "mcGjetsErr":           scaled((    20,      10,      10,      8,      5,      2,      2,     1), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcPhot2JetErr":        scaled((    40,      10,       8,      4,      3,    0.5,    0.5,   0.5), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErr":            scaled((    20,      20,      20,     10,      5,      3,      3,     3), self.lumi()["had"] /self.lumi()["mcZinv"]),
            "mcZmumuErr":           scaled((     4,       3,       3,      3,      2,      1,      1,     1), self.lumi()["mumu"]/self.lumi()["mcZmumu"]),
            }
        self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  0.92,    0.97,    0.99,   0.99,   0.99,   0.99,   0.99, 0.99),
            "mumu":                  (  0.89,    0.94,    0.97,   0.97,   0.97,   0.97,   0.97, 0.97),
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([ttw+zinv for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        self._mcExtra["mcPhot"] = tuple([gJet/purity for gJet,purity in zip(self._mcExpectations["mcGjets"], self._purities["phot"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            #"sigmaLumiLike": 0.0001,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,
            }

class data2011_3(data) :
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    1,     0,     0,     0,     0,     0,     0,     0)
        
        #self._mergeBins =                (    0,     1,     2,     3,     4,     4,     4,     4)
        #self._constantMcRatioAfterHere = (    1,     0,     0,     0,     0)

        #self._mergeBins =                (    0,     1,     2,     2,     2,     2,     2,     2)
        #self._constantMcRatioAfterHere = (    1,     0,     0)

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

        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02)
        
        self._observations = {
            "nHadBulk":scaled(( 4.118e+07, 1.693e+07, 1.158e+07, 3.664e+06, 1.273e+06, 4.934e+05, 2.072e+05, 1.861e+05), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad51":         ( 2.887e+04, 5.499e+03, 1.037e+03, 2.670e+02, 9.200e+01, 2.700e+01, 1.100e+01, 1.100e+01),
            "nHad52":         ( 6.481e+03, 9.260e+02, 3.570e+02, 1.090e+02, 4.500e+01, 1.300e+01, 5.000e+00, 3.000e+00),
            "nHad53":         ( 1.809e+03, 4.000e+02, 2.230e+02, 6.900e+01, 3.200e+01, 1.000e+01, 4.000e+00, 2.000e+00),
            "nHad55":         ( 5.720e+02, 2.370e+02, 1.400e+02, 4.500e+01, 1.800e+01, 3.000e+00, 2.000e+00, 1.000e+00),
            "nPhot":     excl((       630,       227,       233,        81,        33,        15,         6,         3), isExcl),
           #"nPhot2Jet": excl((       255,        94,        99,        31,        11,         3,         1,         0), isExcl),
            "nMuon":          (       262,       100,        78,        31,        12,         4,         0,         0),
           #"nMuon2Jet":      (        86,        23,        25,        10,         2,         0,         0,         0),
            "nMumu":     excl((        22,         5,        11,         6,         3,         0,         0,         0), isExcl),
            }
        self._observations["nHad"] = self._observations["nHad55"]
        self._observations["nHadControl_53_55"] = tuple([n53-n55 for n53,n55 in zip(self._observations["nHad53"], self._observations["nHad55"])])
        self._observations["nHadControl_52_53"] = tuple([n52-n53 for n52,n53 in zip(self._observations["nHad52"], self._observations["nHad53"])])
        self._observations["nHadControl_51_52"] = tuple([n51-n52 for n51,n52 in zip(self._observations["nHad51"], self._observations["nHad52"])])

        self._triggerEfficiencies = {
            "hadBulk":       (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
           #"had":           (     0.957,     0.986,     0.990,     0.990,     0.990,     0.990,     0.990,     0.990),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }
        for item in ["muon"] :
            self._triggerEfficiencies[item] = self._triggerEfficiencies["had"]
        #for item in  ["hadControl_51_52", "hadControl_52_53", "hadControl_53_55"] :
        #    self._triggerEfficiencies[item] = self._triggerEfficiencies["had"]
        
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
        self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  0.92,    0.97,    0.99,   0.99,   0.99,   0.99,   0.99, 0.99),
            "mumu":                  (  0.89,    0.94,    0.97,   0.97,   0.97,   0.97,   0.97, 0.97),
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([ttw+zinv for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        self._mcExtra["mcPhot"] = tuple([gJet/purity for gJet,purity in zip(self._mcExpectations["mcGjets"], self._purities["phot"])])
        
        self._fixedParameters = {
            #"sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaLumiLike": 0.06,
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,
            }

class data2011_3_no_cleaning_cuts(data2011_3) :
    """cleaning cuts removed"""

    def _fill(self) :
        super(data2011_3_no_cleaning_cuts, self)._fill()
        self._observations["nHad51"] = (1.994e+05, 5.523e+04, 2.745e+04, 4.624e+03, 9.530e+02, 1.860e+02, 6.700e+01, 3.000e+01)
        self._observations["nHad52"] = (5.524e+04, 1.355e+04, 5.441e+03, 7.020e+02, 1.280e+02, 3.300e+01, 1.300e+01, 7.000e+00)
        self._observations["nHad53"] = (1.758e+04, 4.171e+03, 1.675e+03, 1.880e+02, 6.000e+01, 2.000e+01, 7.000e+00, 2.000e+00)
        self._observations["nHad55"] = (3.060e+03, 7.890e+02, 3.390e+02, 7.200e+01, 2.000e+01, 6.000e+00, 2.000e+00, 1.000e+00)
        self._observations["nHad"] = self._observations["nHad55"]
        self._observations["nHadControl"] = tuple([n53-n55 for n53,n55 in zip(self._observations["nHad53"], self._observations["nHad55"])])
        
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
        self._htMeans             = ( 265.0,  315.0,  375.0,  475.0) #place-holder values
        self._triggerEfficiencies = {
            "had": (  1.0, 1.0, 1.0, 1.0)
            }

        self._observations = {
            "nHadBulk": (844459, 331948, 225649, 110034),
            "nHad":     (    33,     11,      8,      5),
            "nPhot":    (    24,      4,      6,      1),
            "nMuon":    (    13,      5,      5,      2),
            }
        self._purities = {
            "phot": (1.0, 1.0, 1.0, 1.0)
            }
        self._mcExpectations = {
            "mcMuon": (  12.2,    5.2,    4.1,    1.9  ),
            "mcTtw":  (  10.5,    4.47,   3.415,  1.692),
            "mcPhot": (  22.4,    7.0,    4.4,    2.1  ),
            "mcZinv": (   8.1,    3.9,    2.586,  1.492),
            }
        self._mcExpectations["mcGjets"] = self._mcExpectations["mcPhot"]

        self._mcStatError = {}
        self._mcExtra = {}

        self._fixedParameters = {
            "sigmaLumiLike": 0.04,
            "sigmaPhotZ":    0.40,
            "sigmaMuonW":    0.30,
            "k_qcd_nom"     : 3.3e-2,
            "k_qcd_unc_inp" : 0.66e-2,
            }
