#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.dirname(__file__)+"/..")

import ROOT as r
import utils


def oneHisto(hName="", label=""):
    if mode == "bestFit":
        stem = "nlls"
    if mode == "CL":
        stem = "CLs_asymptotic_binaryExcl"

    f = r.TFile("ra1r/scan/%s/%s_T2cc_2012dev_%s.root" % (subDir, stem, label))
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
    hSigma = oneHisto(label=label, hName="T2cc_nSigma_s0_sHat")

    out = []
    if not all([hVal, hErr, hSigma]):
        return out

    for (iBinX, x, iBinY, y, iBinZ, z) in utils.bins(hVal, interBin="LowEdge"):
        if iBinZ != 1:
            continue

        t = (iBinX, iBinY, iBinZ)
        val = hVal.GetBinContent(*t)
        err = hErr.GetBinContent(*t)
        n = hSigma.GetBinContent(*t)
        if val == 0.0 and err == 0.0:
            continue
        label = "%3d %3d" % (x, y)
        out.append((x, label, val, err, n))
    return out


def bestFitPlots(label=""):
    cont = bestFitContents(label)
    nBins = len(cont)
    poi = r.TH1D("poi", "%s;;best-fit xs value #pm unc (pb)" % label, nBins, 0, nBins)
    poiX = poi.GetXaxis()

    poiR = r.TH1D("poiR", "%s;;best-fit xs / model xs" % label, nBins, 0, nBins)
    poiRX = poiR.GetXaxis()

    rel = r.TH1D("rel", "%s;;best-fit xs value / unc" % label, nBins, 0, nBins)
    relX = rel.GetXaxis()

    nllSigma = r.TH1D("nllSigma", "%s;;#sqrt{2 (nll_{xs = 0}  -  nll_{xs = best-fit})}" % label, nBins, 0, nBins)
    nllSigmaX = nllSigma.GetXaxis()

    xs = r.TH1D("xs", "%s;;model xs (pb)" % label, nBins, 0, nBins)
    xsX = xs.GetXaxis()

    tfile = r.TFile("xs/sms_xs.root")
    xsSB = tfile.Get("stop_or_sbottom").Clone()
    xsSB.SetDirectory(0)
    tfile.Close()

    for i, (x, label, val, err, n) in enumerate(cont):
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
        
        nllSigma.SetBinContent(iBin, n)
        nllSigmaX.SetBinLabel(iBin, label)

        xs.SetBinContent(iBin, xsVal)
        xsX.SetBinLabel(iBin, label)
        
    return poi, poiR, rel, nllSigma, xs


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

    hCls = r.TH1D("CLs", "%s;;CL_{s}" % label, nBins, 0, nBins)
    hClsX = hCls.GetXaxis()

    hClsb = r.TH1D("CLsb", "%s;;CL_{s+b}" % label, nBins, 0, nBins)
    hClsbX = hClsb.GetXaxis()

    for i, (x, label, clb, cls, clsb) in enumerate(cont):
        iBin = 1 + i
        oneMinusCLb.SetBinContent(iBin, 1.0 - clb)
        oneMinusCLbX.SetBinLabel(iBin, label)

        hCls.SetBinContent(iBin, cls)
        hClsX.SetBinLabel(iBin, label)

        hClsb.SetBinContent(iBin, clsb)
        hClsbX.SetBinLabel(iBin, label)

    return [oneMinusCLb, hClsb, hCls]


def onePage(c, name="", label="", mode=""):
    if mode == "bestFit":
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
            h.Draw()
        else:
            c.cd(1)
            h.SetLineColor(r.kRed)
            h.Draw("same")

        h.GetXaxis().SetLabelSize(2.0*h.GetXaxis().GetLabelSize())
        h.GetYaxis().SetTitleSize(2.0*h.GetYaxis().GetTitleSize())
        h.GetYaxis().SetTitleOffset(0.4)
        h.GetYaxis().CenterTitle()
        h.SetStats(False)

        if mode == "bestFit":
            if i:
                h.SetMinimum(0.0)
            if i == 1:
                h.SetMaximum(3.0)
                k.append(line.DrawLine(h.GetXaxis().GetXmin(), 1.0, h.GetXaxis().GetXmax(), 1.0))
        else:
            h.SetMinimum(0.0)
            h.SetMaximum(1.0)
            if i == 2:
                l2 = line.DrawLine(h.GetXaxis().GetXmin(), 0.05, h.GetXaxis().GetXmax(), 0.05)
                l2.SetLineColor(r.kRed)
                k.append(l2)

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


def pdf(fileName="", mode=""):
    c = r.TCanvas()
    if mode == "bestFit":
        c.Divide(1, 4)
    else:
        c.Divide(1, 3)

    c.Print("%s[" % fileName)

    for cat in categories():
        onePage(c, name=fileName, label=cat, mode=mode)

    c.Print("%s]" % fileName)
    os.system("cp -p %s ~/public_html/tmp/" % fileName)


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("e")

    # globals; used in oneHisto()
    #subdirs = ["non-universal-syst", "universal-syst-0b-le3j", "universal-syst-0b-ge4j"]
    subdirs = ["."]
    mode = ["bestFit", "CL"][1]

    for subDir in subdirs:
        pdf(mode=mode,
            fileName="%s%s.pdf" % (mode, "_"+subDir if subDir != "." else ""))
