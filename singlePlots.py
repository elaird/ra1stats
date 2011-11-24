#!/usr/bin/env python

import utils,ROOT as r

def setup() :
    r.gStyle.SetPalette(1)
    r.gROOT.ForceStyle()
    
def histo(fileName = "", histoName = "") :
    f = r.TFile(fileName)
    out = f.Get(histoName)
    out.Clone(histoName+"_clone")
    out.SetDirectory(0)
    f.Close()
    return out

def onePlot(d) :
    h = histo(fileName = d["fileName"], histoName = d["histoName"])
    #h.UseCurrentStyle()
    h.SetStats(False)
    h.SetTitle("")
    can = r.TCanvas()

    if "func" in d : d["func"](h, can)
    h.Draw("colz")
    eps = d["histoName"]+".eps"
    can.Print(eps)
    utils.epsToPdf(eps)

def xs(h,c) :
    h.Rebin2D()
    h.GetXaxis().SetRangeUser(  0.0, 1899.9)
    h.GetXaxis().SetNdivisions(504)
    
    h.GetYaxis().SetRangeUser(125.0,  750.0)
    #h.GetYaxis().SetNdivisions(504)
    
    h.SetMinimum(1.0e-3)
    h.SetMaximum(2.0e+2)
    c.SetLogz()
    c.SetRightMargin(0.15)

def effHadSum(h, c) :
    xs(h, c)
    c.SetLogz(False)
    h.SetMaximum(0.20)
    h.SetMinimum(0.0)
    h.GetZaxis().SetNdivisions(5, False)
    
setup()

onePlot({"fileName": "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effHad.root",
         "histoName": "effHadSum_2D",
         "func": effHadSum,
         }
        )

onePlot({"fileName": "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
         "histoName": "xs_2D",
         "func": xs,
         }
        )
