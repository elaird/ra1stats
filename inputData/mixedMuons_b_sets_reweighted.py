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
            "nHad"               :   ( 2.919e+03, 1.166e+03, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
            "nMuon"              :   ( 949.0, 444.0, 1.707e+03, 748.0, 305.0, 148.0, 81.0, 87.0, ) ,
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
            "mcTtw"              :   ( 1.618e+03, 601.0, 375.0, 128.5, 44.18, 17.49, 5.826, 4.086, ) ,
            "mcZinv"             :   ( 1.506e+03, 631.7, 472.2, 163.9, 62.67, 21.12, 9.074, 6.161, ) ,
            "mcMumu"             :   ( 110.2, 65.53, 254.2, 119.1, 53.41, 24.7, 13.21, 10.71, ) ,
            "mcMuon"             :   ( 1.149e+03, 531.9, 1.887e+03, 856.5, 371.8, 179.7, 85.12, 104.5, ) ,
        }
        
        self._mcStatError = {
            "mcGjetsErr"         :   (  None,    None, 0.04e+3, 0.2e+2, 0.1e+2,  8,   5,   3), #>=0 b-tag
            "mcTtwErr"           :   ( 77.06, 56.91, 5.603, 3.397, 2.109, 1.531, 0.6946, 0.4814, ) ,
            "mcZinvErr"          :   ( 12.1, 7.488, 6.895, 3.962, 2.47, 1.435, 0.8611, 0.6675, ) ,
            "mcMuonErr"          :   ( 64.94, 44.18, 13.23, 8.922, 5.857, 4.717, 2.586, 2.933, ) ,
            "mcMumuErr"          :   ( 7.134, 5.709, 11.16, 7.936, 5.165, 3.397, 3.467, 2.115, ) ,
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
            "mcTtw"              :   ( 432.6, 199.4, 144.7, 50.31, 16.92, 10.06, 2.075, 0.8008, ) ,
            "mcZinv"             :   ( 176.9, 76.16, 50.62, 21.88, 8.212, 2.772, 1.031, 0.88, ) ,
            "mcMumu"             :   ( 19.81, 7.089, 28.69, 14.62, 9.282, 3.116, 1.247, 2.136, ) ,
            "mcMuon"             :   ( 390.6, 170.9, 593.4, 292.8, 138.5, 61.94, 28.65, 29.81, ) ,
	    }
        
        
        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   10,    7,    5,    3,    2,    1),
            "mcTtwErr"           :   ( 23.42, 22.25, 5.427, 3.43, 1.976, 2.221, 0.5263, 0.2402, ) ,
            "mcZinvErr"          :   ( 4.357, 2.619, 2.095, 1.87, 0.835, 0.4906, 0.3131, 0.2947, ) ,
            "mcMuonErr"          :   ( 23.57, 15.14, 10.57, 7.595, 5.525, 4.138, 2.405, 2.22, ) ,
            "mcMumuErr"          :   ( 2.986, 1.878, 3.64, 2.524, 2.072, 1.088, 0.6461, 0.9835, ) ,
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
            "mcTtw"              :   ( 175.1, 66.39, 47.32, 25.34, 8.707, 3.847, 0.6063, 1.139, ) ,
            "mcZinv"             :   ( 19.65, 8.831, 8.274, 2.933, 1.212, 0.3464, 0.07716, 0.0, ) ,
            "mcMumu"             :   ( 3.129, 4.635, 9.793, 3.514, 0.8206, 0.8718, 0.02835, 0.06183, ) ,
            "mcMuon"             :   ( 143.6, 63.06, 266.1, 148.0, 71.06, 29.65, 13.31, 14.37, ) ,
	    }

        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   4, 2, 1, 1, 0.9, 0.9),
            "mcTtwErr"           :   ( 19.57, 6.858, 3.872, 3.303, 1.522, 1.051, 0.3245, 0.4657, ) ,
            "mcZinvErr"          :   ( 1.3, 0.8569, 0.9101, 0.5128, 0.3125, 0.1548, 0.06877, 0.0, ) ,
            "mcMuonErr"          :   ( 9.917, 6.535, 7.99, 5.874, 5.027, 2.564, 1.638, 1.913, ) ,
            "mcMumuErr"          :   ( 0.8724, 4.205, 1.809, 0.8998, 0.3605, 0.5523, 0.02013, 0.06183, ) ,
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
            "mcTtw"              :   ( 14.52, 4.638, 4.115, 2.576, 0.5129, 0.3197, 0.01486, 0.06064, ) ,
            "mcZinv"             :   ( 1.12, 0.5603, 0.3348, 0.1535, 0.0, 0.09399, 0.0, 0.0, ) ,
            "mcMumu"             :   ( 0.01747, 0.0, 0.6829, 0.0, 0.002146, 0.0, 0.0, 0.0, ) ,
            "mcMuon"             :   ( 12.86, 3.949, 25.7, 14.56, 8.121, 2.634, 1.318, 1.882, ) ,
	    }
        
        
        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   0.8, 0.8, 0.0, 0.0, 0.0, 0.0),
            "mcTtwErr"           :   ( 1.916, 0.9796, 1.01, 0.8368, 0.3255, 0.2741, 0.01486, 0.06064, ) ,
            "mcZinvErr"          :   ( 0.4274, 0.224, 0.185, 0.1305, 0.0, 0.09399, 0.0, 0.0, ) ,
            "mcMuonErr"          :   ( 2.82, 0.9221, 2.876, 2.613, 1.296, 0.7105, 0.5531, 0.6301, ) ,
            "mcMumuErr"          :   ( 0.01747, 0.0, 0.5021, 0.0, 0.002146, 0.0, 0.0, 0.0, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)

class data_55_gt0btag(data) :
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
            "nHad"               :   ( 784.0, 370.0, 274.0, 91.0, 31.0, 13.0, 4.0, 2.0, ) ,
            "nMuon"              :   ( 472.0, 201.0, 854.0, 456.0, 192.0, 77.0, 33.0, 44.0, ) ,
            "nMumu"              :   ( 19.0, 12.0, 43.0, 27.0, 15.0, 9.0, 1.0, 6.0, ) ,
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
            "mcTtw"              :   ( 622.3, 270.4, 196.2, 78.23, 26.14, 14.22, 2.697, 2.0, ) ,
            "mcZinv"             :   ( 197.7, 85.56, 59.23, 24.97, 9.424, 3.213, 1.108, 0.88, ) ,
            "mcMumu"             :   ( 22.95, 11.73, 39.17, 18.13, 10.1, 3.987, 1.275, 2.198, ) ,
            "mcMuon"             :   ( 547.1, 237.9, 885.3, 455.5, 217.6, 94.22, 43.29, 46.07, ) ,
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
	    }
        
        self._mcStatError = {
            "mcTtwErr"           :   ( 30.58, 23.3, 6.743, 4.835, 2.515, 2.472, 0.6185, 0.5275, ) ,
            "mcZinvErr"          :   ( 4.567, 2.765, 2.291, 1.944, 0.8916, 0.523, 0.3206, 0.2947, ) ,
            "mcMuonErr"          :   ( 25.72, 16.52, 13.56, 9.95, 7.581, 4.92, 2.962, 2.998, ) ,
            "mcMumuErr"          :   ( 3.111, 4.605, 4.095, 2.679, 2.103, 1.22, 0.6464, 0.9855, ) ,
            "mcGjetsErr": (None,  None,   10,    7,    5,    3,    2,    2),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtraBeforeTrigger = {}
        self._mcExtraBeforeTrigger["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
        
        syst.load(self, mode = self.systMode)
