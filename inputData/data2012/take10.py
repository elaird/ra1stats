from inputData import syst
from data import data
import utils

def common(x) :
    name = x.__class__.__name__
    if "ge2" in name :
        systMode = (0.10, 0.20, 0.60, 0.60)
        x._observations["nHadBulk"] = (630453600, 286166200, 209611400, 69777150, 26101500, 20182300, 4745175, 4745175/3., 4745175/9., 4745175/9.)
    elif "le3" in name :
        systMode = (0.15, 0.30, 0.50, 0.50)
        x._observations["nHadBulk"] = (487992800, 202369400, 134976100, 36965375, 12292400,  8301900, 1925125, 1925125/3., 1925125/9., 1925125/9.)
    elif "ge4" in name :
        systMode = (0.25, 0.35, 0.70, 0.70)
        x._observations["nHadBulk"] = (142460800,  83796800,  74635300, 32811775, 13809100, 11880400, 2820050, 2820050/3., 2820050/9., 2820050/9.)

    x._htBinLowerEdges = ( 275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0, 975.0, 1.075e+03, )
    x._htMaxForPlot    = 1.175e+03

    #improve last 3 (also for bulk yields)
    x._htMeans = (298, 348, 416, 517, 617, 719, 819, 919, 1020, 1240)
    x._mergeBins = None

    x._lumi = {
        "mumu"               :   1.139e+04 ,
        "muon"               :   1.139e+04 ,
        "mcPhot"             :   1.157e+04 ,
        "phot"               :   1.157e+04 ,
        "mcHad"              :   5.125e+03 ,
        "had"                :   5.125e+03 ,
        "mcMuon"             :   1.139e+04 ,
        "mcMumu"             :   1.139e+04 ,
	}

    x._triggerEfficiencies = {
        "hadBulk":       (1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "had":           (0.900, 0.990, 0.990, 0.990, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "muon":          (0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880),
        "phot":          (1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "mumu":          (0.950, 0.960, 0.960, 0.970, 0.970, 0.970, 0.980, 0.980, 0.980, 0.980),
        }

    x._observations["nPhot"] = tuple([None, None]+list(x._observations["nPhot"][2:]))
    syst.load(x, mode = systMode)
    x._fixedParameters.update({"k_qcd_nom":2.96e-2, "k_qcd_unc_inp":utils.quadSum([0.61e-2, 0.463e-2])})

class data_0b_ge2j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 3.309e+03, 1.264e+03, 468.6, 203.9, 80.24, 37.82, 10.11, 11.92, ) ,
		"mcHad"              :   ( 3.215e+03, 1.436e+03, 1.05e+03, 379.7, 144.2, 56.61, 23.84, 9.956, 4.323, 4.341, ) ,
		"mcTtw"              :   ( 1.626e+03, 718.4, 531.9, 188.4, 68.18, 26.4, 10.94, 5.078, 1.847, 1.888, ) ,
		"mcMuon"             :   ( 1.25e+04, 6.89e+03, 6.707e+03, 3.078e+03, 1.395e+03, 672.3, 349.0, 193.2, 100.4, 148.8, ) ,
		"mcZinv"             :   ( 1.589e+03, 717.3, 517.9, 191.3, 76.06, 30.21, 12.9, 4.878, 2.476, 2.453, ) ,
		"mcMumu"             :   ( 1.341e+03, 780.2, 728.7, 327.2, 161.2, 79.55, 39.53, 12.63, 8.266, 17.77, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 96.26, 42.79, 41.59, 23.78, 16.27, 11.19, 8.143, 5.851, 4.265, 5.121, ) ,
		"mcMumuErr"          :   ( 38.43, 29.7, 28.49, 19.56, 13.2, 9.912, 6.594, 3.598, 2.638, 4.292, ) ,
		"mcHadErr"           :   ( 28.46, 10.57, 8.092, 4.497, 2.687, 1.673, 1.056, 0.6903, 0.448, 0.422, ) ,
		"mcZinvErr"          :   ( 8.498, 5.558, 4.206, 2.371, 1.488, 0.9327, 0.6178, 0.3654, 0.2624, 0.2659, ) ,
		"mcTtwErr"           :   ( 27.17, 8.987, 6.913, 3.822, 2.238, 1.389, 0.856, 0.5857, 0.3631, 0.3277, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 57.97, 34.02, 20.89, 14.27, 8.389, 5.664, 2.726, 3.362, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 2.909e+03, 1.067e+03, 351.0, 144.0, 59.0, 22.0, 9.0, 7.0, ) ,
		"nHad"               :   ( 3.296e+03, 1.514e+03, 1.049e+03, 354.0, 128.0, 50.0, 9.0, 12.0, 11.0, 6.0, ) ,
		"nMuon"              :   ( 1.108e+04, 5.683e+03, 5.289e+03, 2.252e+03, 1.039e+03, 441.0, 209.0, 111.0, 73.0, 97.0, ) ,
		"nMumu"              :   ( 1.462e+03, 754.0, 678.0, 261.0, 152.0, 55.0, 28.0, 18.0, 8.0, 8.0, ) ,
	}

        common(self)


class data_0b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 331.3, 245.1, 126.6, 62.22, 31.49, 11.86, 4.985, 4.372, ) ,
		"mcHad"              :   ( 494.8, 199.4, 161.6, 107.8, 50.39, 24.39, 10.73, 4.726, 2.203, 2.143, ) ,
		"mcTtw"              :   ( 305.7, 124.5, 103.4, 66.04, 29.28, 14.13, 5.522, 3.05, 1.288, 1.056, ) ,
		"mcMuon"             :   ( 1.518e+03, 769.6, 844.8, 657.2, 358.0, 186.0, 100.8, 58.93, 31.86, 44.68, ) ,
		"mcZinv"             :   ( 189.1, 74.93, 58.2, 41.76, 21.11, 10.26, 5.205, 1.676, 0.9153, 1.087, ) ,
		"mcMumu"             :   ( 123.6, 70.11, 54.94, 48.7, 34.85, 20.66, 11.79, 2.365, 1.728, 5.722, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 38.05, 12.54, 20.57, 9.866, 7.695, 5.125, 4.221, 3.019, 2.336, 2.617, ) ,
		"mcMumuErr"          :   ( 10.89, 9.264, 7.592, 6.891, 5.996, 4.496, 3.565, 1.488, 1.017, 2.207, ) ,
		"mcHadErr"           :   ( 12.4, 3.851, 3.045, 2.475, 1.552, 1.119, 0.6876, 0.5057, 0.33, 0.2762, ) ,
		"mcZinvErr"          :   ( 2.932, 1.759, 1.402, 1.089, 0.7632, 0.5299, 0.3874, 0.2042, 0.1564, 0.1644, ) ,
		"mcTtwErr"           :   ( 12.05, 3.426, 2.703, 2.222, 1.351, 0.9851, 0.568, 0.4626, 0.2905, 0.2219, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 17.6, 15.24, 10.52, 7.737, 5.323, 3.004, 1.786, 1.866, ) ,
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
		"mcPhot"             :   ( 0.0, 0.0, 2.978e+03, 1.019e+03, 341.9, 141.7, 48.75, 25.95, 5.121, 7.544, ) ,
		"mcHad"              :   ( 2.721e+03, 1.236e+03, 888.3, 271.9, 93.86, 32.23, 13.12, 5.229, 2.12, 2.198, ) ,
		"mcTtw"              :   ( 1.321e+03, 593.9, 428.6, 122.4, 38.91, 12.27, 5.42, 2.027, 0.5588, 0.8318, ) ,
		"mcMuon"             :   ( 1.098e+04, 6.12e+03, 5.862e+03, 2.421e+03, 1.037e+03, 486.2, 248.2, 134.3, 68.6, 104.2, ) ,
		"mcZinv"             :   ( 1.4e+03, 642.4, 459.7, 149.5, 54.95, 19.96, 7.696, 3.202, 1.561, 1.366, ) ,
		"mcMumu"             :   ( 1.217e+03, 710.0, 673.8, 278.6, 126.3, 58.89, 27.74, 10.27, 6.538, 12.04, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 88.43, 40.91, 36.15, 21.64, 14.34, 9.945, 6.964, 5.012, 3.568, 4.402, ) ,
		"mcMumuErr"          :   ( 36.85, 28.22, 27.46, 18.31, 11.76, 8.833, 5.547, 3.276, 2.434, 3.681, ) ,
		"mcHadErr"           :   ( 25.62, 9.84, 7.497, 3.755, 2.194, 1.245, 0.801, 0.4699, 0.303, 0.3191, ) ,
		"mcZinvErr"          :   ( 7.976, 5.273, 3.965, 2.106, 1.277, 0.7676, 0.4812, 0.303, 0.2107, 0.209, ) ,
		"mcTtwErr"           :   ( 24.35, 8.308, 6.363, 3.11, 1.784, 0.9797, 0.6404, 0.3592, 0.2177, 0.2412, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 55.23, 30.41, 18.05, 11.99, 6.484, 4.802, 2.059, 2.797, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 2.601e+03, 854.0, 252.0, 94.0, 35.0, 11.0, 6.0, 4.0, ) ,
		"nHad"               :   ( 2.855e+03, 1.296e+03, 878.0, 241.0, 71.0, 25.0, 4.0, 8.0, 5.0, 2.0, ) ,
		"nMuon"              :   ( 9.698e+03, 5.039e+03, 4.653e+03, 1.808e+03, 779.0, 294.0, 150.0, 77.0, 55.0, 61.0, ) ,
		"nMumu"              :   ( 1.336e+03, 708.0, 623.0, 205.0, 120.0, 44.0, 21.0, 14.0, 6.0, 6.0, ) ,
	}

        common(self)


class data_1b_ge2j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 355.7, 144.7, 58.72, 26.18, 11.65, 5.242, 1.352, 1.597, ) ,
		"mcHad"              :   ( 746.9, 321.7, 240.3, 92.63, 35.33, 12.81, 5.172, 2.225, 1.243, 0.9498, ) ,
		"mcTtw"              :   ( 563.6, 240.0, 180.3, 68.31, 25.34, 8.857, 3.291, 1.56, 0.8874, 0.5844, ) ,
		"mcMuon"             :   ( 4.009e+03, 2.247e+03, 2.168e+03, 1.059e+03, 489.6, 226.9, 112.2, 58.27, 32.22, 38.24, ) ,
		"mcZinv"             :   ( 183.3, 81.66, 60.0, 24.32, 9.988, 3.957, 1.881, 0.6643, 0.3552, 0.3654, ) ,
		"mcMumu"             :   ( 187.3, 105.4, 101.8, 47.3, 24.92, 10.73, 4.479, 1.721, 2.374, 1.882, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 28.03, 20.83, 21.26, 16.75, 12.08, 8.69, 6.332, 4.316, 3.19, 3.573, ) ,
		"mcMumuErr"          :   ( 8.982, 5.172, 5.904, 2.941, 2.925, 1.831, 0.7073, 0.6204, 0.7307, 0.3514, ) ,
		"mcHadErr"           :   ( 8.145, 5.17, 4.641, 3.103, 2.047, 1.138, 0.7326, 0.3918, 0.6034, 0.2435, ) ,
		"mcZinvErr"          :   ( 1.915, 1.154, 0.9271, 0.5557, 0.33, 0.1997, 0.1609, 0.1043, 0.05239, 0.0435, ) ,
		"mcTtwErr"           :   ( 7.917, 5.039, 4.547, 3.053, 2.02, 1.121, 0.7147, 0.3777, 0.6011, 0.2396, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 10.24, 5.514, 2.649, 2.361, 1.621, 1.215, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 364.0, 146.0, 43.0, 21.0, 15.0, 3.0, 2.0, 1.0, ) ,
		"nHad"               :   ( 738.0, 304.0, 237.0, 68.0, 35.0, 8.0, 6.0, 3.0, 1.0, 0.0, ) ,
		"nMuon"              :   ( 4.035e+03, 2.046e+03, 1.815e+03, 857.0, 357.0, 159.0, 82.0, 29.0, 17.0, 28.0, ) ,
		"nMumu"              :   ( 215.0, 113.0, 123.0, 57.0, 29.0, 9.0, 4.0, 8.0, 0.0, 1.0, ) ,
	}

        common(self)


class data_1b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 55.19, 39.71, 22.35, 11.12, 5.335, 1.993, 0.846, 0.7847, ) ,
		"mcHad"              :   ( 267.3, 106.9, 86.81, 50.79, 21.87, 8.574, 3.589, 1.661, 0.9861, 0.7061, ) ,
		"mcTtw"              :   ( 235.1, 94.33, 76.57, 43.22, 18.07, 6.768, 2.608, 1.321, 0.8209, 0.492, ) ,
		"mcMuon"             :   ( 1.412e+03, 742.4, 796.9, 577.7, 299.5, 146.5, 73.5, 39.81, 20.63, 25.09, ) ,
		"mcZinv"             :   ( 32.22, 12.6, 10.24, 7.566, 3.799, 1.806, 0.9814, 0.3404, 0.1652, 0.2141, ) ,
		"mcMumu"             :   ( 30.81, 14.91, 15.62, 13.29, 8.494, 4.585, 2.245, 0.7258, 0.832, 1.033, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 20.72, 15.17, 16.4, 14.99, 11.22, 8.249, 5.842, 4.067, 3.069, 3.403, ) ,
		"mcMumuErr"          :   ( 5.375, 1.565, 2.788, 1.869, 2.241, 1.11, 0.686, 0.5924, 0.5977, 0.3414, ) ,
		"mcHadErr"           :   ( 6.486, 4.031, 3.74, 2.867, 1.962, 1.088, 0.7215, 0.3856, 0.6031, 0.2427, ) ,
		"mcZinvErr"          :   ( 1.169, 0.6589, 0.5526, 0.4251, 0.2428, 0.1688, 0.1314, 0.1008, 0.04976, 0.03876, ) ,
		"mcTtwErr"           :   ( 6.38, 3.977, 3.699, 2.835, 1.947, 1.075, 0.7095, 0.3721, 0.6011, 0.2396, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 4.828, 4.419, 1.892, 2.087, 0.0, 0.0, 0.0, 0.0, ) ,
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
		"mcPhot"             :   ( 0.0, 0.0, 300.5, 105.0, 36.37, 15.06, 6.313, 3.249, 0.5065, 0.8123, ) ,
		"mcHad"              :   ( 479.6, 214.7, 153.4, 41.84, 13.46, 4.24, 1.583, 0.5636, 0.2564, 0.2436, ) ,
		"mcTtw"              :   ( 328.5, 145.7, 103.7, 25.09, 7.275, 2.089, 0.6832, 0.2396, 0.06643, 0.09233, ) ,
		"mcMuon"             :   ( 2.597e+03, 1.504e+03, 1.371e+03, 481.6, 190.1, 80.43, 38.72, 18.46, 11.58, 13.14, ) ,
		"mcZinv"             :   ( 151.1, 69.06, 49.76, 16.75, 6.189, 2.151, 0.9, 0.324, 0.19, 0.1513, ) ,
		"mcMumu"             :   ( 156.5, 90.53, 86.22, 34.0, 16.43, 6.141, 2.234, 0.9948, 1.542, 0.848, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 18.88, 14.27, 13.53, 7.467, 4.472, 2.731, 2.443, 1.443, 0.8703, 1.087, ) ,
		"mcMumuErr"          :   ( 7.197, 4.929, 5.204, 2.27, 1.88, 1.456, 0.1723, 0.184, 0.4204, 0.08326, ) ,
		"mcHadErr"           :   ( 4.926, 3.237, 2.747, 1.187, 0.5825, 0.3352, 0.1268, 0.06982, 0.01745, 0.01973, ) ,
		"mcZinvErr"          :   ( 1.517, 0.9478, 0.7444, 0.3579, 0.2235, 0.1067, 0.09298, 0.02661, 0.01639, 0.01973, ) ,
		"mcTtwErr"           :   ( 4.687, 3.095, 2.644, 1.132, 0.538, 0.3178, 0.08623, 0.06456, 0.005974, 0.0, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 9.025, 3.298, 1.855, 1.105, 1.621, 1.215, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 307.0, 101.0, 27.0, 9.0, 5.0, 2.0, 1.0, 0.0, ) ,
		"nHad"               :   ( 509.0, 213.0, 153.0, 42.0, 9.0, 4.0, 1.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 2.662e+03, 1.434e+03, 1.223e+03, 413.0, 154.0, 51.0, 27.0, 12.0, 7.0, 7.0, ) ,
		"nMumu"              :   ( 184.0, 99.0, 102.0, 42.0, 18.0, 6.0, 2.0, 4.0, 0.0, 1.0, ) ,
	}

        common(self)


class data_2b_ge2j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 30.69, 9.507, 5.868, 2.231, 0.945, 0.2706, 0.07443, 0.08429, ) ,
		"mcHad"              :   ( 200.0, 83.88, 65.37, 27.58, 10.47, 3.85, 1.165, 0.6523, 0.3246, 0.2158, ) ,
		"mcTtw"              :   ( 182.1, 76.32, 59.75, 25.23, 9.617, 3.484, 0.9923, 0.6037, 0.2928, 0.193, ) ,
		"mcMuon"             :   ( 1.798e+03, 986.5, 951.1, 495.8, 232.7, 103.0, 49.22, 25.02, 12.6, 14.45, ) ,
		"mcZinv"             :   ( 17.82, 7.566, 5.621, 2.353, 0.8512, 0.3654, 0.1723, 0.04858, 0.03186, 0.02279, ) ,
		"mcMumu"             :   ( 48.6, 21.77, 22.53, 12.72, 5.862, 1.47, 0.5626, 0.3858, 0.3899, 0.1591, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 13.77, 10.09, 9.92, 7.466, 5.178, 3.473, 2.353, 1.734, 1.169, 1.233, ) ,
		"mcMumuErr"          :   ( 4.045, 2.886, 2.871, 2.62, 1.593, 0.4352, 0.2433, 0.2241, 0.3946, 0.154, ) ,
		"mcHadErr"           :   ( 2.879, 1.802, 1.605, 1.06, 0.6558, 0.4104, 0.1949, 0.1761, 0.1102, 0.08544, ) ,
		"mcZinvErr"          :   ( 0.7072, 0.4165, 0.3329, 0.1958, 0.1087, 0.07206, 0.04882, 0.02048, 0.01797, 0.005276, ) ,
		"mcTtwErr"           :   ( 2.79, 1.753, 1.57, 1.041, 0.6468, 0.404, 0.1887, 0.1749, 0.1088, 0.08528, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 4.539, 2.104, 1.81, 1.047, 0.4155, 0.09437, 0.05195, 0.07333, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 47.0, 20.0, 6.0, 3.0, 2.0, 1.0, 0.0, 1.0, ) ,
		"nHad"               :   ( 210.0, 91.0, 65.0, 37.0, 11.0, 4.0, 0.0, 0.0, 0.0, 1.0, ) ,
		"nMuon"              :   ( 1.699e+03, 866.0, 791.0, 391.0, 177.0, 73.0, 28.0, 13.0, 4.0, 4.0, ) ,
		"nMumu"              :   ( 53.0, 33.0, 19.0, 10.0, 3.0, 1.0, 0.0, 0.0, 0.0, 2.0, ) ,
	}

        common(self)


class data_2b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 8.487, 3.72, 3.221, 1.429, 0.3637, 0.1366, 0.05806, 0.05554, ) ,
		"mcHad"              :   ( 114.2, 45.21, 36.45, 20.72, 8.591, 3.337, 1.032, 0.6298, 0.3021, 0.2068, ) ,
		"mcTtw"              :   ( 109.7, 43.66, 34.9, 19.74, 8.162, 3.122, 0.9259, 0.592, 0.2897, 0.1895, ) ,
		"mcMuon"             :   ( 903.5, 473.1, 495.2, 349.5, 180.1, 83.27, 40.98, 21.79, 10.66, 12.67, ) ,
		"mcZinv"             :   ( 4.55, 1.557, 1.55, 0.9797, 0.4294, 0.2145, 0.1057, 0.03777, 0.01242, 0.01724, ) ,
		"mcMumu"             :   ( 12.66, 5.148, 7.246, 5.648, 2.69, 1.162, 0.3593, 0.2547, 0.1823, 0.1406, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 10.81, 7.783, 7.861, 6.641, 4.76, 3.266, 2.215, 1.67, 1.11, 1.199, ) ,
		"mcMumuErr"          :   ( 2.37, 1.522, 1.819, 1.553, 0.877, 0.385, 0.1699, 0.185, 0.3481, 0.1239, ) ,
		"mcHadErr"           :   ( 2.365, 1.489, 1.319, 0.9682, 0.6161, 0.3987, 0.1883, 0.1756, 0.1087, 0.08512, ) ,
		"mcZinvErr"          :   ( 0.3942, 0.1966, 0.1885, 0.1323, 0.07996, 0.05851, 0.03293, 0.01897, 0.0, 0.0, ) ,
		"mcTtwErr"           :   ( 2.332, 1.476, 1.306, 0.9591, 0.6109, 0.3944, 0.1854, 0.1746, 0.1087, 0.08512, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 2.584, 1.26, 1.29, 0.8418, 0.0, 0.0, 0.0, 0.0, ) ,
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
		"mcPhot"             :   ( 0.0, 0.0, 22.2, 5.787, 2.648, 0.8019, 0.5814, 0.134, 0.01638, 0.02875, ) ,
		"mcHad"              :   ( 85.8, 38.67, 28.94, 6.873, 1.877, 0.5137, 0.1329, 0.02263, 0.02256, 0.009025, ) ,
		"mcTtw"              :   ( 72.53, 32.66, 24.87, 5.499, 1.455, 0.3629, 0.06636, 0.01182, 0.00311, 0.00348, ) ,
		"mcMuon"             :   ( 893.8, 513.3, 456.0, 146.3, 52.63, 19.73, 8.249, 3.23, 1.936, 1.785, ) ,
		"mcZinv"             :   ( 13.27, 6.009, 4.072, 1.374, 0.4217, 0.1508, 0.06657, 0.01081, 0.01945, 0.005545, ) ,
		"mcMumu"             :   ( 35.94, 16.62, 15.28, 7.072, 3.173, 0.3069, 0.2033, 0.1311, 0.2076, 0.01848, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 8.533, 6.421, 6.05, 3.411, 2.04, 1.181, 0.7949, 0.4652, 0.3668, 0.2896, ) ,
		"mcMumuErr"          :   ( 3.278, 2.452, 2.221, 2.11, 1.33, 0.2029, 0.1742, 0.1265, 0.1859, 0.09136, ) ,
		"mcHadErr"           :   ( 1.641, 1.015, 0.913, 0.4305, 0.2249, 0.09704, 0.05036, 0.01266, 0.01844, 0.007378, ) ,
		"mcZinvErr"          :   ( 0.5871, 0.3672, 0.2743, 0.1443, 0.0736, 0.04206, 0.03605, 0.007705, 0.01797, 0.005276, ) ,
		"mcTtwErr"           :   ( 1.532, 0.9458, 0.8708, 0.4056, 0.2125, 0.08744, 0.03517, 0.01005, 0.004135, 0.005157, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 3.732, 1.685, 1.27, 0.6223, 0.4155, 0.09437, 0.05195, 0.07333, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 33.0, 7.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 107.0, 53.0, 24.0, 5.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 876.0, 451.0, 403.0, 120.0, 31.0, 7.0, 3.0, 3.0, 1.0, 0.0, ) ,
		"nMumu"              :   ( 44.0, 26.0, 15.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_3b_ge2j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.8573, 0.3037, 0.2567, 0.08957, 0.02822, 0.006826, 0.002247, 0.002263, ) ,
		"mcHad"              :   ( 17.9, 7.187, 5.79, 3.14, 1.344, 0.5546, 0.1506, 0.1197, 0.04867, 0.03897, ) ,
		"mcTtw"              :   ( 17.43, 6.986, 5.625, 3.062, 1.314, 0.5356, 0.1435, 0.1176, 0.04796, 0.03818, ) ,
		"mcMuon"             :   ( 168.9, 86.44, 86.32, 54.07, 30.27, 14.23, 7.576, 3.794, 2.011, 2.667, ) ,
		"mcZinv"             :   ( 0.469, 0.2004, 0.1654, 0.07858, 0.02991, 0.01904, 0.007084, 0.002085, 0.0007047, 0.0007955, ) ,
		"mcMumu"             :   ( 1.466, 0.5904, 0.7155, 0.4677, 0.2812, 0.08114, 0.02516, 0.01726, 0.02243, 0.009228, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 1.029, 0.7196, 0.7397, 0.6172, 0.4903, 0.3413, 0.2443, 0.1722, 0.1212, 0.1358, ) ,
		"mcMumuErr"          :   ( 0.1004, 0.0665, 0.0821, 0.07167, 0.06129, 0.01928, 0.007781, 0.007993, 0.01056, 0.004335, ) ,
		"mcHadErr"           :   ( 0.2108, 0.1341, 0.1242, 0.09835, 0.06649, 0.04399, 0.02128, 0.02096, 0.01142, 0.009746, ) ,
		"mcZinvErr"          :   ( 0.01998, 0.01134, 0.01042, 0.007194, 0.004268, 0.003164, 0.001878, 0.0007954, 0.0001455, 0.0, ) ,
		"mcTtwErr"           :   ( 0.2098, 0.1337, 0.1237, 0.09809, 0.06635, 0.04388, 0.02119, 0.02095, 0.01142, 0.009746, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.1487, 0.08018, 0.07293, 0.04429, 0.01279, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 19.0, 1.0, 0.0, 1.0, 3.0, 2.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 132.0, 77.0, 68.0, 39.0, 21.0, 11.0, 7.0, 1.0, 1.0, 0.0, ) ,
		"nMumu"              :   ( 2.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_3b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.4622, 0.1728, 0.1745, 0.08567, 0.01277, 0.005001, 0.002075, 0.00193, ) ,
		"mcHad"              :   ( 13.72, 5.303, 4.344, 2.816, 1.263, 0.5319, 0.1466, 0.1194, 0.04841, 0.03886, ) ,
		"mcTtw"              :   ( 13.49, 5.228, 4.263, 2.763, 1.241, 0.5165, 0.1414, 0.1174, 0.0479, 0.03813, ) ,
		"mcMuon"             :   ( 118.5, 59.07, 62.53, 46.89, 27.52, 13.25, 7.17, 3.645, 1.921, 2.574, ) ,
		"mcZinv"             :   ( 0.2328, 0.07501, 0.08115, 0.05331, 0.02235, 0.01543, 0.005271, 0.001967, 0.0005053, 0.0007284, ) ,
		"mcMumu"             :   ( 0.821, 0.3038, 0.4127, 0.3297, 0.1802, 0.07569, 0.02042, 0.01421, 0.0156, 0.009113, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.9249, 0.64, 0.6728, 0.5947, 0.4794, 0.3361, 0.2414, 0.171, 0.1199, 0.1348, ) ,
		"mcMumuErr"          :   ( 0.0833, 0.05561, 0.07133, 0.06134, 0.04334, 0.01917, 0.007271, 0.007472, 0.008727, 0.004335, ) ,
		"mcHadErr"           :   ( 0.1954, 0.1235, 0.1143, 0.09562, 0.06553, 0.04371, 0.02122, 0.02096, 0.01142, 0.009746, ) ,
		"mcZinvErr"          :   ( 0.01646, 0.008213, 0.008445, 0.006446, 0.003974, 0.002933, 0.001458, 0.0007954, 0.0, 0.0, ) ,
		"mcTtwErr"           :   ( 0.1947, 0.1232, 0.114, 0.0954, 0.06541, 0.04361, 0.02117, 0.02095, 0.01142, 0.009746, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.1197, 0.05897, 0.05684, 0.04429, 0.0, 0.0, 0.0, 0.0, ) ,
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
		"mcPhot"             :   ( 0.0, 0.0, 0.395, 0.1309, 0.08225, 0.003893, 0.01545, 0.001825, 0.0001719, 0.0003331, ) ,
		"mcHad"              :   ( 4.178, 1.884, 1.446, 0.3243, 0.08091, 0.02283, 0.003949, 0.0003705, 0.0002604, 0.0001134, ) ,
		"mcTtw"              :   ( 3.942, 1.759, 1.362, 0.299, 0.07335, 0.01922, 0.002136, 0.000252, 6.088e-05, 4.627e-05, ) ,
		"mcMuon"             :   ( 50.4, 27.38, 23.79, 7.176, 2.747, 0.9912, 0.4058, 0.148, 0.08991, 0.09331, ) ,
		"mcZinv"             :   ( 0.2362, 0.1253, 0.08422, 0.02527, 0.007564, 0.003614, 0.001813, 0.0001185, 0.0001995, 6.712e-05, ) ,
		"mcMumu"             :   ( 0.6449, 0.2865, 0.3029, 0.1379, 0.1011, 0.005453, 0.004736, 0.003054, 0.006833, 0.0001163, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.45, 0.3291, 0.3073, 0.1652, 0.1029, 0.05962, 0.03784, 0.02065, 0.01714, 0.01614, ) ,
		"mcMumuErr"          :   ( 0.05604, 0.03646, 0.04066, 0.03707, 0.04333, 0.001984, 0.00277, 0.002839, 0.005951, 0.0, ) ,
		"mcHadErr"           :   ( 0.07898, 0.05239, 0.04848, 0.023, 0.01125, 0.004932, 0.001613, 0.0, 0.0001455, 0.0, ) ,
		"mcZinvErr"          :   ( 0.01133, 0.007821, 0.006112, 0.003194, 0.001555, 0.001187, 0.001183, 0.0, 0.0001455, 0.0, ) ,
		"mcTtwErr"           :   ( 0.07816, 0.0518, 0.04809, 0.02278, 0.01114, 0.004788, 0.001096, 0.0, 0.0, 0.0, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.08826, 0.05433, 0.04569, 0.0, 0.01279, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 6.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 48.0, 29.0, 20.0, 8.0, 3.0, 0.0, 1.0, 0.0, 0.0, 0.0, ) ,
		"nMumu"              :   ( 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_ge4b_ge2j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.008321, 0.004149, 0.003697, 0.002168, 0.0002498, 0.0001104, 4.211e-05, 3.274e-05, ) ,
		"mcHad"              :   ( 0.5344, 0.1948, 0.1793, 0.1497, 0.07892, 0.03959, 0.01042, 0.01147, 0.004272, 0.004006, ) ,
		"mcTtw"              :   ( 0.5301, 0.193, 0.1711, 0.1485, 0.07846, 0.03917, 0.0103, 0.01143, 0.00426, 0.003989, ) ,
		"mcMuon"             :   ( 4.757, 2.213, 2.467, 2.295, 1.679, 0.888, 0.5594, 0.2733, 0.1608, 0.2584, ) ,
		"mcZinv"             :   ( 0.004351, 0.001746, 0.008167, 0.001134, 0.0004602, 0.0004201, 0.0001272, 4.409e-05, 1.208e-05, 1.729e-05, ) ,
		"mcMumu"             :   ( 0.01427, 0.005072, 0.00672, 0.005866, 0.004867, 0.001861, 0.0004574, 0.0002598, 0.0005797, 0.0002716, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.04617, 0.032, 0.0352, 0.04149, 0.04354, 0.03058, 0.02676, 0.01753, 0.01582, 0.02177, ) ,
		"mcMumuErr"          :   ( 0.005143, 0.001148, 0.001146, 0.001331, 0.001451, 0.0006557, 0.0001904, 0.0001483, 0.0004304, 0.0001536, ) ,
		"mcHadErr"           :   ( 0.009657, 0.005656, 0.006087, 0.007495, 0.005407, 0.004681, 0.00224, 0.00285, 0.001435, 0.001412, ) ,
		"mcZinvErr"          :   ( 0.000491, 0.0004522, 0.0002906, 0.0001869, 0.0001122, 0.0001588, 3.964e-05, 2.173e-05, 5.141e-06, 2.419e-06, ) ,
		"mcTtwErr"           :   ( 0.009644, 0.005638, 0.006081, 0.007493, 0.005406, 0.004678, 0.002239, 0.00285, 0.001435, 0.001412, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.002688, 0.001693, 0.001273, 0.001435, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 1.0, 1.0, 0.0, 1.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)


class data_ge4b_ge4j(data) :
    def _fill(self) :
        self._mcExpectationsBeforeTrigger =  	{
		"mcPhot"             :   ( 0.0, 0.0, 0.008321, 0.003335, 0.002992, 0.002168, 0.0002498, 0.0001104, 4.211e-05, 3.274e-05, ) ,
		"mcHad"              :   ( 0.5281, 0.1934, 0.1783, 0.1496, 0.07892, 0.03956, 0.0104, 0.01147, 0.004272, 0.004006, ) ,
		"mcTtw"              :   ( 0.5242, 0.1922, 0.1705, 0.1485, 0.07846, 0.03916, 0.0103, 0.01143, 0.00426, 0.003989, ) ,
		"mcMuon"             :   ( 4.71, 2.193, 2.454, 2.291, 1.677, 0.8874, 0.5588, 0.2731, 0.1606, 0.2584, ) ,
		"mcZinv"             :   ( 0.003818, 0.0012, 0.007859, 0.001107, 0.0004602, 0.0004062, 0.0001063, 4.409e-05, 1.208e-05, 1.729e-05, ) ,
		"mcMumu"             :   ( 0.01384, 0.004911, 0.006618, 0.005863, 0.00429, 0.001861, 0.0004574, 0.0002598, 0.0005797, 0.0002716, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.04585, 0.03184, 0.03516, 0.04149, 0.04354, 0.03058, 0.02676, 0.01753, 0.01582, 0.02177, ) ,
		"mcMumuErr"          :   ( 0.005132, 0.001142, 0.001144, 0.001331, 0.001331, 0.0006557, 0.0001904, 0.0001483, 0.0004304, 0.0001536, ) ,
		"mcHadErr"           :   ( 0.009615, 0.005633, 0.006078, 0.007495, 0.005407, 0.004681, 0.00224, 0.00285, 0.001435, 0.001412, ) ,
		"mcZinvErr"          :   ( 0.0003619, 0.0001552, 0.000168, 0.0001859, 0.0001122, 0.0001582, 3.372e-05, 2.173e-05, 5.141e-06, 2.419e-06, ) ,
		"mcTtwErr"           :   ( 0.009608, 0.005631, 0.006076, 0.007492, 0.005406, 0.004678, 0.002239, 0.00285, 0.001435, 0.001412, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.002688, 0.001484, 0.00106, 0.001435, 0.0, 0.0, 0.0, 0.0, ) ,
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
		"mcPhot"             :   ( 0.0, 0.0, 0.0, 0.0008146, 0.0007053, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcHad"              :   ( 0.00637, 0.00137, 0.0009274, 6.794e-05, 0.0, 3.023e-05, 2.083e-05, 0.0, 0.0, 0.0, ) ,
		"mcTtw"              :   ( 0.005836, 0.0008242, 0.0006196, 4.096e-05, 0.0, 1.63e-05, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcMuon"             :   ( 0.04623, 0.02118, 0.01259, 0.003003, 0.001347, 0.0005714, 0.0006362, 0.0002028, 0.0002289, 0.0, ) ,
		"mcZinv"             :   ( 0.0005335, 0.0005456, 0.0003078, 2.698e-05, 0.0, 1.393e-05, 2.083e-05, 0.0, 0.0, 0.0, ) ,
		"mcMumu"             :   ( 0.000434, 0.000161, 0.000103, 2.847e-06, 0.0005778, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._mcStatError =  	{
		"mcMuonErr"          :   ( 0.005444, 0.003157, 0.001829, 0.0007305, 0.0005235, 0.0004299, 0.0003763, 0.0001545, 0.0002289, 0.0, ) ,
		"mcMumuErr"          :   ( 0.0003365, 0.0001114, 7.289e-05, 2.847e-06, 0.0005778, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcHadErr"           :   ( 0.0008989, 0.0005032, 0.0003378, 4.529e-05, 0.0, 2.144e-05, 2.083e-05, 0.0, 0.0, 0.0, ) ,
		"mcZinvErr"          :   ( 0.0003318, 0.0004247, 0.0002372, 1.931e-05, 0.0, 1.393e-05, 2.083e-05, 0.0, 0.0, 0.0, ) ,
		"mcTtwErr"           :   ( 0.0008354, 0.0002698, 0.0002405, 4.096e-05, 0.0, 1.63e-05, 0.0, 0.0, 0.0, 0.0, ) ,
		"mcPhotErr"          :   ( 0.0, 0.0, 0.0, 0.0008146, 0.0007053, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        self._observations =  	{
		"nPhot"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nHad"               :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMuon"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
		"nMumu"              :   ( 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ) ,
	}

        common(self)
