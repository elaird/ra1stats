from inputData import syst
from data import data,scaled,excl
import utils

## traditional numbers (predictions only ge3b), organized into one file ##

def common(x, systMode = 3) :
    x._htBinLowerEdges = (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
    x._htMaxForPlot = 975.0
    x._htMeans = ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02)
    x._mergeBins = None

    x._lumi = {
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

    x._triggerEfficiencies = {
        "hadBulk":       (     0.878,     0.906,     0.957,     1.000,     1.000,     1.000,     1.000,     1.000),
        "had":           (     0.727,     0.869,     0.943,     1.000,     1.000,     1.000,     1.000,     1.000),
        "muon":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
        "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
        "mumu":          (     0.727,     0.869,     0.950,     0.950,     0.950,     0.950,     0.950,     0.950),
        }

    x._purities = {
        "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
        }
    
    x._mcExtraBeforeTrigger = {}
    x._mcExtraBeforeTrigger["mcHad"] =\
        tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(x._mcExpectationsBeforeTrigger["mcTtw"], x._mcExpectationsBeforeTrigger["mcZinv"])])
    x._mcStatError["mcHadErr"] =\
        tuple([utils.quadSum([a,b]) for a,b in zip(x._mcStatError["mcTtwErr"], x._mcStatError["mcZinvErr"])])

    x._observations["nHadBulk"] = ( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06)
    syst.load(x, mode = systMode)

class data_0b(data) :
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     1,     0)

        self._observations = {
            "nHad"               :   ( 2.919e+03, 1.166e+03, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
            "nMuon"              :   ( 949.0, 444.0, 281.0, 77.0, 23.0, 11.0, 5.0, 0.0, ) ,
            "nMumu"              :   ( 95.0, 53.0, 35.0, 11.0, 4.0, 1.0, 0.0, 1.0, ) ,
            "nPhot"          : excl((  None, None, 1642-221, 596-84, 221-37, 91-16,   32-7,  14-2), isExcl), #>=0 b-tag minus >=1 b-tag
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
        common(self)

class data_1b(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)
        
        self._observations = {
            "nHad"               :   ( 614.0, 294.0, 214.0, 71.0, 20.0, 6.0, 4.0, 0.0, ) ,
            "nMuon"              :   ( 347.0, 146.0, 568.0, 288.0, 116.0, 48.0, 22.0, 26.0, ) ,
            "nMumu"              :   ( 15.0, 9.0, 34.0, 20.0, 10.0, 7.0, 0.0, 6.0, ) ,
            "nPhot":     excl((      None,      None,       200,        74,        31,        12,         7,         2), isExcl),
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
        common(self)

class data_2b(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     1,     0,     0,     0)
        
        self._observations = {
            "nHad"               :   ( 160.0, 68.0, 52.0, 19.0, 11.0, 7.0, 0.0, 2.0, ) ,
            "nMuon"              :   ( 116.0, 49.0, 264.0, 152.0, 63.0, 26.0, 10.0, 14.0, ) ,
            "nMumu"              :   ( 4.0, 3.0, 8.0, 7.0, 5.0, 2.0, 0.0, 0.0, ) ,
            "nPhot":            excl(( None,  None,  20,  10,  6,  4,  0,  0), isExcl),
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
        common(self)

class data_ge3b(data) :  #v4
    """muons and mumu have no alt cut for highest six bins;
    MC expectations computed using measured b-eff. and mis-tag rate and ``matrix algebra''
    including scale factors"""

    def _fill(self) :
        isExcl =                         (    1,     1,     0,     0,     0,     0,     0,     1)
        self._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)

        self._observations = {
            "nHad"               :   ( 10.0, 8.0, 8.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nMuon"              :   ( 9.0, 6.0, 22.0, 16.0, 13.0, 3.0, 1.0, 4.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, ) ,
            "nPhot"              :   (None, None,  1,   0,   0,   0,   0,   0, ),
            }

	self._mcExpectationsBeforeTrigger = {
            "mcGjets"  : excl(       (  None,  None,  1.0, 0.8, 0.0, 0.0, 0.0, 0.0 ), isExcl),
            #"mcTtw"              :   ( 14.98, 4.788, 4.243, 2.604, 0.5211, 0.3001, 0.01408, 0.06082, ) ,
            #"mcTtw"               :   ( 7.313, 2.8670, 2.720, 1.5100,0.640397,0.469682,0.079102,0.064794,), #March 26 (ttw and zInv)
            "mcTtw"               :   (12.783, 5.0463, 4.925, 3.1325,1.291151,0.975077,0.130844,0.117748,), #March 27 (ttw and zInv)

            #"mcZinv"             :   ( 1.079, 0.5188, 0.316, 0.1634, 0.0, 0.09114, 0.0, 0.0, ) ,
            #"mcZinv"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), #March 26 ttw has both
            "mcZinv"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), #March 27 ttw has both

            "mcMumu"             :   ( 0.01635, 0.0, 0.6904, 0.0, 0.002354, 0.0, 0.0, 0.0, ) ,
            #"mcMuon"            :   ( 13.1, 4.235, 26.51, 15.14, 8.438, 2.703, 1.364, 1.872, ) ,
            #"mcMuon"            :   ( 6.90, 2.94,  14.25,  9.20, 5.238, 1.988, 1.103, 1.169,), #March 26
            "mcMuon"             :   (10.87, 4.561, 20.81, 14.80, 9.018, 3.533, 2.003, 2.485,), #March 27
	    }

        self._mcStatError = {
            "mcGjetsErr"         :   ( None,  None,   0.8, 0.8, 0.0, 0.0, 0.0, 0.0),
            #"mcTtwErr"          :   ( 1.686, 0.9518, 0.8906, 0.6971, 0.2472, 0.2281, 0.05278, 0.05092, ) ,
            "mcTtwErr"           :   ( 0.343, 0.2217, 0.1930, 0.1666, 0.1256, 0.1370, 0.04483, 0.034354,), #March 27

            #"mcZinvErr"         :   ( 0.2626, 0.1821, 0.1421, 0.1022, 0.0, 0.07631, 0.0, 0.0, ) ,
            "mcZinvErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), #March 27

            #"mcMuonErr"         :   ( 1.593, 0.8971, 2.259, 1.693, 1.274, 0.7076, 0.5003, 0.5946, ) ,
            #"mcMuonErr"         :   ( 0.333, 0.1958, 0.379, 0.328, 0.325, 0.1546, 0.1190, 0.1576,), #March 26
            "mcMuonErr"          :   ( 0.380, 0.2289, 0.442, 0.392, 0.403, 0.1836, 0.1467, 0.1891,), #March 27

            "mcMumuErr"          :   ( 0.01389, 0.0, 0.3678, 0.0, 0.003354, 0.0, 0.0, 0.0, ) ,
            }
        common(self)
