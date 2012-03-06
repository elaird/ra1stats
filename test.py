#!/usr/bin/env python

import common,workspace
import likelihoodSpec

def signal(i) :

    def scaled(t, factor) :
        return tuple([factor*item for item in t])

    simple = common.signal(xs = 1.0e-2, label = "signal")
    simple.insert("test", {
            "effSimple": (0.30, ),
            })
    
    lm6 = common.signal(xs = 0.3104, label = "LM6 (LO)")
    lm6.insert("55", {
            "effHad": (0.0,     0.0,     0.005,   0.012,  0.019,  0.022,  0.018,  0.029),
            "effMuon":scaled((0.045, 0.045, 0.1568, 0.245, 0.3254, 0.3481, 0.2836, 0.3618), 1.0e-2)})
    lm6.insert("2010", { #mocked up from 2011
            "effHad": (0.0,     0.0,     0.005,   0.012 + 0.019 + 0.022 + 0.018 + 0.029),
            "effMuon":scaled((0.045, 0.045, 0.1568, 0.245 + 0.3254 + 0.3481 + 0.2836 + 0.3618), 1.0e-2)})
    
    p_61_61 = common.signal(xs = 0.0135922203, label = "m_{0}=600 GeV, m_{1/2}=600 GeV (NLO)")
    p_61_61.insert("52", {
            "effHad": [0.000537, 0.000805, 0.002238, 0.000537, 0.000697, 0.000549, 0.001144, 0.011951],
            "effMuon":[0.000000, 0.000000, 8.95e-05, 0.000000, 0.000000, 0.000000, 9.87e-05, 0.000200]})
    p_61_61.insert("53", {
            "effHad": [0.001880, 0.002596, 0.002877, 0.001948, 0.000638, 0.000925, 0.001068, 0.016007],
            "effMuon":[0.000000, 8.95e-05, 0.000000, 8.95e-05, 8.95e-05, 8.00e-05, 0.000000, 0.000859]})
    p_61_61.insert("55", {
            "effHad": [0.020765, 0.014874, 0.012880, 0.007342, 0.004510, 0.004137, 0.006537, 0.060402],
            "effMuon":[0.001253, 0.000985, 0.001404, 0.000259, 0.001022, 0.000789, 0.001111, 0.004416]})

    p_33_53 = common.signal(xs = 0.050740907, label = "RM1")#, label = "m_{0}=320 GeV, m_{1/2}=520 GeV (NLO)")
    p_33_53.insert("52", {
            "effHad": [0.000866, 0.000601, 0.000772, 0.001045, 0.000395, 0.001344, 0.001069, 0.013154],
            "effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000166, 0.000778]})
    p_33_53.insert("53", {
            "effHad": [0.001115, 0.000943, 0.001116, 0.001193, 0.001496, 0.001408, 0.002023, 0.021827],
            "effMuon":[0.000000, 8.59e-05, 0.000000, 0.000000, 0.000259, 0.000177, 0.000000, 0.001152]})
    p_33_53.insert("55", {
            "effHad": [0.008697, 0.004366, 0.004120, 0.005746, 0.007165, 0.011060, 0.014814, 0.079827],
            "effMuon":[0.000498, 0.000514, 0.000512, 0.000850, 0.000758, 0.000766, 0.001994, 0.004008]})

    p_33_53b = common.signal(xs = 0.050740907, label = "RM1 (>=1 b-tag)")#, label = "m_{0}=320 GeV, m_{1/2}=520 GeV (NLO) (>=1 b-tag)")
    p_33_53b.insert("55b_mixed", {
            "effHad": [0.003522, 0.001881, 0.001108, 0.001453, 0.002007, 0.002189, 0.003275, 0.021969],
            "effMuon":[0.000334, 8.59e-05, 0.000170, 0.000494, 0.000429, 0.000343, 0.000678, 0.001018]})

    p_181_19 = common.signal(xs = 5.6887135, label = "m_{0}=1800 GeV, m_{1/2}=180 GeV (NLO)")
    p_181_19.insert("55", {
            "effMuon":[0.000147, 0.000000, 0.000441, 0.000588, 0.000147, 0.000147, 0.000147, 0.000000],
            "effHad": [0.000231, 0.001030, 0.003325, 0.003974, 0.001766, 0.000588, 0.000000, 0.000000]})
    p_181_19.insert("2010", { #mocked up from 2011
            "effMuon":[0.000147, 0.000000, 0.000441, 0.000588 + 0.000147 + 0.000147 + 0.000147 + 0.000000],
            "effHad": [0.000231, 0.001030, 0.003325, 0.003974 + 0.001766 + 0.000588 + 0.000000 + 0.000000]})

    p_181_19.insert("55", {
            "effHad": [0.000609, 0.001324, 0.003472, 0.004121, 0.001766, 0.001030, 0.000000, 0.000147],
            "effMuon":[0.000231, 0.000000, 0.000441, 0.000588, 0.000147, 0.000147, 0.000000, 0.000000]})

    p_181_19.insert("52", {
            "effHad": [0.000000, 0.000294, 0.001030, 0.001324, 0.001471, 0.000588, 0.001030, 0.001117],
            "effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]})

    p_181_19.insert("53", {
            "effHad": [0.000147, 0.000147, 0.001556, 0.002796, 0.001913, 0.000588, 0.000883, 0.000301],
            "effMuon":[0.000000, 0.000000, 0.000000, 0.000294, 0.000000, 0.000000, 0.000147, 0.000000]})

    p_181_29 = common.signal(xs = 0.6430277062, label = "m_{0}=1800 GeV, m_{1/2}=280 GeV (NLO)")
    p_181_29.insert("55b_mixed", { # >=1 btag
            "effHad": [0.000271, 0.000000, 0.000765, 0.000605, 0.001009, 0.000707, 0.000807, 0.001211],
            "effMuon":[0.000000, 0.000292, 9.05e-05, 0.000292, 0.000000, 0.000201, 0.000000, 0.000000]})
    p_181_29.insert("55", {
            "effHad": [0.001630, 0.000473, 0.001420, 0.001079, 0.002310, 0.001313, 0.001211, 0.001595],
            "effMuon":[9.05e-05, 0.000382, 0.000473, 0.000382, 0.000292, 0.000909, 0.000000, 0.000000]})
    p_181_29.insert("52", {
            "effHad": [0.000362, 9.05e-05, 0.000654, 0.000181, 0.000506, 0.000201, 0.001211, 0.002422],
            "effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000201]})
    p_181_29.insert("53", {
            "effHad": [0.000835, 9.05e-05, 0.000362, 0.000403, 0.001192, 0.001009, 0.001009, 0.001080],
            "effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000201, 0.000201, 0.000000, 0.000000]})
    p_181_29.insert("55_0b", {
            "effHad": [0.000815, 0.000473, 0.000654, 0.000473, 0.001301, 0.000605, 0.000403, 0.000384],
            "effMuon":[9.05e-05, 9.05e-05, 0.000382, 9.05e-05, 0.000292, 0.000707, 0.000000, 0.000000]})
    p_181_29.insert("55_1b", {
            "effHad": [0.000181, 0.000000, 0.000675, 0.000403, 0.000201, 0.000304, 0.000605, 0.000605],
            "effMuon":[0.000000, 9.05e-05, 9.05e-05, 0.000292, 0.000000, 0.000201, 0.000000, 0.000000]})
    p_181_29.insert("55_2b", {
            "effHad": [9.05e-05, 0.000000, 0.000000, 0.000201, 0.000403, 0.000201, 0.000201, 0.000403],
            "effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]})
    p_181_29.insert("55_gt2b", {
            "effHad": [0.000000, 0.000000, 9.05e-05, 0.000000, 0.000403, 0.000201, 0.000000, 0.000201],
            "effMuon":[0.000000, 0.000201, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]})

    p_181_41 = common.signal(xs = 0.1048902957, label = "m_{0}=1800 GeV, m_{1/2}=400 GeV (NLO)")
    p_181_41.insert("52", {
            "effHad": [0.001250, 0.000673, 0.001153, 0.000673, 7.61e-05, 0.000268, 0.000351, 0.000586],
            "effMuon":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]})
    p_181_41.insert("53", {
            "effHad":[0.00173086272795, 0.000961590404419, 0.0011539084853, 0.00048079520221, 0.000172270388197, 9.61590404419e-05, 9.61590404419e-05, 0.00127708180703],
            "effMuon":[0.0, 0.0, 0.000192318080884, 0.0, 0.0, 9.61590404419e-05, 0.0, 0.0]})
    p_181_41.insert("55", {
            "effHad": [0.006634, 0.002884, 0.002403, 0.000961, 0.000633, 0.000653, 0.000172, 0.000792],
            "effMuon":[0.000941, 0.000576, 0.000384, 0.000556, 0.000351, 0.000000, 0.000000, 0.000586]})

    t2tt_875 = common.signal(xs = 1.0, label = "T2tt m_{stop}= 875 GeV, m_{LSP}= 225 GeV (1 pb)")
    t2tt_875.insert("52", {
            "effHad":[0.00012, 0.00022, 0.00068, 0.00148, 0.00204, 0.00274, 0.00254, 0.01006],
            "effHadSumUncRelMcStats":0.0317180739848,
            "effMuon":[8e-05, 8e-05, 0.00016, 0.00022, 0.00012, 8e-05, 6e-05, 0.00016],
            "effMuonSumUncRelMcStats":0.144337567297})
    t2tt_875.insert("53", {
            "effHad":[0.00022, 0.00034, 0.00136, 0.00268, 0.0038, 0.00472, 0.0047, 0.0148],
            "effHadSumUncRelMcStats":0.0247612759121,
            "effMuon":[8e-05, 0.00012, 0.00016, 0.00048, 0.00052, 0.0005, 0.00042, 0.00036],
            "effMuonSumUncRelMcStats":0.0870388279778})
    t2tt_875.insert("55", {
            "effHad":[0.00364, 0.0051, 0.01772, 0.03308, 0.04384, 0.04716, 0.03638, 0.05002],
            "effHadSumUncRelMcStats":0.00918746728765,
            "effMuon":[0.0022, 0.0028, 0.0061, 0.00744, 0.0061, 0.00334, 0.00188, 0.00208],
            "effMuonSumUncRelMcStats":0.0250234705106})

    t2tt_500 = common.signal(xs = 1.0, label = "T2tt m_{stop}= 500 GeV, m_{LSP}= 75 GeV (1 pb)")
    t2tt_500.insert("52", {
        "effHad": [0.000668, 0.000787, 0.002673, 0.003460, 0.004128, 0.002482, 0.001622, 0.002338],
        "effMuon":[0.000214, 0.000119, 0.000214, 0.000250, 0.000178, 0.000142, 0.000000, 0.000000]})
    t2tt_500.insert("53", {
        "effHad": [0.001312, 0.001384, 0.004176, 0.006515, 0.006085, 0.004653, 0.002720, 0.002863],
        "effMuon":[0.000334, 0.000453, 0.000714, 0.000535, 0.000321, 0.000178, 3.57e-05, 0.000107]})
    t2tt_500.insert("55", {
        "effHad": [0.014415, 0.018496, 0.039140, 0.037112, 0.020453, 0.010023, 0.003890, 0.002291],
        "effMuon":[0.004486, 0.005107, 0.005321, 0.003714, 0.001500, 0.000535, 0.000464, 0.000214]})
    
    t1_600_100 = {"xs":1.0,
                  "effMuon":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                  "effHad":[0.0016, 0.0033, 0.0142, 0.0283, 0.0341, 0.0210, 0.0099, 0.0075],
                  "label":"T1 m_{gluino} = 600 GeV, m_{LSP} = 100 GeV, xs = 1.0 pb",
                  }
    
    t2_39_7 = {"xs":1.0,
               "effMuon":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               "effHad":[0.0006, 0.0015, 0.0058, 0.0129, 0.0252, 0.0399, 0.0494, 0.2123],
               "label":"T2 39 7, xs = 1.0 pb",
               }

    out  = [p_33_53,  p_33_53b, p_181_29]
    out += [t2tt_875, t2tt_500]
    out += [p_181_19, p_181_41, p_61_61, t2tt_875, lm6, t1_600_100, t2_39_7, simple]
    return out[i]

f = workspace.foo(likelihoodSpec = likelihoodSpec.spec(),
                  #signal = signal(0),
                  signalExampleToStack = signal(2),
                  #trace = True
                  #rhoSignalMin = 0.1,
                  #fIniFactor = 0.1,
                  #extraSigEffUncSources = ["effHadSumUncRelMcStats"],
                  )

cl = 0.95 if f.likelihoodSpec.standardPoi() else 0.68
#out = f.interval(cl = cl, method = ["profileLikelihood", "feldmanCousins"][0], makePlots = True); print out
#out = f.cls(cl = cl, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0},makePlots = True,
#            calculatorType = ["frequentist", "asymptotic"][1],
#            testStatType = 3, nToys = 20, nWorkers = 1); print out
#f.profile()
#f.bestFit(printValues = True)
#f.bestFit(drawMc = False, printValues = False)
#f.bestFit(drawMc = False, printValues = False, drawComponents = False)
#f.bestFit(printPages = True)
#f.qcdPlot()
#f.pValue(nToys = 300)
f.ensemble(nToys = 10)
#print f.clsCustom(nToys = 500, testStatType = 1)
#f.expectedLimit(cl = 0.95, nToys = 300, plusMinus = {"OneSigma": 1.0, "TwoSigma": 2.0}, makePlots = True)
#f.debug()
