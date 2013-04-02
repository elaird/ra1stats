#!/usr/bin/env python

import configuration as conf
import plottingGrid as pg

for model in conf.signal.models():
    pg.makeXsUpperLimitPlots(model=model.name,
                             logZ=True,
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
    #pg.makeEfficiencyPlotBinned(model=model, key=["effHad", "effMuon"][0])
