import selections
from common import selection,nb

class spec(object) :

    def separateSystObs(self) : return True
    def poi(self) :
        return [{"f": (1.0, 0.0, 1.0)}, #{"var": initialValue, min, max)
                {"fZinv_55_0b_7": (0.5, 0.0, 1.0)},
                {"A_qcd_55": (1.0e-2, 0.0, 1.0e-2)},
                {"k_qcd_55": (3.0e-2, 0.01, 0.04)}][0]
    def REwk(self) : return ["", "Linear", "FallingExp", "Constant"][0]
    def RQcd(self) : return ["Zero", "FallingExp", "FallingExpA"][1]
    def nFZinv(self) : return ["All", "One", "Two"][2]
    def constrainQcdSlope(self) : return True

    def selections(self) :
        return self._selections

    def poiList(self) :
        return self.poi().keys()

    def standardPoi(self) :
        return self.poiList()==["f"]

    def add(self, sel = []) :
        self._selections += sel

    def __init__(self) :
        self._selections = []
        #self.__initSimple__()
        self.__init2012__()

    def __initSimple__(self) :
        self.legendTitle = "SIMPLE TEST"
        from inputData.data2011 import simpleOneBin as module
        self.add([
                selection(name = "test",
                          samplesAndSignalEff = {"simple":True},
                          data = module.data_simple(),
                          ),
                ])

    def __init2012__(self) :
        self.legendTitle = "CMS, 1.5 fb^{-1}, #sqrt{s} = 8 TeV"
        from inputData.data2012 import take1 as module
        self.add([
                selection(name = "55_0b",
                          note = "%s= 0"%nb,
                          alphaTMinMax = ("55", None),
                          samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                          data = module.data_0b(),
                          nbTag = "0",
                          fZinvIni = 0.50,
                          AQcdIni = 0.0,

                          universalSystematics = True,
                          universalKQcd = True,
                          ),
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

    def __init2011__(self) :
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
