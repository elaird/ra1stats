import math


def quadSum(l) :
    return math.sqrt(sum([x**2 for x in l]))

def scaled(t, factor) :
    return tuple([factor*a if a!=None else None for a in t])

def excl(counts, isExclusive) :
    out = []
    for i,count,isExcl in zip(range(len(counts)), counts, isExclusive) :
        out.append(count if (isExcl or count==None) else (count-counts[i+1]))
    return tuple(out)

def itMult(l1 = [], l2 = []) :
    return tuple([a*b if a!=None else None for a,b in zip(l1,l2)])

def _trigKey(sample = "") :
    d = {"mcTtw":"had", "mcZinv":"had", "mcHad": "had",
         "mcMumu":"mumu", "mcMuon":"muon", "mcPhot":"phot",
         "mcSimple":"simple", # legacy for simple
         "mcZmumu":"mumu" # legacy for orig
         }
    if sample not in d :
        for key,value in d.iteritems() :
            if sample[:len(key)] == key :
                print "WARNING: using %s trigger efficiency for %s" % ( value, sample )
                return value
    return d[sample]


vars = ["htBinLowerEdges", "htMaxForPlot", "lumi", "htMeans", "systBins",
        "observations", "triggerEfficiencies", "mcStatError", "fixedParameters"]

class data(object) :
    def __init__(self, requireFullImplementation = True, systMode = 1) :
        self.requireFullImplementation = requireFullImplementation
        self.systMode = systMode
        self._fill()
        self._checkVars()
        self._checkLengths()
        self._applyTrigger()
        self._doBinMerge()

    def __str__(self, notes = False) :
        out = ""
        for func in ["observations", "mcExpectations", "mcStatError"] :
            out += "\n".join(["", func, "-"*20, ""])
            d = getattr(self, func)()
            for key in sorted(d.keys()) :
                out += "%s %s\n"%(key, d[key])
            if notes :
                out += r'''
NOTES
-----

- all numbers are after the trigger, i.e.
-- the observations are integers
-- the appropriate MC samples are scaled down to emulate trigger inefficiency
'''
        return out

    def translationFactor(self, tr = ["gZ", "muW", "mumuZ", "muHad"][0], considerLumi = False, afterTrigger = True) :
        dct = {"gZ":   {"num":"mcPhot", "den":"mcZinv"},
               "muW":  {"num":"mcMuon", "den":"mcTtw" },
               "mumuZ":{"num":"mcMumu", "den":"mcZinv"},
               "muHad":{"num":"mcMuon", "den":"mcHad" },
               }[tr]

        value = self.mcExpectations() if afterTrigger else self._mcExpectationsBeforeTrigger
        error = self.mcStatError()
        lumi = self.lumi()

        num = value[dct["num"]]
        den = value[dct["den"]]

        key = dct["num"]+"Err"
        if key in error :
            numErr = error[key]
        else :
            numErr = [0.0]*len(num)
            print "WARNING: no entry found for %s"%key

        key = dct["den"]+"Err"
        if key in error :
            denErr = error[key]
        else :
            denErr = [0.0]*len(den)
            print "WARNING: no entry found for %s"%key

        out = []
        scale = lumi["mcHad"]/lumi[dct["num"]] if considerLumi else 1.0
        for n,d in zip(num,den) :
            if (n is None or not d) :
                out.append(None)
            else :
                out.append(scale * n/d)

        outErr = []
        for n,d,nE,dE,o in zip(num,den,numErr,denErr,out) :
            if (None in [n,d,nE,dE,o]) or (not n) or (not d) :
                outErr.append(None)
            else :
                outErr.append(o*math.sqrt((nE/n)**2 + (dE/d)**2))
        return out,outErr

    def _fill(self) : raise Exception("NotImplemented", "Implement a member function _fill(self)")

    def _checkVars(self) :
        for item in vars+["mcExpectationsBeforeTrigger"] :
            assert hasattr(self, "_%s"%item),item

    def _checkLengths(self) :
        l = len(self._htBinLowerEdges)
        assert len(self._htMeans)==l
        
        for item in ["observations", "mcExpectationsBeforeTrigger", "mcStatError", "systBins", "triggerEfficiencies"] :
            length = self._mergeChecks() if (item=="systBins" and self._mergeBins) else l
            for key,value in getattr(self,"_%s"%item).iteritems() :
                assert len(value)==length,"%s['%s']: %d!=%d"%(item, key, len(value), length)

        for key,value in self._systBins.iteritems() :
            assert min(value)==0, "%s_%s"%(str(key), str(value))
            l = 1+max(value)
            assert key in self._fixedParameters, key
            assert len(self._fixedParameters[key])==l, key

    def _applyTrigger(self) :
        for s in ["mcExpectations"] :
            setattr(self, "_%s"%s, {})
            for sample,t in getattr(self, "_%sBeforeTrigger"%s).iteritems() :
                getattr(self, "_%s"%s)[sample] = itMult(t, self._triggerEfficiencies[_trigKey(sample)])

    def _mergeChecks(self) :
        assert len(self._mergeBins)==len(self._htBinLowerEdges)
        for a,b in zip(self._mergeBins, sorted(self._mergeBins)) :
            assert a==b,"A non-ascending mergeBins spec is not supported."

        s = set(self._mergeBins)
        assert s==set(range(len(s))),"Holes are not supported."
        return len(s)

    def _mergeHtMax(self, nBins) :
        if self._mergeBins.count(nBins-1)>1 :
            i = self._mergeBins.index(nBins-1)+1
            self._htMaxForPlot = self._htBinLowerEdges[i]

    def _mergeHtMeans(self, nBins) :
        newMeans = [0]*nBins
        nBulk = [0]*nBins
        for i,value in enumerate(self._htMeans) :
            bulk = self._observations["nHadBulk"][i]
            newMeans[self._mergeBins[i]] += value*bulk
            nBulk   [self._mergeBins[i]] +=       bulk

        for i in range(nBins) :
            newMeans[i] /= nBulk[i]
        self._htMeans = tuple(newMeans)

    def _mergeHtBinLowerEdges(self, nBins) :
        newBins = []
        for i in range(nBins) :
            htBinLowerIndex = list(self._mergeBins).index(i)
            newBins.append(self._htBinLowerEdges[htBinLowerIndex])
        self._htBinLowerEdges = tuple(newBins)

    def _mergeCounts(self, nBins, items = []) :
        for item in items :
            d = {}
            for key,t in getattr(self, "_%s"%item).iteritems() :
                d[key] = [0]*nBins
                for index,value in enumerate(t) :
                    if value==None :
                        d[key][self._mergeBins[index]] = None
                    else :
                        d[key][self._mergeBins[index]] += value

            for key,value in d.iteritems() :
                getattr(self, "_%s"%item)[key] = tuple(value)

    def _mergeErrors(self, nBins, items = []) :
        for item in items :
            d = {}
            for key,t in getattr(self, "_%s"%item).iteritems() :
                d[key] = [0]*nBins
                for index,value in enumerate(t) :
                    d[key][self._mergeBins[index]] += value*value
            for key,value in d.iteritems() :
                getattr(self, "_%s"%item)[key] = tuple(map(lambda x:math.sqrt(x), value))

    def _doBinMerge(self) :
        if self._mergeBins is None : return

        nBins = self._mergeChecks()
        self._mergeHtMax(nBins)
        self._mergeHtMeans(nBins)
        self._mergeHtBinLowerEdges(nBins)
        self._mergeCounts(nBins, items = ["observations", "mcExpectationsBeforeTrigger", "mcExpectations"])
        self._mergeErrors(nBins, items = ["mcStatError"])
        print "ERROR: Implement trigger efficiency merging."

    #define functions called by outside world
    for item in vars+["mcExpectations"] :
        exec('def %s(self) : return self._%s'%(item, item))

    def mergeEfficiency(self, inList) :
        mergeSpec = self.mergeBins()
        if not mergeSpec : return inList
        l = sorted(list(set(mergeSpec)))
        out = [0]*len(l)
        for index,value in enumerate(inList) :
            out[mergeSpec[index]] += value
        return out
