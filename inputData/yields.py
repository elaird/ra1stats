#!/usr/bin/env python

import ROOT as r
from array import array

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000


def histo(name="", htLowers=[], yields=[]):
    h = r.TH1D(name, "%s;H_{T} (GeV); events / fb^{-1}" % name[:-2], (900-250)/25, 250.0, 900.0)
    for x, y in zip(htLowers, yields):
        if y is None:
            continue
        h.Fill(x, y)

    # shift overflows to final bin
    iFinalBin = h.GetNbinsX()
    h.SetBinContent(iFinalBin, h.GetBinContent(iFinalBin) + h.GetBinContent(1 + iFinalBin))
    h.SetBinContent(1 + iFinalBin, 0)

    # sqrt(n) error bars
    for iBinX in range(1, 1 + iFinalBin):
        h.SetBinError(iBinX, h.GetBinContent(iBinX)**0.5)

    return h

def graph(h1=None, h2=None):
    out = r.TGraphErrors()
    out.SetMarkerStyle(20)
    out.SetMarkerSize(0.4*out.GetMarkerSize())

    iPoint = 0
    for iBinX in range(1, 1 + h1.GetNbinsX()):
        y1 = h1.GetBinContent(iBinX)
        y2 = h2.GetBinContent(iBinX)
        yErr1 = h1.GetBinError(iBinX)
        yErr2 = h2.GetBinError(iBinX)
        if y1 or y2:
            if y1 == 0.0:
                y1 = graphMin
                yErr1 = 1.8 - graphMin

            if y2 == 0.0:
                y2 = graphMin
                yErr2 = 1.8 - graphMin

            out.SetPoint(iPoint, y1, y2)
            out.SetPointError(iPoint, yErr1, yErr2)
            iPoint += 1
    return out


def hMax(h=None):
    iBin = h.GetMaximumBin()
    return h.GetBinContent(iBin) + h.GetBinError(iBin)


def go(spec1={}, spec2={}, spec3={}, mode=None, stem=""):
    canvas = r.TCanvas(stem+mode, stem+mode, 800, 600)

    assert spec1
    assert spec2
    assert mode in ["yields", "ratios", "scatter"], mode
    fileName = "%s_%s.pdf" % (stem, mode)

    label1 = spec1["label"]
    if spec1["byLumi"]:
        label1 += "/L"
    label2 = spec2["label"]
    if spec2["byLumi"]:
        label2 += "/L"
    
    label3 = spec3.get("label", "")
    if spec3.get("byLumi"):
        label3 += "/L"

    canvas.Print(fileName+"[")
    misc = []

    line = r.TLine()

    leg = None
    for name in ["0b_le3j", "1b_le3j", "2b_le3j", "3b_le3j",
                 "0b_ge4j", "1b_ge4j", "2b_ge4j", "3b_ge4j",
                 "ge4b_ge4j"]:

        canvas.cd(0)
        canvas.Clear()
        canvas.Divide(2, 2)

        card1 = getattr(spec1["mod"], "data_%s" % name)()
        card2 = getattr(spec2["mod"], "data_%s" % name)()
        card3 = getattr(spec3["mod"], "data_%s" % name)() if spec3 else None
        #print dir(card1)
        #print card.htBinLowerEdges()
        for iKey, key in enumerate(["nHad", "nMuon", "nMumu", "nPhot"]):
            if ("2b" in name) or ("3b" in name) or ("ge4b" in name):
                if key in ["nMumu", "nPhot"]:
                    continue
            lumiKey = key[1:].lower()

            lumi1 = card1.lumi()[lumiKey]*spec1["lumiFactor"]
            lumi2 = card2.lumi()[lumiKey]*spec2["lumiFactor"]
            lumi3 = card3.lumi()[lumiKey]*spec3["lumiFactor"] if card3 else 0.0

            h1 = histo("%s_%s_1" % (name, key),
                       card1.htBinLowerEdges(),
                       card1.observations()[key])
            h2 = histo("%s_%s_2" % (name, key),
                       card2.htBinLowerEdges(),
                       card2.observations()[key])
            h3 = histo("%s_%s_3" % (name, key),
                       card3.htBinLowerEdges(),
                       card3.observations()[key]) if card3 else None

            if spec1["byLumi"]:
                h1.Scale(1.0 / lumi1)
            if spec2["byLumi"]:
                h2.Scale(1.0 / lumi2)
            if spec3.get("byLumi"):
                h3.Scale(1.0 / lumi3)

            misc += [h1, h2, h3]
            canvas.cd(1 + iKey)

            if mode == "yields":
                h1.SetMarkerStyle(21)
                h1.SetMarkerSize(0.4*h1.GetMarkerSize())
                h1.SetMarkerColor(h1.GetLineColor())
                h1.Draw("pe")
                h1.SetStats(False)

                h2.SetLineColor(r.kRed)
                h2.SetMarkerColor(r.kRed)
                h2.Draw("same")

                maxes = [hMax(h1), hMax(h2)]
                if h3:
                    h3.SetLineColor(8)
                    h3.SetMarkerColor(8)
                    h3.Draw("same")
                    maxes.append(hMax(h3))

                h1.GetYaxis().SetRangeUser(0.0, 1.1*max(maxes))

                if leg is None:
                    leg = r.TLegend(0.65, 0.65, 0.85, 0.85)
                    leg.SetBorderSize(0)
                    leg.SetFillStyle(0)
                    leg.AddEntry(h1, label1, "le")
                    leg.AddEntry(h2, label2, "le")
                    if h3:
                        leg.AddEntry(h3, label3, "le")
                    misc.append(leg)
                leg.Draw("same")

            if mode == "ratios":
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
                gr = graph(h2, h1)
                gr.SetName(h2.GetTitle())
                gr.SetTitle("%s;%s  (%4.1f/fb);%s  (%4.1f/fb)" % (h2.GetTitle(), label2, lumi2, label1, lumi1))

                null = r.TH2D("null_"+gr.GetTitle(), gr.GetTitle(), 1, graphMin, graphMax, 1, graphMin, graphMax)
                null.SetStats(False)
                null.Draw()

                one = r.TF1("one", "(%g)*x" % (lumi1/lumi2), null.GetXaxis().GetXmin(), null.GetXaxis().GetXmax())
                one.SetLineWidth(1)
                one.Draw("same")
                if gr.GetN():
                    gr.Draw("zpsame")

                misc += [gr, one, null]
                r.gPad.SetLogx()
                r.gPad.SetLogy()

                if leg is None:
                    leg = r.TLegend(0.15, 0.65, 0.45, 0.85)
                    leg.SetBorderSize(0)
                    leg.SetFillStyle(0)
                    leg.AddEntry(one, "y = (%4.1f/%4.1f) x" % (lumi1, lumi2), "l")
                    misc.append(leg)
                leg.Draw("same")


            r.gPad.SetTickx()
            r.gPad.SetTicky()

        canvas.Print(fileName)

    canvas.Print(fileName+"]")


if __name__ == "__main__":
    from inputData.data2012hcp import take14
    from inputData.data2012dev import take0, take8
    from inputData.data2012dev import take9_B, take9_C, take9_BC, take9_D

    graphMin = 0.5
    graphMax = 20.0e3

    setup()
    for mode in ["yields", "ratios", "scatter"]:
        go(mode=mode, stem="full",
           spec1={"mod": take14, "label": "ABC_P", "lumiFactor": 1.0e-3, "byLumi": mode != "scatter"},
           spec2={"mod": take8,  "label": "BCD_R", "lumiFactor": 1.0,    "byLumi": mode != "scatter"},
           )

        go(mode=mode, stem="rereco",
           spec1={"mod": take14,   "label": "ABC_P", "lumiFactor": 1.0e-3, "byLumi": mode != "scatter"},
           spec2={"mod": take9_BC, "label": "BC_R",  "lumiFactor": 1.0,    "byLumi": mode != "scatter"},
           )

        go(mode=mode, stem="newdata",
           spec1={"mod": take9_D,  "label": "D_R",  "lumiFactor": 1.0, "byLumi": mode != "scatter"},
           spec2={"mod": take9_BC, "label": "BC_R", "lumiFactor": 1.0, "byLumi": mode != "scatter"},
           )

    go(mode="yields", stem="eras",
       spec1={"mod": take9_B, "label": "B_R", "lumiFactor": 1.0, "byLumi": True},
       spec2={"mod": take9_C, "label": "C_R", "lumiFactor": 1.0, "byLumi": True},
       spec3={"mod": take9_D, "label": "D_R", "lumiFactor": 1.0, "byLumi": True},
       )
