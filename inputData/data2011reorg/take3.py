from inputData import syst
from data import data
import utils,collections

def common(x) :
    x._htBinLowerEdges = (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
    x._htMaxForPlot = 975.0
    x._htMeans = ( 2.960e+02, 3.464e+02, 4.128e+02, 5.144e+02, 6.161e+02, 7.171e+02, 8.179e+02, 9.188e+02)
    x._mergeBins = None
    x._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)

    x._lumi = {
        "had"                :   4980.0,
        "mcHad"              :   4980.0,

        "muon"               :   4980.0,
        "mcMuon"             :   4980.0,

        "mumu"               :   4980.0,
        "mcMumu"             :   4980.0,

        "phot"               :   4850.0,
        "mcPhot"             :   4850.0,
	}

    x._triggerEfficiencies = {
        "hadBulk":       (     0.88,      0.91,      0.96,      1.00,      1.00,      1.00,      1.00,      1.00),
        "had":           (     0.83,      0.96,      0.99,      1.00,      1.00,      1.00,      1.00,      1.00),
        "muon":          (     0.83,      0.96,      0.913,     0.913,     0.913,     0.913,     0.913,     0.913),
        "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
        "mumu":          (     0.83,      0.96,      0.95,      0.95,      0.96,      0.96,      0.96,      0.97),
        }

    x._purities = {
        "phot":                  (  None,    None,    0.98,   0.99,   0.99,   0.99,   0.99, 0.99),
        }

    lst = []
    for purity,mcPhot in zip(x._purities["phot"], x._mcExpectationsBeforeTrigger["mcPhot"]) :
        if (purity is None) or (mcPhot is None) :
            lst.append(None)
        else :
            lst.append(purity*mcPhot)
    x._mcExpectationsBeforeTrigger["mcGjets"] = tuple(lst)
    
    x._mcExtraBeforeTrigger = {}
    x._mcExtraBeforeTrigger["mcHad"] =\
        tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(x._mcExpectationsBeforeTrigger["mcTtw"], x._mcExpectationsBeforeTrigger["mcZinv"])])
    x._mcStatError["mcHadErr"] =\
        tuple([utils.quadSum([a,b]) for a,b in zip(x._mcStatError["mcTtwErr"], x._mcStatError["mcZinvErr"])])

    x._observations["nHadBulk"] = ( 2.792e+08, 1.214e+08, 8.544e+07, 2.842e+07, 9.953e+06, 3.954e+06, 1.679e+06, 1.563e+06)
    syst.load(x, mode = 124)

class data_0b(data) :
    def _fill(self) :
        self._observations = {
            "nHad"               :   ( 2919.0, 1166.0, 769.0, 255.0, 91.0, 31.0, 10.0, 4.0, ) ,
            "nMuon"              :   ( 949.0, 444.0, 281.0, 77.0, 23.0, 11.0, 5.0, 0.0, ) ,
            "nMumu"              :   ( 95.0, 53.0, 35.0, 11.0, 4.0, 1.0, 0.0, 1.0, ) ,
            "nPhot"              :   ( None, None, 909.0, 328.0, 109.0, 50.0, 13.0, 12.0, ) ,
            }

        self._mcExpectationsBeforeTrigger = {
            "mcPhot"             :   ( None, None, 1185.0, 389.9, 163.9, 50.86, 17.09, 13.9, ) ,
            "mcHad"              :   ( 3.185e+03, 1.3e+03, 897.0, 312.2, 114.3, 39.14, 15.51, 10.3, ) ,
            "mcTtw"              :   ( 1653.0, 634.6, 396.1, 135.3, 46.53, 16.7, 6.068, 3.879, ) ,
            "mcMuon"             :   ( 1198.0, 563.9, 305.8, 104.6, 41.44, 13.92, 5.235, 3.19, ) ,
            "mcZinv"             :   ( 1.532e+03, 665.5, 500.9, 176.9, 67.75, 22.44, 9.445, 6.426, ) ,
            "mcMumu"             :   ( 120.3, 70.26, 47.21, 16.62, 8.834, 2.355, 0.1308, 1.351, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 63.0, 43.93, 4.764, 2.659, 1.823, 0.9047, 0.5631, 0.4456, ) ,
            "mcMumuErr"          :   ( 7.357, 5.855, 4.826, 2.929, 2.084, 1.05, 0.1308, 0.7376, ) ,
            "mcHadErr"           :   ( 75.85, 56.09, 8.645, 5.226, 3.211, 1.807, 1.023, 0.7874, ) ,
            "mcZinvErr"          :   ( 12.05, 7.545, 6.928, 4.141, 2.51, 1.409, 0.8549, 0.6651, ) ,
            "mcTtwErr"           :   ( 74.89, 55.58, 5.17, 3.189, 2.002, 1.131, 0.5627, 0.4215, ) ,
            "mcPhotErr"          :   ( None, None, 28.41, 15.62, 9.98, 5.527, 3.158, 2.819, ) ,
            }
        common(self)

class data_1b(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
    def _fill(self) :
        self._observations =  	{
            "nPhot"              :   ( None,  None, 126.0, 43.0, 19.0, 5.0, 5.0, 2.0, ) ,
            "nHad"               :   ( 614.0, 294.0, 214.0, 71.0, 20.0, 6.0, 4.0, 0.0, ) ,
            "nMuon"              :   ( 347.0, 146.0, 568.0, 288.0, 116.0, 48.0, 22.0, 26.0, ) ,
            "nMumu"              :   ( 15.0, 9.0, 34.0, 20.0, 10.0, 7.0, 0.0, 6.0, ) ,
            }
        
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 139.5, 50.32, 22.63, 7.505, 2.917, 2.52, ) ,
            "mcHad"              :   ( 719.2, 302.6, 222.4, 88.66, 30.4, 13.92, 3.612, 2.717, ) ,
            "mcTtw"              :   ( 531.0, 218.4, 160.4, 64.47, 20.73, 10.34, 2.204, 1.674, ) ,
            "mcMuon"             :   ( 465.9, 203.2, 698.0, 352.2, 160.4, 70.58, 33.13, 38.57, ) ,
            "mcZinv"             :   ( 188.2, 84.16, 61.98, 24.19, 9.67, 3.577, 1.408, 1.043, ) ,
            "mcMumu"             :   ( 18.83, 9.013, 38.95, 16.91, 7.856, 4.197, 1.47, 2.376, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 16.74, 10.21, 15.95, 13.11, 10.86, 9.597, 4.544, 4.261, ) ,
            "mcMumuErr"          :   ( 2.7, 2.017, 3.088, 1.875, 1.129, 1.355, 0.1227, 1.806, ) ,
            "mcHadErr"           :   ( 17.57, 9.945, 9.948, 8.786, 3.76, 2.773, 0.7372, 0.4608, ) ,
            "mcZinvErr"          :   ( 2.871, 1.843, 1.281, 0.934, 0.5089, 0.3007, 0.09626, 0.123, ) ,
            "mcTtwErr"           :   ( 17.34, 9.773, 9.865, 8.736, 3.725, 2.756, 0.7309, 0.4441, ) ,
            "mcPhotErr"          :   ( None, None, 4.317, 3.315, 1.491, 0.1532, 1.789, 1.643, ) ,
            }
        common(self)

class data_2b(data) :
    """muons and mumu have no alt cut for highest six bins"""
    
    def _fill(self) :
        self._observations =  	{
            "nPhot"              :   ( None, None, 10.0, 4.0, 2.0, 4.0, 0.0, 0.0, ) ,
            "nHad"               :   ( 160.0, 68.0, 52.0, 19.0, 11.0, 7.0, 0.0, 2.0, ) ,
            "nMuon"              :   ( 116.0, 49.0, 264.0, 152.0, 63.0, 26.0, 10.0, 14.0, ) ,
            "nMumu"              :   ( 4.0, 3.0, 8.0, 7.0, 5.0, 2.0, 0.0, 0.0, ) ,
            }
        
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 11.54, 3.964, 2.244, 0.7155, 0.2059, 0.2112, ) ,
            "mcHad"              :   ( 175.2, 69.75, 60.04, 26.96, 9.038, 6.249, 0.8612, 0.7922, ) ,
            "mcTtw"              :   ( 155.0, 61.11, 53.4, 24.68, 8.047, 5.922, 0.7604, 0.723, ) ,
            "mcMuon"             :   ( 147.4, 67.01, 279.3, 151.4, 75.46, 29.22, 15.05, 14.54, ) ,
            "mcZinv"             :   ( 20.27, 8.638, 6.646, 2.277, 0.9903, 0.3273, 0.1008, 0.06919, ) ,
            "mcMumu"             :   ( 3.561, 3.035, 9.176, 2.615, 1.024, 0.4874, 0.1777, 0.1956, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 7.866, 5.03, 7.422, 5.702, 4.649, 2.438, 1.74, 1.738, ) ,
            "mcMumuErr"          :   ( 0.8359, 3.322, 1.465, 0.6624, 0.3746, 0.34, 0.2085, 0.05043, ) ,
            "mcHadErr"           :   ( 6.363, 4.161, 3.013, 2.106, 1.242, 1.525, 0.4001, 0.3482, ) ,
            "mcZinvErr"          :   ( 0.9973, 0.6455, 0.5708, 0.2959, 0.2137, 0.0947, 0.03249, 0.01663, ) ,
            "mcTtwErr"           :   ( 6.284, 4.11, 2.959, 2.085, 1.224, 1.522, 0.3988, 0.3478, ) ,
            "mcPhotErr"          :   ( None, None, 2.106, 0.9376, 0.8827, 0.374, 0.06543, 0.05762, ) ,
            }
        common(self)

class data_ge3b(data) :
    def _fill(self) :
        self._observations =  	{
            "nPhot"              :   ( None, None, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nHad"               :   ( 10.0, 8.0, 8.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nMuon"              :   ( 9.0, 6.0, 22.0, 16.0, 13.0, 3.0, 1.0, 4.0, ) ,
            "nMumu"              :   ( 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, ) ,
            }
        
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 0.2498, 0.08695, 0.1018, 0.01385, 0.00884, 0.01918, ) ,
            "mcHad"              :   ( 12.79, 5.185, 5.254, 3.464, 1.33, 1.086, 0.1341, 0.1268, ) ,
            "mcTtw"              :   ( 12.19, 4.937, 5.071, 3.389, 1.284, 1.069, 0.1327, 0.1261, ) ,
            "mcMuon"             :   ( 11.52, 4.897, 22.5, 15.88, 9.567, 3.794, 2.272, 2.899, ) ,
            "mcZinv"             :   ( 0.5948, 0.2481, 0.1827, 0.0749, 0.04606, 0.0175, 0.001412, 0.0006948, ) ,
            "mcMumu"             :   ( 0.1276, 0.1614, 0.2761, 0.1189, 0.04669, 0.0194, 0.00844, 0.01099, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 0.409, 0.2464, 0.4792, 0.4196, 0.4401, 0.1948, 0.1632, 0.2102, ) ,
            "mcMumuErr"          :   ( 0.02782, 0.1423, 0.045, 0.02654, 0.01654, 0.001666, 0.007508, 0.001048, ) ,
            "mcHadErr"           :   ( 0.3398, 0.2381, 0.207, 0.1857, 0.1331, 0.1533, 0.04773, 0.03737, ) ,
            "mcZinvErr"          :   ( 0.03363, 0.02136, 0.0182, 0.01237, 0.01112, 0.007328, 0.000951, 0.0, ) ,
            "mcTtwErr"           :   ( 0.3381, 0.2371, 0.2062, 0.1853, 0.1327, 0.1531, 0.04772, 0.03737, ) ,
            "mcPhotErr"          :   ( None, None, 0.06227, 0.02414, 0.04888, 0.01385, 0.0, 0.0, ) ,
            }
        common(self)


def add(lst = []) :
    dct = collections.defaultdict(float)
    lens = []
    for t in lst :
        lens.append(len(t))
        for i,x in enumerate(t) :
            if x!=None :
                dct[i] += x
            else :
                dct[i] = None
    assert len(set(lens))==1,set(lens)
    return tuple([dct[i] for i in range(len(dct))])

def fetched(lst = [], func = "", attr = "", key = "") :
    return [(getattr(x,func)() if func else getattr(x,attr))[key] for x in lst]
    
class data_ge1b(data) :
    def _fill(self, lst = [data_1b(), data_2b(), data_ge3b()]) :
        self._observations = {}
        for key in ["nPhot", "nHad", "nMuon", "nMumu"] :
            self._observations[key] = add(fetched(lst = lst, func = "observations", key = key))

        self._mcExpectationsBeforeTrigger = {}
        for key in ["mcPhot", "mcHad", "mcTtw", "mcMuon", "mcZinv", "mcMumu"] :
            self._mcExpectationsBeforeTrigger[key] = add(fetched(lst = lst, attr = "_mcExpectationsBeforeTrigger", key = key))

        self._mcStatError = {}
        for key in ["mcMuonErr", "mcMumuErr", "mcHadErr", "mcZinvErr", "mcTtwErr", "mcPhotErr"] :
            self._mcStatError[key] = lst[0].mcStatError()[key]
        common(self)

d = data_ge1b()
