import ROOT as r


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
