import selections

class spec(object) :
    _selections = []

    def separateSystObs(self) : return False
    def poi(self) : return [{"f": (1.0, 0.0, 1.0)}, {"A_qcd_55": (1.0e-2, 0.0, 1.0e-2)}, {"k_qcd_55": (3.0e-2, 0.01, 0.04)}][0] #{"var": initialValue, min, max)
    def REwk(self) : return ["", "Linear", "FallingExp", "Constant"][0]
    def RQcd(self) : return ["Zero", "FallingExp", "FallingExpA"][1]
    def nFZinv(self) : return ["All", "One", "Two"][2]
    def constrainQcdSlope(self) : return True

    def selections(self) :
        return self._selections

    def standardPoi(self) :
        return self.poi().keys()==["f"]

    def add(self, sel = []) :
        self._selections += sel

    def __init__(self) :
        systMode = 3

        slices = False
        b = True
        multib = False


        # multib suboptions
        aT0b = True # use aT cut in 0b slice
        gt0_only  = False # only use gt0b selection on top of =0 selection
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
#        self.add( selections.twentyTen() )

