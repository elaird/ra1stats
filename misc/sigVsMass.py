#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.dirname(__file__)+"/..")

import ROOT as r
import utils


def oneHisto(hName="", label=""):
    if mode.startswith("bestFit"):
        stem = "nlls" + mode.replace("bestFit", "")
    if mode == "CL":
        stem = "CLs_asymptotic_binaryExcl"

    f = r.TFile("ra1r/scan/%s/%s_T2cc_2015ea_%s.root" % (subDir, stem, label))
    if f.IsZombie():
        sys.exit()
    h = f.Get(hName)
    if h:
        h = h.Clone()
        h.SetDirectory(0)
        f.Close()
        return h
    else:
        print "ERROR: histogram %s:%s not found." % (f.GetName(), hName)


def bestFitContents(label=""):
    hVal = oneHisto(label=label,   hName="T2cc_poiVal")
    hErr = oneHisto(label=label,   hName="T2cc_poiErr")
    hSigma0 = oneHisto(label=label, hName="T2cc_nSigma_s0_sHat")
    if mode == "bestFit_binaryExcl":
        hSigma1 = oneHisto(label=label, hName="T2cc_nSigma_sNom_sHat")
    else:
        hSigma1 = None

    out = []
    if not all([hVal, hErr, hSigma0]):
        return out

    for (iBinX, x, iBinY, y, iBinZ, z) in utils.bins(hVal, interBin="LowEdge"):
        if iBinZ != 1:
            continue

        t = (iBinX, iBinY, iBinZ)
        val = hVal.GetBinContent(*t)
        err = hErr.GetBinContent(*t)
        n0 = hSigma0.GetBinContent(*t)
        n1 = hSigma1.GetBinContent(*t) if hSigma1 else None
        if val == 0.0 and err == 0.0:
            continue
        label = "%3d %3d" % (x, y)
        out.append((x, label, val, err, n0, n1))
    return out


def bestFitPlots(label=""):
    cont = bestFitContents(label)
    nBins = len(cont)
    if mode == "bestFit":
        words = "value #pm unc (pb)"
    if mode == "bestFit_binaryExcl":
        words = "factor #pm unc"

    poi = r.TH1D("poi", "%s;;best-fit xs %s" % (label, words), nBins, 0, nBins)
    poiX = poi.GetXaxis()

    poiR = r.TH1D("poiR", "%s;;best-fit xs / model xs" % label, nBins, 0, nBins)
    poiRX = poiR.GetXaxis()

    rel = r.TH1D("rel", "%s;;best-fit xs value / unc" % label, nBins, 0, nBins)
    relX = rel.GetXaxis()

    nllSigma0 = r.TH1D("nllSigma0", "%s;;#pm #sqrt{2 (nll_{xs = 0}  -  nll_{xs = best-fit})}" % label, nBins, 0, nBins)
    nllSigma0X = nllSigma0.GetXaxis()

    nllSigma1 = r.TH1D("nllSigma1", "%s;;#pm #sqrt{2 (nll_{xs = nom}  -  nll_{xs = best-fit})}" % label, nBins, 0, nBins)
    nllSigma1X = nllSigma1.GetXaxis()

    xs = r.TH1D("xs", "%s;;model xs (pb)" % label, nBins, 0, nBins)
    xsX = xs.GetXaxis()

    tfile = r.TFile("xs/sms_xs.root")
    xsSB = tfile.Get("stop_or_sbottom").Clone()
    xsSB.SetDirectory(0)
    tfile.Close()

    for i, (x, label, val, err, n0, n1) in enumerate(cont):
        iBin = 1 + i
        poi.SetBinContent(iBin, val)
        poi.SetBinError(iBin, err)
        poiX.SetBinLabel(iBin, label)

        xsVal = xsSB.GetBinContent(xsSB.FindBin(x))
        poiR.SetBinContent(iBin, val / xsVal)
        poiR.SetBinError(iBin, err / xsVal)
        poiRX.SetBinLabel(iBin, label)

        rel.SetBinContent(iBin, val/err)
        relX.SetBinLabel(iBin, label)
        
        nllSigma0.SetBinContent(iBin, n0)
        nllSigma0X.SetBinLabel(iBin, label)

        if mode == "bestFit_binaryExcl":
            nllSigma1.SetBinContent(iBin, n1)
            nllSigma1X.SetBinLabel(iBin, label)

        xs.SetBinContent(iBin, xsVal)
        xsX.SetBinLabel(iBin, label)

    if mode == "bestFit":
        return poi, poiR, rel, nllSigma0, xs
    elif mode == "bestFit_binaryExcl":
        return nllSigma1, poi, rel, nllSigma0, xs


def clbContents(label=""):
    hClb = oneHisto(label=label,   hName="T2cc_CLb")
    hCls = oneHisto(label=label,   hName="T2cc_CLs")
    hClsb = oneHisto(label=label,  hName="T2cc_CLs+b")

    out = []
    if not all([hClb, hCls]):
        return out

    for (iBinX, x, iBinY, y, iBinZ, z) in utils.bins(hClb, interBin="LowEdge"):
        if iBinZ != 1:
            continue

        t = (iBinX, iBinY, iBinZ)
        clb = hClb.GetBinContent(*t)
        cls = hCls.GetBinContent(*t)
        clsb = hClsb.GetBinContent(*t)
        if clb == 0.0:
            continue
        label = "%3d %3d" % (x, y)
        out.append((x, label, clb, cls, clsb))
    return out


def clPlots(label=""):
    cont = clbContents(label)
    nBins = len(cont)

    oneMinusCLb = r.TH1D("1-CLb", "%s;;1 - CL_{b}" % label, nBins, 0, nBins)
    oneMinusCLbX = oneMinusCLb.GetXaxis()

    hCls = r.TH1D("CLs", "%s;;CL_{s} = CL_{s+b} / CL_{b}" % label, nBins, 0, nBins)
    hClsX = hCls.GetXaxis()

    hClsb = r.TH1D("CLsb", "%s;;CL_{s+b}" % label, nBins, 0, nBins)
    hClsbX = hClsb.GetXaxis()

    oneMinusCLb_over_oneMinusCLsb = r.TH1D("1-CLb_over_1-CLsb", "%s;;(1 - CL_{b})  /  (1 - CL_{s+b})" % label, nBins, 0, nBins)
    oneMinusCLb_over_oneMInusCLsbX = oneMinusCLb_over_oneMinusCLsb.GetXaxis()

    for i, (x, label, clb, cls, clsb) in enumerate(cont):
        iBin = 1 + i
        oneMinusCLb.SetBinContent(iBin, 1.0 - clb)
        oneMinusCLbX.SetBinLabel(iBin, label)

        hCls.SetBinContent(iBin, cls)
        hClsX.SetBinLabel(iBin, label)

        hClsb.SetBinContent(iBin, clsb)
        hClsbX.SetBinLabel(iBin, label)

        oneMinusCLb_over_oneMinusCLsb.SetBinContent(iBin, (1.0 - clb) / (1.0 - clsb))
        oneMinusCLb_over_oneMInusCLsbX.SetBinLabel(iBin, label)

    return [hClsb, hCls, oneMinusCLb, oneMinusCLb_over_oneMinusCLsb]


def onePage(c, name="", label=""):
    if mode.startswith("bestFit"):
        hs = bestFitPlots(label)
    elif mode == "CL":
        hs = clPlots(label)
    else:
        assert False

    k = []
    line = r.TLine()

    for i, h in enumerate(hs):
        if i < 4:
            c.cd(1+i)
            h.Draw("p")
        elif mode == "bestFit":
            c.cd(1)
            h.SetLineColor(r.kRed)
            h.Draw("histsame")

        h.GetXaxis().SetLabelSize(2.0*h.GetXaxis().GetLabelSize())
        h.GetYaxis().SetLabelSize(1.5*h.GetYaxis().GetLabelSize())
        h.GetYaxis().SetTitleSize(2.0*h.GetYaxis().GetTitleSize())
        h.GetYaxis().SetTitleOffset(0.4)
        h.GetYaxis().CenterTitle()
        h.SetStats(False)
        h.SetMarkerColor(h.GetLineColor())
        h.SetMarkerStyle(20)
        h.SetMarkerSize(0.4 * h.GetMarkerSize())

        xMin = h.GetXaxis().GetXmin()
        xMax = h.GetXaxis().GetXmax()
        if mode.startswith("bestFit"):
            if i == 0 and mode == "bestFit_binaryExcl":
                h.SetMinimum(-4.0)
                yLine = 0.0
                k.append(line.DrawLine(xMin, yLine, xMax, yLine))
            if i:
                h.SetMinimum(0.0)
            if i == 1:
                h.SetMaximum(3.0)
                yLine = 1.0
                k.append(line.DrawLine(xMin, 1.0, xMax, 1.0))
        else:
            h.SetMinimum(0.0)
            h.SetMaximum(1.1)
            if i == 1:
                yLine = 0.05
                l2 = line.DrawLine(xMin, yLine, xMax, yLine)
                l2.SetLineColor(r.kRed)
                k.append(l2)
            if 2 <= i:
                h.SetMinimum(1.0e-2)
                h.SetMaximum(2.0)
                r.gPad.SetLogy()
                r.gPad.SetGridy()

        r.gPad.SetTopMargin(0.0)
        r.gPad.SetBottomMargin(0.17)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

    c.cd(0)
    c.Print(name)


def categories():
    indiv = ["0b_le3j", "0b_ge4j", "1b_ge4j", "1b_le3j"]  # ugh: order matters
    out = []
    #out += indiv
    #out += ["_".join(indiv[:2])]
    out += ["_".join(indiv[:3])]
    #out += ["_".join(indiv)]
    return out


def pdf(fileName=""):
    c = r.TCanvas()
    c.Divide(1, 4)

    c.Print("%s[" % fileName)

    for cat in categories():
        onePage(c, name=fileName, label=cat)

    c.Print("%s]" % fileName)
    os.system("cp -p %s ~/public_html/tmp/" % fileName)


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("e")

    # globals; used in oneHisto()
    #subdirs = ["non-universal-syst", "universal-syst-0b-le3j", "universal-syst-0b-ge4j"]
    subdirs = ["."]
    modes = ["bestFit", "bestFit_binaryExcl", "CL"][:]

    for mode in modes:
        for subDir in subdirs:
            pdf(fileName="%s%s.pdf" % (mode.replace("binaryExcl", "xsNom"), "_"+subDir if subDir != "." else ""))
