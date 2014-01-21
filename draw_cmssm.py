#!/usr/bin/env python

import ROOT as r
import patches

def setup() :
    r.gErrorIgnoreLevel = 2000
    r.gROOT.SetBatch(True)
    
def susyCanvas(fileName = "xs/GridTanb10_v1.root", canvasName = "GridCanvas") :
    #http://arxiv.org/abs/1202.6580
    #https://twiki.cern.ch/twiki/bin/view/CMS/SUSY42XSUSYScan#mSUGRA_Templates
    f = r.TFile(fileName)
    canvas = f.Get(canvasName).Clone("%s_clone"%canvasName)
    f.Close()
    return canvas

def enclosedBand(graph1 = None, graph2 = None) :
    #inspired by http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=6346&p=26175
    out = r.TGraph()
    out.SetName("%s_%s"%(graph1.GetName(), graph2.GetName()))

    x = r.Double()
    y = r.Double()

    n1 = graph1.GetN()
    n2 = graph2.GetN()

    for i in range(n1) :
        graph1.GetPoint(i, x, y)
        out.SetPoint(i, float(x), float(y))

    for i in range(n2) :
        graph2.GetPoint(n2-i-1, x, y)
        out.SetPoint(n1+i, float(x), float(y))
    return out

def tgraph(points = []) :
    graph = r.TGraph()
    for i,(x,y) in enumerate(points) :
        graph.SetPoint(i, x, y)
    return graph

def spline(points = [], title = "") :
    return r.TSpline3(title, tgraph(points))

def go(outFile = "", model = "tanBeta10", bandOutline = False) :
    curves = patches.curves().get(model)
    assert curves

    #ROOT
    setup()

    #clone and draw template from SUSY group
    canvas = susyCanvas()
    canvas.Draw()

    #expected band
    expM = tgraph(curves[("ExpectedUpperLimit_-1_Sigma", "default")])
    expP = tgraph(curves[("ExpectedUpperLimit_+1_Sigma", "default")])
    band = enclosedBand(expM, expP)
    band.SetFillStyle(3001)
    band.SetFillColor(r.kGreen-9)
    band.Draw("fsame")

    if bandOutline :
        for exp in [expM, expP] :
            exp.SetLineColor(r.kBlue)
            exp.SetLineStyle(1)
            exp.SetLineWidth(1)
            exp.Draw("lsame")

    #median expected limit
    exp = spline(curves[("ExpectedUpperLimit", "default")], title = "Median Expected Limit #pm 1 #sigma")
    exp.SetLineColor(r.kGreen+3)
    exp.SetLineStyle(7)
    exp.SetLineWidth(2)
    exp.Draw("lsame")

    #legend entry for expected curves/band
    expLeg = exp.Clone("%s_clone"%exp.GetName())
    expLeg.SetFillStyle(band.GetFillStyle())
    expLeg.SetFillColor(band.GetFillColor())

    #observed limit (xs variations)
    obsD = spline(curves[("UpperLimit", "down")], title = "Observed Limit #pm 1 #sigma th. unc.")
    obsD.SetLineStyle(4)
    obsD.Draw("lsame")

    obsU = spline(curves[("UpperLimit", "up")])
    obsU.SetLineStyle(4)
    obsU.Draw("lsame")

    #observed limit (xs = default)
    obs = spline(curves[("UpperLimit", "default")], "Observed Limit (95% C.L.)")
    obs.SetLineWidth(3)
    obs.Draw("lsame")

    #populate and draw legend
    legend = r.TLegend(0.41, 0.55, 0.76, 0.77)
    legend.SetFillColor(0)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.AddEntry(obs, obs.GetTitle(), "l")
    legend.AddEntry(obsD, obsD.GetTitle(), "l")
    legend.AddEntry(expLeg, expLeg.GetTitle(), "fl")
    legend.Draw()

    #CMS stamp
    text = r.TLatex()
    text.SetNDC()
    text.SetTextSize(0.8*text.GetTextSize())
    #stamp = text.DrawLatex(0.35, 0.77, "CMS Preliminary, 4.98 fb^{-1}, #sqrt{s} = 7 TeV")
    stamp = text.DrawLatex(0.40, 0.77, "CMS, L = 4.98 fb^{-1}, #sqrt{s} = 7 TeV")
    #print to file
    canvas.Print(outFile)

    f = r.TFile(outFile+".root", "RECREATE")
    obs.SetName("ObservedLimitSpline")
    obs.Write()
    f.Close()


#the points defining the curves are stored in points.py
go(outFile = "RA1_CMSSM.pdf", bandOutline = False)
