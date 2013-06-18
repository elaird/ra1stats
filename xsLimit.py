#!/usr/bin/env python

import configuration as conf
import plottingGrid as pg

for model in conf.signal.models():
    interBinOut = "Center"
    pg.makeXsUpperLimitPlots(model=model,
                             logZ=True,
                             debug=False,
                             pruneYMin=True,
                             curveGopts="c",
                             interBinOut=interBinOut,
                             #mDeltaFuncs={"mDeltaMin": 0.0,
                             #             "mDeltaMax": 400.0,
                             #             "nSteps": 4,
                             #             "mGMax": 1250.,
                             #             },
                             #diagonalLine=True,
                             expectedOnly=False,
                             )
    pg.makeEfficiencyPlots(model=model,
                           key="effHad",
                           interBinOut=interBinOut,
                           separateCategories=True,
                           includeNonUsedCategories=True,
                           )
