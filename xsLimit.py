#!/usr/bin/env python

import plottingGrid as pg

pg.makeTopologyXsLimitPlots(logZ = True,
                            #name = "upperLimit95",
                            name = "UpperLimit",
                            simpleExcl = True,
                            #drawGraphs = False,
                            #mDeltaFuncs = {"mDeltaMin":0.0, "mDeltaMax":400.0, "nSteps":4, "mGMax":1250.},
                            )
