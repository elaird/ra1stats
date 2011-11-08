import collections
import ROOT as r

def histoSpec(model) :
    base = "/vols/cms02/elaird1/25_sms_reference_xs_from_mariarosaria"
    tgqFile = "%s/TGQ_xSec.root"%base
    tgqHisto = "clone"
    tgqFactor = 1.0
    d = {"T1":        {"histo": "gluino", "factor": 1.0, "file": "%s/reference_xSec.root"%base},
         "T2":        {"histo": "squark", "factor": 0.8, "file": "%s/reference_xSec.root"%base},
         "T2tt":      {"histo": "stop",   "factor": 1.0, "file": "%s/reference_xSec_stop.root"%base},
         "TGQ_0p0":   {"histo": tgqHisto, "factor": tgqFactor, "file": tgqFile},
         "TGQ_0p2":   {"histo": tgqHisto, "factor": tgqFactor, "file": tgqFile},
         "TGQ_0p4":   {"histo": tgqHisto, "factor": tgqFactor, "file": tgqFile},
         "TGQ_0p8":   {"histo": tgqHisto, "factor": tgqFactor, "file": tgqFile},
         }
    assert model in d,model
    return d[model]

def refXsHisto(model) :
    hs = histoSpec(model)
    f = r.TFile(hs["file"])
    out = f.Get(hs["histo"]).Clone("%s_clone"%hs["histo"])
    out.SetDirectory(0)
    f.Close()
    out.Scale(hs["factor"])
    return out

def mDeltaFuncs(mDeltaMin = None, mDeltaMax = None, nSteps = None, mGMax = None) :
    out = []
    for iStep in range(1+nSteps) :
        mDelta = mDeltaMin + (mDeltaMax - mDeltaMin)*(iStep+0.0)/nSteps
        out.append( r.TF1("ml_vs_mg_%d"%iStep, "sqrt(x*x-x*(%g))"%mDelta, mDelta, mGMax) )

    for f in out :
        f.SetLineWidth(1)
        f.SetNpx(1000)
        f.SetLineColor(r.kBlack)

    return out
        
def graphs(h, model, interBin, pruneAndExtrapolate = False, yValueToPrune = None, noOneThird = False) :
    out = [{"factor": 1.0 , "label": "#sigma^{prod} = #sigma^{NLO-QCD}",     "color": r.kBlack, "lineStyle": 1, "lineWidth": 3, "markerStyle": 20},
           {"factor": 3.0 , "label": "#sigma^{prod} = 3 #sigma^{NLO-QCD}",   "color": r.kBlack, "lineStyle": 2, "lineWidth": 3, "markerStyle": 20},
           ]
    if not noOneThird :
        out.append({"factor": 1/3., "label": "#sigma^{prod} = 1/3 #sigma^{NLO-QCD}", "color": r.kBlack, "lineStyle": 3, "lineWidth": 3, "markerStyle": 20})
    for d in out :
        d["graph"] = excludedGraph(h, d["factor"], model, interBin)
        stylize(d["graph"], d["color"], d["lineStyle"], d["lineWidth"], d["markerStyle"])
        d["histo"] = excludedHistoSimple(h, d["factor"], model, interBin)
    return out

def binWidth(h, axisString) :
    a = getattr(h, "Get%saxis"%axisString)()
    return (a.GetXmax()-a.GetXmin())/getattr(h, "GetNbins%s"%axisString)()

def allMatch(value, y, threshold, iStart, N) :
    count = 0
    for i in range(iStart, N) :
        if abs(y[i]-value)<threshold :
            count +=1
    return count==(N-iStart)

def excludedGraph(h, factor = None, model = None, interBin = "CenterOrLowEdge", prune = False) :
    def fail(xs, xsLimit) :
        return xs<=xsLimit or not xsLimit

    refHisto = refXsHisto(model)
    twoD = refHisto.ClassName()[:3]=="TH2"
    
    d = collections.defaultdict(list)
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = getattr(h.GetXaxis(),"GetBin%s"%interBin)(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = getattr(h.GetYaxis(),"GetBin%s"%interBin)(iBinY)
            coords = (x,) if not twoD else (x,y)
            xs = factor*refHisto.GetBinContent(refHisto.FindBin(*coords))
            if not xs : continue
            
            xsLimit     = h.GetBinContent(iBinX, iBinY)
            xsLimitPrev = h.GetBinContent(iBinX, iBinY-1)
            xsLimitNext = h.GetBinContent(iBinX, iBinY+1)
            transition = (fail(xs, xsLimitPrev) or fail(xs, xsLimitNext)) and not fail(xs, xsLimit)
            if transition : d[x].append(y)
        if len(d[x])==1 :
            print "INFO: %s (factor %g) hit iBinX = %d (x = %g), y = %g repeated"%(h.GetName(), factor, iBinX, x, d[x][0])
            d[x].append(d[x][0])
            
    l1 = []
    l2 = []
    for x in sorted(d.keys()) :
        values = sorted(d[x])
        values.reverse()
        if prune : values = [values[0], values[-1]]
        
        l1+= [(x,y) for y in values[:-1]]
        l2+= [(x,y) for y in values[-1:]]
    l2.reverse()

    out = r.TGraph()
    out.SetName("%s_graph"%h.GetName())
    for i,t in enumerate(l1+l2) :
        out.SetPoint(i,*t)

    return out

def excludedHistoSimple(h, factor = None, model = None, interBin = "CenterOrLowEdge") :
    refHisto = refXsHisto(model)
    out = h.Clone("%s_excludedHistoSimple"%h.GetName())
    out.Reset()
    out.GetZaxis().SetTitle("bin excluded or not")
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = getattr(h.GetXaxis(),"GetBin%s"%interBin)(iBinX)
        xs = factor*refHisto.GetBinContent(refHisto.FindBin(x))
        for iBinY in range(1, 1+h.GetNbinsY()) :
            xsLimit = h.GetBinContent(iBinX, iBinY)
            if not xsLimit : continue
            out.SetBinContent(iBinX, iBinY, 2*(xsLimit<xs)-1)
    return out

def reordered(inGraph, factor) :
    def truncated(gr) :
        N = gr.GetN()
        if N%2 :
            out = r.TGraph()
            out.SetName("%s_truncated"%gr.GetName())
            x = gr.GetX()
            y = gr.GetY()
            for i in range(N-1) :
                out.SetPoint(i, x[i], y[i])
            print "ERROR: discarded from graph %s (factor %g) the point %d, %g, %g"%(gr.GetName(), factor, N-1, x[N-1], y[N-1])
            return out
        else :
            return gr

    g = truncated(inGraph)
    N = g.GetN()
    l1 = []
    l2 = []
    for i in range(N/2) :
        j = 2*i+1
        l1.append(j)
        l2.append(N-j-1)

    gOut = r.TGraph()
    #e.g., 1,3,5,7,6,4,2,0
    #print l1+l2
    for i,j in enumerate(l1+l2) :
        gOut.SetPoint(i, g.GetX()[j], g.GetY()[j])
    return gOut

def stylize(g, color = None, lineStyle = None, lineWidth = None, markerStyle = None) :
    g.SetLineColor(color)
    g.SetLineStyle(lineStyle)
    g.SetLineWidth(lineWidth)
    g.SetMarkerColor(color)
    g.SetMarkerStyle(markerStyle)
    return

def drawGraphs(graphs) :
    legend = r.TLegend(0.2, 0.67, 0.7, 0.67+0.04*len(graphs))
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    for d in graphs :
        g = d["graph"]
        legend.AddEntry(g, d["label"], "l")
        if g.GetN() : g.Draw("lsame")
    legend.Draw("same")
    return legend,graphs

def extrapolatedGraph(h, gr, yValueToPrune) :
    grOut = r.TGraph()
    grOut.SetName("%s_extrapolated"%gr.GetName())
    X = gr.GetX()
    Y = gr.GetY()
    N = gr.GetN()
    if N :
        grOut.SetPoint(0, X[0] - binWidth(h, "X")/2.0, Y[0] - binWidth(h, "Y")/2.0)
        index = 1
        more = True
        for i in range(N) :
            if not more : continue
            if allMatch(value = yValueToPrune, y = Y, threshold = 0.1, iStart = i, N = N) :
                more = False #prune points if "y=100.0 from here to end"
            grOut.SetPoint(index, X[index-1], Y[index-1])
            index +=1
        grOut.SetPoint(index, X[index-2], yValueToPrune - binWidth(h, "Y")/2.0)
    return grOut
    
def excludedGraphOld(h, factor = None, model = None, interBin = "CenterOrLowEdge", pruneAndExtrapolate = False, yValueToPrune = -80) :
    def fail(xs, xsLimit) :
        return xs<=xsLimit or not xsLimit

    refHisto = refXsHisto(model)

    out = r.TGraph()
    out.SetName("%s_graph"%h.GetName())
    index = 0
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = getattr(h.GetXaxis(),"GetBin%s"%interBin)(iBinX)
        xs = factor*refHisto.GetBinContent(refHisto.FindBin(x))
        nHit = 0
        lastHit = None
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = getattr(h.GetYaxis(),"GetBin%s"%interBin)(iBinY)
            xsLimit     = h.GetBinContent(iBinX, iBinY)
            xsLimitPrev = h.GetBinContent(iBinX, iBinY-1)
            xsLimitNext = h.GetBinContent(iBinX, iBinY+1)
            if (not fail(xs, xsLimit)) and (fail(xs, xsLimitPrev) or fail(xs, xsLimitNext)) :
                lastHit = (x, y)
                out.SetPoint(index, *lastHit)
                index +=1
                nHit +=1

        if nHit==1 : #if "top" and "bottom" bin are the same
            out.SetPoint(index, *lastHit)
            index += 1
            print "INFO: %s (factor %g) hit iBinX = %d, nHit = %d, lastHit = %s repeated"%(out.GetName(), factor, iBinX, nHit, str(lastHit))

    out = reordered(out, factor)
    if pruneAndExtrapolate :
        out = extrapolatedGraph(h, out, yValueToPrune)
    return out
