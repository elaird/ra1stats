from inputData import syst
import utils
from data import data,scaled,excl

class data_55_0btag(data) :
    """muons and mumu have alt in all bins"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)
        
        self._lumi = {
            "had"                :   4.98e+03 ,
            "mcHad"              :   4.98e+03 ,
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
            "nHad"               :   ( 2.919e+03, 1.166e+03, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
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
            "mcTtw"              :   ( 1.653e+03, 634.6, 396.1, 135.3, 46.53, 16.7, 6.068, 3.879, ) ,
            "mcHad"              :   ( 3.185e+03, 1.3e+03, 897.0, 312.2, 114.3, 39.14, 15.51, 10.3, ) ,
            "mcZinv"             :   ( 1.532e+03, 665.5, 500.9, 176.9, 67.75, 22.44, 9.445, 6.426, ) ,
            "mcMumu"             :   ( 120.3, 70.26, 47.21, 16.62, 8.834, 2.355, 0.1308, 1.351, ) ,
            "mcMuon"             :   ( 1.198e+03, 563.9, 305.8, 104.6, 41.44, 13.92, 5.235, 3.19, ) ,
	    }
        
        self._mcStatError = {
            "mcGjetsErr"         :   (  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,  8,   5,   3), #>=0 b-tag
            "mcTtwErr"           :   ( 74.89, 55.58, 5.17, 3.189, 2.002, 1.131, 0.5627, 0.4215, ) ,
            "mcZinvErr"          :   ( 12.05, 7.545, 6.928, 4.141, 2.51, 1.409, 0.8549, 0.6651, ) ,
            "mcMuonErr"          :   ( 63.0, 43.93, 4.764, 2.659, 1.823, 0.9047, 0.5631, 0.4456, ) ,
            "mcMumuErr"          :   ( 7.357, 5.855, 4.826, 2.929, 2.084, 1.05, 0.1308, 0.7376, ) ,
            "mcHadErr"           :   ( 75.85, 56.09, 8.645, 5.226, 3.211, 1.807, 1.023, 0.7874, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        syst.load(self, mode = self.systMode)

