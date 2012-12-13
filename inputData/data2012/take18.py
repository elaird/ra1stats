from data import data
import utils

def common1(x) :
    x._lumi =  	{
        "mumu"  : 1.139e+04,
        "muon"  : 1.139e+04,
        "mcPhot": 1.157e+04,
        "phot"  : 1.157e+04,
        "mcHad" : 1.166e+04,
        "had"   : 1.166e+04,
        "mcMuon": 1.139e+04,
        "mcMumu": 1.139e+04,
	}

    x._triggerEfficiencies = {
        "hadBulk":       (1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "muon":          (0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880, 0.880),
        "phot":          (1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
        "mumu":          (0.950, 0.960, 0.960, 0.970, 0.970, 0.970, 0.980, 0.980),
        }

    x._htBinLowerEdges = (275.0, 325.0, 375.0, 475.0, 575.0, 675.0, 775.0, 875.0)
    x._htMaxForPlot    = 975.0
    x._htMeans         = (298.0, 348.0, 416.0, 517.0, 617.0, 719.0, 819.0, 1044.)

    x._observations["nPhot"] = tuple([None, None]+list(x._observations["nPhot"][2:]))

def common(x) :
    common1(x)

    systBins = tuple([0,1]+[2]*2+[3]*2+[4]*2)
    name = x.__class__.__name__

    if "ge2j" in name :
        systMagnitudes = (0.10, 0.10, 0.20, 0.20, 0.30)
        #x._observations["nHadBulk"] = (653500000, 294800000, 214600000, 72190000, 26470000, 10860000, 4741000, 4718000) #v2 db
        x._triggerEfficiencies["had"] = (0.870, 0.986, 0.994, 1.000, 1.000, 1.000, 1.000, 1.000)
    elif "le3j" in name :
        systMagnitudes = (0.10, 0.10, 0.20, 0.20, 0.20)
        x._triggerEfficiencies["had"] = (0.891, 0.987, 0.990, 1.000, 1.000, 1.000, 1.000, 1.000)
        x._observations["nHadBulk"] = (559500000, 252400000, 180600000, 51650000, 17060000, 6499000, 2674000, 2501000) #v2 db
    elif "ge4j" in name :
        systMagnitudes = (0.10, 0.10, 0.20, 0.20, 0.30)
        x._triggerEfficiencies["had"] = (0.837, 0.982, 0.997, 1.000, 1.000, 1.000, 1.000, 1.000)
        x._observations["nHadBulk"] = ( 93940000, 42330000, 33950000, 20540000,  9410000,  4363000, 2067000, 2217000) #v2 db

    if "ge4b" in name :
        x._mergeBins = (0, 1, 2, 2, 2, 2, 2, 2)
        systMagnitudes = (0.25,)
        systBins = (0, 0, 0)
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
        }
