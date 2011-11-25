#!/usr/bin/env python

import sys,utils
import ROOT as r

if len(sys.argv)<2 :
    print "Usage: %s root-file"%sys.argv[0]
    exit()

def histos(keyList = ["bDist", "sbDist", "tsObs"]) :
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

def go() :
    ps = sys.argv[1].replace(".root", "_tsLook.ps")

    can = r.TCanvas()
    can.SetTickx()
    can.SetTicky()
    can.Print(ps+"[")

    for d in histos() :
        b = scaled(d["bDist"])
        sb = scaled(d["sbDist"])

        b.SetStats(False)
        b.SetLineColor(r.kBlue)
        b.Draw("hist")

        sb.SetLineColor(r.kRed)
        sb.Draw("histsame")

        yMax = 1.1*max(b.GetMaximum(), sb.GetMaximum())
        b.SetMaximum(yMax)

        xObs = d["tsObs"].GetBinContent(1)
        obsLine = r.TLine()
        obsLine.DrawLine(xObs, 0.0, xObs, 0.8*yMax)
        can.Print(ps)
    
    can.Print(ps+"]")
    utils.ps2pdf(ps)

go()
