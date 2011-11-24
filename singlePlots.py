#!/usr/bin/env python

import utils,ROOT as r

def setup() :
    r.gStyle.SetPalette(1)
    r.gROOT.ForceStyle()
    
def histo(fileName = "", histoName = "") :
    f = r.TFile(fileName)
    out = f.Get(histoName)
    assert out, "%s, %s"%(fileName, histoName)
    out.Clone(histoName+"_clone")
    out.SetDirectory(0)
    f.Close()
    return out

def onePlot(d) :
    h = histo(fileName = d["fileName"], histoName = d["histoName"])
    if "fileNameDen" in d and "histoNameDen" in d :
        den = histo(fileName = d["fileNameDen"], histoName = d["histoNameDen"])
        h.Divide(den)
    
    #h.UseCurrentStyle()
    h.SetStats(False)
    h.SetTitle("")
    can = r.TCanvas()

    if "func" in d : d["func"](h, can)
    for l in ["x", "y", "z"] :
        key = "%sTitle"%l
        if key not in d : continue
        axis = getattr(h, "Get%saxis"%(l.capitalize()))().SetTitle(d[key])
    if "pTitle" in d :
        h.GetListOfFunctions().FindObject("palette").GetAxis().SetTitle(d["pTitle"])

    h.Draw("colz")
    eps = "%s.eps"%(d["outName"] if "outName" in d else d["histoName"])
    can.Print(eps)
    utils.epsToPdf(eps)
    return h

def setRange(h, min = None, max = None) :
    name = h.GetName()
    oldMin = h.GetBinContent(h.GetMinimumBin())
    oldMax = h.GetBinContent(h.GetMaximumBin())
    if min!=None :
        if min>oldMin : print "WARNING: %s minimum %g --> %g"%(name, oldMin, min)
        h.SetMinimum(min)
    if max!=None :
        if max<oldMax : print "WARNING: %s maximum %g --> %g"%(name, oldMax, max)
        h.SetMaximum(max)

def common(h, c) :
    h.Rebin2D()
    h.GetXaxis().SetRangeUser(  0.0, 1899.9)
    h.GetXaxis().SetNdivisions(504)
    h.GetYaxis().SetRangeUser(125.0,  750.0)
    #h.GetYaxis().SetNdivisions(504)

    c.SetRightMargin(0.15)
    c.SetTickx()
    c.SetTicky()
    
def xs(h,c) :
    common(h, c)
    setRange(h, 1.0e-3, 3.0e+2)
    c.SetLogz()

def xsRatio(h,c) :
    common(h, c)
    setRange(h, 0.0, 2.0)

def effHadSum(h, c) :
    common(h, c)
    setRange(h, 0.0, 0.20)
    h.GetZaxis().SetNdivisions(5, False)
    
def effMuonSum(h, c) :
    common(h, c)
    setRange(h, 0.00, 0.03)
    #h.GetZaxis().SetNdivisions(5, False)
    
def effMuonHadRatio(h, c) :
    common(h, c)
    setRange(h, 0.0, 1.0)

setup()

order = "lo"

#onePlot({"fileName": "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root"%order,
#         "histoName": "xs_2D",
#         "outName": "xs_%s_2D"%order,
#         "func": xs,
#         }
#        )

onePlot({"fileName":     "output/CLs_tanBeta10_nlo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
         "histoName":    "xs_2D",
         "fileNameDen":  "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
         "histoNameDen": "xs_2D",
         "outName": "xsRatio_2D",
         "func": xsRatio,
         "pTitle": "NLO xs / LO xs",
         }
        )

#onePlot({"fileName": "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effHad.root",
#         "histoName": "effHadSum_2D",
#         "outName": "effHadSum_lo_2D",
#         "func": effHadSum,
#         "pTitle": "efficiency of hadronic selection (all bins summed)",
#         }
#        )

#onePlot({"fileName": "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effMu.root",
#         "histoName": "effMuonSum_2D",
#         "outName": "effMuonSum_lo_2D",
#         "func": effMuonSum,
#         "pTitle": "efficiency of muon selection (all bins summed)",
#         }
#        )

#onePlot({"fileName":     "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effMu.root"%order,
#         "histoName":    "effMuonSum_2D",
#         "fileNameDen":  "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effHad.root"%order,
#         "histoNameDen": "effHadSum_2D",
#         "outName": "effMuonHadRatio_%s_2D"%order,
#         "func": effMuonHadRatio,
#         "pTitle": "eff. muon selection / eff. had selection",
#         }
#        )
