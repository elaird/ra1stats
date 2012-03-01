import selections
from collections import Iterable

class spec(dict) :
    def __init__(self, simpleOneBin = False) :
        self._selections = []
        self.load()

        #for compatibility; to be rewritten
        d = self

        if simpleOneBin :
            assert False
            d["simpleOneBin"] = {"b":3.0}
            key = max(d["alphaT"].keys())
            d["alphaT"] = {key: {"samples": [("had", True)]} }
        else :
            d["simpleOneBin"] = {}
    
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

    def add(self, sel = None) :
        if not isinstance( sel, Iterable ) :
            self._selections.append(sel)
        else :
            for s in sel :
                self._selections.append(s)

    def load(self) :
        systMode = 3

        slices = False
        b = False
        multib = True

        aT0b = True

        assert sum([slices,b,multib]) == 1
        
        if slices :
            self.add( selections.alphaT_slices(systMode) )
        if b :
            self.add( selections.btag(systMode) )
        if multib :
            if aT0b :
                self.add( selections.alphaT_0btags(systMode) )
            else :
                self.add( selections.noAlphaT_0btags(systMode) )
            self.add( selections.btags_1_2_gt2(systMode) )
