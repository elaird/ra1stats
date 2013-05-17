import collections
import configuration.signal
import ROOT as r


def refXsHisto(model=None):
    hs = configuration.signal.xsHistoSpec(model=model)
    f = r.TFile(hs["file"])
    h = f.Get(hs["histo"])
    if not h:
        print "Could not find %s: available are these:" % hs["histo"]
        f.ls()
        assert False
    out = h.Clone("%s_clone" % hs["histo"])
    out.SetDirectory(0)
    f.Close()
    return out


def mDeltaFuncs(mDeltaMin=None, mDeltaMax=None, nSteps=None, mGMax=None):
    out = []
    for iStep in range(1+nSteps):
        mDelta = mDeltaMin + (mDeltaMax - mDeltaMin)*(iStep+0.0)/nSteps
        out.append(r.TF1("ml_vs_mg_%d" % iStep,
                         "sqrt(x*x-x*(%g))" % mDelta,
                         mDelta,
                         mGMax)
                   )

    for f in out:
        f.SetLineWidth(1)
        f.SetNpx(1000)
        f.SetLineColor(r.kBlack)

    return out


def binWidth(h, axisString):
    a = getattr(h, "Get%saxis" % axisString)()
    return (a.GetXmax()-a.GetXmin())/getattr(h, "GetNbins%s" % axisString)()


def allMatch(value, y, threshold, iStart, N):
    count = 0
    for i in range(iStart, N):
        if abs(y[i]-value) < threshold:
            count += 1
    return count == (N-iStart)


def content(h=None, coords=(0.0,), variation=0.0, factor=1.0):
    assert h.ClassName()[:2] == "TH"
    dim = int(h.ClassName()[2])
    args = tuple(coords[:dim])
    bin = h.FindBin(*args)
    return factor*(h.GetBinContent(bin) + variation*h.GetBinError(bin))


def excludedGraph(h, xsFactor=None, variation=0.0, model=None,
                  interBin="", prune=False):
    assert interBin in ["Center", "LowEdge"], interBin

    def fail(xs, xsLimit):
        return (xs <= xsLimit) or not xsLimit

    whiteList = configuration.signal.whiteListOfPoints(model.name)
    refHisto = refXsHisto(model)
    d = collections.defaultdict(list)
    for iBinX in range(1, 1+h.GetNbinsX()):
        x = getattr(h.GetXaxis(), "GetBin%s" % interBin)(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()):
            y = getattr(h.GetYaxis(), "GetBin%s" % interBin)(iBinY)
            xs = content(h=refHisto, coords=(x, y),
                         variation=variation, factor=xsFactor)
            if not xs:
                continue
            if (x, y) in whiteList:
                xsPlain = content(h=refHisto, coords=(x, y))
                print ("x=%g, y=%g, " % (x, y) +
                       "xs(plain) = %g, " % xsPlain +
                       "xs(factor %g, variation %s) = %g" % (xsFactor,
                                                             variation,
                                                             xs)
                       )
            xsLimit = h.GetBinContent(iBinX, iBinY)
            xsLimitPrev = h.GetBinContent(iBinX, iBinY-1)
            xsLimitNext = h.GetBinContent(iBinX, iBinY+1)
            passed = not fail(xs, xsLimit)
            otherFailed = fail(xs, xsLimitPrev) or fail(xs, xsLimitNext)
            transition = passed and otherFailed
            if transition:
                d[x].append(y)
        if len(d[x]) == 1:
            print "INFO: %s (factor %g) hit " % (h.GetName(), xsFactor) + \
                  "iBinX = %d (x = %g), y = %g repeated" % (iBinX, x, d[x][0])
            d[x].append(d[x][0])

    l1 = []
    l2 = []
    for x in sorted(d.keys()):
        values = sorted(d[x])
        values.reverse()
        if prune:
            values = [values[0], values[-1]]

        l1 += [(x, y) for y in values[:-1]]
        l2 += [(x, y) for y in values[-1:]]
    l2.reverse()

    out = r.TGraph()
    out.SetName("%s_graph" % h.GetName())
    for i, t in enumerate(l1+l2):
        out.SetPoint(i, *t)

    return out


def exclHisto(h, xsFactor=None, model=None, interBin="", variation=0.0,
              tag="", zTitle="", func=lambda xsLimit, xs: 0.0):
    assert interBin in ["Center", "LowEdge"], interBin
    cutFunc = None
    refHisto = refXsHisto(model)
    out = h.Clone(h.GetName()+tag)
    out.Reset()
    out.GetZaxis().SetTitle(zTitle)
    for iBinX in range(1, 1+h.GetNbinsX()):
        x = getattr(h.GetXaxis(), "GetBin%s" % interBin)(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()):
            y = getattr(h.GetYaxis(), "GetBin%s" % interBin)(iBinY)
            xsLimit = h.GetBinContent(iBinX, iBinY)
            if not xsLimit:
                continue
            if cutFunc and not cutFunc(iBinX, x, iBinY, y, 1, 0.0):
                continue
            xs = content(h=refHisto, coords=(x, y),
                         variation=variation, factor=xsFactor)
            if not xs:
                continue
            out.SetBinContent(iBinX, iBinY, func(xsLimit, xs))
    return out


def reordered(inGraph, xsFactor):
    def truncated(gr):
        N = gr.GetN()
        if N % 2:
            out = r.TGraph()
            out.SetName("%s_truncated" % gr.GetName())
            x = gr.GetX()
            y = gr.GetY()
            for i in range(N-1):
                out.SetPoint(i, x[i], y[i])
            print "ERROR: discarded from graph %s " % (gr.GetName(),) + \
                  " (factor %g) the point " % (xsFactor,) + \
                  "%d, %g, %g" % (N-1, x[N-1], y[N-1])
            return out
        else:
            return gr

    g = truncated(inGraph)
    N = g.GetN()
    l1 = []
    l2 = []
    for i in range(N/2):
        j = 2*i+1
        l1.append(j)
        l2.append(N-j-1)

    gOut = r.TGraph()
    #e.g., 1,3,5,7,6,4,2,0
    #print l1+l2
    for i, j in enumerate(l1+l2):
        gOut.SetPoint(i, g.GetX()[j], g.GetY()[j])
    return gOut


def extrapolatedGraph(h, gr, yValueToPrune):
    grOut = r.TGraph()
    grOut.SetName("%s_extrapolated" % gr.GetName())
    X = gr.GetX()
    Y = gr.GetY()
    N = gr.GetN()
    if N:
        grOut.SetPoint(0,
                       X[0] - binWidth(h, "X")/2.0,
                       Y[0] - binWidth(h, "Y")/2.0,
                       )
        index = 1
        more = True
        for i in range(N):
            if not more:
                continue
            if allMatch(value=yValueToPrune, y=Y,
                        threshold=0.1, iStart=i, N=N):
                more = False  # prune points if "y=100.0 from here to end"
            grOut.SetPoint(index, X[index-1], Y[index-1])
            index += 1
        grOut.SetPoint(index, X[index-2], yValueToPrune - binWidth(h, "Y")/2.0)
    return grOut


def excludedGraphOld(h, factor=None, model=None, interBin="",
                     pruneAndExtrapolate=False, yValueToPrune=-80):
    assert interBin in ["Center", "LowEdge"], interBin

    def fail(xs, xsLimit):
        return (xs <= xsLimit) or not xsLimit

    refHisto = refXsHisto(model)

    out = r.TGraph()
    out.SetName("%s_graph" % h.GetName())
    index = 0
    for iBinX in range(1, 1+h.GetNbinsX()):
        x = getattr(h.GetXaxis(), "GetBin%s" % interBin)(iBinX)
        xs = factor*refHisto.GetBinContent(refHisto.FindBin(x))
        nHit = 0
        lastHit = None
        for iBinY in range(1, 1+h.GetNbinsY()):
            y = getattr(h.GetYaxis(), "GetBin%s" % interBin)(iBinY)
            xsLimit = h.GetBinContent(iBinX, iBinY)
            xsLimitPrev = h.GetBinContent(iBinX, iBinY-1)
            xsLimitNext = h.GetBinContent(iBinX, iBinY+1)

            passed = not fail(xs, xsLimit)
            otherFailed = fail(xs, xsLimitPrev) or fail(xs, xsLimitNext)
            if passed and otherFailed:
                lastHit = (x, y)
                out.SetPoint(index, *lastHit)
                index += 1
                nHit += 1

        if nHit == 1:  # if "top" and "bottom" bin are the same
            out.SetPoint(index, *lastHit)
            index += 1
            print "INFO: %s (factor %g) hit " % (out.GetName(), factor) + \
                  "iBinX = %d, nHit = %d, " % (iBinX, nHit) + \
                  "lastHit = %s repeated" % (str(lastHit))

    out = reordered(out, factor)
    if pruneAndExtrapolate:
        out = extrapolatedGraph(h, out, yValueToPrune)
    return out
