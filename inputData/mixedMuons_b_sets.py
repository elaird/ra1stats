import syst
from data import data,scaled,excl

class data_55_0btag(data) :
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
            "nHad"               :   ( 2919.0, 1166.0, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
            "nMuon"              :   ( 949.0, 444.0, 1707.0, 748.0, 305.0, 148.0, 81.0, 87.0, ) ,
            "nMumu"              :   ( 95.0, 53.0, 216.0, 86.0, 48.0, 23.0, 5.0, 11.0, ) ,
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
            "mcMumu"             :   ( 110.6, 65.92, 255.8, 120.0, 53.79, 24.3, 13.31, 10.74, ) ,
            "mcMuon"             :   ( 1145.0, 532.1, 1886.0, 857.3, 371.9, 179.5, 85.31, 104.5, ) ,
	    }
        
        self._mcStatError = {
            "mcGjetsErr"         :   (  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,  8,   5,   3), #>=0 b-tag
            "mcTtwErr"           :   ( 66.98, 40.54, 4.864, 2.85, 1.656, 1.151, 0.5746, 0.4422, ) ,
            "mcZinvErr"          :   ( 9.983, 6.39, 5.518, 3.25, 2.01, 1.167, 0.7642, 0.6292, ) ,
            "mcMuonErr"          :   ( 55.42, 38.09, 11.08, 7.601, 4.916, 3.504, 2.212, 2.589, ) ,
            "mcMumuErr"          :   ( 6.532, 5.065, 10.01, 6.854, 4.576, 3.086, 2.29, 2.037, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])

        syst.load(self, mode = self.systMode)

class data_55_1btag(data) :
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
            "nHad"               :   ( 614.0, 294.0, 214.0, 71.0, 20.0, 6.0, 4.0, 0.0, ) ,
            "nMuon"              :   ( 347.0, 146.0, 568.0, 288.0, 116.0, 48.0, 22.0, 26.0, ) ,
            "nMumu"              :   ( 15.0, 9.0, 34.0, 20.0, 10.0, 7.0, 0.0, 6.0, ) ,
            "nPhot":     excl((      None,      None,       200,        74,        31,        12,         7,         2), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcGjets":        excl(  (  None,    None,     2.0e2,    72,     31,     12,      6,    3  ), isExcl), #>=1 b-tag
            "mcTtw"              :   ( 428.6, 199.0, 143.2, 49.2, 16.34, 9.632, 2.014, 0.7877, ) ,
            "mcZinv"             :   ( 170.1, 72.91, 48.15, 20.86, 7.816, 2.654, 0.9874, 0.8448, ) ,
            "mcMumu"             :   ( 19.41, 6.645, 27.72, 13.81, 8.911, 3.04, 1.211, 2.145, ) ,
            "mcMuon"             :   ( 386.9, 169.7, 582.6, 286.7, 136.0, 60.56, 27.97, 29.74, ) ,
	    }
        
        
        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   10,    7,    5,    3,    2,    1),
            "mcTtwErr"           :   ( 20.84, 16.65, 4.627, 2.682, 1.532, 1.247, 0.4522, 0.2632, ) ,
            "mcZinvErr"          :   ( 3.357, 2.164, 1.754, 1.154, 0.7066, 0.4118, 0.2512, 0.2323, ) ,
            "mcMuonErr"          :   ( 19.8, 12.09, 9.159, 6.487, 4.503, 2.997, 1.957, 1.934, ) ,
            "mcMumuErr"          :   ( 2.598, 1.604, 3.101, 2.188, 1.8, 0.9922, 0.6249, 0.8243, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)

class data_55_2btag(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     1,     0,     0,     0)
        
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
            "nHad"               :   ( 160.0, 68.0, 52.0, 19.0, 11.0, 7.0, 0.0, 2.0, ) ,
            "nMuon"              :   ( 116.0, 49.0, 264.0, 152.0, 63.0, 26.0, 10.0, 14.0, ) ,
            "nMumu"              :   ( 4.0, 3.0, 8.0, 7.0, 5.0, 2.0, 0.0, 0.0, ) ,
            "nPhot":            excl(( None,  None,  20,  10,  6,  4,  0,  0), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectationsBeforeTrigger = {
            "mcGjets"  : excl(       (  None,  None,  25, 9, 3, 3, 0.9, 0.9 ), isExcl),
            "mcTtw"              :   ( 181.1, 69.64, 49.37, 26.42, 8.904, 3.795, 0.6144, 1.183, ) ,
            "mcZinv"             :   ( 19.91, 8.835, 8.185, 2.92, 1.218, 0.3464, 0.07037, 0.0, ) ,
            "mcMumu"             :   ( 3.331, 4.9, 10.42, 3.777, 0.8922, 0.9244, 0.03023, 0.06706, ) ,
            "mcMuon"             :   ( 149.8, 67.0, 281.1, 156.0, 74.87, 31.07, 14.01, 15.05, ) ,
	    }

        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   4, 2, 1, 1, 0.9, 0.9),
            "mcTtwErr"           :   ( 12.19, 6.101, 2.981, 2.186, 1.211, 0.8435, 0.3401, 0.4419, ) ,
            "mcZinvErr"          :   ( 1.137, 0.7513, 0.7231, 0.4319, 0.279, 0.1488, 0.06705, 0.0, ) ,
            "mcMuonErr"          :   ( 8.983, 6.111, 7.206, 5.346, 3.707, 2.384, 1.586, 1.637, ) ,
            "mcMumuErr"          :   ( 0.9278, 1.373, 1.7, 0.9549, 0.395, 0.5199, 0.05894, 0.05347, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)

class data_55_gt2btag(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)

        self._htBinLowerEdges =          (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     1,     0,     0,     0)
        
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
            "nHad"               :   ( 10.0, 8.0, 8.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nMuon"              :   ( 9.0, 6.0, 22.0, 16.0, 13.0, 3.0, 1.0, 4.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, ) ,
            "nPhot"              :   (None, None,  1,   0,   0,   0,   0,   0, ),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectationsBeforeTrigger = {
            "mcGjets"  : excl(       (  None,  None,  1.0, 0.8, 0.0, 0.0, 0.0, 0.0 ), isExcl),
            "mcTtw"              :   ( 14.98, 4.788, 4.243, 2.604, 0.5211, 0.3001, 0.01408, 0.06082, ) ,
            "mcZinv"             :   ( 1.079, 0.5188, 0.316, 0.1634, 0.0, 0.09114, 0.0, 0.0, ) ,
            "mcMumu"             :   ( 0.01635, 0.0, 0.6904, 0.0, 0.002354, 0.0, 0.0, 0.0, ) ,
            "mcMuon"             :   ( 13.1, 4.235, 26.51, 15.14, 8.438, 2.703, 1.364, 1.872, ) ,
	    }
        
        
        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   0.8, 0.8, 0.0, 0.0, 0.0, 0.0),
            "mcTtwErr"           :   ( 1.686, 0.9518, 0.8906, 0.6971, 0.2472, 0.2281, 0.05278, 0.05092, ) ,
            "mcZinvErr"          :   ( 0.2626, 0.1821, 0.1421, 0.1022, 0.0, 0.07631, 0.0, 0.0, ) ,
            "mcMuonErr"          :   ( 1.593, 0.8971, 2.259, 1.693, 1.274, 0.7076, 0.5003, 0.5946, ) ,
            "mcMumuErr"          :   ( 0.01389, 0.0, 0.3678, 0.0, 0.003354, 0.0, 0.0, 0.0, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)

class data_55_gt2btag_v2(data) :
    """muons and mumu have no alt cut for highest six bins;
    MC expectations computed using measured b-eff. and mis-tag rate and ``matrix algebra''"""

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
            "nHad"               :   ( 10.0, 8.0, 8.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nMuon"              :   ( 9.0, 6.0, 22.0, 16.0, 13.0, 3.0, 1.0, 4.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, ) ,
            "nPhot"              :   (None, None,  1,   0,   0,   0,   0,   0, ),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectationsBeforeTrigger = {
            "mcGjets"  : excl(       (  None,  None,  1.0, 0.8, 0.0, 0.0, 0.0, 0.0 ), isExcl),
            #"mcTtw"              :   ( 14.98, 4.788, 4.243, 2.604, 0.5211, 0.3001, 0.01408, 0.06082, ) ,
            #"mcZinv"             :   ( 1.079, 0.5188, 0.316, 0.1634, 0.0, 0.09114, 0.0, 0.0, ) ,
            "mcTtw"               :   ( 7.313, 2.8670, 2.720, 1.5100,0.640397,0.469682,0.079102,0.064794,), #March 26 (ttw and zInv)
            "mcZinv"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), #March 26 ttw has both

            "mcMumu"             :   ( 0.01635, 0.0, 0.6904, 0.0, 0.002354, 0.0, 0.0, 0.0, ) ,
            #"mcMuon"            :   ( 13.1, 4.235, 26.51, 15.14, 8.438, 2.703, 1.364, 1.872, ) ,
            "mcMuon"             :   ( 6.90, 2.94,  14.25,  9.20, 5.238, 1.988, 1.103, 1.169,), #March 26
	    }

        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   0.8, 0.8, 0.0, 0.0, 0.0, 0.0),
            "mcTtwErr"           :   ( 1.686, 0.9518, 0.8906, 0.6971, 0.2472, 0.2281, 0.05278, 0.05092, ) ,
            "mcZinvErr"          :   ( 0.2626, 0.1821, 0.1421, 0.1022, 0.0, 0.07631, 0.0, 0.0, ) ,
            "mcHadErr"           :   (0.266442,0.180258,0.155991,0.137346,0.105424,0.116832,0.039850,0.029252,), #March 26
            #"mcMuonErr"          :   ( 1.593, 0.8971, 2.259, 1.693, 1.274, 0.7076, 0.5003, 0.5946, ) ,
            "mcMuonErr"         :   ( 0.333, 0.1958, 0.379, 0.328, 0.325, 0.1546, 0.1190, 0.1576,), #March 26
            "mcMumuErr"          :   ( 0.01389, 0.0, 0.3678, 0.0, 0.003354, 0.0, 0.0, 0.0, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])

        syst.load(self, mode = self.systMode)
