import likelihood


class l2011(likelihood.base):
    def _fill(self, updated=True):
        self._name = self.__class__.__name__[1:]
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self._initialValuesFromMuonSample = False
        self._initialFZinvFromMc = False
        self._poiIniMinMax = (0.005, 0.0, 0.1)
        self._rhoSignalMin = 0.1
        self._REwk = ""
        self._RQcd = "FallingExp"
        self._nFZinv = "Two"
        self._legendTitle = "CMS, L = 4.98 fb^{-1}, #sqrt{s} = 7 TeV"
        if updated :
            from ra1i.data2011reorg import take3 as module
        else :
            from ra1i.data2011reorg import take1 as module

        self.add([likelihood.selection(name = "55_0b",
                                       note = "%s= 0"%likelihood.nb,
                                       boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
                                       data = module.data_0b(),
                                       bJets = "btag_==_0",
                                       universalSystematics = True,
                                       universalKQcd = True,
                                       ),
#                  likelihood.selection(name = "55_ge0b",
#                                       note = "%s>= 0"%likelihood.nb,
#                                       boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
#                                       data = module.data_ge0b(),
#                                       ),
#                  likelihood.selection(name = "55_ge1b",
#                                       note = "%s>= 1"%likelihood.nb,
#                                       boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
#                                       data = module.data_ge1b(),
#                                       bJets = "btag_>_0",
#                                       fZinvIni = 0.25,
#                                       AQcdIni = 0.0,
#                                       ),
                  likelihood.selection(name = "55_1b",
                                       note = "%s= 1"%likelihood.nb,
                                       boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
                                       data = module.data_1b(),
                                       bJets = "btag_==_1",
                                       fZinvIni = 0.25,
                                       AQcdIni = 0.0,
                                       ),
                  likelihood.selection(name = "55_2b",
                                       note = "%s= 2"%likelihood.nb,
                                       boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
                                       data = module.data_2b(),
                                       bJets = "btag_==_2",
                                       fZinvIni = 0.1,
                                       AQcdIni = 0.0,
                                       ),
#                  likelihood.selection(name = "55_ge2b",
#                            note = "%s>= 2"%likelihood.nb,
#                            boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
#                            data = module.data_ge2b(),
#                            bJets = "btag_>_1",
#                            fZinvIni = 0.1,
#                            AQcdIni = 0.0,
#                            ),
                  likelihood.selection(name = "55_gt2b", #v4!!
                                       note = "%s#geq 3"%likelihood.nb,
                                       boxes = {"had":True, "muon":True}.keys(),
                                       muonForFullEwk = True,
                                       data = module.data_ge3b(),
                                       #requested studies
                                       #boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
                                       #muonForFullEwk = True,
                                       #data = mixedMuons_b_sets.data_55_gt2btag_v4_ford_test( systMode = systMode ),
                                       bJets = "btag_>_2",
                                       fZinvIni = 0.1,
                                       AQcdIni = 0.0,
                                       AQcdMax = 1.0 if updated else 100.0,
                                       ),
                  ])

