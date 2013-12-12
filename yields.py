#!/usr/bin/env python

import ROOT as r
from array import array

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000


def histo(name="", htLowers=[], yields=[], lumi=None):
    h = r.TH1D(name, "%s;H_{T} (GeV); events / fb^{-1}" % name[:-2], 12*4, 0.0, 1200.0)
    for x, y in zip(htLowers, yields):
        if y is None:
            continue
        iBin = h.FindBin(x)
        den = lumi if lumi else 1.0
        h.SetBinContent(iBin, y / den)
        h.SetBinError(iBin, (y**0.5) / den)
    return h


def go(spec1={}, spec2={}, mode=None):
    canvas = r.TCanvas("canvas", "canvas", 800, 600)

    assert mode in ["yields", "ratios", "scatter"], mode

    fileName = {"yields": "yields.pdf",
                "ratios": "yields_ratios.pdf",
                "scatter": "yields_scatter.pdf",
                }[mode]

    label1 = spec1["label"]
    if spec1["lumiFactor"]:
        label1 += "/L"
    label2 = spec2["label"]
    if spec2["lumiFactor"]:
        label2 += "/L"
    
    canvas.Print(fileName+"[")
    misc = []

    line = r.TLine()

    graph = r.TGraph()
    iGraphPoint = 0

    for name in ["0b_le3j", "1b_le3j", "2b_le3j", "3b_le3j",
                 "0b_ge4j", "1b_ge4j", "2b_ge4j", "3b_ge4j",
                 "ge4b_ge4j"]:

        if mode != "scatter":
            canvas.cd(0)
            canvas.Clear()
            canvas.Divide(2, 2)

        card1 = getattr(spec1["mod"], "data_%s" % name)()
        card2 = getattr(spec2["mod"], "data_%s" % name)()
        #print dir(card1)
        #print card.htBinLowerEdges()
        for iKey, key in enumerate(["nHad", "nMuon", "nMumu", "nPhot"]):
            lumiKey = key[1:].lower()
            h1 = histo("%s_%s_1" % (name, key),
                       card1.htBinLowerEdges(),
                       card1.observations()[key],
                       lumi=card1.lumi()[lumiKey]*spec1["lumiFactor"] if spec1["byLumi"] else 0.0)
            h2 = histo("%s_%s_2" % (name, key),
                       card2.htBinLowerEdges(),
                       card2.observations()[key],
                       lumi=card2.lumi()[lumiKey]*spec2["lumiFactor"] if spec2["byLumi"] else 0.0)

            if mode == "yields":
                canvas.cd(1 + iKey)
                h1.Draw()
                h1.SetStats(False)
                h2.SetLineColor(r.kRed)
                h2.SetMarkerColor(r.kRed)
                h2.Draw("same")

            if mode == "ratios":
                canvas.cd(1 + iKey)
                h2.Divide(h1)
                for iBinX in range(1, 1 + h1.GetNbinsX()):
                    relError1 = h1.GetBinError(iBinX)/h1.GetBinContent(iBinX) if h1.GetBinContent(iBinX) else 0.0
                    h2.SetBinError(iBinX, h2.GetBinContent(iBinX)*relError1)
                h2.Draw()
                h2.SetStats(False)
                h2.SetMinimum(0.5)
                h2.SetMaximum(1.5)
                h2.GetYaxis().SetTitle("%s   /   %s" % (label2, label1))
                misc += [line.DrawLine(h2.GetXaxis().GetXmin(), 1.05, h2.GetXaxis().GetXmax(), 1.05),
                         line.DrawLine(h2.GetXaxis().GetXmin(), 0.95, h2.GetXaxis().GetXmax(), 0.95),
                         ]

            if mode == "scatter":
                for iBinX in range(1, 1 + h1.GetNbinsX()):
                    y1 = h1.GetBinContent(iBinX)
                    y2 = h2.GetBinContent(iBinX)
                    if y1 and y2:
                        graph.SetPoint(iGraphPoint, y2, y1)
                        iGraphPoint += 1
                graph.SetTitle(";%s;%s" % (label2, label1))

            r.gPad.SetTickx()
            r.gPad.SetTicky()

            misc.append(h1)
            misc.append(h2)

        if mode != "scatter":
            canvas.cd(0)
            canvas.Print(fileName)

    if mode == "scatter":
        graph.SetMarkerStyle(20)

        if True:
            null = r.TH2D("null", graph.GetTitle(), 1, 0.5, 20.0e3, 1, 0.5, 20.0e3)
            null.SetStats(False)
            null.Draw()

            one = r.TF1("one", "(%g)*x" % (1.0), null.GetXaxis().GetXmin(), null.GetXaxis().GetXmax())
            one.Draw("same")
            graph.Draw("psame")
        else:
            graph.Draw("ap")
        r.gPad.SetLogx()
        r.gPad.SetLogy()
        canvas.Print(fileName)

    canvas.Print(fileName+"]")


if __name__ == "__main__":
    from inputData.data2012hcp import take14
    from inputData.data2012dev import take0, take8

    setup()
    for mode in ["yields", "ratios", "scatter"]:
        go(mode=mode,
           spec1={"mod": take14, "label": "ABC_P", "lumiFactor": 1.0e-3, "byLumi": mode != "scatter"},
           spec2={"mod": take8,  "label": "BCD_R", "lumiFactor": 1.0,    "byLumi": mode != "scatter"},
           )
