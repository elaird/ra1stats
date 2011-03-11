import ROOT as r

def histoSpec(model) :
    assert (model in ["T1", "T2"]),"%s"%model
    if model=="T1" :
        histo = "gluino"
        factor = 1.0        
    if model=="T2" :
        histo = "squark"
        factor = 0.8
    return {"file": "/vols/cms02/elaird1/25_sms_reference_xs_from_mariarosaria/reference_xSec.root", "histo": histo, "factor": factor}

def graphs(h, model, interBin) :
    out = [{"factor": 1.0 , "label": "#sigma^{prod} = #sigma^{NLO-QCD}",     "color": r.kBlack, "lineStyle": 1, "lineWidth": 3, "markerStyle": 20},
           {"factor": 3.0 , "label": "#sigma^{prod} = 3 #sigma^{NLO-QCD}",   "color": r.kBlack, "lineStyle": 2, "lineWidth": 3, "markerStyle": 20},
           {"factor": 1/3., "label": "#sigma^{prod} = 1/3 #sigma^{NLO-QCD}", "color": r.kBlack, "lineStyle": 3, "lineWidth": 3, "markerStyle": 20},
           ]
    for d in out :
        d["graph"] = reordered(*excludedGraph(h, d["factor"], model, interBin))
        stylize(d["graph"], d["color"], d["lineStyle"], d["lineWidth"], d["markerStyle"])
    return out

def excludedGraph(h, factor = None, model = None, interBin = "CenterOrLowEdge") :
    def fail(xs, xsLimit) :
        return xs<=xsLimit or not xsLimit
    
    refXs = histoSpec(model)
    f = r.TFile(refXs["file"])
    refHisto = f.Get(refXs["histo"]).Clone("%s_clone"%refXs["histo"])
    refHisto.SetDirectory(0)
    f.Close()

    out = r.TGraph()
    out.SetName("%s_graph"%h.GetName())
    index = 0
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = getattr(h.GetXaxis(),"GetBin%s"%interBin)(iBinX)
        xs = factor*refHisto.GetBinContent(refHisto.FindBin(x))*refXs["factor"]
        nHit = 0
        lastHit = None
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = getattr(h.GetYaxis(),"GetBin%s"%interBin)(iBinY)
            xsLimit     = h.GetBinContent(iBinX, iBinY)
            xsLimitPrev = h.GetBinContent(iBinX, iBinY-1)
            xsLimitNext = h.GetBinContent(iBinX, iBinY+1)
            if (not fail(xs, xsLimit)) and (fail(xs, xsLimitPrev) or fail(xs, xsLimitNext)) :
                out.SetPoint(index, x, y)
                index +=1
                nHit +=1
                lastHit = (index, x, y)

        if nHit==1 : #if "top" and "bottom" bin are the same
            out.SetPoint(*lastHit)
            index += 1
            print "INFO: %s (factor %g) hit iBinX = %d, nHit = %d, lastHit = %s repeated"%(out.GetName(), factor, iBinX, nHit, str(lastHit))
    return out,factor

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
    legend = r.TLegend(0.15, 0.7, 0.75, 0.85)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    for d in graphs :
        g = d["graph"]
        legend.AddEntry(g, d["label"], "l")
        if g.GetN() : g.Draw("lsame")
    legend.Draw("same")
    return legend,graphs

