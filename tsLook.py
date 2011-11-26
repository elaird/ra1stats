#!/usr/bin/env python

import sys,utils
import ROOT as r

if len(sys.argv)<2 :
    print "Usage: %s root-file"%sys.argv[0]
    exit()

def histos(keyList = ["bDist", "sbDist", "tsObs", "CLs", "CLb", "CLsplusb", "testStatisticType"]) :
    out = []
    f = r.TFile(sys.argv[1])
    for i in range(1) :
        d = {}
        for item in keyList :
            d[item] = f.Get("%s%d"%(item, i)).Clone()
            d[item].SetDirectory(0)
        out.append(d)
    f.Close()
    return out

def scaled(h) :
    h.Scale(1.0/h.Integral(0, 2+h.GetNbinsX(), "width"))
    return h

def stylized(h, key = "", colors = {}, widths = {}) :
    if key in colors : h.SetLineColor(colors[key])
    if key in widths : h.SetLineWidth(widths[key])
    return h

def values(d) :
    out = {}
    for item in ["tsObs", "CLs", "CLb", "CLsplusb", "testStatisticType"] :
        for error in ["", "Error"] :
            key = item + error
            if key not in d : continue
            out[key] = d[key].GetBinContent(1)
    return out

def go(colors = {}, widths = {}, valuesInLegend = True, multiPage = False) :
    ps = sys.argv[1].replace(".root", "_tsLook.ps")
    eps = ps.replace(".ps", ".eps")

    can = r.TCanvas()
    can.SetTickx()
    can.SetTicky()

    histoList = histos()
    if multiPage :
        can.Print(ps+"[")
    else :
        assert len(histoList)==1,"histoList has length %d"%len(histoList)

    for d in histoList :
        leg = r.TLegend(0.45, 0.7, 0.85, 0.85)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)

        val = values(d)
            
        b = stylized(scaled(d["bDist"]), "bDist", colors, widths)
        sb = stylized(scaled(d["sbDist"]), "sbDist", colors, widths)
        yMax = 1.1*max(b.GetMaximum(), sb.GetMaximum())

        assert abs(val["testStatisticType"]-3.0)<0.01,"modify x axis title for TS %g"%val["testStatisticType"]
        null = r.TH2D("null", ";q_{1};p.d.f.", 1, 0.0, 20.0, 1, 0.0, yMax)
        null.SetStats(False)
        null.Draw()

        sb.Draw("histsame")
        b.Draw("histsame")

        leg.AddEntry(sb,            "S+B%s"%("" if not valuesInLegend else "  (CL_{s+b} = %4.2f)"%val["CLsplusb"]), "l")
        leg.AddEntry( b, "#color[0]{S+}B%s"%("" if not valuesInLegend else "  (CL_{b#color[0]{+s}} = %4.2f)"%val["CLb"]), "l")
        
        line = stylized(r.TLine(), "tsObs", colors, widths)
        obsLine = line.DrawLine(val["tsObs"], 0.0, val["tsObs"], 0.5*yMax)
        leg.AddEntry(obsLine, "observed value", "l")
        leg.Draw()
        if multiPage :
            can.Print(ps)
        else :
            can.Print(eps)
            can.Print(eps.replace(".eps", ".C"))

    if multiPage :
        can.Print(ps+"]")
        utils.ps2pdf(ps)
    else :
        utils.epsToPdf(eps)
        
go(colors = {"bDist":r.kBlue, "sbDist":r.kRed, "tsObs":r.kBlack},
   widths = {"bDist":2, "sbDist":2, "tsObs":2},
   )
