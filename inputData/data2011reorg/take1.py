from inputData import syst
from data import data,scaled,excl

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
    #self._mcExtraBeforeTrigger["mcHad"] =\
    #    tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectationsBeforeTrigger["mcTtw"], self._mcExpectationsBeforeTrigger["mcZinv"])])
    #self._mcStatError["mcHadErr"] =\
    #    tuple([utils.quadSum([x,y]) for x,y in zip(self._mcStatError["mcTtwErr"], self._mcStatError["mcZinvErr"])])

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

class data_ge3b(data) :
    def _fill(self) :
        self._observations =  	{
            "nPhot"              :   ( None, None, None, None, 0.0, 0.0, 0.0, 0.0, ) ,
            "nHad"               :   ( 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nMuon"              :   ( 7.0, 3.0, 1.0, 2.0, 1.0, 1.0, 0.0, 1.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
            }
        
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, None, None, 0.0, 0.0, 0.0, 0.0, ) ,
            "mcHad"              :   ( 1.66, 0.5574, 0.4085, 0.3462, 0.5055, 0.1435, 0.1701, 0.07223, ) ,
            "mcTtw"              :   ( 1.564, 0.5395, 0.4072, 0.3462, 0.3517, 0.1435, 0.08606, 0.07223, ) ,
            "mcMuon"             :   ( 8.184, 4.701, 3.612, 4.695, 1.649, 1.07, 0.8091, 0.8097, ) ,
            "mcZinv"             :   ( 0.09607, 0.01792, 0.001227, 0.0, 0.1538, 0.0, 0.08399, 0.0, ) ,
            "mcMumu"             :   ( 0.05593, 0.03217, 0.0233, 0.08809, 0.02021, 0.01015, 0.005773, 0.002408, ) ,
            }
        
        self._mcStatError =  	{
            "mcMuonErr"          :   ( 0.3687, 0.2328, 0.1914, 0.1731, 0.08445, 0.07864, 0.063, 0.06324, ) ,
            "mcMumuErr"          :   ( 0.01281, 0.007656, 0.006344, 0.04631, 0.008503, 0.00691, 0.005625, 0.001729, ) ,
            "mcHadErr"           :   ( 0.1238, 0.04481, 0.04065, 0.03996, 0.1361, 0.03214, 0.08661, 0.01196, ) ,
            "mcZinvErr"          :   ( 0.05165, 0.01405, 0.001198, 0.0, 0.129, 0.0, 0.08122, 0.0, ) ,
            "mcTtwErr"           :   ( 0.1125, 0.04255, 0.04064, 0.03996, 0.0433, 0.03214, 0.03009, 0.01196, ) ,
            "mcPhotErr"          :   ( None, None, None, None, 0.0, 0.0, 0.0, 0.0, ) ,
            }
        common(self)
