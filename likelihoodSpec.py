nb = "n_{b}^{#color[0]{b}}" #graphical hack (white superscript)
nj = "n_{j}^{#color[0]{j}}" #graphical hack (white superscript)

class selection(object) :
    '''Each key appearing in samplesAndSignalEff is used in the likelihood;
    the corresponding value determines whether signal efficiency is considered for that sample.'''

    def __init__(self, name = "", note = "", samplesAndSignalEff = {}, data = None,
                 bJets = "", jets = "", fZinvIni = 0.5, fZinvRange = (0.0, 1.0),
                 AQcdIni = 1.0e-2, AQcdMax = 100.0, yAxisLogMinMax = (0.3, None),
                 zeroQcd = False, muonForFullEwk = False,
                 universalSystematics = False, universalKQcd = False) :
        for item in ["name", "note", "samplesAndSignalEff", "data",
                     "bJets", "jets", "fZinvIni", "fZinvRange", "yAxisLogMinMax",
                     "AQcdIni", "AQcdMax", "zeroQcd", "muonForFullEwk",
                     "universalSystematics", "universalKQcd"] :
            setattr(self, item, eval(item))

class spec(object) :

    def separateSystObs(self) :
        return self._separateSystObs
    def poi(self) :
        return [{"f": (1.0, 0.0, 1.0)}, #{"var": initialValue, min, max)
                {"fZinv_55_0b_7": (0.5, 0.0, 1.0)},
                {"A_qcd_55": (1.0e-2, 0.0, 1.0e-2)},
                {"k_qcd_55": (3.0e-2, 0.01, 0.04)}][0]
    def REwk(self) :
        return "" if self._ignoreHad else self._REwk
    def RQcd(self) :
        return "Zero" if self._ignoreHad else self._RQcd
    def nFZinv(self) :
        return "All" if self._ignoreHad else self._nFZinv
    def constrainQcdSlope(self) :
        return False if self._ignoreHad else self._constrainQcdSlope
    def qcdParameterIsYield(self) :
        return self._qcdParameterIsYield
    def legendTitle(self) :
        return self._legendTitle+(" [QCD=0; NO HAD IN LLK]" if self._ignoreHad else "")
    def ignoreHad(self) :
        return self._ignoreHad

    def selections(self) :
        if self._whiteList :
            return filter(lambda x:x.name in self._whiteList, self._selections)
        else :
            return self._selections

    def poiList(self) :
        return self.poi().keys()

    def standardPoi(self) :
        return self.poiList()==["f"]

    def add(self, sel = []) :
        if self._ignoreHad :
            for s in sel :
                del s.samplesAndSignalEff["had"]
        self._selections += sel

    def __init__(self, dataset = "2012dev", separateSystObs = True, whiteList = [], ignoreHad = False) :
        for item in ["dataset", "separateSystObs", "whiteList", "ignoreHad"] :
            setattr(self, "_"+item, eval(item))

        self._RQcd = None
        self._nFZinv = None
        self._REwk = None
        self._selections = []

        assert self._dataset in ["", "2011", "2012ichep", "2012dev"],self._dataset
        if self._dataset=="" :
            self.__initSimple__()
        elif self._dataset=="2011" :
            self.__init2011reorg__(updated = True)
        elif self._dataset=="2012ichep" :
            self.__init2012ichep__()
        elif self._dataset=="2012dev" :
            self.__init2012dev__()

        assert self._RQcd in ["Zero", "FallingExp", "FallingExpA"]
        assert self._nFZinv in ["All", "One", "Two"]
        assert self._REwk in ["", "Linear", "FallingExp", "Constant"]

    def __initSimple__(self) :
        self._constrainQcdSlope = False
        self._qcdParameterIsYield = False
        self._legendTitle = "SIMPLE TEST"
        from inputData.dataMisc import simpleOneBin as module
        self.add([
                selection(name = "test",
                          samplesAndSignalEff = {"simple":True},
                          data = module.data_simple(),
                          ),
                ])

    def __init2012dev__(self) :
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = True
        self._REwk = ""
        self._RQcd = "FallingExp"
        self._nFZinv = "Two"
        self._legendTitle = "CMS Preliminary, 11.7 fb^{-1}, #sqrt{s} = 8 TeV"
        from inputData.data2012 import take14 as module

        lst = []
        for b in ["0", "1", "2", "3", "ge4"] :
            for j in ["ge2", "le3", "ge4"][1:] :
                if b=="ge4" and j!="ge4" : continue
                if b=="3"   and j!="ge4" : continue

                yAxisLogMinMax = {"0"  :(0.3, None),
                                  "1"  :(0.3, None),
                                  "2"  :(0.3, 1.0e3) if j!="le3" else (0.05, None),
                                  "3"  :(0.05, None),
                                  "ge4":(0.1, 1.0e2),
                                  }[b]

                fZinvIni = {"0b"  : {"ge2j":0.57, "le3j":0.57, "ge4j":0.40},
                            "1b"  : {"ge2j":0.40, "le3j":0.40, "ge4j":0.20},
                            "2b"  : {"ge2j":0.10, "le3j":0.10, "ge4j":0.10},
                            "3b"  : {"ge2j":0.05, "le3j":0.05, "ge4j":0.05},
                            "ge4b": {"ge2j":0.01, "le3j":0.01, "ge4j":0.01},
                            }[b+"b"][j+"j"]

                name  = "%sb_%sj"%(b,j)
                #name  = "%sb_%sj_alphaTmuon"%(b,j)
                note  = "%s%s%s"%(nb, "= " if "ge" not in b else "#", b)
                note += "; %s#%s"%(nj, j)
                note = note.replace("ge","geq ").replace("le","leq ")

                if b=="0" :
                    options = [{"had":True, "muon":True, "phot":False, "mumu":False}]
                elif b=="1" :
                    options = [{"had":True, "muon":True, "phot":False, "mumu":False}]
                    #options += [{"had":True, "muon":True}]
                elif b=="2" :
                    options = [{"had":True, "muon":True}]
                    #options += [{"had":True, "muon":True, "phot":False, "mumu":False}]
                else :
                    options = [{"had":True, "muon":True}]

                for samplesAndSignalEff in options :
                    sel = selection(name = name, note = note,
                                    samplesAndSignalEff = samplesAndSignalEff,
                                    muonForFullEwk = len(samplesAndSignalEff)==2,
                                    data = getattr(module, "data_%s"%name)(),
                                    bJets = ("eq%sb"%b).replace("eqge","ge"),
                                    jets = "%sj"%j,
                                    fZinvIni = fZinvIni,
                                    AQcdIni = 0.0,
                                    yAxisLogMinMax = yAxisLogMinMax,
                                    )
                    lst.append(sel)
        self.add(lst)

    def __init2012ichep__(self) :
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self._REwk = ""
        self._RQcd = "FallingExp"
        self._nFZinv = "Two"
        self._legendTitle = "CMS Preliminary, 3.9 fb^{-1}, #sqrt{s} = 8 TeV"
        from inputData.data2012 import take5_unweighted as module

        self.add([
                selection(name = "55_0b",
                          note = "%s= 0"%nb,
                          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                          data = module.data_0b(),
                          bJets = "_btag_==_0",
                          fZinvIni = 0.50,
                          AQcdIni = 0.0,
                          ),
                #selection(name = "55_0b_no_aT",
                #          note = "%s= 0"%nb,
                #          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                #          data = module.data_0b_no_aT(),
                #          bJets = "_btag_==_0",
                #          fZinvIni = 0.50,
                #          AQcdIni = 0.0,
                #          ),
                selection(name = "55_1b",
                          note = "%s= 1"%nb,
                          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                          data = module.data_1b(),
                          bJets = "_btag_==_1",
                          fZinvIni = 0.25,
                          AQcdIni = 0.0,
                          ),
                selection(name = "55_2b",
                          note = "%s= 2"%nb,
                          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                          data = module.data_2b(),
                          bJets = "_btag_==_2",
                          fZinvIni = 0.1,
                          AQcdIni = 0.0,
                          ),
                selection(name = "55_gt2b",
                          note = "%s#geq 3"%nb,
                          samplesAndSignalEff = {"had":True, "muon":True},
                          muonForFullEwk = True,
                          data = module.data_ge3b(),
                          bJets = "_btag_>_2",
                          fZinvIni = 0.1,
                          AQcdIni = 0.0,
                          ),
                ])

    def __init2011reorg__(self, updated = True) :
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self._REwk = ""
        self._RQcd = "FallingExp"
        self._nFZinv = "Two"
        self._legendTitle = "CMS, L = 4.98 fb^{-1}, #sqrt{s} = 7 TeV"
        if updated :
            from inputData.data2011reorg import take3 as module
        else :
            from inputData.data2011reorg import take1 as module

        self.add([selection(name = "55_0b",
                            note = "%s= 0"%nb,
                            alphaTMinMax = ("55", None),
                            samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                            data = module.data_0b(),
                            nbTag = "0",
                            universalSystematics = True,
                            universalKQcd = True,
                            ),
#                  selection(name = "55_ge0b",
#                            note = "%s>= 0"%nb,
#                            alphaTMinMax = ("55", None),
#                            samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
#                            data = module.data_ge0b(),
#                            ),
#                  selection(name = "55_ge1b",
#                            note = "%s>= 1"%nb,
#                            alphaTMinMax = ("55", None),
#                            samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
#                            data = module.data_ge1b(),
#                            bTagLower = "0",
#                            fZinvIni = 0.25,
#                            AQcdIni = 0.0,
#                            ),
                  selection(name = "55_1b",
                            note = "%s= 1"%nb,
                            alphaTMinMax = ("55", None),
                            samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                            data = module.data_1b(),
                            nbTag = "1",
                            fZinvIni = 0.25,
                            AQcdIni = 0.0,
                            ),
                  selection(name = "55_2b",
                            note = "%s= 2"%nb,
                            alphaTMinMax = ("55", None),
                            samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                            data = module.data_2b(),
                            nbTag = "2",
                            fZinvIni = 0.1,
                            AQcdIni = 0.0,
                            ),
#                  selection(name = "55_ge2b",
#                            note = "%s>= 2"%nb,
#                            alphaTMinMax = ("55", None),
#                            samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
#                            data = module.data_ge2b(),
#                            bTagLower = "1",
#                            fZinvIni = 0.1,
#                            AQcdIni = 0.0,
#                            ),
                  selection(name = "55_gt2b", #v4!!
                            note = "%s#geq 3"%nb,
                            alphaTMinMax = ("55", None),
                            samplesAndSignalEff = {"had":True, "muon":True},
                            muonForFullEwk = True,
                            data = module.data_ge3b(),
                            #requested studies
                            #samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                            #muonForFullEwk = True,
                            #data = mixedMuons_b_sets.data_55_gt2btag_v4_ford_test( systMode = systMode ),
                            bTagLower = "2",
                            fZinvIni = 0.1,
                            AQcdIni = 0.0,
                            AQcdMax = 1.0 if updated else 100.0,
                            ),
                ])

