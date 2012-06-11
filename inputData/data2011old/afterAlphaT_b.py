from inputData import syst
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

            "nHad":           (     396.0,     203.0,     156.0,      50.0,      17.0,       7.0,       3.0,       2.0),
            "nMuon":          (     304.0,     114.0,     116.0,      44.0,      14.0,       4.0,       2.0,       1.0),
            "nMumu":          (       9.0,       5.0,       5.0,       1.0,       1.0,       0.0,       0.0,       1.0),
            "nPhot":     excl((      None,      None,       101,        28,        11,         5,         1,         1), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcMuon":          scaled(( 359.75, 173.21,  109.14,   39.67,  19.36,   4.84,   0.85,   0.52), self.lumi()["muon"]/self.lumi()["mcMuon"]),
            "mcTtw":           scaled(( 391.76, 163.16,  133.24,   52.21,  16.98,   8.90,   1.10,   1.49), self.lumi()["muon"]/self.lumi()["mcTtw"]),
            "mcGjets":    excl(scaled((  None,    None,      91,      34,     15,      7,      4,    0.7), self.lumi()["phot"]/self.lumi()["mcGjets"]), isExcl),
            "mcZinv":                 (  86.75,  35.80,   25.30,   10.69,    3.5,    1.4,    0.5,    0.2),
            "mcMumu":         scaled((  13.55,   6.17,    2.13,    2.64,    0.1,    0.6,    0.1,    1.0), self.lumi()["mumu"]/self.lumi()["mcMumu"]),
            }

        self._mcStatError = {
            "mcMuonErr": (15.88, 11.03, 4.28, 2.57, 1.82, 0.94, 0.34, 0.23),
            "mcTtwErr":  (15.90, 11.24, 4.76, 3.00, 1.65, 1.25, 0.42, 0.49),
            "mcGjetsErr":( None,  None, 8   ,    5,    3,    2,    2,  0.7),
            "mcZinvErr": (2.40,  1.51, 1.27, 0.82, 0.47, 0.30, 0.18, 0.13),
            "mcMumuErr":(2.07,  1.54, 0.81, 0.93, 0.01, 0.49, 0.16, 0.53),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)
