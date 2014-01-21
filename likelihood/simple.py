import likelihood


class simple(likelihood.spec):
    def _fill(self):
        self._name = self.__class__.__name__
        self._constrainQcdSlope = False
        self._qcdParameterIsYield = True
        self._initialValuesFromMuonSample = False
        self._initialFZinvFromMc = False
        self._REwk = ""
        self._RQcd = "Zero"
        self._nFZinv = "All"
        self._legendTitle = "SIMPLE TEST"
        from inputData.dataMisc import simpleOneBin as module
        self.add([
                likelihood.selection(name = "test",
                          samplesAndSignalEff = {"simple":True},
                          data = module.data_simple(),
                          ),
                ])

