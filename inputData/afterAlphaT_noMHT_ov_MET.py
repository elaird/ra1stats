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

            "nHad":           ( 1.028e+04,   3.2e+03, 1.526e+03,     401.0,     127.0,      44.0,      14.0,       6.0),
            "nMuon":          (    1421.0,     645.0,     517.0,     169.0,      52.0,      18.0,       8.0,       1.0),
            "nMumu":          (     114.0,      65.0,      42.0,      15.0,       7.0,       1.0,       0.0,       2.0),
            "nPhot":     excl((      None,      None,      1642,       596,       221,        91,        32,        14), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcMuon":          scaled((1690.37, 771.57,  525.06,  181.64,  70.84,  22.64,   7.53,   5.19), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":           scaled((2244.21, 874.85,  571.91,  206.83,  70.18,  31.07,   8.48,   6.14), self.lumi()["muon"]/self.lumi()["mcTtw"]),
            "mcGjets":    excl(scaled((  None,    None, 2.00e+3,  7.1e+2, 2.7e+2,     92,     34,     14), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
        #    "mcZinv01":               (1706.7,  718.03,     0.0,     0.0,    0.0,    0.0,    0.0,    0.0),
        #    "mcZinv27":   excl(scaled((    0.0,    0.0,  8.9e+2,  3.3e+2,    121,     44,     17,      7), self.lumi()["had"] /self.lumi()["mcZinv"]), isExcl),
            "mcMumu":          scaled((133.43,   77.45,   46.82,   17.74,   9.43,   3.03,   0.13,   1.91), self.lumi()["mumu"]/self.lumi()["mcMumu"]),
            "mcZinv"          :        ( 1.888e+03, 778.2, 565.0, 194.6, 73.72, 24.79, 10.24, 7.041, )
            }

        for item in ["mcTtw"] :
            total = [0.0]*8
            for key,value in { 
                              "mcHadWJets"         :   ( 1.957e+03, 703.3, 412.2, 137.5, 48.12, 15.92, 6.587, 4.475, ) ,
                              "mcHadtt"            :   ( 777.4, 312.5, 238.4, 84.89, 23.97, 15.53, 1.68, 1.161, ) ,
                              "mcHadWZ"            :   ( 18.85, 6.555, 3.345, 0.927, 0.3728, 0.155, 0.01635, 0.04432, ) ,
                              "mcHadWW"            :   ( 19.92, 5.773, 3.597, 1.29, 0.2639, 0.1313, 0.08237, 0.0, ) ,
                              "mcHadZZ"            :   ( 12.96, 4.669, 2.851, 0.7757, 0.1871, 0.08342, 0.0154, 0.001839, ) ,
                              "mcHadDY"            :   ( 20.61, 6.944, 6.033, 1.151, 0.4669, 0.0, 0.0, 0.0, ) ,
                              "mcHadt"             :   ( 68.54, 25.19, 15.61, 5.128, 1.681, 0.6776, 0.1033, 0.5094, ) ,
            }.iteritems() :
                for i in range(len(total)) :
                    total[i] += value[i]
            self._mcExpectationsBeforeTrigger[item] = total


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
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        self._mcExtraBeforeTrigger["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectationsBeforeTrigger["mcGjets"], self._purities["phot"])])
        
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
            "mcMumu": 4650.,
            }
        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02) #old
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),

            "nHad":           (     None,      None,      None,      None,     131.0,      58.0,      11.0,      15.0),
            "nMuon":          (     None,      None,      None,      None,      36.0,      18.0,       4.0,       5.0),
            "nMumu":          (     None,      None,      None,      None,       2.0,       2.0,       0.0,       1.0),
            "nPhot":     excl((     None,      None,      None,      None,      50.0,      18.0,      11.0,       7.0), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcMuon":         scaled((   None,   None,    None,    None,   46.64,  17.35,   6.12,   4.85), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":          scaled((   None,   None,    None,    None,   65.31,  30.30,  11.55,   8.47), self.lumi()["muon"]/self.lumi()["mcTtw"]),
            "mcGjets":   excl(scaled((   None,   None,    None,    None,    68.0,   26.0,   13.0,    7.0), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcMumu":        scaled((   None,   None,    None,    None,     3.1,    0.7,    0.0,    0.4), self.lumi()["mumu"]/self.lumi()["mcMumu"]),
            "mcZinv":    ( None, None, None, None, 39.77, 12.92, 6.197, 5.867, )
            }

        for item in ["mcTtw"] :
            total = [0.0]*8
            for key,value in { 
                              "mcHadWJets"         :   ( 0.0, 0.0, 0.0, 0.0, 40.42, 15.11, 6.196, 5.155, ) ,
                              "mcHadtt"            :   ( 0.0, 0.0, 0.0, 0.0, 30.96, 18.3, 4.996, 2.883, ) ,
                              "mcHadWZ"            :   ( 0.0, 0.0, 0.0, 0.0, 0.1078, 0.05251, 0.04993, 0.06678, ) ,
                              "mcHadWW"            :   ( 0.0, 0.0, 0.0, 0.0, 0.341, 0.01148, 0.0, 0.0, ) ,
                              "mcHadZZ"            :   ( 0.0, 0.0, 0.0, 0.0, 0.1407, 0.03368, 0.02328, 0.01147, ) ,
                              "mcHadDY"            :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8456, 0.0, ) ,
                              "mcHadt"             :   ( 0.0, 0.0, 0.0, 0.0, 2.184, 0.6881, 0.4183, 0.5959, ) ,
            }.iteritems() :
                for i in range(len(total)) :
                    total[i] += value[i]
            self._mcExpectationsBeforeTrigger[item] = total

        self._mcStatError = {
            "mcMuonErr":                   (  None,    None,    None,   None,    2.4,    1.3,    0.8,   0.7),
            "mcTtwErr":                    (  None,    None,    None,   None,    2.6,    1.9,    1.2,   0.8),
            "mcGjetsErr":           scaled((  None,    None,    None,   None,    7.0,    4.0,    3.0,   2.0), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErr":                   (  None,    None,    None,   None,    1.5,    0.9,    0.6,   0.6),
            "mcMumuErr":                   (  None,    None,    None,   None,    1.0,    0.5,    0.0,   0.4),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        self._mcExtraBeforeTrigger["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectationsBeforeTrigger["mcGjets"], self._purities["phot"])])
        
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

            "nHad":           (     None,      None,      None,      None,      None,      None,      23.0,      30.0),
            "nMuon":          (     None,      None,      None,      None,      None,      None,       2.0,       9.0),
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
            "mcMuon":         scaled((   None,   None,    None,    None,    None,   None,   10.1,    7.2), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":          scaled((   None,   None,    None,    None,    None,   None,   18.9,   12.3), self.lumi()["muon"]/self.lumi()["mcTtw"]),
            "mcGjets":   excl(scaled((   None,   None,    None,    None,    None,   None,    4.0,    2.0), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcMumu":         scaled((   None,   None,    None,    None,    None,   None,    0.0,    0.4), self.lumi()["mumu"]/self.lumi()["mcMumu"]),
            "mcZinv":   ( None, None, None, None, None, None, 8.789, 8.168, ) ,
            }

        for item in ["mcTtw"] :
            total = [0.0]*8
            for key,value in { 
                              "mcHadWJets"         :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.277, 6.026, ) ,
                              "mcHadtt"            :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.274, 6.368, ) ,
                              "mcHadWZ"            :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.032, 0.06486, ) ,
                              "mcHadWW"            :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02859, 0.03513, ) ,
                              "mcHadZZ"            :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01413, 0.01994, ) ,
                              "mcHadDY"            :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4669, 0.0, ) ,
                              "mcHadt"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.787, 0.7636, ) ,
            }.iteritems() :
                for i in range(len(total)) :
                    total[i] += value[i]
            self._mcExpectationsBeforeTrigger[item] = total

        self._mcStatError = {
            "mcMuonErr":                   (  None,    None,    None,   None,   None,   None,    1.1,   0.9),
            "mcTtwErr":                    (  None,    None,    None,   None,   None,   None,    1.5,   1.2),
            "mcGjetsErr":           scaled((  None,    None,    None,   None,   None,   None,    3.0,   2.0), self.lumi()["phot"]/self.lumi()["mcGjets"]),
            "mcZinvErr":                   (  None,    None,    None,   None,   None,   None,    0.7,   0.7),
            "mcMumuErr":                   (  None,    None,    None,   None,   None,   None,    0.0,   0.4),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        self._mcExtraBeforeTrigger["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectationsBeforeTrigger["mcGjets"], self._purities["phot"])])
        
        syst.load(self, mode = self.systMode)
