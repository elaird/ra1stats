nb = "n_{b}^{#color[0]{b}}" #graphical hack (white superscript)
nj = "n_{j}^{#color[0]{j}}" #graphical hack (white superscript)

class selection(object) :
    '''Each key appearing in samplesAndSignalEff is used in the likelihood;
    the corresponding value determines whether signal efficiency is considered for that sample.'''

    def __init__(self, name = "", note = "", samplesAndSignalEff = {}, data = None,
                 alphaTMinMax = (None, None), nbTag = None, bTagLower = None,
                 fZinvIni = 0.5, fZinvRange = (0.0, 1.0), AQcdIni = 1.0e-2, AQcdMax = 100.0,
                 zeroQcd = False, muonForFullEwk = False,
                 universalSystematics = False, universalKQcd = False) :
        for item in ["name", "note", "samplesAndSignalEff", "data",
                     "alphaTMinMax","nbTag", "bTagLower",
                     "fZinvIni", "fZinvRange", "AQcdIni", "AQcdMax",
                     "zeroQcd", "muonForFullEwk",
                     "universalSystematics", "universalKQcd"] :
            setattr(self, item, eval(item))

class spec(object) :

    def separateSystObs(self) : return self._separateSystObs
    def poi(self) :
        return [{"f": (1.0, 0.0, 1.0)}, #{"var": initialValue, min, max)
                {"fZinv_55_0b_7": (0.5, 0.0, 1.0)},
                {"A_qcd_55": (1.0e-2, 0.0, 1.0e-2)},
                {"k_qcd_55": (3.0e-2, 0.01, 0.04)}][0]
    def REwk(self) : return ["", "Linear", "FallingExp", "Constant"][0]
    def RQcd(self) : return ["Zero", "FallingExp", "FallingExpA"][1]
    def nFZinv(self) : return ["All", "One", "Two"][2]
    def constrainQcdSlope(self) : return self._constrainQcdSlope
    def qcdParameterIsYield(self) : return self._qcdParameterIsYield

    def selections(self) :
        return self._selections[self._iLower:self._iUpper]

    def poiList(self) :
        return self.poi().keys()

    def standardPoi(self) :
        return self.poiList()==["f"]

    def add(self, sel = []) :
        self._selections += sel

    def __init__(self, iLower = None, iUpper = None, dataset = "2011", separateSystObs = True) :
        self._iLower = iLower
        self._iUpper = iUpper
        self._dataset = dataset
        self._selections = []
        self._separateSystObs = separateSystObs

        assert self._dataset in ["", "2011", "2012ichep", "2012dev"],self._dataset
        if self._dataset=="" :
            self.__initSimple__()
        elif self._dataset=="2011" :
            self.__init2011reorg__(updated = True)
        elif self._dataset=="2012ichep" :
            self.__init2012ichep__()
        elif self._dataset=="2012dev" :
            self.__init2012dev__()

    def __initSimple__(self) :
        self._constrainQcdSlope = False
        self._qcdParameterIsYield = False
        self.legendTitle = "SIMPLE TEST"
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
        self.legendTitle = ""
        from inputData.data2012 import take10 as module

        lst = []
        for b in ["0", "1", "2", "3", "ge4"] :
            fZinvIni = {"0"  : 0.50,
                        "1"  : 0.25,
                        "2"  : 0.10,
                        "3"  : 0.05,
                        "ge4": 0.01,
                        }[b]

            for j in ["ge2", "le3", "ge4"] :
                if j=="le3" :
                    print "skipping %sb, %sj"%(b,j)
                    continue
                if b=="ge4" and j!="ge4" : continue

                name  = "%sb_%sj"%(b,j)
                note  = "%s%s%s"%(nb, "= " if "ge" not in b else "#", b)
                note += "; %s#%s"%(nj, j)
                note = note.replace("ge","geq ").replace("le","leq ")

                samplesAndSignalEff = {"had":True, "muon":True}
                if b in ["0", "1", "2"] :
                    samplesAndSignalEff.update({"phot":False, "mumu":False})

                sel = selection(name = name,
                                note = note,
                                alphaTMinMax = ("55", None),
                                samplesAndSignalEff = samplesAndSignalEff,
                                muonForFullEwk = len(samplesAndSignalEff)==2,
                                data = getattr(module, "data_%s"%name)(),
                                #nbTag = "0", #argh, must re-make signal eff. with extra dimension of binning
                                fZinvIni = fZinvIni,
                                AQcdIni = 0.0,
                                )
                lst.append(sel)
        self.add(lst)

    def __init2012ichep__(self) :
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self.legendTitle = "CMS Preliminary, 3.9 fb^{-1}, #sqrt{s} = 8 TeV"
        from inputData.data2012 import take5_unweighted as module
        #self.legendTitle = "CMS, 5.0 fb^{-1}, #sqrt{s} = 8 TeV"
        #from inputData.data2012 import take6_unweighted as module
        self.add([
                selection(name = "55_0b",
                          note = "%s= 0"%nb,
                          alphaTMinMax = ("55", None),
                          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                          data = module.data_0b(),
                          nbTag = "0",
                          fZinvIni = 0.50,
                          AQcdIni = 0.0,
                          ),
                #selection(name = "55_0b_no_aT",
                #          note = "%s= 0"%nb,
                #          alphaTMinMax = ("55", None),
                #          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                #          data = module.data_0b_no_aT(),
                #          nbTag = "0",
                #          fZinvIni = 0.50,
                #          AQcdIni = 0.0,
                #          ),
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
                selection(name = "55_gt2b",
                          note = "%s#geq 3"%nb,
                          alphaTMinMax = ("55", None),
                          samplesAndSignalEff = {"had":True, "muon":True},
                          muonForFullEwk = True,
                          data = module.data_ge3b(),
                          bTagLower = "2",
                          fZinvIni = 0.1,
                          AQcdIni = 0.0,
                          ),
                ])

    def __init2011reorg__(self, updated = True) :
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self.legendTitle = "CMS, L = 4.98 fb^{-1}, #sqrt{s} = 7 TeV"
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

    def __init2011old__(self) :
        import selections
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = False
        self.legendTitle = "CMS, 5.0 fb^{-1}, #sqrt{s} = 7 TeV"
        args = {}
        args["systMode"] = 3
        args["reweighted"] = predictedGe3b = True
        args["predictionsEverywhere"] = False

        slices = False
        b = False
        multib = True


        # multib suboptions
        aT0b = True # use aT cut in 0b slice
        gt0_only  = False # only use gt0b selection on top of =0 selection
                         # when false: use 1,2,gt2

        assert sum([slices,b,multib]) == 1
        if args["predictionsEverywhere"] :
            assert args["reweighted"]

        if slices :
            self.add( selections.alphaT_slices(**args) )

        if b :
            self.add( selections.noAlphaT_gt0b(**args) )

        if multib :
            if aT0b :
                self.add( selections.alphaT_0btags(**args) )
            else :
                self.add( selections.noAlphaT_0btags(**args) )

            if gt0_only :
                self.add( selections.noAlphaT_gt0b(universalSystematics = False, universalKQcd = False, **args) )
            else :
                self.add( selections.btags_1_2_gt2(predictedGe3b = predictedGe3b, **args) )

#        self.add( selections.alphaT_slices_noMHTovMET(systMode) )
#        self.add( selections.twentyTen() )
