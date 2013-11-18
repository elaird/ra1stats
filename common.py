import ROOT as r

class signal(object):
    def __init__(self, xs=None, sumWeightIn=None, label="",
                 effUncRel=None, lineColor=r.kPink+7, lineStyle=2,
                 x=None, y=None,
                 ):

        # not checked
        for item in ["sumWeightIn", "x", "y"]:
            setattr(self, item, eval(item))

        for item in ["xs", "label", "effUncRel", "lineColor", "lineStyle"]:
            assert eval(item) != None, item
            setattr(self, item, eval(item))
        self.__selEffs = {}

    def effs(self, sel=""):
        return self.__selEffs.get(sel)

    def insert(self, key, value):
        self.__selEffs[key] = value

    def keyPresent(self, key=""):
        for dct in self.__selEffs():
            if key in dct.keys():
                return True
        return False

    def anyEffHad(self, key="effHadSum"):
        for dct in self.__selEffs.values():
            if dct.get(key):
                return True
        return False

    def __str__(self):
        out = []
        out.append("s = common.signal(xs=%g, sumWeightIn=%g, x=%s, y=%s)" %
                   (self.xs, self.sumWeightIn, self.x, self.y))
        for sel, dct in sorted(self.__selEffs.iteritems()):
            out.append('s.insert("%s", {' % sel)
            for key, value in sorted(dct.iteritems()):
                o = ('"%s":' % key).ljust(17)
                if type(value) is list:
                    s = ", ".join(["%8.2e" % x for x in value])
                    out.append('%s [%s],' % (o, s))
                else:
                    out.append('%s %g,' % (o, value))
            out.append("})")
        return "\n".join(out)

    def flattened(self):
        out = {}
        for item in ["xs", "x", "y", "sumWeightIn"]:
            out[item] = (getattr(self, item), '')

        for sel, dct in self.__selEffs.iteritems():
            for key, value in dct.iteritems():
                outKey = "%s_%s" % (sel, key)
                if type(value) in [float, int, bool]:
                    out[outKey] = (value, '')
                elif type(value) in [tuple, list]:
                    for i, x in enumerate(value):
                        out["%s_%d" % (outKey, i)] = (x, '')
                else:
                    assert False, type(value)
        return out


def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def floatingVars(w) :
    out = []
    vars = w.allVars()
    it = vars.createIterator()
    while it.Next() :
        if it.getMax()==r.RooNumber.infinity() : continue
        if it.getMin()==-r.RooNumber.infinity() : continue
        if not it.hasError() : continue

        d = {}
        d["name"] = it.GetName()
        d["value"] = it.getVal()
        d["error"] = it.getError()
        d["min"] = it.getMin()
        d["max"] = it.getMax()
        out.append(d)
    return out

def obs(w) :
    return w.set("obs")

def pdf(w) :
    return w.pdf("model")

def pseudoData(wspace, nToys) :
    out = []
    #make pseudo experiments with current parameter values
    dataset = pdf(wspace).generate(obs(wspace), nToys)
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        data = r.RooDataSet("pseudoData%d"%i, "title", argSet)
        data.add(argSet)
        out.append(data)
    return out

def ni(name = "", label = "", i = None) :
    out = name
    if label : out += "_%s"%label
    if i!=None : out +="_%d"%i
    return out

def sampleCode(samples) :
    yes = []
    no = []
    for box,considerSignal in samples.iteritems() :
        (yes if considerSignal else no).append(box)

    d = {"had":"h", "phot":"p", "muon":"1", "mumu":"2", "simple":"s"}
    out = ""
    for item in yes :
        out+=d[item]
    if no :
        out += "x"
        for item in no : out+=d[item]
    return out

def note(likelihoodSpec = {}) :
    l = likelihoodSpec
    out = "%s_"%l._dataset
    
    if l.REwk() : out += "REwk%s_"%l.REwk()
    out += "RQcd%s"%l.RQcd()
    if l.constrainQcdSlope() : out += "Ext"

    out += "_fZinv%s"%l.nFZinv()
    if not l.standardPoi() :  out += "_poi__%s"%("__".join(l.poiList()))

    for selection in l.selections() :
        out += "_%s-%s"%(selection.name, sampleCode(selection.samplesAndSignalEff))
    return out

def split(key) :
    try:
        fields = key.split("_")
        if len(fields)==4 :
            sample,nB,nJ,iHt = fields
        else :
            assert False,"unsupported length %d"%len(fields)
        return sample,nB,nJ,iHt
    except:
        assert False,"Could not split key %s"%key
