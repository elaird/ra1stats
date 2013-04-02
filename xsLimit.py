#!/usr/bin/env python

import plottingGrid

plottingGrid.makeXsUpperLimitPlots(logZ=True,
                                   debug=False,
                                   pruneYMin=True,
                                   curveGopts="l",
                                   #mDeltaFuncs={"mDeltaMin": 0.0,
                                   #             "mDeltaMax": 400.0,
                                   #             "nSteps": 4,
                                   #             "mGMax": 1250.,
                                   #             },
                                   #printXs=True,
                                   diagonalLine=True,
                                   expectedOnly=False,
                                   )

#plottingGrid.makeEfficiencyPlotBinned(key=["effHad", "effMuon"][0])
