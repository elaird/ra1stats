import likelihood


class l2011eps(likelihood.base):
    def _fill(self):
        self._name = self.__class__.__name__[1:]
        self._constrainQcdSlope = False
        self._qcdParameterIsYield = True
        self._initialValuesFromMuonSample = False
        self._initialFZinvFromMc = False
        self._poiIniMinMax = (0.005, 0.0, 0.1)
        self._rhoSignalMin = 0.1
        self._REwk = "Constant"
        self._RQcd = "FallingExp"
        self._nFZinv = "All"
        self._legendTitle = "CMS (re-analyzed), L = 1.1 fb^{-1}, #sqrt{s} = 7 TeV"
        from ra1i.dataMisc import orig as module

        self.add([likelihood.selection(name="55",
                                       boxes={"had":True, "muon":True, "phot":False}.keys(),
                                       data=module.data_2011_4(),
                                       fZinvRange=(0.2, 0.8),
                                       ),
                  ])
