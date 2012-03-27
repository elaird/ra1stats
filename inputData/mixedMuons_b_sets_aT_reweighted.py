import syst,utils
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
            "mcTtw"              :   ( 1.618e+03, 601.0, 375.0, 128.5, 44.18, 17.49, 5.826, 4.086, ) ,
            "mcHad"              :   ( 3.125e+03, 1.233e+03, 847.2, 292.4, 106.8, 38.61, 14.9, 10.25, ) ,
            "mcZinv"             :   ( 1.506e+03, 631.7, 472.2, 163.9, 62.67, 21.12, 9.074, 6.161, ) ,
            "mcMumu"             :   ( 110.2, 65.53, 42.25, 12.8, 7.516, 2.394, 0.0, 0.9159, ) ,
            "mcMuon"             :   ( 1.149e+03, 531.9, 292.9, 102.7, 38.61, 12.55, 4.882, 3.063, ) ,
	    }
        
        self._mcStatError = {
            "mcGjetsErr"         :   (  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,  8,   5,   3), #>=0 b-tag
            "mcTtwErr"           :   ( 77.06, 56.91, 5.603, 3.397, 2.109, 1.531, 0.6946, 0.4814, ) ,
            "mcZinvErr"          :   ( 12.1, 7.488, 6.895, 3.962, 2.47, 1.435, 0.8611, 0.6675, ) ,
            "mcMuonErr"          :   ( 64.94, 44.18, 5.665, 3.087, 1.992, 0.9132, 0.5747, 0.4453, ) ,
            "mcMumuErr"          :   ( 7.134, 5.709, 4.533, 2.59, 1.923, 1.067, 0.0, 0.6509, ) ,
            "mcHadErr"           :   ( 78.0, 57.4, 8.884, 5.219, 3.248, 2.098, 1.106, 0.823, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        syst.load(self, mode = self.systMode)
