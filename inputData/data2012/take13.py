from data import data
import utils

def common1(x) :
    x._lumi = {
        "mumu"  : 1.139e+04,
        "muon"  : 1.139e+04,
        "mcPhot": 1.157e+04,
        "phot"  : 1.157e+04,
        "mcHad" : 5.125e+03,
        "had"   : 5.125e+03,
        "mcMuon": 1.139e+04,
        "mcMumu": 1.139e+04,
	}

    x._triggerEfficiencies = {
        "hadBulk":       (1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "muon":          (0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880),
        "phot":          (1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "mumu":          (0.950, 0.960, 0.960, 0.970, 0.970, 0.970, 0.980, 0.980, 0.980, 0.980),
        }

    x._htBinLowerEdges = ( 275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0, 975.0, 1.075e+03, )
    x._htMaxForPlot    = 1.175e+03
    x._htMeans         = ( 298.0, 348.0, 416.0, 517.0, 617.0, 719.0, 819.0, 1044.,   0.0,       0.0, )

    x._observations["nPhot"] = tuple([None, None]+list(x._observations["nPhot"][2:]))

    uncs = {"btagUncert": 0.035, "lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10} # SMS other than T1, T2
    uncs["btagUncert"] = 0.12 #T1, T2, cMSSM tb10 only
    return utils.quadSum(uncs.values())

def common(x) :
    lumiLikeValue = common1(x)

    #systBins = tuple([0]*4+[1]*2+[2]*2)
    systBins = tuple([0,1]+[2]*2+[3]*2+[4]*2)
    name = x.__class__.__name__

    if "ge2j" in name :
        systMagnitudes = (0.10, 0.10, 0.20, 0.20, 0.30)
        #x._observations["nHadBulk"] = (630453600, 286166200, 209611400, 69777150, 26101500, 20182300, 4745175, 4776350, 0, 0)
        x._triggerEfficiencies["had"] = (0.870, 0.986, 0.994, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000)
    elif "le3j" in name :
        #systMagnitudes = (0.10, 0.20, 0.20)
        systMagnitudes = (0.10, 0.10, 0.20, 0.20, 0.20)
        x._observations["nHadBulk"] = (487992800, 202369400, 134976100, 36965375, 12292400,  8301900, 1925125, 1768325, 0, 0)
        x._triggerEfficiencies["had"] = (0.891, 0.987, 0.990, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000)
    elif "ge4j" in name :
        #systMagnitudes = (0.10, 0.20, 0.30)
        systMagnitudes = (0.10, 0.10, 0.20, 0.20, 0.30)
        x._triggerEfficiencies["had"] = (0.837, 0.982, 0.997, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000)
        x._observations["nHadBulk"] = (142460800,  83796800,  74635300, 32811775, 13809100, 11880400, 2820050, 3008025, 0, 0)

    if "ge4b" in name :
        x._mergeBins = (0, 1, 2, 2, 2, 2, 2, 2, 2, 2)
        systMagnitudes = (0.25,)
        systBins = (0, 0, 0)
    else :
        x._mergeBins = (0, 1, 2, 3, 4, 5, 6, 7, 7, 7)

    x._systBins = {
        "sigmaLumiLike": [0]*len(systBins),
        "sigmaPhotZ": systBins,
        "sigmaMuonW": systBins,
        "sigmaMumuZ": systBins,
        }

    x._fixedParameters = {
        "sigmaLumiLike": tuple([lumiLikeValue]*1),
        "sigmaPhotZ": systMagnitudes,
        "sigmaMuonW": systMagnitudes,
        "sigmaMumuZ": systMagnitudes,
        "k_qcd_nom":2.96e-2,
        "k_qcd_unc_inp":utils.quadSum([0.61e-2, 0.463e-2])
        }

class data_0b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 279.2, 205.1, 106.6, 52.39, 26.34, 9.899, 4.181, 3.907, ) ,
		"mcHad"              :   ( 482.7, 194.4, 156.5, 103.9, 48.61, 23.67, 10.38, 4.592, 2.094, 2.049, ) ,
		"mcTtw"              :   ( 296.3, 120.7, 100.2, 64.02, 28.41, 13.83, 5.38, 2.986, 1.213, 1.004, ) ,
		"mcMuon"             :   ( 1.473e+03, 747.5, 820.9, 637.8, 349.3, 181.6, 98.24, 57.73, 30.88, 43.57, ) ,
		"mcZinv"             :   ( 186.5, 73.71, 56.34, 39.92, 20.2, 9.84, 5.003, 1.606, 0.8815, 1.045, ) ,
		"mcMumu"             :   ( 120.6, 68.48, 53.69, 47.66, 34.22, 20.25, 11.59, 2.3, 1.374, 5.686, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 37.33, 12.27, 20.21, 9.643, 7.573, 5.046, 4.144, 2.987, 2.284, 2.577, ) ,
		"mcMumuErr"          :   ( 10.67, 9.08, 7.455, 6.776, 5.93, 4.446, 3.519, 1.479, 0.9188, 2.189, ) ,
		"mcHadErr"           :   ( 12.25, 3.79, 2.983, 2.419, 1.516, 1.099, 0.6738, 0.4974, 0.3156, 0.2677, ) ,
		"mcZinvErr"          :   ( 2.891, 1.732, 1.362, 1.042, 0.7307, 0.5087, 0.3725, 0.1958, 0.1508, 0.1582, ) ,
		"mcTtwErr"           :   ( 11.9, 3.371, 2.654, 2.183, 1.328, 0.9738, 0.5615, 0.4573, 0.2772, 0.216, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 14.73, 12.72, 8.791, 6.476, 4.451, 2.507, 1.498, 1.581, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 308.0, 213.0, 99.0, 50.0, 24.0, 11.0, 3.0, 3.0, ) ,
		"nHad"               :   ( 441.0, 218.0, 171.0, 113.0, 57.0, 25.0, 5.0, 4.0, 6.0, 4.0, ) ,
		"nMuon"              :   ( 1.383e+03, 644.0, 636.0, 444.0, 260.0, 147.0, 59.0, 34.0, 18.0, 36.0, ) ,
		"nMumu"              :   ( 126.0, 46.0, 55.0, 56.0, 32.0, 11.0, 7.0, 4.0, 2.0, 2.0, ) ,
	}

        common(self)


class data_0b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 2.517e+03, 866.4, 292.6, 120.2, 41.39, 21.7, 4.298, 7.045, ) ,
		"mcHad"              :   ( 2.681e+03, 1.217e+03, 867.2, 264.2, 91.27, 31.3, 12.76, 5.086, 2.054, 2.146, ) ,
		"mcTtw"              :   ( 1.294e+03, 583.1, 421.7, 120.7, 38.48, 12.1, 5.343, 2.005, 0.5471, 0.8288, ) ,
		"mcMuon"             :   ( 1.081e+04, 6.034e+03, 5.79e+03, 2.394e+03, 1.029e+03, 483.0, 246.0, 133.5, 67.96, 103.6, ) ,
		"mcZinv"             :   ( 1.387e+03, 633.9, 445.5, 143.5, 52.79, 19.2, 7.414, 3.082, 1.507, 1.317, ) ,
		"mcMumu"             :   ( 1.198e+03, 699.4, 664.4, 274.9, 125.1, 58.28, 27.49, 10.19, 6.261, 11.96, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 87.46, 40.48, 35.8, 21.45, 14.26, 9.895, 6.916, 4.999, 3.543, 4.389, ) ,
		"mcMumuErr"          :   ( 36.37, 27.87, 27.15, 18.11, 11.67, 8.767, 5.506, 3.261, 2.338, 3.662, ) ,
		"mcHadErr"           :   ( 25.44, 9.747, 7.393, 3.689, 2.157, 1.222, 0.7884, 0.4615, 0.2963, 0.3141, ) ,
		"mcZinvErr"          :   ( 7.901, 5.209, 3.854, 2.021, 1.227, 0.7389, 0.4636, 0.2916, 0.2034, 0.2015, ) ,
		"mcTtwErr"           :   ( 24.18, 8.238, 6.308, 3.086, 1.773, 0.9737, 0.6376, 0.3577, 0.2155, 0.241, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 46.46, 25.64, 15.3, 10.1, 5.461, 4.016, 1.729, 2.453, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 2.601e+03, 854.0, 252.0, 94.0, 35.0, 11.0, 6.0, 4.0, ) ,
		"nHad"               :   ( 2.855e+03, 1.296e+03, 878.0, 241.0, 71.0, 25.0, 4.0, 8.0, 5.0, 2.0, ) ,
		"nMuon"              :   ( 9.698e+03, 5.039e+03, 4.653e+03, 1.808e+03, 779.0, 294.0, 150.0, 77.0, 55.0, 61.0, ) ,
		"nMumu"              :   ( 1.336e+03, 708.0, 623.0, 205.0, 120.0, 44.0, 21.0, 14.0, 6.0, 6.0, ) ,
	}

        common(self)


class data_1b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 49.77, 35.57, 19.85, 9.664, 4.593, 1.734, 0.7183, 0.7129, ) ,
		"mcHad"              :   ( 269.9, 108.2, 87.55, 51.28, 22.06, 8.646, 3.586, 1.689, 1.002, 0.7193, ) ,
		"mcTtw"              :   ( 235.9, 94.85, 76.97, 43.59, 18.23, 6.855, 2.62, 1.352, 0.8419, 0.5087, ) ,
		"mcMuon"             :   ( 1.425e+03, 750.6, 805.9, 584.9, 301.8, 147.4, 76.18, 40.21, 21.49, 26.28, ) ,
		"mcZinv"             :   ( 33.97, 13.3, 10.58, 7.682, 3.829, 1.791, 0.9664, 0.3372, 0.1605, 0.2107, ) ,
		"mcMumu"             :   ( 32.52, 15.74, 16.14, 13.86, 8.551, 4.546, 2.321, 0.6568, 0.7918, 1.069, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 19.61, 14.55, 15.76, 14.24, 10.67, 7.8, 5.736, 3.825, 3.104, 3.223, ) ,
		"mcMumuErr"          :   ( 5.105, 1.488, 2.638, 1.761, 1.928, 0.844, 0.6152, 0.4107, 0.4764, 0.3426, ) ,
		"mcHadErr"           :   ( 6.184, 3.862, 3.574, 2.714, 1.844, 1.018, 0.6744, 0.3696, 0.5508, 0.2249, ) ,
		"mcZinvErr"          :   ( 1.114, 0.6339, 0.5234, 0.387, 0.2219, 0.1436, 0.1167, 0.09054, 0.04054, 0.03715, ) ,
		"mcTtwErr"           :   ( 6.083, 3.81, 3.536, 2.686, 1.83, 1.008, 0.6642, 0.3583, 0.5493, 0.2218, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 3.928, 3.449, 1.524, 1.515, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 57.0, 45.0, 16.0, 12.0, 10.0, 1.0, 1.0, 1.0, ) ,
		"nHad"               :   ( 229.0, 91.0, 84.0, 26.0, 26.0, 4.0, 5.0, 3.0, 1.0, 0.0, ) ,
		"nMuon"              :   ( 1.373e+03, 612.0, 592.0, 444.0, 203.0, 108.0, 55.0, 17.0, 10.0, 21.0, ) ,
		"nMumu"              :   ( 31.0, 14.0, 21.0, 15.0, 11.0, 3.0, 2.0, 4.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_1b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 271.5, 94.96, 33.38, 13.21, 5.461, 2.805, 0.4304, 0.7563, ) ,
		"mcHad"              :   ( 496.5, 222.7, 158.0, 42.96, 13.77, 4.279, 1.589, 0.5719, 0.2531, 0.2438, ) ,
		"mcTtw"              :   ( 336.6, 149.9, 106.6, 25.9, 7.513, 2.141, 0.7016, 0.2477, 0.06788, 0.09477, ) ,
		"mcMuon"             :   ( 2.699e+03, 1.565e+03, 1.424e+03, 502.1, 195.5, 82.78, 40.77, 18.82, 12.19, 13.67, ) ,
		"mcZinv"             :   ( 159.8, 72.87, 51.45, 17.06, 6.252, 2.138, 0.8874, 0.3242, 0.1852, 0.1491, ) ,
		"mcMumu"             :   ( 167.9, 96.6, 91.37, 36.07, 16.84, 6.306, 2.37, 0.9984, 1.612, 0.8805, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 18.28, 13.91, 13.21, 7.261, 4.343, 2.657, 2.408, 1.381, 0.8714, 1.055, ) ,
		"mcMumuErr"          :   ( 7.01, 4.783, 5.046, 2.185, 1.787, 1.281, 0.1686, 0.1591, 0.5566, 0.08259, ) ,
		"mcHadErr"           :   ( 4.794, 3.158, 2.676, 1.151, 0.5641, 0.3193, 0.1215, 0.06737, 0.01642, 0.01901, ) ,
		"mcZinvErr"          :   ( 1.476, 0.9256, 0.7154, 0.3358, 0.2096, 0.0972, 0.08807, 0.02464, 0.01569, 0.01901, ) ,
		"mcTtwErr"           :   ( 4.561, 3.019, 2.578, 1.101, 0.5237, 0.3042, 0.08364, 0.0627, 0.004852, 0.0, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 7.444, 2.717, 1.556, 0.9106, 1.309, 0.9782, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 307.0, 101.0, 27.0, 9.0, 5.0, 2.0, 1.0, 0.0, ) ,
		"nHad"               :   ( 509.0, 213.0, 153.0, 42.0, 9.0, 4.0, 1.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 2.662e+03, 1.434e+03, 1.223e+03, 413.0, 154.0, 51.0, 27.0, 12.0, 7.0, 7.0, ) ,
		"nMumu"              :   ( 184.0, 99.0, 102.0, 42.0, 18.0, 6.0, 2.0, 4.0, 0.0, 1.0, ) ,
	}

        common(self)


class data_2b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 7.644, 3.518, 2.874, 1.315, 0.3224, 0.1239, 0.04991, 0.05121, ) ,
		"mcHad"              :   ( 121.1, 47.87, 38.68, 22.12, 9.203, 3.549, 1.128, 0.662, 0.3534, 0.2246, ) ,
		"mcTtw"              :   ( 116.1, 46.16, 37.04, 21.06, 8.747, 3.318, 1.016, 0.6203, 0.3396, 0.2072, ) ,
		"mcMuon"             :   ( 939.1, 488.8, 512.5, 364.9, 187.7, 87.18, 42.35, 22.97, 10.97, 13.58, ) ,
		"mcZinv"             :   ( 4.996, 1.708, 1.639, 1.052, 0.4564, 0.2306, 0.1121, 0.04174, 0.01381, 0.0174, ) ,
		"mcMumu"             :   ( 13.26, 5.4, 7.522, 5.944, 2.993, 1.391, 0.4205, 0.3346, 0.413, 0.1366, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 10.69, 7.713, 7.789, 6.57, 4.689, 3.207, 2.155, 1.629, 1.084, 1.138, ) ,
		"mcMumuErr"          :   ( 2.363, 1.519, 1.813, 1.544, 0.8728, 0.3834, 0.1696, 0.1835, 0.5349, 0.1151, ) ,
		"mcHadErr"           :   ( 2.337, 1.474, 1.305, 0.9537, 0.6044, 0.3894, 0.1832, 0.1691, 0.1053, 0.08021, ) ,
		"mcZinvErr"          :   ( 0.3925, 0.1956, 0.1852, 0.1273, 0.07698, 0.0564, 0.03162, 0.01813, 0.0, 0.0, ) ,
		"mcTtwErr"           :   ( 2.303, 1.461, 1.292, 0.9452, 0.5995, 0.3853, 0.1805, 0.1682, 0.1053, 0.08021, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 2.165, 1.054, 1.081, 0.7053, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 14.0, 13.0, 5.0, 1.0, 2.0, 1.0, 0.0, 1.0, ) ,
		"nHad"               :   ( 103.0, 38.0, 41.0, 32.0, 10.0, 3.0, 0.0, 0.0, 0.0, 1.0, ) ,
		"nMuon"              :   ( 823.0, 415.0, 388.0, 271.0, 146.0, 66.0, 25.0, 10.0, 3.0, 4.0, ) ,
		"nMumu"              :   ( 9.0, 7.0, 4.0, 7.0, 3.0, 1.0, 0.0, 0.0, 0.0, 2.0, ) ,
	}

        common(self)


class data_2b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 20.37, 5.481, 2.991, 0.7672, 0.545, 0.1508, 0.01409, 0.02647, ) ,
		"mcHad"              :   ( 93.34, 41.74, 30.96, 7.375, 2.011, 0.5633, 0.1433, 0.0262, 0.02325, 0.009448, ) ,
		"mcTtw"              :   ( 78.77, 35.26, 26.64, 5.909, 1.559, 0.3954, 0.07274, 0.014, 0.003769, 0.003834, ) ,
		"mcMuon"             :   ( 943.9, 537.8, 476.6, 154.3, 55.57, 20.85, 8.747, 3.621, 2.004, 2.008, ) ,
		"mcZinv"             :   ( 14.56, 6.474, 4.317, 1.466, 0.4523, 0.1679, 0.0706, 0.0122, 0.01948, 0.005613, ) ,
		"mcMumu"             :   ( 37.86, 17.87, 16.41, 7.572, 3.498, 0.4949, 0.2172, 0.1536, 0.3478, 0.0208, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 8.596, 6.446, 6.056, 3.404, 2.043, 1.184, 0.7924, 0.4748, 0.3663, 0.2865, ) ,
		"mcMumuErr"          :   ( 3.313, 2.514, 2.265, 2.094, 1.343, 0.2605, 0.1847, 0.134, 0.3096, 0.09546, ) ,
		"mcHadErr"           :   ( 1.673, 1.025, 0.9203, 0.4307, 0.225, 0.09698, 0.04956, 0.0136, 0.01787, 0.007429, ) ,
		"mcZinvErr"          :   ( 0.5937, 0.3694, 0.274, 0.141, 0.07255, 0.04195, 0.03509, 0.007887, 0.01737, 0.005219, ) ,
		"mcTtwErr"           :   ( 1.564, 0.9559, 0.8785, 0.4069, 0.213, 0.08744, 0.035, 0.01109, 0.004198, 0.005287, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 3.211, 1.442, 1.233, 0.5326, 0.3494, 0.1006, 0.04418, 0.07017, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 33.0, 7.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 107.0, 53.0, 24.0, 5.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 876.0, 451.0, 403.0, 120.0, 31.0, 7.0, 3.0, 3.0, 1.0, 0.0, ) ,
		"nMumu"              :   ( 44.0, 26.0, 15.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_3b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.4763, 0.1519, 0.15, 0.09958, 0.01166, 0.004726, 0.001806, 0.001801, ) ,
		"mcHad"              :   ( 13.73, 5.359, 4.45, 2.812, 1.269, 0.5242, 0.1527, 0.1065, 0.05052, 0.03642, ) ,
		"mcTtw"              :   ( 13.48, 5.285, 4.339, 2.761, 1.245, 0.5049, 0.1478, 0.1044, 0.04963, 0.03566, ) ,
		"mcMuon"             :   ( 111.4, 56.17, 58.54, 43.22, 26.09, 12.53, 5.82, 3.364, 1.754, 1.786, ) ,
		"mcZinv"             :   ( 0.2432, 0.07373, 0.1113, 0.05118, 0.024, 0.01938, 0.004861, 0.00215, 0.0008849, 0.0007568, ) ,
		"mcMumu"             :   ( 0.7758, 0.4906, 0.4988, 0.1918, 0.2519, 0.1712, 0.03311, 0.05029, 0.1461, 0.001803, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.813, 0.5808, 0.5956, 0.5085, 0.4252, 0.2938, 0.1799, 0.1439, 0.1048, 0.0672, ) ,
		"mcMumuErr"          :   ( 0.07209, 0.09057, 0.08259, 0.02786, 0.04958, 0.03204, 0.009651, 0.01609, 0.03195, 0.0, ) ,
		"mcHadErr"           :   ( 0.1765, 0.1137, 0.1053, 0.08498, 0.05761, 0.03806, 0.01835, 0.01748, 0.008957, 0.006744, ) ,
		"mcZinvErr"          :   ( 0.01479, 0.006769, 0.009861, 0.004853, 0.003645, 0.003475, 0.0007711, 0.0005841, 0.0, 0.0, ) ,
		"mcTtwErr"           :   ( 0.1758, 0.1134, 0.1049, 0.08484, 0.0575, 0.0379, 0.01833, 0.01747, 0.008957, 0.006744, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.1191, 0.03855, 0.0453, 0.04558, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 13.0, 1.0, 0.0, 1.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 84.0, 48.0, 48.0, 31.0, 18.0, 11.0, 6.0, 1.0, 1.0, 0.0, ) ,
		"nMumu"              :   ( 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_3b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.4168, 0.09992, 0.08908, 0.00374, 0.01024, 0.003415, 0.0001497, 0.0002994, ) ,
		"mcHad"              :   ( 4.446, 1.928, 1.503, 0.3164, 0.08007, 0.02439, 0.003253, 0.0005669, 0.0002071, 0.0001335, ) ,
		"mcTtw"              :   ( 4.066, 1.809, 1.391, 0.2927, 0.0717, 0.01933, 0.002021, 0.0003853, 0.0001028, 6.319e-05, ) ,
		"mcMuon"             :   ( 48.46, 26.74, 22.84, 6.779, 2.599, 1.014, 0.332, 0.1528, 0.08135, 0.07003, ) ,
		"mcZinv"             :   ( 0.3802, 0.1186, 0.1115, 0.02373, 0.008371, 0.005062, 0.001232, 0.0001817, 0.0001044, 7.029e-05, ) ,
		"mcMumu"             :   ( 0.7383, 0.4935, 0.4525, 0.07905, 0.1267, 0.02031, 0.0065, 0.008028, 0.04072, 0.0001592, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.3912, 0.2977, 0.2702, 0.1386, 0.09005, 0.05262, 0.02714, 0.01814, 0.01453, 0.007129, ) ,
		"mcMumuErr"          :   ( 0.04835, 0.06057, 0.04733, 0.01646, 0.04983, 0.003465, 0.003742, 0.006408, 0.03794, 0.0, ) ,
		"mcHadErr"           :   ( 0.0707, 0.04769, 0.04496, 0.02003, 0.009804, 0.00428, 0.0008998, 0.0, 5.027e-05, 0.0, ) ,
		"mcZinvErr"          :   ( 0.01014, 0.006392, 0.007152, 0.002378, 0.001423, 0.00142, 0.0006226, 0.0, 5.027e-05, 0.0, ) ,
		"mcTtwErr"           :   ( 0.06997, 0.04726, 0.04438, 0.01989, 0.009701, 0.004038, 0.0006496, 0.0, 0.0, 0.0, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.08855, 0.03534, 0.04105, 0.0, 0.005764, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 6.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 48.0, 29.0, 20.0, 8.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, ) ,
		"nMumu"              :   ( 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_ge4b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.01013, 0.002804, 0.002494, 0.003531, 0.0002346, 0.0001087, 3.709e-05, 3.078e-05, ) ,
		"mcHad"              :   ( 0.4948, 0.1856, 0.1745, 0.1435, 0.07364, 0.03469, 0.01003, 0.008307, 0.004241, 0.003525, ) ,
		"mcTtw"              :   ( 0.4906, 0.1845, 0.1662, 0.1425, 0.07314, 0.03418, 0.009932, 0.008262, 0.004193, 0.003506, ) ,
		"mcMuon"             :   ( 3.927, 1.86, 2.113, 1.882, 1.438, 0.7395, 0.3893, 0.2068, 0.1228, 0.1275, ) ,
		"mcZinv"             :   ( 0.004169, 0.00103, 0.008274, 0.0009513, 0.0004987, 0.0005043, 9.882e-05, 4.49e-05, 4.742e-05, 1.851e-05, ) ,
		"mcMumu"             :   ( 0.007411, 0.01161, 0.009415, 0.002853, 0.008145, 0.009216, 0.001135, 0.003348, 0.02733, 2.98e-05, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.03423, 0.02336, 0.03767, 0.03577, 0.03824, 0.02312, 0.03382, 0.0119, 0.01121, 0.009922, ) ,
		"mcMumuErr"          :   ( 0.0009008, 0.002346, 0.001558, 0.0004899, 0.002043, 0.002687, 0.0004024, 0.001644, 0.0207, 1.539e-05, ) ,
		"mcHadErr"           :   ( 0.008676, 0.005132, 0.006672, 0.008511, 0.004441, 0.003534, 0.001751, 0.001895, 0.001319, 0.001197, ) ,
		"mcZinvErr"          :   ( 0.0006269, 0.0001073, 0.0002374, 0.0001198, 0.0001006, 0.0001462, 2.995e-05, 1.635e-05, 3.957e-05, 5.13e-06, ) ,
		"mcTtwErr"           :   ( 0.008654, 0.00513, 0.006668, 0.00851, 0.00444, 0.003531, 0.001751, 0.001895, 0.001319, 0.001197, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.003214, 0.001003, 0.0008057, 0.002068, 5.903e-05, 5.225e-05, 1.806e-05, 1.468e-05, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 1.0, 1.0, 0.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_ge4b_le3j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0004057, 0.0005308, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcHad"              :   ( 0.005887, 0.001701, 0.0006908, 3.979e-05, 0.0, 3.048e-05, 5.783e-06, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 0.004672, 0.0006728, 0.0005847, 2.434e-05, 0.0, 9.681e-06, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcMuon"             :   ( 0.03297, 0.01724, 0.009967, 0.001966, 0.001088, 0.0004155, 0.0003155, 0.0001229, 0.0001649, 0.0, ) ,
		"mcZinv"             :   ( 0.001215, 0.001028, 0.0001061, 1.545e-05, 0.0, 2.08e-05, 5.783e-06, 0.0, 0.0, 0.0, ) ,
		"mcMumu"             :   ( 0.0003232, 0.0004445, 0.00014, 4.736e-07, 0.0007713, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.003308, 0.002114, 0.00142, 0.0005098, 0.0004078, 0.0003127, 0.0001866, 9.608e-05, 0.0001649, 0.0, ) ,
		"mcMumuErr"          :   ( 0.0002505, 0.0003088, 9.907e-05, 4.736e-07, 0.0007713, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcHadErr"           :   ( 0.001245, 0.0009714, 0.0002244, 2.673e-05, 0.0, 2.294e-05, 5.783e-06, 0.0, 0.0, 0.0, ) ,
		"mcZinvErr"          :   ( 0.00105, 0.0009455, 6.515e-05, 1.106e-05, 0.0, 2.08e-05, 5.783e-06, 0.0, 0.0, 0.0, ) ,
		"mcTtwErr"           :   ( 0.0006689, 0.0002228, 0.0002147, 2.433e-05, 0.0, 9.68e-06, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0004057, 0.0005308, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)

import collections

def add(lst = [], quad = False) :
    dct = collections.defaultdict(float)
    lens = []
    for t in lst :
        lens.append(len(t))
        for i,x in enumerate(t) :
            if x!=None :
                dct[i] += x if not quad else x*x
            else :
                dct[i] = None
    if quad :
        for key in dct.keys() :
            if dct[key]!=None : dct[key] = dct[key]**0.5

    assert len(set(lens))==1,set(lens)
    return tuple([dct[i] for i in range(len(dct))])

def fetched(lst = [], func = "", attr = "", key = "") :
    return [(getattr(x,func)() if func else getattr(x,attr))[key] for x in lst]

def fill(x, lst = []) :
    x._observations = {}
    for key in ["nPhot", "nHad", "nMuon", "nMumu", "nHadBulk"] :
        x._observations[key] = add(fetched(lst = lst, attr = "_observations", key = key))

    x._mcExpectationsBeforeTrigger = {}
    for key in ["mcPhot", "mcHad", "mcTtw", "mcMuon", "mcZinv", "mcMumu"] :
        x._mcExpectationsBeforeTrigger[key] = add(fetched(lst = lst, attr = "_mcExpectationsBeforeTrigger", key = key))

    x._mcStatError = {}
    for key in ["mcMuonErr", "mcMumuErr", "mcHadErr", "mcZinvErr", "mcTtwErr", "mcPhotErr"] :
        x._mcStatError[key] = add(fetched(lst, attr = "_mcStatError", key = key), quad = True)

    common(x)

    x._mergeBins = None
    print "ERROR: assert uniformity"
    x._htBinLowerEdges = lst[0]._htBinLowerEdges
    x._htMaxForPlot    = lst[0]._htMaxForPlot
    x._htMeans         = lst[0]._htMeans

class data_0b_ge2j(data) :
    def _fill(self) :
        fill(self,  lst = [data_0b_le3j(), data_0b_ge4j()])
