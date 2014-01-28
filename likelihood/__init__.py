# graphical hacks (white superscript)
nb = "n_{b}^{#color[0]{b}}"
nj = "n_{j}^{#color[0]{j}}"


def spec(name="", **kargs):
    exec("from likelihood import l%s" % name)
    llk = eval("l%s.l%s" % (name, name))
    return llk(**kargs)


class selection(object):
    def __init__(self, name="", note="", boxes=[], data=None,
                 bJets="", jets="", fZinvIni=0.5, fZinvRange=(0.0, 1.0),
                 AQcdIni=1.0e-2, AQcdMax=100.0, yAxisLogMinMax=(0.3, None),
                 zeroQcd=False, muonForFullEwk=False,
                 universalSystematics=False, universalKQcd=False):
        for item in ["name", "note", "boxes", "data", "bJets",
                     "jets", "fZinvIni", "fZinvRange", "yAxisLogMinMax",
                     "AQcdIni", "AQcdMax", "zeroQcd", "muonForFullEwk",
                     "universalSystematics", "universalKQcd"]:
            setattr(self, item, eval(item))
            assert type(boxes) is list


def sampleCode(boxes=[]):
    d = {"had": "h", "phot": "p", "muon": "1", "mumu": "2", "simple": "s"}
    out = [d[box] for box in boxes]
    return "".join(sorted(out))


class base(object):
    def separateSystObs(self):
        return self._separateSystObs

    def poi(self):
        #return {"var": (initialValue, min, max)}
        return {"f": (0.1, 0.0, 0.1)}
        #return {"fZinv_55_0b_7": (0.5, 0.0, 1.0)}
        #return {"qcd_0b_le3j_0": (0.0, 0.0, 1.0e3)}
        #return {"k_qcd_0b_le3j": (3.0e-2, 0.01, 0.04)}
        #return {"ewk_0b_le3j_0": (2.22e4, 2.0e4, 2.5e4)}

    def REwk(self):
        return "" if self._ignoreHad else self._REwk

    def RQcd(self):
        return "Zero" if self._ignoreHad else self._RQcd

    def nFZinv(self):
        return "All" if self._ignoreHad else self._nFZinv

    def constrainQcdSlope(self):
        return False if self._ignoreHad else self._constrainQcdSlope

    def qcdParameterIsYield(self):
        return self._qcdParameterIsYield

    def initialValuesFromMuonSample(self):
        return self._initialValuesFromMuonSample

    def initialFZinvFromMc(self):
        return self._initialFZinvFromMc

    def legendTitle(self):
        more = " [QCD=0; NO HAD IN LLK]" if self._ignoreHad else ""
        return self._legendTitle + more

    def ignoreHad(self):
        return self._ignoreHad

    def selections(self):
        out = self._selections
        if self._whiteList:
            out = filter(lambda x: x.name in self._whiteList, out)
        if self._blackList:
            out = filter(lambda x: x.name not in self._blackList, out)
        return out

    def poiList(self):
        return self.poi().keys()

    def standardPoi(self):
        return self.poiList() == ["f"]

    def note(self):
        out = "%s_" % self._name

        if self.REwk():
            out += "REwk%s_" % self.REwk()

        out += "RQcd%s" % self.RQcd()

        if self.constrainQcdSlope():
            out += "Ext"

        out += "_fZinv%s" % self.nFZinv()
        if not self.standardPoi():
            out += "__".join(["poi"] + self.poiList())

        for selection in self.selections():
            code = sampleCode(selection.boxes)
            out += "_%s-%s" % (selection.name, code)
        return out

    def add(self, sel=[]):
        if self._ignoreHad:
            for s in sel:
                del s.boxes["had"]
        self._selections += sel

    def _fill(self):
        raise Exception("NotImplemented", "Implement _fill(self)")

    def __init__(self, separateSystObs=True,
                 whiteList=[], blackList=[], ignoreHad=False):
        for item in ["separateSystObs",
                     "whiteList", "blackList", "ignoreHad"]:
            setattr(self, "_"+item, eval(item))

        self._name = ""
        self._REwk = None
        self._RQcd = None
        self._nFZinv = None
        self._qcdParameterIsYield = None
        self._constrainQcdSlope = None
        self._initialValuesFromMuonSample = None
        self._initialFZinvFromMc = None
        self._selections = []

        self._fill()

        assert self._name
        assert self._RQcd in ["Zero", "FallingExp"]
        assert self._nFZinv in ["All", "One", "Two"]
        assert self._REwk in ["", "Linear", "FallingExp", "Constant"]
        for item in ["qcdParameterIsYield", "constrainQcdSlope",
                     "initialValuesFromMuonSample",
                     "initialFZinvFromMc"]:
            assert getattr(self, "_"+item) in [False, True], item
