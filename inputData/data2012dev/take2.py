from inputData.units import fb
from data import data
import utils


def common1(x) :
    x._lumi = {"mumu"               :   19.25/fb,
               "muon"               :   19.25/fb,
               "mcPhot"             :   20.34/fb,
               "mcHad"              :   18.58/fb,
               "mcTtw"              :   18.58/fb,
               "had"                :   18.58/fb,
               "mcMuon"             :   19.25/fb,
               "mcZinv"             :   18.58/fb,
               "mcMumu"             :   19.25/fb,
               "phot"               :   20.34/fb,
               }

    x._triggerEfficiencies = {}
    for key in ["hadBulk", "had", "muon", "phot", "mumu"]:
        x._triggerEfficiencies[key] = tuple([1.0]*10)

    x._htBinLowerEdges = ( 200.0, 275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0, 975.0, )
    x._htMaxForPlot    = 1075.0
    x._htMeans         = (240.0, 298.0, 348.0, 416.0, 517.0, 617.0, 719.0, 819.0, 920.0, 1144.)  # tmp

    iPhot = 3
    x._observations["nPhot"] = tuple([None]*iPhot + list(x._observations["nPhot"][iPhot:]))


def common(x) :
    common1(x)

    systBins = tuple([0, 1, 2] + [3]*2 + [4]*2 + [5]*3)  # tmp
    name = x.__class__.__name__

    if "le3j" in name :
        systMagnitudes = (0.10, 0.10, 0.10, 0.20, 0.20, 0.20)  # tmp
        x._observations["nHadBulk"] = (559500000, 559500000, 252400000, 180600000, 51650000,
                                       17060000, 6499000, 2674000, 2501000, 2501000)  # tmp
    elif "ge4j" in name :
        systMagnitudes = (0.10, 0.10, 0.10, 0.20, 0.20, 0.30)  # tmp
        x._observations["nHadBulk"] = (93940000, 93940000, 42330000, 33950000, 20540000,
                                       9410000,  4363000, 2067000, 2217000, 2217000)  # tmp

    if "ge4b" in name :
        x._mergeBins = (0, 1, 2, 3, 3, 3, 3, 3, 3, 3)
        systMagnitudes = (0.25,)
        systBins = (0, 0, 0, 0)
    else :
        x._mergeBins = None

    x._systBins = {
        "sigmaPhotZ": systBins,
        "sigmaMuonW": systBins,
        "sigmaMumuZ": systBins,
        }

    x._fixedParameters = {
        "sigmaPhotZ": systMagnitudes,
        "sigmaMuonW": systMagnitudes,
        "sigmaMumuZ": systMagnitudes,
        "k_qcd_nom":2.96e-2,
        "k_qcd_unc_inp":utils.quadSum([0.61e-2, 0.463e-2])
        #"k_qcd_unc_inp":utils.quadSum([2.5*0.61e-2, 2.5*0.463e-2])
        }


class data_0b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 561.0, 381.7, 216.4, 105.7, 52.44, 19.51, 23.51, ) ,
		"mcTtw"              :   ( 255.3, 1342.0, 469.6, 370.1, 229.6, 104.7, 42.54, 20.45, 7.549, 10.02, ) ,
		"mcHad"              :   ( 394.8, 2039.0, 744.5, 587.1, 382.5, 184.3, 78.73, 36.8, 15.66, 17.84, ) ,
		"mcMuon"             :   ( 803.0, 2688.0, 1260.0, 1366.0, 1047.0, 580.0, 308.2, 168.7, 91.82, 123.3, ) ,
		"mcZinv"             :   ( 139.5, 697.0, 274.9, 217.0, 152.9, 79.67, 36.19, 16.35, 8.115, 7.826, ) ,
		"mcMumu"             :   ( 64.93, 214.3, 102.4, 102.7, 87.71, 52.75, 31.23, 16.42, 9.002, 14.37, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 11.3, 19.1, 12.22, 11.59, 9.677, 7.151, 5.166, 3.807, 2.826, 3.281, ) ,
		"mcMumuErr"          :   ( 5.281, 6.284, 4.689, 2.173, 1.425, 1.104, 1.094, 0.5775, 0.4294, 0.5371, ) ,
		"mcZinvErr"          :   ( 4.799, 7.966, 4.614, 3.058, 1.757, 1.225, 0.8005, 0.5396, 0.3947, 0.3785, ) ,
		"mcHadErr"           :   ( 7.783, 15.88, 8.86, 6.915, 4.916, 3.22, 2.064, 1.454, 0.8614, 1.027, ) ,
		"mcTtwErr"           :   ( 6.127, 13.74, 7.564, 6.202, 4.591, 2.978, 1.902, 1.351, 0.7657, 0.9542, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 29.71, 24.18, 17.61, 12.85, 8.83, 5.116, 5.457, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 561.0, 381.7, 216.4, 105.7, 52.44, 19.51, 23.51, ) ,
		"nHad"               :   ( 394.8, 2039.0, 744.5, 587.1, 382.5, 184.3, 78.73, 36.8, 15.66, 17.84, ) ,
		"nMuon"              :   ( 803.0, 2688.0, 1260.0, 1366.0, 1047.0, 580.0, 308.2, 168.7, 91.82, 123.3, ) ,
		"nMumu"              :   ( 64.93, 214.3, 102.4, 102.7, 87.71, 52.75, 31.23, 16.42, 9.002, 14.37, ) ,
	}

        common(self)


class data_0b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 4568.0, 1581.0, 548.1, 213.2, 87.11, 46.41, 22.81, ) ,
		"mcTtw"              :   ( 1.182e+04, 5483.0, 2313.0, 1614.0, 454.5, 142.1, 47.83, 17.14, 8.136, 5.742, ) ,
		"mcHad"              :   ( 2.269e+04, 1.064e+04, 4661.0, 3314.0, 993.1, 335.1, 117.4, 45.99, 20.48, 16.19, ) ,
		"mcMuon"             :   ( 4.801e+04, 1.873e+04, 1.023e+04, 9795.0, 4016.0, 1718.0, 809.1, 400.8, 219.1, 291.5, ) ,
		"mcZinv"             :   ( 1.087e+04, 5161.0, 2348.0, 1700.0, 538.6, 193.0, 69.53, 28.85, 12.34, 10.45, ) ,
		"mcMumu"             :   ( 5067.0, 2049.0, 1160.0, 1147.0, 503.7, 221.1, 107.0, 55.18, 29.32, 41.23, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 94.74, 55.29, 37.8, 32.99, 20.02, 13.1, 9.031, 6.281, 4.674, 5.376, ) ,
		"mcMumuErr"          :   ( 44.18, 15.81, 10.35, 7.29, 3.272, 2.129, 1.475, 1.065, 0.7819, 0.9185, ) ,
		"mcZinvErr"          :   ( 41.9, 20.61, 13.18, 8.079, 3.25, 1.941, 1.151, 0.7491, 0.4856, 0.4555, ) ,
		"mcHadErr"           :   ( 61.83, 35.91, 22.17, 15.73, 7.436, 4.206, 2.401, 1.461, 0.9978, 0.8515, ) ,
		"mcTtwErr"           :   ( 45.46, 29.42, 17.83, 13.5, 6.688, 3.731, 2.107, 1.254, 0.8717, 0.7194, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 85.02, 47.59, 28.41, 17.9, 11.06, 8.163, 5.922, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 4568.0, 1581.0, 548.1, 213.2, 87.11, 46.41, 22.81, ) ,
		"nHad"               :   ( 2.269e+04, 1.064e+04, 4661.0, 3314.0, 993.1, 335.1, 117.4, 45.99, 20.48, 16.19, ) ,
		"nMuon"              :   ( 4.801e+04, 1.873e+04, 1.023e+04, 9795.0, 4016.0, 1718.0, 809.1, 400.8, 219.1, 291.5, ) ,
		"nMumu"              :   ( 5067.0, 2049.0, 1160.0, 1147.0, 503.7, 221.1, 107.0, 55.18, 29.32, 41.23, ) ,
	}

        common(self)


class data_1b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 135.3, 841.7, 324.4, 258.7, 143.1, 59.99, 22.03, 9.162, 3.998, 3.807, ) ,
		"mcHad"              :   ( 153.9, 947.7, 366.5, 293.8, 167.6, 72.59, 28.91, 12.36, 5.405, 5.061, ) ,
		"mcMuon"             :   ( 638.4, 2287.0, 1185.0, 1277.0, 923.4, 479.0, 237.2, 120.9, 65.35, 76.64, ) ,
		"mcZinv"             :   ( 18.6, 106.0, 42.11, 35.11, 24.53, 12.6, 6.883, 3.199, 1.407, 1.254, ) ,
		"mcMumu"             :   ( 14.96, 52.24, 23.11, 27.24, 22.2, 13.06, 7.801, 3.897, 2.022, 3.875, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 7.705, 14.44, 10.39, 10.85, 9.1, 6.463, 4.549, 3.19, 2.315, 2.446, ) ,
		"mcMumuErr"          :   ( 1.108, 2.108, 1.162, 1.129, 0.9299, 0.6727, 0.5801, 0.3552, 0.2423, 0.3719, ) ,
		"mcZinvErr"          :   ( 1.015, 1.801, 0.936, 0.6438, 0.3746, 0.2576, 0.1894, 0.1308, 0.08427, 0.06868, ) ,
		"mcHadErr"           :   ( 3.603, 8.771, 5.485, 4.826, 3.436, 2.202, 1.248, 0.872, 0.5316, 0.4551, ) ,
		"mcTtwErr"           :   ( 3.457, 8.584, 5.405, 4.783, 3.416, 2.186, 1.233, 0.8621, 0.5248, 0.4499, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 153.9, 947.7, 366.5, 293.8, 167.6, 72.59, 28.91, 12.36, 5.405, 5.061, ) ,
		"nMuon"              :   ( 638.4, 2287.0, 1185.0, 1277.0, 923.4, 479.0, 237.2, 120.9, 65.35, 76.64, ) ,
		"nMumu"              :   ( 14.96, 52.24, 23.11, 27.24, 22.2, 13.06, 7.801, 3.897, 2.022, 3.875, ) ,
	}

        common(self)


class data_1b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 2038.0, 1140.0, 497.0, 345.4, 81.95, 20.83, 7.586, 2.144, 0.7973, 0.7425, ) ,
		"mcHad"              :   ( 2930.0, 1624.0, 718.4, 512.0, 134.5, 38.26, 15.01, 5.093, 2.069, 1.638, ) ,
		"mcMuon"             :   ( 1.032e+04, 4314.0, 2452.0, 2225.0, 787.0, 310.5, 133.9, 62.81, 32.22, 42.62, ) ,
		"mcZinv"             :   ( 891.4, 484.0, 221.4, 166.6, 52.54, 17.43, 7.429, 2.949, 1.272, 0.896, ) ,
		"mcMumu"             :   ( 618.2, 262.4, 147.2, 138.0, 57.18, 23.69, 11.39, 5.526, 2.832, 4.604, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 31.6, 19.78, 14.87, 13.85, 7.906, 4.799, 3.003, 2.03, 1.401, 1.537, ) ,
		"mcMumuErr"          :   ( 7.552, 3.713, 2.81, 2.155, 1.219, 0.6984, 0.4376, 0.3053, 0.2247, 0.2865, ) ,
		"mcZinvErr"          :   ( 6.321, 3.425, 2.074, 1.287, 0.5374, 0.2853, 0.194, 0.1213, 0.07629, 0.06071, ) ,
		"mcHadErr"           :   ( 14.9, 10.32, 6.705, 5.456, 2.422, 1.1, 0.6296, 0.2988, 0.1755, 0.1563, ) ,
		"mcTtwErr"           :   ( 13.5, 9.736, 6.376, 5.302, 2.362, 1.062, 0.599, 0.273, 0.1581, 0.144, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 2930.0, 1624.0, 718.4, 512.0, 134.5, 38.26, 15.01, 5.093, 2.069, 1.638, ) ,
		"nMuon"              :   ( 1.032e+04, 4314.0, 2452.0, 2225.0, 787.0, 310.5, 133.9, 62.81, 32.22, 42.62, ) ,
		"nMumu"              :   ( 618.2, 262.4, 147.2, 138.0, 57.18, 23.69, 11.39, 5.526, 2.832, 4.604, ) ,
	}

        common(self)


class data_2b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 53.44, 370.7, 146.3, 116.0, 69.4, 27.16, 9.735, 3.086, 2.449, 1.661, ) ,
		"mcHad"              :   ( 55.81, 386.3, 152.6, 121.4, 73.04, 28.84, 10.7, 3.572, 2.64, 1.773, ) ,
		"mcMuon"             :   ( 380.2, 1415.0, 741.4, 780.3, 555.2, 290.0, 131.7, 63.67, 34.52, 37.07, ) ,
		"mcZinv"             :   ( 2.376, 15.58, 6.321, 5.472, 3.64, 1.677, 0.9653, 0.4858, 0.1909, 0.1119, ) ,
		"mcMumu"             :   ( 4.666, 18.48, 7.598, 10.37, 8.639, 4.833, 2.146, 0.8998, 0.5934, 0.9808, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 5.378, 10.36, 7.576, 7.814, 6.473, 4.646, 3.103, 2.038, 1.494, 1.507, ) ,
		"mcMumuErr"          :   ( 0.5748, 1.198, 0.6961, 0.8111, 0.75, 0.5377, 0.3552, 0.1892, 0.1773, 0.2002, ) ,
		"mcZinvErr"          :   ( 0.2886, 0.6583, 0.3642, 0.2605, 0.1405, 0.08707, 0.06259, 0.04926, 0.03232, 0.01364, ) ,
		"mcHadErr"           :   ( 1.866, 4.911, 3.117, 2.803, 2.135, 1.306, 0.7452, 0.4289, 0.4449, 0.2806, ) ,
		"mcTtwErr"           :   ( 1.843, 4.867, 3.095, 2.791, 2.13, 1.303, 0.7425, 0.4261, 0.4437, 0.2803, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 55.81, 386.3, 152.6, 121.4, 73.04, 28.84, 10.7, 3.572, 2.64, 1.773, ) ,
		"nMuon"              :   ( 380.2, 1415.0, 741.4, 780.3, 555.2, 290.0, 131.7, 63.67, 34.52, 37.07, ) ,
		"nMumu"              :   ( 4.666, 18.48, 7.598, 10.37, 8.639, 4.833, 2.146, 0.8998, 0.5934, 0.9808, ) ,
	}

        common(self)


class data_2b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 292.7, 248.4, 115.8, 83.49, 19.53, 4.788, 1.4, 0.1173, 0.01808, 0.02153, ) ,
		"mcHad"              :   ( 370.9, 292.2, 136.2, 97.78, 23.82, 6.118, 1.914, 0.3208, 0.1089, 0.05943, ) ,
		"mcMuon"             :   ( 3067.0, 1430.0, 814.8, 732.3, 236.0, 82.9, 31.31, 12.19, 6.263, 7.239, ) ,
		"mcZinv"             :   ( 78.16, 43.81, 20.4, 14.29, 4.291, 1.33, 0.5148, 0.2035, 0.09083, 0.0379, ) ,
		"mcMumu"             :   ( 150.1, 57.71, 29.89, 23.97, 8.519, 3.515, 1.076, 0.6253, 0.2446, 0.3209, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 15.95, 10.85, 8.254, 7.869, 4.478, 2.562, 1.502, 0.9238, 0.6367, 0.6424, ) ,
		"mcMumuErr"          :   ( 3.795, 2.035, 1.473, 1.204, 0.6705, 0.4475, 0.1935, 0.164, 0.116, 0.07777, ) ,
		"mcZinvErr"          :   ( 1.899, 1.054, 0.6686, 0.4002, 0.1541, 0.08091, 0.04533, 0.03155, 0.02306, 0.007856, ) ,
		"mcHadErr"           :   ( 4.69, 4.106, 2.854, 2.449, 1.232, 0.5709, 0.2634, 0.05472, 0.02331, 0.009514, ) ,
		"mcTtwErr"           :   ( 4.288, 3.968, 2.774, 2.416, 1.222, 0.5651, 0.2595, 0.04471, 0.003457, 0.005367, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 370.9, 292.2, 136.2, 97.78, 23.82, 6.118, 1.914, 0.3208, 0.1089, 0.05943, ) ,
		"nMuon"              :   ( 3067.0, 1430.0, 814.8, 732.3, 236.0, 82.9, 31.31, 12.19, 6.263, 7.239, ) ,
		"nMumu"              :   ( 150.1, 57.71, 29.89, 23.97, 8.519, 3.515, 1.076, 0.6253, 0.2446, 0.3209, ) ,
	}

        common(self)


class data_3b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 4.351, 35.58, 14.71, 11.27, 8.268, 3.328, 1.099, 0.3587, 0.3074, 0.3391, ) ,
		"mcHad"              :   ( 4.413, 36.33, 15.0, 11.52, 8.489, 3.405, 1.159, 0.3949, 0.3232, 0.3449, ) ,
		"mcMuon"             :   ( 36.45, 141.7, 73.63, 78.25, 60.37, 34.39, 15.94, 7.493, 4.419, 4.345, ) ,
		"mcZinv"             :   ( 0.06142, 0.7512, 0.2919, 0.2454, 0.2207, 0.07746, 0.06026, 0.03618, 0.0158, 0.005791, ) ,
		"mcMumu"             :   ( 0.2793, 1.234, 0.5484, 0.7328, 0.6274, 0.3441, 0.1277, 0.04968, 0.0934, 0.0673, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.8206, 1.602, 1.201, 1.269, 1.082, 0.8671, 0.5556, 0.4052, 0.2761, 0.2827, ) ,
		"mcMumuErr"          :   ( 0.07406, 0.1756, 0.1231, 0.1439, 0.1212, 0.07831, 0.02699, 0.01543, 0.07264, 0.01542, ) ,
		"mcZinvErr"          :   ( 0.009942, 0.07396, 0.04167, 0.01966, 0.02312, 0.007114, 0.0078, 0.008532, 0.008513, 0.001344, ) ,
		"mcHadErr"           :   ( 0.2711, 0.7404, 0.4766, 0.4114, 0.3797, 0.2347, 0.09834, 0.08613, 0.1077, 0.07985, ) ,
		"mcTtwErr"           :   ( 0.2709, 0.7367, 0.4748, 0.411, 0.379, 0.2346, 0.09803, 0.08571, 0.1074, 0.07984, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 4.413, 36.33, 15.0, 11.52, 8.489, 3.405, 1.159, 0.3949, 0.3232, 0.3449, ) ,
		"nMuon"              :   ( 36.45, 141.7, 73.63, 78.25, 60.37, 34.39, 15.94, 7.493, 4.419, 4.345, ) ,
		"nMumu"              :   ( 0.2793, 1.234, 0.5484, 0.7328, 0.6274, 0.3441, 0.1277, 0.04968, 0.0934, 0.0673, ) ,
	}

        common(self)


class data_3b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 8.529, 10.84, 5.62, 4.436, 1.004, 0.3387, 0.141, 0.001597, 0.0001378, 0.0001487, ) ,
		"mcHad"              :   ( 9.208, 11.75, 6.032, 4.675, 1.077, 0.3714, 0.1569, 0.004698, 0.001029, 0.0004074, ) ,
		"mcMuon"             :   ( 121.7, 67.17, 36.61, 33.18, 11.17, 3.866, 1.404, 0.4644, 0.2477, 0.2482, ) ,
		"mcZinv"             :   ( 0.679, 0.9028, 0.4113, 0.2386, 0.07296, 0.03265, 0.01587, 0.003101, 0.0008911, 0.0002587, ) ,
		"mcMumu"             :   ( 2.241, 1.131, 0.6702, 0.7199, 0.2483, 0.05315, 0.01767, 0.03684, 0.003409, 0.007924, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 1.418, 1.092, 0.8151, 0.805, 0.4656, 0.265, 0.1514, 0.07745, 0.05962, 0.05186, ) ,
		"mcMumuErr"          :   ( 0.2128, 0.1132, 0.1253, 0.1497, 0.08149, 0.008267, 0.004144, 0.01938, 0.002114, 0.004255, ) ,
		"mcZinvErr"          :   ( 0.07702, 0.09753, 0.06285, 0.02016, 0.009932, 0.009061, 0.006269, 0.0006471, 0.0003211, 6.72e-05, ) ,
		"mcHadErr"           :   ( 0.343, 0.3912, 0.3037, 0.2638, 0.127, 0.07428, 0.07021, 0.001082, 0.0003227, 8.187e-05, ) ,
		"mcTtwErr"           :   ( 0.3343, 0.3789, 0.2971, 0.263, 0.1266, 0.07373, 0.06992, 0.0008676, 3.284e-05, 4.677e-05, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 9.208, 11.75, 6.032, 4.675, 1.077, 0.3714, 0.1569, 0.004698, 0.001029, 0.0004074, ) ,
		"nMuon"              :   ( 121.7, 67.17, 36.61, 33.18, 11.17, 3.866, 1.404, 0.4644, 0.2477, 0.2482, ) ,
		"nMumu"              :   ( 2.241, 1.131, 0.6702, 0.7199, 0.2483, 0.05315, 0.01767, 0.03684, 0.003409, 0.007924, ) ,
	}

        common(self)


class data_ge4b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 0.07077, 0.7629, 0.3572, 0.2574, 0.3211, 0.1254, 0.04396, 0.01001, 0.005333, 0.04613, ) ,
		"mcHad"              :   ( 0.07114, 0.7719, 0.3615, 0.2615, 0.3276, 0.1268, 0.04537, 0.011, 0.005621, 0.04625, ) ,
		"mcMuon"             :   ( 0.6997, 3.013, 1.623, 1.894, 1.941, 1.329, 0.6641, 0.3518, 0.2072, 0.2273, ) ,
		"mcZinv"             :   ( 0.0003775, 0.009055, 0.004306, 0.004138, 0.006484, 0.001349, 0.001411, 0.0009841, 0.0002888, 0.0001187, ) ,
		"mcMumu"             :   ( 0.003757, 0.03658, 0.02252, 0.02249, 0.01333, 0.01153, 0.002249, 0.000958, 0.001592, 0.001692, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.03602, 0.08605, 0.06761, 0.08183, 0.08138, 0.07255, 0.04342, 0.03937, 0.02616, 0.02602, ) ,
		"mcMumuErr"          :   ( 0.001421, 0.02036, 0.01285, 0.01333, 0.004019, 0.005317, 0.0005672, 0.0004478, 0.001329, 0.0005895, ) ,
		"mcZinvErr"          :   ( 6.409e-05, 0.001256, 0.001309, 0.001072, 0.002858, 0.0002338, 0.0003356, 0.0004157, 0.0001798, 4.031e-05, ) ,
		"mcHadErr"           :   ( 0.01135, 0.03915, 0.02876, 0.02436, 0.03616, 0.01504, 0.00536, 0.002679, 0.002329, 0.01745, ) ,
		"mcTtwErr"           :   ( 0.01135, 0.03913, 0.02873, 0.02434, 0.03605, 0.01503, 0.005349, 0.002647, 0.002322, 0.01745, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 0.07114, 0.7719, 0.3615, 0.2615, 0.3276, 0.1268, 0.04537, 0.011, 0.005621, 0.04625, ) ,
		"nMuon"              :   ( 0.6997, 3.013, 1.623, 1.894, 1.941, 1.329, 0.6641, 0.3518, 0.2072, 0.2273, ) ,
		"nMumu"              :   ( 0.003757, 0.03658, 0.02252, 0.02249, 0.01333, 0.01153, 0.002249, 0.000958, 0.001592, 0.001692, ) ,
	}

        common(self)
