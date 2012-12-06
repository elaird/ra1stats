import collections,utils,signalAux,patches
import configuration as conf
import ROOT as r

##helper functions
def ratio(file, numDir, numHisto, denDir, denHisto) :
    f = r.TFile(file)
    assert not f.IsZombie(), file

    hOld = f.Get("%s/%s"%(numDir, numHisto))
    assert hOld,"%s:%s/%s"%(file, numDir, numHisto)
    h = hOld.Clone("%s_clone"%hOld.GetName())
    h.SetDirectory(0)
    h.Divide(f.Get("%s/%s"%(denDir, denHisto)))
    f.Close()
    return h

def oneHisto(file = "", dir = "", name = "") :
    f = r.TFile(file)
    assert not f.IsZombie(), file

    hOld = f.Get("%s/%s"%(dir, name))
    assert hOld,"%s/%s"%(dir, name)
    h = hOld.Clone("%s_clone"%hOld.GetName())
    h.SetDirectory(0)
    f.Close()
    return h

def checkHistoBinning(histoList = []) :
    def axisStuff(axis) :
        return (axis.GetXmin(), axis.GetXmax(), axis.GetNbins())

    def properties(histos) :
        out = collections.defaultdict(list)
        for h in histos :
            try:
                out["type"].append(type(h))
                out["x"].append(axisStuff(h.GetXaxis()))
                out["y"].append(axisStuff(h.GetYaxis()))
                out["z"].append(axisStuff(h.GetZaxis()))
            except AttributeError as ae :
                h.Print()
                raise ae
        return out

    for axis,values in properties(histoList).iteritems() :
        #print "Here are the %s binnings: %s"%(axis, str(values))
        sv = set(values)
        if len(sv)!=1 :
            print "The %s binnings do not match: %s"%(axis, str(values))
            for h in histoList :
                print h,properties([h])
            assert False

def modifyHisto(h = None, model = "") :
    fillPoints(h, points = patches.overwriteOutput()[model])
    killPoints(h, cutFunc = patches.cutFunc().get(model, None))

def fillPoints(h, points = []) :
    def avg(items) :
        out = sum(items)
        n = len(items) - items.count(0.0)
        if n : return out/n
        return None

    for point in points :
        if len(point)==3:
            iBinX,iBinY,iBinZ = point
            neighbors = "ewns"
        elif len(point)==4 :
            iBinX,iBinY,iBinZ,neighbors = point
        else :
            assert False,point

        valueOld = h.GetBinContent(iBinX, iBinY, iBinZ)

        items = []
        if ("w" in neighbors) and iBinX!=1             : items.append(h.GetBinContent(iBinX-1, iBinY  , iBinZ))
        if ("e" in neighbors) and iBinX!=h.GetNbinsX() : items.append(h.GetBinContent(iBinX+1, iBinY  , iBinZ))
        if ("n" in neighbors) and iBinY!=h.GetNbinsY() : items.append(h.GetBinContent(iBinX  , iBinY+1, iBinZ))
        if ("s" in neighbors) and iBinY!=1             : items.append(h.GetBinContent(iBinX  , iBinY-1, iBinZ))

        value = avg(items)
        if value!=None :
            h.SetBinContent(iBinX, iBinY, iBinZ, value)
            print "WARNING: histo %s bin (%3d, %3d, %3d) [%d zero neighbors]: %g has been overwritten with %g"%\
                  (h.GetName(), iBinX, iBinY, iBinZ, items.count(0.0), valueOld, value)

def killPoints(h, cutFunc = None) :
    for iBinX,x,iBinY,y,iBinZ,z in utils.bins(h, interBin = signalAux.interBin()) :
        if cutFunc and not cutFunc(iBinX,x,iBinY,y,iBinZ,z) : h.SetBinContent(iBinX, iBinY, iBinZ, 0.0)
    return h

##signal-related histograms
def xsHisto() :
    s = conf.switches()
    model = s["signalModel"]
    if s["binaryExclusionRatherThanUpperLimit"] :
        return xsHistoPhysical(model = model, cmssmProcess = "" if s["isSms"] else "total", xsVariation = s["xsVariation"])
    else :
        return xsHistoAllOne(model, cutFunc = patches.cutFunc()[model])

def xsHistoPhysical(model = "", cmssmProcess = "", xsVariation = "") :
    #get example histo and reset
    isSms = not cmssmProcess
    dummyHisto = "m0_m12_mChi_noweight" if isSms else "m0_m12_gg"
    s = signalAux.effHistoSpec(model = model, box = "had")
    out = ratio(s["file"], s["beforeDir"], dummyHisto, s["beforeDir"], dummyHisto)
    out.Reset()

    spec = signalAux.xsHistoSpec(model = model, cmssmProcess = cmssmProcess, xsVariation = xsVariation)
    assert spec["factor"]==1.0,"will need to accommodate factor of %g"%spec["factor"]
    h = oneHisto(spec["file"], "/", spec["histo"])
    assert h.ClassName()[:2]=="TH",h.ClassName()
    dim = int(h.ClassName()[2:3])
    assert dim in [1,2],dim

    for iX,x,iY,y,iZ,z in utils.bins(out, interBin = signalAux.interBin()) :
        iBin = h.FindBin(x) if dim==1 else h.FindBin(x,y)
        out.SetBinContent(iX, iY, iZ, h.GetBinContent(iBin))
    return out

def xsHistoAllOne(model, cutFunc = None) :
    ls = conf.likelihoodSpec()
    kargs = {} if ls._dataset=="2012ichep" else {"bJets":"eq0b", "jets":"le3j"}

    h = smsEffHisto(model = model, box = "had", scale = None,
                    htLower = 875, htUpper = None, **kargs)
    for iX,x,iY,y,iZ,z in utils.bins(h, interBin = signalAux.interBin()) :
        content = 1.0
        if cutFunc and not cutFunc(iX,x,iY,y,iZ,z) :
            content = 0.0
        h.SetBinContent(iX, iY, iZ, content)
    return h

def nEventsInHisto() :
    model = conf.switches()["signalModel"]
    s = signalAux.effHistoSpec(model = model, box = "had")
    return oneHisto(s["file"], s["beforeDir"], "m0_m12_mChi_noweight")

def effHisto(**args) :
    s = conf.switches()
    model = s["signalModel"]
    ignore = s["ignoreEff"]
    if (model in ignore) and (args["box"] in ignore[model]) :
        print "WARNING: ignoring %s efficiency for %s"%(args["box"], model)
        return None
    if not s["isSms"] :
        return cmssmEffHisto(model = model, xsVariation = s["xsVariation"], **args)
    else :
        return smsEffHisto(model = model, **args)

def cmssmEffHisto(**args) :
    s = signalAux.effHistoSpec(**args)
    out = None

    #Note! Implement some check of the agreement in sets of processes between yield file and xs file
    for proc in signalAux.processes() :
        h = ratio(s["file"], s["afterDir"], "m0_m12_%s"%proc, s["beforeDir"], "m0_m12_%s"%proc) #efficiency of a process
        h.Multiply(xsHistoPhysical(model = args["model"], cmssmProcess = proc, xsVariation = args["xsVariation"])) #weight by xs of the process
        if out is None : out = h.Clone("effHisto")
        else :           out.Add(h)
    out.SetDirectory(0)
    out.Divide(xsHistoPhysical(model = args["model"], cmssmProcess = "total", xsVariation = args["xsVariation"])) #divide by total xs
    return out

def smsEffHisto(**args) :
    switches = conf.switches()
    s = signalAux.effHistoSpec(**args)
    #out = ratio(s["file"], s["afterDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi")
    out = ratio(s["file"], s["afterDir"], "m0_m12_mChi_noweight", s["beforeDir"], "m0_m12_mChi_noweight")
    fillPoints(out, points = patches.overwriteInput()[switches["signalModel"]])
    return out

##signal point selection
def points() :
    out = []
    s = conf.switches()
    whiteList = s["whiteListOfPoints"]
    h = xsHisto()
    for iBinX,x,iBinY,y,iBinZ,z in utils.bins(h, interBin = signalAux.interBin()) :
        if whiteList and (x,y) not in whiteList : continue
        content = h.GetBinContent(iBinX, iBinY, iBinZ)
        if not content : continue
        if s["multiplesInGeV"] and ((x/s["multiplesInGeV"])%1 != 0.0) : continue
        if patches.cutFunc()[s['signalModel']](iBinX,x,iBinY,y,iBinZ,z):
            out.append( (iBinX, iBinY, iBinZ) )
    return out

##warnings
def printHoles(h) :
    for iBinX,x,iBinY,y,iBinZ,z in utils.bins(h, interBin = "Center") :
        xNeighbors = h.GetBinContent(iBinX+1, iBinY  , iBinZ)!=0.0 and h.GetBinContent(iBinX-1, iBinY  , iBinZ)
        yNeighbors = h.GetBinContent(iBinX  , iBinY+1, iBinZ)!=0.0 and h.GetBinContent(iBinX  , iBinY-1, iBinZ)
        if h.GetBinContent(iBinX, iBinY, iBinZ)==0.0 and (xNeighbors or yNeighbors) :
            print "WARNING: found hole (%d, %d, %d) = (%g, %g, %g)"%(iBinX, iBinY, iBinZ, x, y, z)
    return

def printMaxes(h) :
    s = conf.switches()
    for iBinX,x,iBinY,y,iBinZ,z in utils.bins(h, interBin = "Center") :
        if abs(h.GetBinContent(iBinX, iBinY, iBinZ)-s["masterSignalMax"])<2.0 :
            print "found max: (%d, %d, %d) = (%g, %g, %g)"%(iBinX, iBinY, iBinZ, x, y, z)
    return
