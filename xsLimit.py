#!/usr/bin/env python

import configuration.signal
import plottingGrid as pg

for model in configuration.signal.models():
    interBinOut = "LowEdge"
    pg.makeXsUpperLimitPlots(model=model,
                             logZ=True,
                             pruneYMin=True,
                             curveGopts="pl", #@@ "c"
                             interBinOut=interBinOut,
                             #mDeltaFuncs={"mDeltaMin": 0.0,
                             #             "mDeltaMax": 400.0,
                             #             "nSteps": 4,
                             #             "mGMax": 1250.,
                             #             },
                             #diagonalLine=True,
                             expectedMapsOnly=False,
                             observedCurves=True,
                             debug=False,
                             info=False,
                             )
    pg.makeEfficiencyPlots(model=model,
                           key="effHad",
                           interBinOut=interBinOut,
                           separateCategories=False,
                           includeNonUsedCategories=True,
                           debug=False,
                           info=False,
                           )
