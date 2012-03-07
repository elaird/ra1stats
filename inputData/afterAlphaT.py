import syst
from data import data,scaled,excl

class data_55_v1(data) :
    """all samples have an alphaT cut applied in all bins"""
    
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
            "mcMumu":  4650.,
            }
        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02) #old
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),

            "nHad":           (    3703.0,    1536.0,    1043.0,     346.0,     122.0,      44.0,      14.0,       6.0),
            "nMuon":          (    1421.0,     645.0,     517.0,     169.0,      52.0,      18.0,       8.0,       1.0),
            "nMumu":          (     114.0,      65.0,      42.0,      15.0,       7.0,       1.0,       0.0,       2.0),
            "nPhot":     excl((      None,      None,      1642,       596,       221,        91,        32,        14), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcMuon":               scaled((1690.37, 771.57,  525.06,  181.64,  70.84,  22.64,   7.53,   5.19), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":                scaled((2244.21, 874.85,  571.91,  206.83,  70.18,  31.07,   8.48,   6.14), self.lumi()["muon"]/self.lumi()["mcTtw"]),
            "mcGjets":         excl(scaled((  None,    None, 2.00e+3,  7.1e+2, 2.7e+2,     92,     34,     14), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcMumu":               scaled((133.43,   77.45,   46.82,   17.74,   9.43,   3.03,   0.13,   1.91), self.lumi()["mumu"]/self.lumi()["mcMumu"]),
            }
        
        self._mcExpectationsBeforeTrigger["mcZinv"] = tuple([a+b for a,b in zip((1706.7,  718.03,  0.0, 0,0, 0.0, 0.0, 0.0, 0.0),
                                                                                excl(scaled((0.0,  0.0, 8.9e+2, 3.3e+2, 121, 44, 17, 7),
                                                                                            self.lumi()["had"] /self.lumi()["mcZinv"]),
                                                                                     isExcl))
                                                             ])

        self._mcStatError = {
            "mcMuonErr":                   (  59.5,    40.4,     7.0,    4.1,    2.7,    1.4,    0.7,   0.6),
            "mcTtwErr":                    (  71.2,    44.2,     7.3,    4.5,    2.5,    1.9,    0.8,   0.6),
            "mcGjetsErr":           scaled((  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,      8,      5,     3), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErrTM":          scaled(( 10.39,    6.71,  0.2e+2, 0.1e+2,      6,      4,      2,     1), self.lumi()["had"] /self.lumi()["mcZinv"]),
            "mcZinvErrDB":                 ( 10.59,    6.79,     5.8,    3.4,    2.1,    1.2,    0.8,   0.6),
            "mcMumuErr":                   (  7.09,    5.48,     4.2,    2.5,    1.9,    1.0,    0.1,   0.7),
            }
        self._mcStatError["mcZinvErr"] = self._mcStatError["mcZinvErrDB"]
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) \
                                                          for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        self._mcExtraBeforeTrigger["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) \
                                                          for gJet,purity in zip(self._mcExpectationsBeforeTrigger["mcGjets"], self._purities["phot"])])

        syst.load(self, mode = self.systMode)

class data_53_v1(data) :
    """all samples have an alphaT cut applied in all bins"""
    
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
            "mcMumu":  4650.,
            }
        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02) #old
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad":           (     None,      None,      None,      None,      93.0,     44.0,      6.0,       13.0, ),
            "nMuon":          (     None,      None,      None,      None,      30.0,     12.0,      3.0,        5.0,  ),
            "nMumu":          (     None,      None,      None,      None,       2.0,      2.0,      0.0,        0.0,    ),
            "nPhot":     excl((     None,      None,      None,      None,      50.0,     18.0,      11.0,       7.0), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcMuon"             : ( 0.0, 0.0, 0.0, 0.0, 35.67, 14.08, 5.375, 4.364, ),
            "mcTtw"              : ( 0.0, 0.0, 0.0, 0.0, 52.73, 24.21, 8.981, 7.198, ),
            "mcZinv"             : ( 0.0, 0.0, 0.0, 0.0, 27.65, 10.29, 4.737, 4.541, ),
            "mcMumu"             : ( 0.0, 0.0, 0.0, 0.0, 2.068, 0.2834,0.0, 0.01233, ),
            #"mcMumu"             : ( 0.0, 0.0, 0.0, 0.0, 2.068, 0.283, 0.0,   0.012, ),
            "mcGjets": excl(scaled((   None,   None,    None,    None,    68.0,   26.0,   13.0,    7.0), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            }

        print "check sensitivity to mumu"

        self._mcStatError = {
            "mcMuonErr"          :   ( 0.0, 0.0, 0.0, 0.0, 2.202, 1.266, 0.7977, 0.775, ) ,
            "mcMumuErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.851, 0.3309, 0.0, 0.01206, ) ,
            "mcZinvErr"          :   ( 0.0, 0.0, 0.0, 0.0, 1.329, 0.8108, 0.5501, 0.5386, ) ,
            "mcTtwErr"           :   ( 0.0, 0.0, 0.0, 0.0, 2.461, 1.729, 1.087, 0.8485, ) ,
            "mcGjetsErr":           scaled((  None,    None,    None,   None,    7.0,    4.0,    3.0,   2.0), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None)\
                                                          for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        self._mcExtraBeforeTrigger["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None)\
                                                          for gJet,purity in zip(self._mcExpectationsBeforeTrigger["mcGjets"], self._purities["phot"])])
        
        syst.load(self, mode = self.systMode)

class data_52_v1(data) :
    """all samples have an alphaT cut applied in all bins"""
    
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
            "mcMumu":  4650.,
            }
        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02) #old
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),

            "nHad":           (     None,      None,      None,      None,      None,      None,      15.0,      17.0),
            "nMuon":          (     None,      None,      None,      None,      None,      None,       1.0,       4.0),
            "nMumu":          (     None,      None,      None,      None,      None,      None,       0.0,       0.0),
            "nPhot":     excl((     None,      None,      None,      None,      None,      None,       5.0,       3.0), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcMuon":         scaled((   None,   None,    None,    None,    None,   None,    7.0,    4.2), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":          scaled((   None,   None,    None,    None,    None,   None,   12.2,    7.6), self.lumi()["muon"]/self.lumi()["mcTtw"]),
            "mcGjets":   excl(scaled((   None,   None,    None,    None,    None,   None,    4.0,    2.0), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcZinv":                (   None,   None,    None,    None,    None,   None,    5.4,    5.2),
            "mcMumu":         scaled((   None,   None,    None,    None,    None,   None,    0.0,    0.47), self.lumi()["mumu"]/self.lumi()["mcMumu"]),
            }

        self._mcStatError = {
            "mcMuonErr":                   (  None,    None,    None,   None,   None,   None,    1.0,   0.6),
            "mcTtwErr":                    (  None,    None,    None,   None,   None,   None,    1.2,   1.0),
            "mcGjetsErr":           scaled((  None,    None,    None,   None,   None,   None,    2.0,   1.0), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErr":                   (  None,    None,    None,   None,   None,   None,    0.6,   0.6),
            "mcMumuErr":                   (  None,    None,    None,   None,   None,   None,    0.0,   0.4),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None)\
                                                          for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        self._mcExtraBeforeTrigger["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None)\
                                                          for gJet,purity in zip(self._mcExpectationsBeforeTrigger["mcGjets"], self._purities["phot"])])
        
        syst.load(self, mode = self.systMode)
