import utils,syst
from data import data,scaled,excl

class data_55_v1(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
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
            "nHad": (784.0, 370.0, 274.0, 91.0, 31.0, 13.0, 4.0, 2.0), 
            "nMuon": (472.0, 201.0, 854.0, 456.0, 192.0, 77.0, 33.0, 44.0), 
            "nMumu": (19.0, 12.0, 43.0, 27.0, 15.0, 9.0, 1.0, 6.0),
            "nPhot":     excl((      None,      None,       221,        84,        37,        16,         7,         2), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcTtw"              :   ( 624.7, 273.4, 196.8, 78.22, 25.77, 13.73, 2.643, 2.032, ) ,
            "mcZinv"             :   ( 191.1, 82.26, 56.65, 23.94, 9.035, 3.092, 1.058, 0.8448, ) ,
            "mcMumu"             :   ( 22.76, 11.55, 38.84, 17.58, 9.805, 3.965, 1.241, 2.212, ) ,
            "mcMuon"             :   ( 549.9, 241.0, 890.1, 457.8, 219.3, 94.33, 43.34, 46.66, ) ,
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
	    }
        
        print "put in new stat errors"
        self._mcStatError = {
            "mcMuonErr": (15.88, 11.03,10.16, 7.38, 5.10, 3.30, 2.22, 2.14),
            "mcTtwErr":  (15.90, 11.24, 4.76, 3.00, 1.65, 1.25, 0.42, 0.49),
            "mcGjetsErr": (None,  None,   10,    7,    5,    3,    2,    2),
            "mcZinvErr": (2.40,  1.51, 1.27, 0.82, 0.47, 0.30, 0.18, 0.13),
            "mcMumuErr":(2.07,  1.54, 2.63, 1.59, 1.07, 0.83, 0.64, 0.79),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)
