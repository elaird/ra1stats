from inputData import syst
from data import data,scaled

# TypeI PF MET

def common(x, systMode = 124) :
    x._htBinLowerEdges = (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
    x._htMaxForPlot = 975.0
    x._htMeans = ( 297.96, 347.558, 415.942, 516.723, 617.19, 718.153, 818.612, 1044.56 )

    x._mergeBins = None
    x._constantMcRatioAfterHere = (    0,     0,     0,     0,     0,     0,     0,     1)
    x._lumi =  	{
        "mumu"               :   3.676e+03 ,
        "muon"               :   3.676e+03 ,
        "mcPhot"             :   3.889e+03 ,
        "phot"               :   3.889e+03 ,
        "mcHad"              :   3.871e+03 ,
        "had"                :   3.871e+03 ,
        "mcMuon"             :   3.676e+03 ,
        "mcMumu"             :   3.676e+03 ,
	}
    x._triggerEfficiencies = {
        "hadBulk":       (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
        "had":           (     0.900,     0.990,     0.990,     0.990,     1.000,     1.000,     1.000,     1.000),
        "muon":          (     0.880,     0.880,     0.880,     0.880,     0.880,     0.880,     0.880,     0.880),
        "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
        "mumu":          (     0.950,     0.960,     0.960,     0.970,     0.970,     0.970,     0.980,     0.980),
        }
    x._purities = {
        "phot":          (     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000,     1.000),
        }
    x._mcExpectationsBeforeTrigger["mcGjets"] =  x._mcExpectationsBeforeTrigger["mcPhot"]
    x._mcExtraBeforeTrigger = {}
    x._observations["nHadBulk"] = (231496000, 103615000, 76347400, 25456300, 9467480, 3855680, 1729150, 1750550)
    syst.load(x, mode = systMode)


class data_0b_no_aT(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 1.235e+03, 476.3, 166.4, 59.11, 18.75, 22.26, ) ,
            "mcHad"              :   ( 3.063e+03, 1.146e+03, 857.9, 322.8, 120.5, 48.34, 19.85, 15.6, ) ,
            "mcTtw"              :   ( 1.591e+03, 516.1, 382.6, 147.6, 54.0, 19.67, 8.966, 6.858, ) ,
            "mcMuon"             :   ( 4.831e+03, 2.402e+03, 2.344e+03, 1.095e+03, 518.7, 244.8, 131.1, 149.2, ) ,
            "mcZinv"             :   ( 1.472e+03, 630.4, 475.3, 175.2, 66.55, 28.67, 10.88, 8.745, ) ,
            "mcMumu"             :   ( 503.5, 290.5, 281.5, 103.2, 49.63, 23.51, 11.5, 17.67, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 190.7, 52.11, 31.31, 21.52, 13.97, 12.04, 6.731, 6.693, ) ,
            "mcMumuErr"          :   ( 40.36, 27.03, 29.9, 15.13, 16.46, 5.054, 4.372, 8.364, ) ,
            "mcHadErr"           :   ( 178.2, 21.18, 14.97, 8.212, 5.031, 3.187, 2.256, 1.788, ) ,
            "mcZinvErr"          :   ( 17.81, 10.83, 8.762, 4.698, 2.775, 1.991, 1.135, 1.054, ) ,
            "mcTtwErr"           :   ( 177.3, 18.2, 12.14, 6.735, 4.196, 2.489, 1.95, 1.445, ) ,
            "mcPhotErr"          :   ( None, None, 45.99, 30.33, 16.49, 9.3, 3.335, 4.052, ) ,
            }

        self._observations =  	{
            "nPhot"              :   ( None, None, 1.052e+03, 360.0, 140.0, 49.0, 14.0, 12.0, ) ,
            "nHad"               :   ( 2.461e+03, 1.124e+03, 755.0, 290.0, 85.0, 41.0, 8.0, 22.0, ) ,
            "nMuon"              :   ( 3.582e+03, 1.878e+03, 1.784e+03, 731.0, 324.0, 130.0, 86.0, 97.0, ) ,
            "nMumu"              :   ( 465.0, 222.0, 195.0, 85.0, 59.0, 20.0, 11.0, 6.0, ) ,
            }
        common(self)

class data_0b(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 1.235e+03, 476.3, 166.4, 59.11, 18.75, 22.26, ) ,
            "mcHad"              :   ( 3.063e+03, 1.146e+03, 857.9, 322.8, 120.5, 48.34, 19.85, 15.6, ) ,
            "mcTtw"              :   ( 1.591e+03, 516.1, 382.6, 147.6, 54.0, 19.67, 8.966, 6.858, ) ,
            "mcMuon"             :   ( 918.6/0.9, 441.8/1.1, 310.3, 129.8, 49.3, 15.87, 8.536, 5.967, ) ,
            "mcZinv"             :   ( 1.472e+03, 630.4, 475.3, 175.2, 66.55, 28.67, 10.88, 8.745, ) ,
            "mcMumu"             :   ( 97.7, 44.08, 70.79/2.1, 29.26/2.3, 9.926/2.3, 1.017, 0.1, 0.01982, ) ,
            }
        
        self._mcStatError =  	{
            "mcMuonErr"          :   ( 43.41, 31.41, 10.67, 6.801, 4.045, 2.057, 1.618, 1.454, ) ,
            "mcMumuErr"          :   ( 13.58, 10.76, 16.73, 10.65, 5.794, 0.8148, 0.0, 0.009589, ) ,
            "mcHadErr"           :   ( 178.2, 21.18, 14.97, 8.212, 5.031, 3.187, 2.256, 1.788, ) ,
            "mcZinvErr"          :   ( 17.81, 10.83, 8.762, 4.698, 2.775, 1.991, 1.135, 1.054, ) ,
            "mcTtwErr"           :   ( 177.3, 18.2, 12.14, 6.735, 4.196, 2.489, 1.95, 1.445, ) ,
            "mcPhotErr"          :   ( None, None, 45.99, 30.33, 16.49, 9.3, 3.335, 4.052, ) ,
            }
        
        self._observations =  	{
            "nPhot"              :   ( None, None, 1.052e+03, 360.0, 140.0, 49.0, 14.0, 12.0, ) ,
            "nHad"               :   ( 2.461e+03, 1.124e+03, 755.0, 290.0, 85.0, 41.0, 8.0, 22.0, ) ,
            "nMuon"              :   ( 694.0, 294.0, 247.0, 69.0, 25.0, 5.0, 5.0, 1.0, ) ,
            "nMumu"              :   ( 103.0, 52.0, 31.0, 15.0, 2.0, 2.0, 2.0, 0.0, ) ,
            }
        common(self)

class data_1b(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 106.7, 44.54, 18.96, 8.065, 2.729, 3.991, ) ,
            "mcHad"              :   ( 582.2, 255.4, 195.2, 75.05, 29.1, 9.102, 6.013, 3.139, ) ,
            "mcTtw"              :   ( 443.4, 194.2, 149.5, 56.37, 22.04, 5.681, 4.403, 1.992, ) ,
            "mcMuon"             :   ( 1.547e+03, 843.6, 766.3, 416.5, 189.4, 85.91, 46.0*1.6, 50.52, ) ,
            "mcZinv"             :   ( 138.8, 61.2, 45.72, 18.68, 7.059, 3.421, 1.61, 1.147, ) ,
            "mcMumu"             :   ( 76.91, 52.26, 37.28, 18.53, 10.96/1.25, 4.842/1.2, 1.507/0.8, 2.948, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 105.1, 34.56, 30.99, 27.0, 19.04, 9.306, 10.64, 9.086, ) ,
            "mcMumuErr"          :   ( 8.732, 4.762, 3.976, 1.068, 2.215, 1.23, 0.16, 0.1196, ) ,
            "mcHadErr"           :   ( 31.53, 21.52, 15.57, 11.81, 6.063, 1.175, 5.091, 0.3925, ) ,
            "mcZinvErr"          :   ( 3.03, 1.745, 1.589, 1.087, 0.6234, 0.2117, 0.108, 0.06531, ) ,
            "mcTtwErr"           :   ( 31.38, 21.45, 15.49, 11.76, 6.031, 1.156, 5.09, 0.3871, ) ,
            "mcPhotErr"          :   ( None, None, 6.515, 6.144, 2.261, 2.0, 0.164, 2.035, ) ,
            }

        self._observations =  	{
            "nPhot"              :   ( None, None, 143.0, 57.0, 15.0, 11.0, 4.0, 1.0, ) ,
            "nHad"               :   ( 556.0, 219.0, 178.0, 60.0, 19.0, 7.0, 2.0, 3.0, ) ,
            "nMuon"              :   ( 1.339e+03, 655.0, 601.0, 274.0, 128.0, 59.0, 29.0, 16.0, ) ,
            "nMumu"              :   ( 64.0, 34.0, 33.0, 20.0, 6.0, 2.0, 3.0, 1.0, ) ,
            }
        common(self)

class data_2b(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 6.199, 3.191, 3.322/3, 0.6338, 0.2079, 0.2514, ) ,
            "mcHad"              :   ( 133.0, 60.34, 47.5, 19.77, 9.974, 1.872, 1.803, 0.5382, ) ,
            "mcTtw"              :   ( 118.9, 53.75, 42.66, 17.95, 9.351, 1.495, 1.693, 0.4544, ) ,
            "mcMuon"             :   ( 611.3, 357.8, 319.0, 173.0, 81.33, 34.25/2, 20.3, 17.63, ) ,
            "mcZinv"             :   ( 14.17, 6.599, 4.84, 1.826, 0.6229, 0.3772, 0.1101, 0.08387, ) ,
            "mcMumu"             :   ( 18.9, 18.88/1.7, 7.874, 3.874, 2.579/1.5, 1.079, 3*0.08308, 0.3381, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 21.04, 17.01, 13.15, 10.78, 6.666, 4.341, 3.39, 2.877, ) ,
            "mcMumuErr"          :   ( 3.39, 6.256, 2.246, 1.131, 1.801, 0.9193, 0.06169, 0.1644, ) ,
            "mcHadErr"           :   ( 12.76, 5.265, 6.042, 3.29, 2.659, 0.4508, 0.5764, 0.1782, ) ,
            "mcZinvErr"          :   ( 1.329, 1.191, 0.6783, 0.4256, 0.1641, 0.179, 0.0293, 0.03705, ) ,
            "mcTtwErr"           :   ( 12.69, 5.128, 6.003, 3.263, 2.654, 0.4137, 0.5756, 0.1743, ) ,
            "mcPhotErr"          :   ( None, None, 1.325, 1.004, 2.415, 0.295, 0.07802, 0.09564, ) ,
            }

        self._observations =  	{
            "nPhot"              :   ( None, None, 15.0, 6.0, 1.0, 1.0, 0.0, 1.0, ) ,
            "nHad"               :   ( 155.0, 67.0, 45.0, 27.0, 8.0, 1.0, 0.0, 2.0, ) ,
            "nMuon"              :   ( 568.0, 267.0, 276.0, 137.0, 53.0, 24.0, 12.0, 8.0, ) ,
            "nMumu"              :   ( 9.0, 9.0, 11.0, 4.0, 0.0, 1.0, 0.0, 2.0, ) ,
            }
        common(self)

class data_ge3b(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
            "mcPhot"             :   ( None, None, 0.1363, 0.08019, 0.08443, 0.0183, 0.002538, 0.002942, ) ,
            "mcHad"              :   ( 6.655, 3.405, 2.965, 1.984, 1.233, 0.2284, 0.4989, 0.07586, ) ,
            "mcTtw"              :   ( 6.34, 3.263, 2.855, 1.928, 1.214, 0.2111, 0.4966, 0.07338, ) ,
            "mcMuon"             :   ( 28.77, 18.15, 17.28, 16.26, 7.872, 4.25/2, 2*2.233, 2.753, ) ,
            "mcZinv"             :   ( 0.3155, 0.142, 0.1105, 0.05665, 0.01871, 0.01731, 0.002341, 0.002481, ) ,
            "mcMumu"             :   ( 0.6668, 0.6171, 0.2938, 0.2222, 0.2484, 0.1421, 0.002956, 0.01683, ) ,
            }

        self._mcStatError =  	{
            "mcMuonErr"          :   ( 0.7083, 0.6965, 0.5697, 0.6696, 0.4458, 0.338, 0.2107, 0.2126, ) ,
            "mcMumuErr"          :   ( 0.1098, 0.1976, 0.07472, 0.05487, 0.15, 0.08991, 0.0009591, 0.009199, ) ,
            "mcHadErr"           :   ( 0.457, 0.2199, 0.2575, 0.2239, 0.1882, 0.0386, 0.06081, 0.02093, ) ,
            "mcZinvErr"          :   ( 0.03114, 0.02592, 0.0162, 0.01441, 0.004668, 0.008651, 0.0008252, 0.001048, ) ,
            "mcTtwErr"           :   ( 0.4559, 0.2184, 0.257, 0.2235, 0.1881, 0.03762, 0.06081, 0.0209, ) ,
            "mcPhotErr"          :   ( None, None, 0.02852, 0.02472, 0.05991, 0.01062, 0.002247, 0.0, ) ,
            }
        
        self._observations =  	{
            "nPhot"              :   ( None, None, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
            "nHad"               :   ( 14.0, 1.0, 2.0, 2.0, 0.0, 1.0, 0.0, 0.0, ) ,
            "nMuon"              :   ( 35.0, 24.0, 26.0, 13.0, 7.0, 2.0, 1.0, 2.0, ) ,
            "nMumu"              :   ( 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
            }
        common(self)
