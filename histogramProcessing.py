import configuration.limit
import configuration.signal
import likelihood
import patches
import utils

import ROOT as r


##helper functions
def ratio(file, numDir, numHisto, denDir, denHisto):
    f = r.TFile(file)
    assert not f.IsZombie(), file

    hOld = f.Get("%s/%s" % (numDir, numHisto))
    assert hOld, "%s:%s/%s" % (file, numDir, numHisto)
    h = hOld.Clone("%s_clone" % hOld.GetName())
    h.SetDirectory(0)
    h.Divide(f.Get("%s/%s" % (denDir, denHisto)))
    f.Close()
    return h


def oneHisto(file="", dir="", name=""):
    f = r.TFile(file)
    assert not f.IsZombie(), file

    key = "%s/%s" % (dir, name) if dir else name
    hOld = f.Get(key)
    assert hOld, key
    h = hOld.Clone("%s_clone" % hOld.GetName())
    h.SetDirectory(0)
    f.Close()
    return h


def setRange(var, model, histo, axisString):

    ranges = configuration.signal.ranges(model.name)
    if var not in ranges:
        return
    nums = ranges[var]
    axis = getattr(histo, "Get%saxis" % axisString)()
    axis.SetRangeUser(*nums[:2])
    if len(nums) == 3:
        r.gStyle.SetNumberContours(nums[2])
    if axisString == "Z":
        maxContent = histo.GetBinContent(histo.GetMaximumBin())
        if maxContent > nums[1]:
            print " ".join(["ERROR: histo truncated in Z",
                            "(maxContent = %g," % maxContent,
                            "maxSpecified = %g)" % nums[1],
                            histo.GetName()])

    divKey = axisString.lower()+"Divisions"
    if ranges.get(divKey):
        axis.SetNdivisions(*ranges[divKey])


def modifiedHisto(h3=None,
                  model=None,
                  shiftX=False,#None,
                  shiftY=False,#None,
                  shiftErrors=True,
                  range=None,
                  info=True,
                  ):
    for arg in ["shiftX", "shiftY", "shiftErrors", "range"]:
        value = eval(arg)
        assert type(value) is bool, "(%s is %s)" % (arg, type(value))

    h = utils.shifted(utils.threeToTwo(h3),
                      shift=(shiftX, shiftY),
                      shiftErrors=shiftErrors,
                      info=info)
    fillPoints(h, points=patches.overwriteOutput().get(model.name, []), info=info)
    killPoints(h, model)

    if range:
        setRange("xRange", model, h, "X")
        setRange("yRange", model, h, "Y")

    return h


def fillPoints(h, points=[], info=True):
    def avg(items):
        out = sum(items)
        n = len(items) - items.count(0.0)
        if n:
            return out/n
        return None

    for point in points:
        if len(point) == 3:
            iBinX, iBinY, iBinZ = point
            neighbors = "ewns"
        elif len(point) == 4:
            iBinX, iBinY, iBinZ, neighbors = point
        else:
            assert False, point

        valueOld = h.GetBinContent(iBinX, iBinY, iBinZ)

        items = []
        if ("w" in neighbors) and iBinX != 1:
            items.append(h.GetBinContent(iBinX-1, iBinY, iBinZ))

        if ("e" in neighbors) and iBinX != h.GetNbinsX():
            items.append(h.GetBinContent(iBinX+1, iBinY, iBinZ))

        if ("n" in neighbors) and iBinY != h.GetNbinsY():
            items.append(h.GetBinContent(iBinX, iBinY+1, iBinZ))

        if ("s" in neighbors) and iBinY != 1:
            items.append(h.GetBinContent(iBinX, iBinY-1, iBinZ))

        value = avg(items)
        if value is not None:
            h.SetBinContent(iBinX, iBinY, iBinZ, value)
            out = "INFO: histo %s bin (%3d, %3d, %3d)" % (h.GetName(),
                                                          iBinX,
                                                          iBinY,
                                                          iBinZ,
                                                          )
            out += "[%d zero neighbors]: %g has been overwritten with %g" % \
                   (items.count(0.0), valueOld, value)
            if info:
                print out


def killPoints(h,model=None) :
    cutFunc=patches.cutFunc().get(model.name, None)
    interBin=model.interBin
    for iBinX, x, iBinY, y, iBinZ, z in utils.bins(h, interBin=interBin):
        if cutFunc and not cutFunc(iBinX, x, iBinY, y, iBinZ, z) and \
               model.region and not model.region(iBinX, x, iBinY, y, iBinZ, z):
            h.SetBinContent(iBinX, iBinY, iBinZ, 0.0)
    return h


##signal-related histograms
def xsHisto(model=None):
    if model.binaryExclusion:
        cmssmProcess = "" if model.isSms else "total"
        return xsHistoPhysical(model=model, cmssmProcess=cmssmProcess)
    else:
        return xsHistoAllOne(model=model)


def xsHistoPhysical(model=None, cmssmProcess=""):
    #get example histo and reset
    dummyHisto = model.weightedHistName
    s = configuration.signal.effHistoSpec(model=model, box="had")
    out = ratio(s["file"],
                s["beforeDir"], dummyHisto,
                s["beforeDir"], dummyHisto)
    out.Reset()

    spec = configuration.signal.xsHistoSpec(model=model, cmssmProcess=cmssmProcess)

    h = oneHisto(spec["file"], "/", spec["histo"])
    assert h.ClassName()[:2] == "TH", h.ClassName()
    dim = int(h.ClassName()[2:3])
    assert dim in [1, 2], dim

    for iX, x, iY, y, iZ, z in utils.bins(out, interBin=model.interBin):
        iBin = h.FindBin(x) if dim == 1 else h.FindBin(x, y)
        out.SetBinContent(iX, iY, iZ, h.GetBinContent(iBin))

    assert len(model.xsFactors) == 1, model.xsFactors
    out.Scale(model.xsFactors[0])

    return out


def xsHistoAllOne(model=None):
    cutFunc=patches.cutFunc().get(model.name,None)
    spec = configuration.signal.effHistoSpec(model=model, **model.exampleKargs)
    h = smsEffHisto(spec=spec, model=model)
    for iX, x, iY, y, iZ, z in utils.bins(h, interBin=model.interBin):
        content = 1.0
        if cutFunc and not cutFunc(iX, x, iY, y, iZ, z) and \
               model.region and not model.region(iX, x, iY, y, iZ, z):
            content = 0.0
        h.SetBinContent(iX, iY, iZ, content)
    return h


def sumWeightInHisto(model=None):
    s = configuration.signal.effHistoSpec(model=model, box="had")
    return oneHisto(s["file"], s["beforeDir"], s["weightedHistName"])


def effUncRelHisto(model=None, box="had", bJets="", jets=""):
    s = configuration.signal.effUncRelHistoSpec(model=model,
                                                box=box,
                                                bJets=bJets,
                                                jets=jets)
    return oneHisto(s["file"], s["histDir"], s["effUncRelHistName"])


def effHisto(model=None, box="",
             htLower=None, htUpper=None,
             bJets="", jets=""):
    spec = configuration.signal.effHistoSpec(model=model,
                                             box=box,
                                             htLower=htLower,
                                             htUpper=htUpper,
                                             bJets=bJets,
                                             jets=jets)
    if model.isSms:
        return smsEffHisto(spec=spec, model=model)
    else:
        return cmssmEffHisto(spec=spec, model=model)


def meanWeightSigMc(model=None, box="",
                    htLower=None, htUpper=None,
                    bJets="", jets=""):
    spec = configuration.signal.effHistoSpec(model=model,
                                             box=box,
                                             htLower=htLower,
                                             htUpper=htUpper,
                                             bJets=bJets,
                                             jets=jets)
    assert model.isSms
    return ratio(spec["file"],
                 spec["afterDir"], spec["weightedHistName"],
                 spec["afterDir"], spec["unweightedHistName"])


def nEventsSigMc(model=None, box="",
                 htLower=None, htUpper=None,
                 bJets="", jets=""):
    spec = configuration.signal.effHistoSpec(model=model,
                                             box=box,
                                             htLower=htLower,
                                             htUpper=htUpper,
                                             bJets=bJets,
                                             jets=jets)
    assert model.isSms
    return oneHisto(spec["file"], spec["afterDir"], spec["unweightedHistName"])


def cmssmEffHisto(spec={}, model=None):
    out = None

    # FIXME: Implement some check of the agreement
    # in sets of processes between yield file and xs file
    for proc in configuration.signal.processes():
        # efficiency of a process
        h = ratio(spec["file"],
                  spec["afterDir"], "m0_m12_%s" % proc,
                  spec["beforeDir"], "m0_m12_%s" % proc)

        # weight by xs of the process
        h.Multiply(xsHistoPhysical(model=model, cmssmProcess=proc))

        if out is None:
            out = h.Clone("effHisto")
        else:
            out.Add(h)

    out.SetDirectory(0)
    # divide by total xs
    out.Divide(xsHistoPhysical(model=model, cmssmProcess="total"))
    return out


def smsEffHisto(spec={}, model=None):
    out = ratio(spec["file"],
                spec["afterDir"], spec["weightedHistName"],
                spec["beforeDir"], spec["weightedHistName"])
    return out


def perSelHistos(model=None, htThresholds=None, jets="", bJets=""):
    d = {}
    for box in model.boxes():
        Box = box.capitalize()
        itemFunc = {"eff%s" % Box: effHisto}
        if model.sigMcUnc:
            itemFunc["meanWeightSigMc%s" % Box] = meanWeightSigMc
            itemFunc["nEventsSigMc%s" % Box] = nEventsSigMc
        for item, func in itemFunc.iteritems():
            d[item] = [func(model=model,
                            box=box,
                            htLower=l,
                            htUpper=u,
                            bJets=bJets,
                            jets=jets,
                            ) for l, u in htThresholds]
    return d


def perSelHisto(model=None, jets="", bJets=""):
    print "FIXME: Signal Unc. for muon"
    for box in model.boxes():
        assert box == "had", " %s signal systematic not yet implemented" % box
        d = effUncRelHisto(model=model,
                           box=box,
                           bJets=bJets,
                           jets=jets,
                           )
        return d


def effHistos(model=None, allCategories=False):
    out = {}
    for sel in likelihood.spec(name=model.llk).selections():
        if (not allCategories) and (sel.name not in model.whiteList):
            continue
        bins = sel.data.htBinLowerEdges()
        htThresholds = zip(bins, list(bins[1:])+[None])
        out[sel.name] = perSelHistos(model=model,
                                     htThresholds=htThresholds,
                                     jets=sel.jets,
                                     bJets=sel.bJets)
    return out


def effUncRelHistos(model=None, allCategories=False):
    out = {}
    for sel in likelihood.spec(name=model.llk).selections():
        if (not allCategories) and (sel.name not in model.whiteList):
            continue
        out[sel.name] = perSelHisto(model=model,
                                    jets=sel.jets,
                                    bJets=sel.bJets)
    return out


##signal point selection
def points(respectWhiteList=False):
    out = []
    multiples = configuration.limit.multiplesInGeV()

    for model in configuration.signal.models():
        whiteList = configuration.signal.whiteListOfPoints(model.name, respect=respectWhiteList)
        h = sumWeightInHisto(model)
        bins = utils.bins(h, interBin=model.interBin)
        for iBinX, x, iBinY, y, iBinZ, z in bins:
            if whiteList and (x, y) not in whiteList:
                continue
            content = h.GetBinContent(iBinX, iBinY, iBinZ)
            if not model.sumWeightInRange(content):
                continue
            if multiples and ((x/multiples) % 1 != 0.0):
                continue
            cutFunc = patches.cutFunc().get(model.name,None)
            if cutFunc and cutFunc(iBinX, x, iBinY, y, iBinZ, z) and \
                   model.region and model.region(iBinX, x, iBinY, y, iBinZ, z):
                out.append((model.name, iBinX, iBinY, iBinZ))
    return out


##warnings
def printHoles(h):
    for iBinX, x, iBinY, y, iBinZ, z in utils.bins(h, interBin="Center"):
        xNeighbors = h.GetBinContent(iBinX+1, iBinY,   iBinZ)
        xNeighbors *= h.GetBinContent(iBinX-1, iBinY,   iBinZ)
        yNeighbors = h.GetBinContent(iBinX,   iBinY+1, iBinZ)
        yNeighbors *= h.GetBinContent(iBinX,   iBinY-1, iBinZ)
        empty = h.GetBinContent(iBinX, iBinY, iBinZ) == 0.0
        if empty and (xNeighbors or yNeighbors):
            print "WARNING: found hole (%d, %d, %d) = (%g, %g, %g)" % (iBinX,
                                                                       iBinY,
                                                                       iBinZ,
                                                                       x, y, z)
    return
