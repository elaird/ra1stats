#!/usr/bin/env python

import ROOT as r
import refXsProcessing as rxs
import os

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)

def mother(model) :
    d = {}
    d["T1"] = "gluino"
    d["T2"] = "squark"
    return d[model]

def ranges(model) :
    d = {}

    d["smsXRange"] = (400.0, 999.9) #(min, max)
    d["smsYRange"] = (100.0, 975.0)
    d["smsXsZRangeLin"] = (0.0, 40.0, 40) #(zMin, zMax, nContours)
    d["smsXsZRangeLog"] = (0.4, 40.0, 40)
    d["smsEffZRange"]   = (0.0, 0.60, 30)
    d["smsLimZRange"]   = (0.0, 40.0, 40)
    d["smsLimLogZRange"]= (0.1, 80.0, 40)

    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.50, 50)
    return d

def specs() :
    d = {}
    dir = "/home/hep/elaird1/60_ra_comparison"
    #d["razor"] = {"T1_Eff": ("%s/razor/razor.root"%dir,"T1_EFF"),
    #              "T2_Eff": ("%s/razor/razor.root"%dir,"T2_EFF"),
    #              "T1_Lim": ("%s/razor/razor.root"%dir,"T1_LIMIT"),
    #              "T2_Lim": ("%s/razor/razor.root"%dir,"T2_LIMIT"),
    #              "extra": "",
    #              "shiftX": False,
    #              "shiftY": False,
    #              }

    d["razor"] = {"T1_Eff": ("%s/razor/v2/t1_eff.root"%dir,"hist"),
                  "T2_Eff": ("%s/razor/v2/t2_eff.root"%dir,"hist"),
                  "T1_Lim": ("%s/razor/v2/t1_limit.root"%dir,"hist"),
                  "T2_Lim": ("%s/razor/v2/t2_limit.root"%dir,"hist"),
                  "name": "Razor",
                  "shiftX": False,
                  "shiftY": False,
                  }

    d["ra2"] = {"T1_Eff": ("%s/ra2/v2/t1_eff.root"%dir,"DefaultAcceptance"),
                "T2_Eff": ("%s/ra2/v2/t2_eff.root"%dir,"DefaultAcceptance"),
                "T1_Lim": ("%s/ra2/v3/t1_limit.root"%dir,"hlimit_gluino_T1_MHT"),
                "T2_Lim": ("%s/ra2/v3/t2_limit.root"%dir,"hlimit_squark_T2_MHT"),
                "T1_EffUncExp": ("%s/ra2/v2/t1_effUncExp.root"%dir,"ExpRelUnc_gluino_T1_MHT"),
                "T2_EffUncExp": ("%s/ra2/v2/t2_effUncExp.root"%dir,"ExpRelUnc_squark_T2_MHT"),
                "T1_EffUncTh":  ("%s/ra2/v2/t1_effUncTh.root"%dir,"theoryUnc_gluino_T1_MHT"),
                "T2_EffUncTh":  ("%s/ra2/v2/t2_effUncTh.root"%dir,"theoryUnc_squark_T2_MHT"),
                "name": "Jets +",
                "name2": "Missing HT",
                "shiftX": False,
                "shiftY": True,
                }

    d["ra1"] = {"T1_Eff": ("%s/ra1/T1_eff.root"%dir,"m0_m12_0"),
                "T2_Eff": ("%s/ra1/T2_eff.root"%dir,"m0_m12_0"),
                "T1_Lim": ("%s/ra1/profileLikelihood_T1_lo_1HtBin_expR_xsLimit.root"%dir,"UpperLimit_2D"),
                "T2_Lim": ("%s/ra1/profileLikelihood_T2_lo_1HtBin_expR_xsLimit.root"%dir,"UpperLimit_2D"),
                "T1_EffUncExp": ("%s/ra1/T1_effUncRelExp.root"%dir,"effUncRelExperimental_2D"),
                "T2_EffUncExp": ("%s/ra1/T2_effUncRelExp.root"%dir,"effUncRelExperimental_2D"),
                "T1_EffUncTh":  ("%s/ra1/T1_effUncRelTh.root"%dir,"effUncRelTheoretical_2D"),
                "T2_EffUncTh":  ("%s/ra1/T2_effUncRelTh.root"%dir,"effUncRelTheoretical_2D"),
                "name": "#alpha_{T}",
                "shiftX": True,
                "shiftY": True,
                }

    d["analyses"] = ["ra1", "ra2", "razor"]
    d["printC"] = False
    d["printTxt"] = False
    
    return d

def shifted(h, shiftX, shiftY) :
    binWidthX = (h.GetXaxis().GetXmax() - h.GetXaxis().GetXmin())/h.GetNbinsX() if shiftX else 0.0
    binWidthY = (h.GetYaxis().GetXmax() - h.GetYaxis().GetXmin())/h.GetNbinsY() if shiftY else 0.0

    out = r.TH2D(h.GetName()+"_shifted","",
                 h.GetNbinsX(), h.GetXaxis().GetXmin() - binWidthX/2.0, h.GetXaxis().GetXmax() - binWidthX/2.0,
                 h.GetNbinsY(), h.GetYaxis().GetXmin() - binWidthY/2.0, h.GetYaxis().GetXmax() - binWidthY/2.0,
                 )

    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            out.SetBinContent(iBinX, iBinY, h.GetBinContent(iBinX, iBinY))
    return out

def freshHisto(h) :
    out = r.TH2D(h.GetName()+"_fresh","",
                 h.GetNbinsX(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax(),
                 h.GetNbinsY(), h.GetYaxis().GetXmin(), h.GetYaxis().GetXmax(),
                 )
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            out.SetBinContent(iBinX, iBinY, h.GetBinContent(iBinX, iBinY))
    return out

def fetchHisto(file, dir, histo, name) :
    f = r.TFile(file)
    hOld = f.Get("%s/%s"%(dir, histo))
    assert hOld, "%s %s %s"%(file, dir, histo)
    h = hOld.Clone(name)
    h.SetDirectory(0)
    f.Close()
    return freshHisto(h)

def setRange(var, ranges, histo, axisString) :
    if var not in ranges : return
    nums = ranges[var]
    getattr(histo,"Get%saxis"%axisString)().SetRangeUser(*nums[:2])
    #if len(nums)==3 : r.gStyle.SetNumberContours(nums[2])
    if axisString=="Z" :
        maxContent = histo.GetBinContent(histo.GetMaximumBin())
        if maxContent>nums[1] :
            print "ERROR: histo truncated in Z (maxContent = %g, maxSpecified = %g) %s"%(maxContent, nums[1], histo.GetName())

def adjust(h) :
    h.UseCurrentStyle()
    h.SetStats(False)
    h.GetXaxis().SetTitleOffset(1.0)
    h.GetYaxis().SetTitleOffset(1.05)
    h.GetZaxis().SetTitleOffset(1.0)
    h.GetXaxis().CenterTitle(False)
    h.GetYaxis().CenterTitle(False)
    h.GetZaxis().CenterTitle(False)

    for a,s in zip([h.GetXaxis(), h.GetYaxis(), h.GetZaxis()], [1.5, 1.5, 1.3]) :
        a.SetTitleSize(s*a.GetTitleSize())
        #a.CenterTitle()
    
def printText(h, tag, ana) :
    out = open("%s_%s.txt"%(tag, ana), "w")
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinCenter(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = h.GetYaxis().GetBinCenter(iBinY)
            c = h.GetBinContent(iBinX, iBinY)
            out.write("%g %g %g\n"%(x,y,c))
    out.close()


def plotMulti(model = "", suffix = "", zAxisLabel = "", analyses = [], logZ = False) :
    tag = "%s_%s%s"%(model, suffix, "_logZ" if logZ else "")
    rangeDict = ranges(model)
    
    c = r.TCanvas("canvas_%s"%tag,"canvas", 1500, 500)
    c.Divide(3,1)

    out = []
    for i,ana in enumerate(analyses) :
        c.cd(i+1)
        r.gPad.SetTopMargin(0.15)
        r.gPad.SetBottomMargin(0.15)
        r.gPad.SetLeftMargin(0.15)
        r.gPad.SetRightMargin(0.15)
        if logZ : r.gPad.SetLogz(True)
        d = specs()[ana]

        key = tag.replace("_logZ","")
        if key not in d : continue
        t = d[key]
        h = fetchHisto(t[0], "/", t[1], name = "%s_%s"%(tag, ana))
        h = shifted(h, d["shiftX"], d["shiftY"])
        adjust(h)
        h.SetTitle(";m_{%s} (GeV); m_{LSP} (GeV);%s"%(mother(model), zAxisLabel))
        h.Draw("colz")

        if specs()["printTxt"] : printText(h, tag, ana.upper())
        setRange("smsXRange", rangeDict, h, "X")
        setRange("smsYRange", rangeDict, h, "Y")
        setRange("sms%s%sZRange"%(suffix, "Log" if logZ else ""), rangeDict, h, "Z")
        if suffix=="Lim" :
            stuff = rxs.drawGraphs(rxs.graphs(h, model, "Center"))
            out.append(stuff)
        out.append(stampCmsPrel())
        out.append(stampName(d["name"], d["name2"] if "name2" in d else ""))
        out.append(h)
    printOnce(c, "%s.eps"%tag)

def epsToPdf(fileName, tight = True) :
    if not tight : #make pdf
        os.system("epstopdf "+fileName)
        os.system("rm       "+fileName)
    else : #make pdf with tight bounding box
        epsiFile = fileName.replace(".eps",".epsi")
        os.system("ps2epsi "+fileName+" "+epsiFile)
        os.system("epstopdf "+epsiFile)
        os.system("rm       "+epsiFile)
        os.system("rm       "+fileName)
    #print "%s has been written."%fileName.replace(".eps",".pdf")

def stampCmsPrel() :
    text = r.TText()
    text.SetNDC()
    text.SetTextAlign(22)
    text.DrawText(0.5, 0.9, "CMS Preliminary")
    return text

def stampName(name, name2) :
    text = r.TLatex()
    text.SetNDC()
    text.SetTextAlign(11)
    text.SetTextSize(1.3*text.GetTextSize())
    if name2 :
        text.DrawLatex(0.18, 0.66, name)
        text.DrawLatex(0.18, 0.60, name2)
    else :
        text.DrawLatex(0.18, 0.63, name)        
    return text

def printOnce(canvas, fileName) :
    canvas.Print(fileName)
    if specs()["printC"] : canvas.Print(fileName.replace(".eps",".C"))
    epsToPdf(fileName)

setup()
for model in ["T1", "T2"] :
    #plotMulti(model = model, suffix = "Eff", zAxisLabel = "analysis efficiency", analyses = specs()["analyses"])
    ##plotMulti(model = model, suffix = "Lim", zAxisLabel = "limit on #sigma (pb)", analyses = specs()["analyses"], logZ = False)
    plotMulti(model = model, suffix = "Lim", zAxisLabel = "limit on #sigma (pb)", analyses = specs()["analyses"], logZ = True)
    #plotMulti(model = model, suffix = "EffUncExp", zAxisLabel = "experimental unc.", analyses = specs()["analyses"])
    #plotMulti(model = model, suffix = "EffUncTh", zAxisLabel = "theoretical unc.", analyses = specs()["analyses"])
