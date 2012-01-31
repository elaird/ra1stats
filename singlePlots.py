#!/usr/bin/env python

import utils,ROOT as r

def setup() :
    r.gStyle.SetPalette(1)
    r.gROOT.ForceStyle()
    
def histo(fileName = "", histoName = "", mask = None) :
    f = r.TFile(fileName)
    out = f.Get(histoName)
    assert out, "%s, %s"%(fileName, histoName)
    out.Clone(histoName+"_clone")
    out.SetDirectory(0)
    f.Close()

    if mask :
        for b in bins(out) :
            if not mask.GetBinContent(*b) :
                out.SetBinContent(b[0], b[1], b[2], 0.0)
    return out

def onePlot(d) :
    h = histo(fileName = d["fileName"],
              histoName = d["histoName"],
              mask = None if "mask" not in d else d["mask"])

    for s,function in {"Den":"Divide", "Num":"Multiply"}.iteritems() :
        if "fileName%s"%s in d and "histoName%s"%s in d :
            h2 = histo(fileName = d["fileName%s"%s],
                       histoName = d["histoName%s"%s],
                       mask = None if "mask" not in d else d["mask"])
            getattr(h, function)(h2)

    if "factor" in d :
        h.Scale(d["factor"])
        
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

def bins(h) :
    out = []
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                out.append( (iBinX, iBinY, iBinZ) )
    return out
    
def histoMask(h, func) :
    out = h.Clone("mask_%s"%h.GetName())
    out.Reset()
    for b in bins(h) :
        c = h.GetBinContent(*b)
        out.SetBinContent(b[0], b[1], b[2], func(c))

    #can = r.TCanvas()
    #can.SetRightMargin(0.15)
    #out.Draw("colz")
    #eps = "%s.eps"%("foo")
    #can.Print(eps)
    #utils.epsToPdf(eps)
        
    return out
    
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

def common(h, c, rebin = True) :
    if rebin : h.Rebin2D()
    h.GetXaxis().SetRangeUser(  0.0, 1899.9)
    h.GetXaxis().SetNdivisions(504)
    h.GetYaxis().SetRangeUser(125.0,  750.0)
    #h.GetYaxis().SetNdivisions(504)

    c.SetRightMargin(0.15)
    c.SetTickx()
    c.SetTicky()
    
def xs(h, c) :
    common(h, c)
    setRange(h, 1.0e-3, 4.0e+2)
    c.SetLogz()

def xsRatio(h, c) :
    common(h, c)
    setRange(h, 0.0, 2.0)

def xsRatioNoRebin(h, c) :
    common(h, c, rebin = False)
    setRange(h, 0.0, 2.0)

def effHadSum(h, c) :
    common(h, c)
    setRange(h, 0.0, 0.20)
    h.GetZaxis().SetNdivisions(5, False)
    
def yieldHadSum(h, c) :
    common(h, c)
    setRange(h, 1.0, 1.0e3)
    c.SetLogz()
    #h.GetZaxis().SetNdivisions(5, False)
    
def effMuonSum(h, c) :
    common(h, c)
    setRange(h, 0.00, 0.03)
    #h.GetZaxis().SetNdivisions(5, False)
    
def effMuonHadRatio(h, c) :
    common(h, c)
    setRange(h, 0.0, 1.0)

setup()

#determine mask
nloOverLoFull = onePlot({"fileName":     "output/CLs_tanBeta10_nlo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
                         "histoName":    "xs_2D",
                         "fileNameDen":  "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
                         "histoNameDen": "xs_2D",
                         "outName": "xsRatioFull_2D",
                         "func": xsRatioNoRebin,
                         "pTitle": "NLO xs / LO xs",
                         }
                        )

mask = histoMask(nloOverLoFull, lambda x:x>0.5)

#XS ratio
onePlot({"fileName":     "output/CLs_tanBeta10_nlo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
         "histoName":    "xs_2D",
         "fileNameDen":  "output/CLs_tanBeta10_lo_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root",
         "histoNameDen": "xs_2D",
         "outName": "xsRatio_2D",
         "func": xsRatio,
         "mask": mask,
         "pTitle": "NLO xs / LO xs",
         }
        )

#others
order = "nlo"
onePlot({"fileName": "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root"%order,
         "histoName": "xs_2D",
         "outName": "xs_%s_2D"%order,
         "func": xs,
         "mask": mask,
         }
        )

onePlot({"fileName": "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effHad.root"%order,
         "histoName": "effHadSum_2D",
         "outName": "effHadSum_%s_2D"%order,
         "func": effHadSum,
         "mask": mask,
         "pTitle": "efficiency of hadronic selection (all bins summed)",
         }
        )

lumi = 1.1e3 #lumi in 1/pb
onePlot({"fileName": "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_xs.root"%order,
         "histoName": "xs_2D",
         "fileNameNum": "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effHad.root"%order,
         "histoNameNum": "effHadSum_2D",
         
         "outName": "yieldHadSum_%s_2D"%order,
         "func": yieldHadSum,
         "mask": mask,
         "factor": lumi,
         "pTitle": "yield of hadronic selection (all bins summed) for %3.1f/fb"%(lumi/1.0e3),
         }
        )

onePlot({"fileName": "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effMu.root"%order,
         "histoName": "effMuonSum_2D",
         "outName": "effMuonSum_%s_2D"%order,
         "func": effMuonSum,
         "mask": mask,
         "pTitle": "efficiency of muon selection (all bins summed)",
         }
        )

onePlot({"fileName":     "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effMu.root"%order,
         "histoName":    "effMuonSum_2D",
         "fileNameDen":  "output/CLs_tanBeta10_%s_TS3_REwkConstant_RQcdFallingExp_fZinvAll_h1xp_effHad.root"%order,
         "histoNameDen": "effHadSum_2D",
         "outName": "effMuonHadRatio_%s_2D"%order,
         "func": effMuonHadRatio,
         "mask": mask,
         "pTitle": "eff. muon selection / eff. had selection",
         }
        )
