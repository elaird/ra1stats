import syst
from data import data,scaled,excl

class data_55_0btag(data) :
    """muons and mumu have alt in all bins"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     1,     0)
        
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
            "nHad"               :   ( 2919.0, 1166.0, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
            "nMuon"              :   ( 949.0, 444.0, 281.0, 77.0, 23.0, 11.0, 5.0, 0.0, ) ,
            "nMumu"              :   ( 95.0, 53.0, 35.0, 11.0, 4.0, 1.0, 0.0, 1.0, ) ,
            "nPhot"          : excl((  None, None, 1642-221, 596-84, 221-37, 91-16,   32-7,  14-2), isExcl), #>=0 b-tag minus >=1 b-tag
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectationsBeforeTrigger = {
            "mcGjets": excl((  None,    None, 2.00e+3 - 2.3e2, 7.1e+2 - 82, 2.7e+2 - 35,  92-15,   34-6,  14-3), isExcl), #>=0 b-tag minus >=1 b-tag
            "mcTtw"              :   ( 1620.0, 601.5, 375.3, 128.7, 44.36, 17.35, 5.84, 4.109, ) ,
            "mcZinv"             :   ( 1515.0, 635.8, 475.6, 165.3, 63.21, 21.3, 9.142, 6.196, ) ,
            "mcMumu"             :   ( 110.6, 65.92, 42.55, 12.92, 7.587, 2.416, 0.0, 0.9096, ) ,
            "mcMuon"             :   ( 1145.0, 532.1, 292.5, 102.7, 38.63, 12.6, 4.923, 3.084, ) ,
	    }
        
        self._mcStatError = {
            "mcGjetsErr"         :   (  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,  8,   5,   3), #>=0 b-tag
            "mcTtwErr"           :   ( 66.98, 40.54, 4.864, 2.85, 1.656, 1.151, 0.5746, 0.4422, ) ,
            "mcZinvErr"          :   ( 9.983, 6.39, 5.518, 3.25, 2.01, 1.167, 0.7642, 0.6292, ) ,
            "mcMuonErr"          :   ( 55.42, 38.09, 4.415, 2.585, 1.71, 0.8321, 0.5146, 0.3822, ) ,
            "mcMumuErr"          :   ( 6.532, 5.065, 4.06, 2.238, 1.715, 0.9733, 0.0, 0.576, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])

        syst.load(self, mode = self.systMode)
