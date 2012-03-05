import selections

class spec(dict) :
    def __init__(self) :
        self._selections = []
        self.load()

        #for compatibility; to be rewritten
        d = self

        #{"var": initialValue, min, max)
        d["poi"] = [{"f": (1.0, 0.0, 1.0)},
                    {"A_qcd_55": (1.0e-2, 0.0, 1.0e-2)},
                    {"k_qcd_55": (3.0e-2, 0.01, 0.04)},
                    ][0]
        
        d["selections"] = self.selections()
        d["REwk"] = ["", "Linear", "FallingExp", "Constant"][0]
        d["RQcd"] = ["Zero", "FallingExp", "FallingExpA"][1]
        d["nFZinv"] = ["All", "One", "Two"][2]
        d["constrainQcdSlope"] = True
    
    def selections(self) :
        return self._selections

    def standardPoi(self) :
        return self["poi"].keys()==["f"]

    def add(self, sel = []) :
        self._selections += sel

    def load(self) :
        systMode = 3

        slices = False
        b = False
        multib = True


        # multib suboptions
        aT0b = True # use aT cut in 0b slice
        gt0_only  = True # only use gt0b selection on top of =0 selection
                         # when false: use 1,2,gt2

        assert sum([slices,b,multib]) == 1
        
        if slices :
            self.add( selections.alphaT_slices(systMode) )

        if b :
            self.add( selections.noAlphaT_gt0b(systMode) )

        if multib :
            if aT0b :
                self.add( selections.alphaT_0btags(systMode) )
            else :
                self.add( selections.noAlphaT_0btags(systMode) )

            if gt0_only :
                self.add( selections.noAlphaT_gt0b(systMode, universalSystematics = False, universalKQcd = False) )
            else :
                self.add( selections.btags_1_2_gt2(systMode) )

#        self.add( selections.alphaT_slices_noMHTovMET(systMode) )
