import ROOT as r

class signal(dict) :
    def __init__(self, xs = None, label = "", effUncRel = None, lineColor = r.kPink+7, lineStyle = 1) :
        for item in ["xs", "label", "effUncRel", "lineColor", "lineStyle"] :
            assert eval(item)!=None,item
            setattr(self, item, eval(item))
    
    def insert(self, key = "", dct = {}) :
        self[key] = dct

    def keyPresent(self, key = "") :
        for dct in self.values() :
            for k in dct.keys() :
                if k==key : return True
        return False

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
