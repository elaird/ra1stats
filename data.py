import math,copy

def scaled(t, factor) :
    return tuple([factor*a if a!=None else None for a in t])

def trig(t, eff) :
    return tuple([a*b if a!=None else None for a,b in zip(t,eff)])

def excl(counts, isExclusive) :
    out = []
    for i,count,isExcl in zip(range(len(counts)), counts, isExclusive) :
        out.append(count if (isExcl or count==None) else (count-counts[i+1]))
    return tuple(out)

vars = ["mergeBins", "constantMcRatioAfterHere", "htBinLowerEdges", "htMaxForPlot", "lumi", "htMeans", "systBins",
        "observations", "triggerEfficiencies", "purities", "mcExpectations", "mcExtra", "mcStatError", "fixedParameters"]

class data(object) :
    def __init__(self, requireFullImplementation = True, systMode = 1) :
        self.requireFullImplementation = requireFullImplementation
        self.systMode = systMode
        self._fill()
        self._checkVars()
        self._checkLengths()
        self._stashInput()
        self._doBinMerge()

    def _fill(self) : raise Exception("NotImplemented", "Implement a member function _fill(self)")

    def _checkVars(self) :
        for item in vars :
            assert hasattr(self, "_%s"%item),item

    def _checkLengths(self) :
        l = len(self._htBinLowerEdges)
        assert len(self._htMeans)==l
        
        if not self._mergeBins :
            assert len(self._constantMcRatioAfterHere)==l
            
        for item in ["observations", "mcExpectations", "mcExtra", "mcStatError", "systBins"] :
            for key,value in getattr(self,"_%s"%item).iteritems() :
                assert len(value)==l,"%s: %s"%(item, key)

        for key,value in self._systBins.iteritems() :
            assert min(value)==0, "%s_%s"%(str(key), str(value))
            l = 1+max(value)
            assert key in self._fixedParameters, key
            assert len(self._fixedParameters[key])==l, key

    def _stashInput(self) :
        self._htBinLowerEdgesInput = copy.copy(self._htBinLowerEdges)

    def _doBinMerge(self) :
        if self._mergeBins is None : return
        assert len(self._mergeBins)==len(self._htBinLowerEdges)
        for a,b in zip(self._mergeBins, sorted(self._mergeBins)) :
            assert a==b,"A non-ascending mergeBins spec is not supported."

        l = sorted(list(set(self._mergeBins)))
        assert len(l)==len(self._constantMcRatioAfterHere),"wrong length of _constantMcRatioAfterHere when using _mergeBins"
        for a,b in zip(l, range(len(l))) :
            assert a==b, "Holes are not allowed."

        #adjust HT means (before the others are adjusted)
        newMeans = [0]*len(l)
        nBulk = [0]*len(l)
        for index,value in enumerate(self._htMeans) :
            newMeans[self._mergeBins[index]] += value*self._observations["nHadBulk"][index]
            nBulk   [self._mergeBins[index]] +=       self._observations["nHadBulk"][index]
        for i in range(len(l)) :
            newMeans[i] /= nBulk[i]
        self._htMeans = newMeans

        #adjust self._htBinLowerEdges
        newBins = []
        for index in range(len(l)) :
            htBinLowerIndex = list(self._mergeBins).index(index)
            newBins.append(self._htBinLowerEdges[htBinLowerIndex])
        self._htBinLowerEdges = tuple(newBins)

        #adjust count dictionaries
        for item in ["observations", "mcExpectations", "mcExtra"] :
            d = {}
            for key,t in getattr(self, "_%s"%item).iteritems() :
                d[key] = [0]*len(l)
                for index,value in enumerate(t) :
                    d[key][self._mergeBins[index]]+=value
            for key,value in d.iteritems() :
                getattr(self, "_%s"%item)[key] = tuple(value)

        #adjust errors
        for item in ["mcStatError"] :
            d = {}
            for key,t in getattr(self, "_%s"%item).iteritems() :
                d[key] = [0]*len(l)
                for index,value in enumerate(t) :
                    d[key][self._mergeBins[index]] += value*value
            for key,value in d.iteritems() :
                getattr(self, "_%s"%item)[key] = tuple(map(lambda x:math.sqrt(x), value))

        if self.requireFullImplementation :
            assert False,"Implement trigger efficiency merging."
            assert False,"Implement purity merging."
            assert False,"Implement sigEffCorr merging."
        else :
            print "WARNING: Purity merging is not implemented.  Results are nonsense."
            print "WARNING: Trigger efficiency merging is not implemented.  Results are nonsense."
            print "WARNING: Signal efficiency correction merging is not implemented.  Results are nonsense."
        return

    #define functions called by outside world
    for item in vars+["htBinLowerEdgesInput"] :
        exec('def %s(self) : return self._%s'%(item, item))

    def mergeEfficiency(self, inList) :
        mergeSpec = self.mergeBins()
        if not mergeSpec : return inList
        l = sorted(list(set(mergeSpec)))
        out = [0]*len(l)
        for index,value in enumerate(inList) :
            out[mergeSpec[index]] += value
        return out
