import ROOT as r

class signal(dict) :
    def __init__(self, xs = None, label = "") :
        for item in ["xs", "label"] :
            assert item
            setattr(self, item, eval(item))
    
    def insert(self, key = "", dct = {}) :
        self[key] = dct

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def obs(w) :
    return w.set("obs")

def pdf(w) :
    return w.pdf("model")

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

    d = {"had":"h", "phot":"p", "muon":"1", "mumu":"2"}
    out = ""
    for item in yes :
        out+=d[item]
    if no :
        out += "x"
        for item in no : out+=d[item]
    return out

def note(likelihoodSpec = {}) :
    l = likelihoodSpec
    out = ""
    if l["simpleOneBin"] : return "simpleOneBin"
    
    if l["REwk"] : out += "REwk%s_"%l["REwk"]
    out += "RQcd%s"%l["RQcd"]
    if l["constrainQcdSlope"] : out += "Ext"

    out += "_fZinv%s"%l["nFZinv"]
    if not l.standardPoi() :  out += "_poi__%s"%("__".join(l["poi"].keys()))

    for selection in l["selections"] :
        out += "_%s-%s"%(selection.name, sampleCode(selection.samplesAndSignalEff))
    return out
