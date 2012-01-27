import utils
from data import data,scaled,excl,trig

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

            "mumu":    4650.,
            "mcZmumu": 4650.,
            }
        self._htMeans =       ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02) #old
        self._sigEffCorr =    (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)
        self._observations = {
            "nHadBulk":scaled(( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06), self.lumi()["had"]/self.lumi()["hadBulk"]),

            "nHad":           (     396.0,     203.0,     156.0,      50.0,      17.0,       7.0,       3.0,       2.0),
            "nMuon":          (     304.0,     114.0,     116.0,      44.0,      14.0,       4.0,       2.0,       1.0),
            "nMumu":          (       9.0,       5.0,       5.0,       1.0,       1.0,       0.0,       0.0,       1.0),
            }

        self._triggerEfficiencies = {
            "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
            "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
            }

        self._mcExpectations = {
            "mcMuon":     trig(     scaled(( 359.75, 173.21,  109.14,   39.67,  19.36,   4.84,   0.85,   0.52), self.lumi()["muon"]/self.lumi()["mcMuon"]),
                                    self._triggerEfficiencies["had"]),
            "mcTtw":      trig(     scaled(( 391.76, 163.16,  133.24,   52.21,  16.98,   8.90,   1.10,   1.49), self.lumi()["muon"]/self.lumi()["mcTtw"]),
                                    self._triggerEfficiencies["had"]),
            "mcZinv":     trig(            (  86.75,  35.80,   25.30,   10.69,    3.5,    1.4,    0.5,    0.2),
                                    self._triggerEfficiencies["had"]),
            "mcZmumu":    trig(     scaled((  13.55,   6.17,    2.13,    2.64,    0.0,    0.6,    0.1,    1.0), self.lumi()["mumu"]/self.lumi()["mcZmumu"]),
                                    self._triggerEfficiencies["had"]),
            }

        self._mcStatError = {
            "mcMuonErr": (15.88, 11.03, 4.28, 2.57, 1.82, 0.94, 0.34, 0.23),
            "mcTtwErr":  (15.90, 11.24, 4.76, 3.00, 1.65, 1.25, 0.42, 0.49),
            "mcZinvErr": (2.40,  1.51, 1.27, 0.82, 0.47, 0.30, 0.18, 0.13),
            "mcZmumuErr":(2.07,  1.54, 0.81, 0.93, 0.01, 0.49, 0.16, 0.53),
            }
        #self._mcStatError["mcHadErr"] = tuple([utils.quadSum([ttwErr, zinvErr]) for ttwErr,zinvErr in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

        print "the mumu purities are old"
        self._purities = {
            "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
            "mumu":                  (  0.89,    0.94,    0.97,   0.97,   0.97,   0.97,   0.97, 0.97),#old
            }

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        self._mcExtra["mcMumu"] = tuple([(zMumu/purity if (zMumu and purity) else None) for zMumu,purity in zip(self._mcExpectations["mcZmumu"], self._purities["mumu"])])
        
        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,

            "k_qcd_nom"     : 2.89e-2,
            "k_qcd_unc_inp" : 0.76e-2,

            #"k_qcd_nom"     : 3.30e-2,
            #"k_qcd_unc_inp" : 0.66e-2,

            #"k_qcd_nom"     : 2.89e-2,
            #"k_qcd_unc_inp" : 0.01e-2,
            }
