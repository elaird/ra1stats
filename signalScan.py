class scan(object):
    def __init__(self,
                 dataset="",
                 tag="",
                 com=None,
                 xsVariation="default",
                 xsFactors=[1.0],
                 had="",
                 muon="",
                 phot="",
                 mumu="",
                 interBin="LowEdge",
                 aT={},
                 extraVars=[],
                 weightedHistName="",
                 unweightedHistName="",
                 minSumWeightIn=1,
                 maxSumWeightIn=None,
                 llk=None,
                 whiteList=[],
                 exampleKargs={},
                 sigMcUnc=False,
                 binaryExclusion=False,
                 flatEffUncRel=True,
                 ):

        assert xsVariation in ["default", "up", "down"], xsVariation

        self._boxNames = ["had", "muon", "phot", "mumu"]
        for item in ["dataset", "tag", "interBin", "com",
                     "xsVariation", "xsFactors", "aT", "extraVars",
                     "weightedHistName", "unweightedHistName",
                     "minSumWeightIn", "maxSumWeightIn",
                     "llk", "whiteList", "exampleKargs",
                     "sigMcUnc", "binaryExclusion",
                     "flatEffUncRel",
                     ]+self._boxNames:
            setattr(self, "_"+item, eval(item))

    @property
    def name(self):
        out = self._dataset
        if self._tag:
            out += "_"+self._tag
        if self._com != 8:
            out += "_%d" % self._com
        return out

    @property
    def isSms(self):
        return not ("tanBeta" in self._dataset)

    @property
    def com(self):
        return self._com

    @property
    def interBin(self):
        return self._interBin

    @property
    def xsVariation(self):
        return self._xsVariation

    @property
    def xsFactors(self):
        return self._xsFactors

    @property
    def aT(self):
        return self._aT

    @property
    def extraVars(self):
        return self._extraVars

    @property
    def weightedHistName(self):
        return self._weightedHistName

    @property
    def unweightedHistName(self):
        return self._unweightedHistName

    @property
    def llk(self):
        return self._llk

    @property
    def whiteList(self):
        return self._whiteList

    @property
    def exampleKargs(self):
        return self._exampleKargs

    @property
    def sigMcUnc(self):
        return self._sigMcUnc

    @property
    def binaryExclusion(self):
        return self._binaryExclusion

    @property
    def flatEffUncRel(self):
        return self._flatEffUncRel

    def tags(self):
        out = [self.name]
        if not self.isSms:
            out.append(self.xsVariation)
        out += [self.llk] + self.whiteList
        return out

    def sumWeightInRange(self, sumWeightIn):
        out = True
        if self._minSumWeightIn is not None:
            out &= (self._minSumWeightIn <= sumWeightIn)
        if self._maxSumWeightIn is not None:
            out &= (sumWeightIn <= self._maxSumWeightIn)
        return out

    def boxes(self):
        out = []
        for boxName in self._boxNames:
            if getattr(self, "_" + boxName):
                out.append(boxName)
        return out
