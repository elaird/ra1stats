import likelihood


class simple(likelihood.base):
    def _fill(self):
        self._name = self.__class__.__name__
        self._constrainQcdSlope = False
        self._qcdParameterIsYield = True
        self._initialValuesFromMuonSample = False
        self._initialFZinvFromMc = False
        self._poiIniMinMax = (0.0, -1.0, 2.0)
        self._rhoSignalMin = 0.0
        self._REwk = ""
        self._RQcd = "Zero"
        self._nFZinv = "All"
        self._legendTitle = "SIMPLE TEST"
        from ra1i.dataMisc import simpleOneBin as module
        self.add([
                likelihood.selection(name="test",
                                     boxes=["simple"],
                                     data=module.data_simple(),
                                     ),
                ])
