#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.dirname(__file__)+"/..")

import ROOT as r
import utils


def oneHisto(hName="", label=""):
    f = r.TFile("ra1r/scan/%s/CLs_asymptotic_T2cc_2012dev_%s.root" % (subDir, label))
    if f.IsZombie():
        sys.exit()
    h = f.Get(hName)
    assert h
    h = h.Clone()
    h.SetDirectory(0)
    f.Close()
    return h

def contents(label=""):
    hVal = oneHisto(label=label,   hName="T2cc_poiVal")
    hErr = oneHisto(label=label,   hName="T2cc_poiErr")
    hSigma = oneHisto(label=label, hName="T2cc_nSigma")

    out = []
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


def oneD(label=""):
    cont = contents(label)
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


def onePage(c, name="", label=""):
    hs = oneD(label)
    xs = hs[-1]

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

        if i:
            h.SetMinimum(0.0)

        if i == 1:
            h.SetMaximum(3.0)
            k.append(line.DrawLine(h.GetXaxis().GetXmin(), 1.0, h.GetXaxis().GetXmax(), 1.0))
        r.gPad.SetTopMargin(0.0)
        r.gPad.SetBottomMargin(0.17)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

    c.cd(0)
    c.Print(name)


def categories():
    indiv = ["0b_le3j", "0b_ge4j", "1b_le3j", "1b_ge4j"]  # ugh: order matters
    out = []
    out += indiv
    out += ["_".join(indiv[:2])]
    out += ["_".join(indiv[:2]+indiv[-1:])]
    out += ["_".join(indiv)]
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

    # global; used in oneHisto()
    for subDir in ["non-universal-syst",
                   "universal-syst-0b-le3j",
                   "universal-syst-0b-ge4j",
                   ]:
        pdf(fileName="%s.pdf" % subDir)
