import utils
from data import data,scaled,excl,trig
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
        self._sigEffCorr =    (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)

        #### 
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad"               :   ( 2919.0, 1166.0, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
            "nMuon"              :   ( 949.0, 444.0, 1707.0, 748.0, 305.0, 148.0, 81.0, 87.0, ) ,
            "nMumu"              :   ( 95.0, 53.0, 216.0, 86.0, 48.0, 23.0, 5.0, 11.0, ) ,
            "nPhot":     excl((      None,      None,       221,        84,        37,        16,         7,         2), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectations = {
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
            "mcTtw"          : trig(  ( 1620.0, 601.5, 375.3, 128.7, 44.36, 17.35, 5.84, 4.109, ), self._triggerEfficiencies["had"]) ,
            "mcZinv"         : trig(  ( 1515.0, 635.8, 475.6, 165.3, 63.21, 21.3, 9.142, 6.196, ), self._triggerEfficiencies["had"]) ,
            "mcMumu"         : trig(  ( 110.6, 65.92, 255.8, 120.0, 53.79, 24.3, 13.31, 10.74, ), self._triggerEfficiencies["had"]) ,
            "mcMuon"         : trig(  ( 1145.0, 532.1, 1886.0, 857.3, 371.9, 179.5, 85.31, 104.5, ), self._triggerEfficiencies["had"]) ,
	    }
        
        
        print "put in new stat errors"
        self._mcStatError = {
            "mcGjetsErr": (None,  None,   10,    7,    5,    3,    2,    2),
            "mcTtwErr"           :   ( 66.98, 40.54, 4.864, 2.85, 1.656, 1.151, 0.5746, 0.4422, ) ,
            "mcZinvErr"          :   ( 9.983, 6.39, 5.518, 3.25, 2.01, 1.167, 0.7642, 0.6292, ) ,
            "mcMuonErr"          :   ( 55.42, 38.09, 11.08, 7.601, 4.916, 3.504, 2.212, 2.589, ) ,
            "mcMumuErr"          :   ( 6.532, 5.065, 10.01, 6.854, 4.576, 3.086, 2.29, 2.037, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaPhotZ": 0.20,
            "sigmaMuonW": 0.20,
            "sigmaMumuZ": 0.20,

            "k_qcd_nom"     : 2.89e-2,
            "k_qcd_unc_inp" : 0.76e-2,
            }

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
        self._sigEffCorr =    (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)

        #### 
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad"               :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.0, 7.0, ) ,
            "nMuon"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 22.0, 26.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.0, ) ,
            "nPhot":     excl((      None,      None,       221,        84,        37,        16,         7,         2), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectations = {
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
            "mcTtw"          : trig(  ( 1620.0, 601.5, 375.3, 128.7, 44.36, 17.35, 5.84, 4.109, ), self._triggerEfficiencies["had"]) ,
            "mcTtw"          : trig(  ( None, None, 0.0, 0.0, 0.0, 0.0, 3.013, 2.083, ) , self._triggerEfficiencies["had"]) ,
            "mcZinv"         : trig(  ( None, None, 0.0, 0.0, 0.0, 0.0, 0.8416, 0.353, ) , self._triggerEfficiencies["had"]) ,
            "mcMumu"         : trig(  ( None, None, 0.0, 0.0, 0.0, 0.0, 1.211, 2.145, ) , self._triggerEfficiencies["had"]) ,
            "mcMuon"         : trig(  ( None, None, 0.0, 0.0, 0.0, 0.0, 27.97, 29.74, ) , self._triggerEfficiencies["had"]) ,
	    }
        
        
        print "put in new stat errors"
        self._mcStatError = {
            "mcGjetsErr": (None,  None,   10,    7,    5,    3,    2,    2),
            "mcTtwErr"           :   ( None, None, 0.0, 0.0, 0.0, 0.0, 0.6712, 0.5333, ) ,
            "mcZinvErr"          :   ( None, None, 0.0, 0.0, 0.0, 0.0, 0.2319, 0.1502, ) ,
            "mcMuonErr"          :   ( None, None, 0.0, 0.0, 0.0, 0.0, 1.957, 1.934, ) ,
            "mcMumuErr"          :   ( None, None, 0.0, 0.0, 0.0, 0.0, 0.6249, 0.8243, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaPhotZ": 0.20,
            "sigmaMuonW": 0.20,
            "sigmaMumuZ": 0.20,

            "k_qcd_nom"     : 2.89e-2,
            "k_qcd_unc_inp" : 0.76e-2,
            }

class data_55_2btag(data) :
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
        self._sigEffCorr =    (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)

        #### 
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad"               :   ( 0.0, 0.0, 0.0, 0.0, 11.0, 3.0, 0.0, 2.0, ) ,
            "nMuon"              :   ( 0.0, 0.0, 0.0, 0.0, 63.0, 26.0, 10.0, 14.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 5.0, 2.0, 0.0, 0.0, ) ,
            "nPhot":     excl((      None,      None,       221,        84,        37,        16,         7,         2), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectations = {
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
            "mcTtw"          : trig(( None, None, 0.0, 0.0, 9.137, 3.998, 1.44, 0.7699, ) , self._triggerEfficiencies["had"]) ,
            "mcZinv"         : trig(( None, None, 0.0, 0.0, 0.338, 0.1909, 0.297, None, ) , self._triggerEfficiencies["had"]) ,
            "mcMumu"         : trig(( None, None, 0.0, 0.0, 0.8922, 0.9244, 0.0, 0.0, )   , self._triggerEfficiencies["had"]) ,
            "mcMuon"         : trig(( None, None, 0.0, 0.0, 74.87, 31.07, 14.01, 15.05, ) , self._triggerEfficiencies["had"]) ,
	    }
        
        
        print "put in new stat errors"
        self._mcStatError = {
            "mcGjetsErr": (None,  None,   10,    7,    5,    3,    2,    2),
            "mcTtwErr"  : ( None, None, 0.0, 0.0, 1.296, 0.854, 0.4876, 0.371, ) ,
            "mcZinvErr" : ( None, None, 0.0, 0.0, 0.1469, 0.1104, 0.1377, None, ) ,
            "mcMuonErr" : ( None, None, 0.0, 0.0, 3.707, 2.384, 1.586, 1.637, ) ,
            "mcMumuErr" : ( None, None, 0.0, 0.0, 0.395, 0.5199, 0.05894, 0.05347, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaPhotZ": 0.20,
            "sigmaMuonW": 0.20,
            "sigmaMumuZ": 0.20,

            "k_qcd_nom"     : 2.89e-2,
            "k_qcd_unc_inp" : 0.76e-2,
            }

class data_55_gt2btag(data) :
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
        self._sigEffCorr =    (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)

        #### 
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),
            "nHad"               :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, ) ,
            "nMuon"              :   ( 0.0, 0.0, 0.0, 0.0, 13.0, 3.0, 1.0, 4.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, ) ,
            "nPhot":     excl((      None,      None,       221,        84,        37,        16,         7,         2), isExcl),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
            "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
            }

	self._mcExpectations = {
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
            "mcTtw"  : trig(  ( None, None, 0.0, 0.0, 1.733, 0.6396, 0.01408, 0.7542, ) , self._triggerEfficiencies["had"]) ,
            "mcZinv" : trig(  ( None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) , self._triggerEfficiencies["had"]) ,
            "mcMumu" : trig(  ( None, None, 0.0, 0.0, 0.002354, 0.0, 0.0, 0.0, ) , self._triggerEfficiencies["had"]) ,
            "mcMuon" : trig(  ( None, None, 0.0, 0.0, 8.438, 2.703, 1.364, 1.872, ) , self._triggerEfficiencies["had"]) ,
	    }
        
        
        print "put in new stat errors"
        self._mcStatError = {
            "mcGjetsErr": (None,  None,   10,    7,    5,    3,    2,    2),
            "mcTtwErr"           :   ( None, None, 0.0, 0.0, 0.5483, 0.3557, 0.05278, 0.3725, ) ,
            "mcZinvErr"          :   ( None, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "mcMuonErr"          :   ( None, None, 0.0, 0.0, 1.274, 0.7076, 0.5003, 0.5946, ) ,
            "mcMumuErr"          :   ( None, None, 0.0, 0.0, 0.003354, 0.0, 0.0, 0.0, ) ,
            }

        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaPhotZ": 0.20,
            "sigmaMuonW": 0.20,
            "sigmaMumuZ": 0.20,

            "k_qcd_nom"     : 2.89e-2,
            "k_qcd_unc_inp" : 0.76e-2,
            }
