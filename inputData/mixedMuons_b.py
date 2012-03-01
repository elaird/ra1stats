import utils,syst
from data import data,scaled,excl,trig

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
        self._sigEffCorr =    (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)
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

	self._mcExpectations = {
	    #"mcMumuZZ": (22.7621, 11.547633999999999, 38.84205, 17.582320000000003, 9.805179999999998, 3.9646, 1.2411299999999998, 2.211829), 
	    "mcMumuZinv": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
	    "mcMumuDY": (16.41, 11.24, 25.85, 11.73, 7.567, 2.454, 0.7908, 1.313), 
	    "mcMuonWZ": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
	    "mcHadWJets": (161.6, 91.0, 42.2414, 16.54185, 6.697, 2.102, 1.271, 0.5106), 
	    "mcMuonWW": (2.474, 1.268, 2.042, 0.9139, 0.5024, 0.08564, 0.04701, 0.107), 
	    "mcHadZinv": (191.109, 82.2594, 56.65, 23.94, 9.035, 3.092, 1.058, 0.8448), 
	    "mcMuonZinv": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
	    "mcMuonZZ": (0.0249, 0.01165, 0.02684, 0.03279, 0.0, 0.0, 0.0, 0.0), 
	    "mcMuonWJets": (128.6, 48.15, 187.5704, 86.74132399999999, 41.89, 19.57, 10.49, 14.19), 
	    "mcHadtt": (418.8, 165.3, 141.9, 57.39, 17.69, 11.12, 1.315, 1.147), 
	    "mcHadWZ": (2.548, 0.9855, 0.5878, 0.1452, 0.07848, 0.02962, 0.0, 0.0), 
	    "mcMuont": (37.495000000000005, 17.7392, 49.422, 25.298, 10.824, 4.951, 2.5544, 2.4328000000000003), 
	    "mcHadWW": (3.433, 0.745, 0.6808, 0.3378, 0.02124, 0.07282, 0.0, 0.0), 
	    "mcMuontt": (379.7, 173.4, 644.8, 343.9, 164.3, 68.99, 30.25, 29.42), 
	    "mcHadZZ": (2.751, 1.007, 0.6232, 0.1678, 0.03932, 0.01381, 0.004294, 0.0), 
	    "mcMumut": (0.30479999999999996, 0.047154, 0.5078, 0.32467, 0.174, 0.05267, 0.0323, 0.06706), 
	    "mcMumuWW": (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
	    "mcMumuWJets": (0.0, 0.0, 0.04564, 0.0, 0.0, 0.0, 0.0, 0.0), 
	    "mcMumutt": (5.641, 0.1031, 12.19, 5.322, 2.019, 1.434, 0.4057, 0.8132), 
	    "mcMuonDY": (0.7421, 0.1496, 5.7, 0.6145, 1.707, 0.9712, 0.0, 0.4268), 
	    "mcMumuWZ": (0.1605, 0.04718, 0.09031, 0.08585, 0.01541, 0.0, 0.01233, 0.01233), 
	    "mcHadDY": (1.628, 0.4649, 1.503, 0.4368, 0.0, 0.0, 0.0, 0.0), 
	    "mcHadt": (33.961999999999996, 13.878499999999999, 9.2675, 3.2643, 1.3421699999999999, 0.39313, 0.05267, 0.37420000000000003),
            "mcGjets": excl(       (  None,    None,     2.3e2,    82,     35,     15,      6,    3  ), isExcl),
	    }
        
        for item in ["mcMuon", "mcMumu"] :
            total = [0.0]*8
            for key,value in self._mcExpectations.iteritems() :
                if key[:len(item)]!=item : continue
                for i in range(len(total)) :
                    total[i] += value[i]
            self._mcExpectations[item] = trig(total, self._triggerEfficiencies[item.replace("mc", "").lower()])
        
        for item in ["mcTtw"] :
            total = [0.0]*8
            for key,value in {"mcHadWJets": (161.6, 91.0, 42.2414, 16.54185, 6.697, 2.102, 1.271, 0.5106), 
                              "mcHadtt": (418.8, 165.3, 141.9, 57.39, 17.69, 11.12, 1.315, 1.147), 
                              "mcHadWZ": (2.548, 0.9855, 0.5878, 0.1452, 0.07848, 0.02962, 0.0, 0.0), 
                              "mcHadWW": (3.433, 0.745, 0.6808, 0.3378, 0.02124, 0.07282, 0.0, 0.0), 
                              "mcHadZZ": (2.751, 1.007, 0.6232, 0.1678, 0.03932, 0.01381, 0.004294, 0.0), 
                              "mcHadDY": (1.628, 0.4649, 1.503, 0.4368, 0.0, 0.0, 0.0, 0.0), 
                              "mcHadt": (33.961999999999996, 13.878499999999999, 9.2675, 3.2643, 1.3421699999999999, 0.39313, 0.05267, 0.37420000000000003)}.iteritems() :
                for i in range(len(total)) :
                    total[i] += value[i]
            self._mcExpectations[item] = trig(total, self._triggerEfficiencies["had"])

        self._mcExpectations["mcZinv"] = self._mcExpectations["mcHadZinv"]
        
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

        self._mcExtra = {}
        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        
        syst.load(self, mode = self.systMode)
