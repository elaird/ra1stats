#!/usr/bin/env python

import plottingGrid

plottingGrid.makeXsUpperLimitPlots(logZ = True,
                                   debug = False,
                                   pruneYMin = True,
                                   #exclusionCurves = False,
                                   #mDeltaFuncs = {"mDeltaMin":0.0, "mDeltaMax":400.0, "nSteps":4, "mGMax":1250.},
                                   #printXs = True,
                                   stampPrelim = False,
                                   **{"shiftX":True, "shiftY":True, "interBin":"Center"}
                                   #**{"shiftX":False, "shiftY":False, "interBin":"LowEdge"}
                                   )

plottingGrid.makeEfficiencyPlot()
