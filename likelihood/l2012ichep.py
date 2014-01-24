import likelihood

class l2012ichep(likelihood.spec):
    def _fill(self):
        self._name = self.__class__.__name__[1:]
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self._initialValuesFromMuonSample = False
        self._initialFZinvFromMc = False
        self._REwk = ""
        self._RQcd = "FallingExp"
        self._nFZinv = "Two"
        self._legendTitle = "CMS Preliminary, 3.9 fb^{-1}, #sqrt{s} = 8 TeV"
        from inputData.data2012hcp import take5_unweighted as module

        self.add([
                likelihood.selection(name = "55_0b",
                          note = "%s= 0"%likelihood.nb,
                          boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
                          data = module.data_0b(),
                          bJets = "btag_==_0",
                          fZinvIni = 0.50,
                          AQcdIni = 0.0,
                          ),
                #likelihood.selection(name = "55_0b_no_aT",
                #          note = "%s= 0"%likelihood.nb,
                #          boxes = {"had":True, "muon":True, "phot":False, "mumu":False}.keys(),
                #          data = module.data_0b_no_aT(),
                #          bJets = "btag_==_0",
                #          fZinvIni = 0.50,
                #          AQcdIni = 0.0,
                #          ),
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
                likelihood.selection(name = "55_gt2b",
                          note = "%s#geq 3"%likelihood.nb,
                          boxes = {"had":True, "muon":True}.keys(),
                          muonForFullEwk = True,
                          data = module.data_ge3b(),
                          bJets = "btag_>_2",
                          fZinvIni = 0.1,
                          AQcdIni = 0.0,
                          ),
                ])
