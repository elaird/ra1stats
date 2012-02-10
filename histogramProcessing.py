import collections
import configuration as conf
import histogramSpecs as hs
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

def oneHisto(file, dir, name) :
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
        if len(set(values))!=1 :
            print "The %s binnings do not match: %s"%(axis, str(values))
            for h in histoList :
                print h,properties([h])
            assert False

def fillPoints(h, points = []) :
    def avg(items) :
        out = sum(items)
        n = len(items) - items.count(0.0)
        if n : return out/n
        return None

    for point in points :
        iBinX,iBinY,iBinZ = point
        valueOld = h.GetBinContent(iBinX, iBinY, iBinZ)
        
        items = []
        if iBinX!=1             : items.append(h.GetBinContent(iBinX-1, iBinY  , iBinZ))
        if iBinX!=h.GetNbinsX() : items.append(h.GetBinContent(iBinX+1, iBinY  , iBinZ))
        if iBinY!=h.GetNbinsY() : items.append(h.GetBinContent(iBinX  , iBinY+1, iBinZ))
        if iBinY!=1             : items.append(h.GetBinContent(iBinX  , iBinY-1, iBinZ))

        value = avg(items)
        if value!=None :
            h.SetBinContent(iBinX, iBinY, iBinZ, value)
            print "WARNING: histo %s bin (%3d, %3d, %3d) [%d zero neighbors]: %g has been overwritten with %g"%\
                  (h.GetName(), iBinX, iBinY, iBinZ, items.count(0.0), valueOld, value)
        
def killPoints(h, cutFunc = None) :
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinLowEdge(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = h.GetYaxis().GetBinLowEdge(iBinY)
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                z = h.GetZaxis().GetBinLowEdge(iBinZ)
                if cutFunc and not cutFunc(iBinX,x,iBinY,y,iBinZ,z) : h.SetBinContent(iBinX, iBinY, iBinZ, 0.0)
    return h

##signal-related histograms
def xsHisto() :
    s = conf.switches()
    model = s["signalModel"]
    if not s["isSms"] : return cmssmNloXsHisto(model) if s["nlo"] else cmssmLoXsHisto(model)
    else : return smsXsHisto(model, cutFunc = s["smsCutFunc"][s["signalModel"]])

def nEventsInHisto() :
    s = conf.switches()
    model = s["signalModel"]
    return cmssmNEventsInHisto(model) if not s["isSms"] else smsNEventsInHisto(model)

def effHisto(**args) :
    s = conf.switches()
    model = s["signalModel"]
    if not s["isSms"] : return cmssmNloEffHisto(model = model, **args) if s["nlo"] else cmssmLoEffHisto(model = model, **args)
    else : return smsEffHisto(model = model, **args)

def cmssmNEventsInHisto(model, box = "had", scale = "1") :
    s = hs.histoSpec(model = model, box = box, scale = scale)
    return oneHisto(s["file"], s["beforeDir"], "m0_m12_mChi_noweight")

def cmssmLoXsHisto(model) :
    s = hs.histoSpec(model = model, box = "had", scale = "1")
    out = ratio(s["file"], s["beforeDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi_noweight")
    out.Scale(conf.switches()["icfDefaultNEventsIn"]/conf.switches()["icfDefaultLumi"])
    #mData = mEv.GetSusyCrossSection()*mDesiredLumi/10000;
    #http://svnweb.cern.ch/world/wsvn/icfsusy/trunk/AnalysisV2/framework/src/common/Compute_Helpers.cc
    #http://svnweb.cern.ch/world/wsvn/icfsusy/trunk/AnalysisV2/hadronic/src/common/mSuGraPlottingOps.cc
    return out

def cmssmLoEffHisto(**args) :
    s = hs.histoSpec(**args)
    out = ratio(s["file"], s["afterDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi")
    return out

def cmssmNloXsHisto(model, scale = "1") :
    s = hs.histoSpec(model = model, box = "had", scale = scale)
    out = None
    for process in conf.processes() :
        h = ratio(s["file"], s["beforeDir"], "m0_m12_%s"%process, s["beforeDir"], "m0_m12_%s_noweight"%process)
        if out is None : out = h.Clone("nloXsHisto")
        else :           out.Add(h)
    out.SetDirectory(0)
    #see links in loXsHisto
    return out

def cmssmNloEffHisto(**args) :
    s = hs.histoSpec(**args)
    out = None
    for process in conf.processes() :
        h = ratio(s["file"], s["afterDir"], "m0_m12_%s"%process, s["beforeDir"], "m0_m12_%s_noweight"%process) #eff weighted by xs
        if out is None : out = h.Clone("nloEffHisto")
        else :           out.Add(h)
    out.SetDirectory(0)
    out.Divide(cmssmNloXsHisto(model = args["model"], scale = args["scale"])) #divide by total xs
    return out

def smsXsHisto(model, cutFunc = None) :
    h = smsEffHisto(model = model, box = "had", scale = None,
                    htLower = 875, htUpper = None,
                    alphaTLower = "55", alphaTUpper = None)
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinLowEdge(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = h.GetYaxis().GetBinLowEdge(iBinY)
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                z = h.GetZaxis().GetBinLowEdge(iBinZ)
                if cutFunc and not cutFunc(iBinX,x,iBinY,y,iBinZ,z) : continue
                h.SetBinContent(iBinX, iBinY, iBinZ, 1.0)
    return h

def smsNEventsInHisto(model) :
    s = hs.histoSpec(model = model, box = "had", htLower = 875, htUpper = None)
    return oneHisto(s["file"], s["beforeDir"], "m0_m12_mChi_noweight")

def smsEffHisto(**args) :
    switches = conf.switches()
    s = hs.histoSpec(**args)
    #out = ratio(s["file"], s["afterDir"], "m0_m12_mChi", s["beforeDir"], "m0_m12_mChi")
    out = ratio(s["file"], s["afterDir"], "m0_m12_mChi_noweight", s["beforeDir"], "m0_m12_mChi_noweight")
    fillPoints(out, points = switches["overwriteInput"][switches["signalModel"]])
    return out

##signal point selection
def fullPoints() :
    out = []
    s = conf.switches()
    h = xsHisto()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        if "xWhiteList" in s and s["xWhiteList"] and iBinX not in s["xWhiteList"] : continue
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                content = h.GetBinContent(iBinX, iBinY, iBinZ)
                min = s["minSignalXsForConsideration"]
                max = s["maxSignalXsForConsideration"]
                if min!=None and content<min : continue
                if max!=None and content>max : continue
                if s["fiftyGeVStepsOnly"] and ((h.GetXaxis().GetBinLowEdge(iBinX)/50.0)%1 != 0.0) : continue
                out.append( (iBinX, iBinY, iBinZ) )
    return out

def points() :
    p = conf.switches()["listOfTestPoints"]
    if p : return p
    return fullPoints()

##warnings
def printHoles(h) :
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                xNeighbors = h.GetBinContent(iBinX+1, iBinY  , iBinZ)!=0.0 and h.GetBinContent(iBinX-1, iBinY  , iBinZ)
                yNeighbors = h.GetBinContent(iBinX  , iBinY+1, iBinZ)!=0.0 and h.GetBinContent(iBinX  , iBinY-1, iBinZ)
                if h.GetBinContent(iBinX, iBinY, iBinZ)==0.0 and (xNeighbors or yNeighbors) :
                    print "found hole: (%d, %d, %d) = (%g, %g, %g)"%(iBinX, iBinY, iBinZ,
                                                                     h.GetXaxis().GetBinCenter(iBinX),
                                                                     h.GetYaxis().GetBinCenter(iBinY),
                                                                     h.GetZaxis().GetBinCenter(iBinZ))
    return
    
def printMaxes(h) :
    s = conf.switches()
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                if abs(h.GetBinContent(iBinX, iBinY, iBinZ)-s["masterSignalMax"])<2.0 :
                    print "found max: (%d, %d, %d) = (%g, %g, %g)"%(iBinX, iBinY, iBinZ,
                                                                    h.GetXaxis().GetBinCenter(iBinX),
                                                                    h.GetYaxis().GetBinCenter(iBinY),
                                                                    h.GetZaxis().GetBinCenter(iBinZ))
    return
