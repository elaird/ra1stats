#!/usr/bin/env python

import sys,utils
import ROOT as r

if len(sys.argv)<2 :
    print "Usage: %s root-file"%sys.argv[0]
    exit()

def histos() :
    out = []
    f = r.TFile(sys.argv[1])
    for i in range(len(f.GetListOfKeys())/2) :
        bDist = f.Get("bDist%d"%i).Clone(); bDist.SetDirectory(0)
        sbDist = f.Get("sbDist%d"%i).Clone(); sbDist.SetDirectory(0)
        out.append( {"bDist": bDist, "sbDist": sbDist} )
    f.Close()
    return out

def scaled(h) :
    h.Scale(1.0/h.Integral(0, 2+h.GetNbinsX(), "width"))
    return h

def go() :
    ps = sys.argv[1].replace(".root", "_tsLook.ps")

    can = r.TCanvas()
    can.Print(ps+"[")
    for d in histos() :
        b = scaled(d["bDist"])
        sb = scaled(d["sbDist"])
        
        b.SetLineColor(r.kBlue)
        b.Draw()

        sb.SetLineColor(r.kRed)
        sb.Draw("same")
        
        b.SetMaximum(1.1*max(b.GetMaximum(), sb.GetMaximum()))
        can.Print(ps)
    
    can.Print(ps+"]")
    utils.ps2pdf(ps)

go()
