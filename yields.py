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
        if y1 and y2:
            out.SetPoint(iPoint, y1, y2)
            out.SetPointError(iPoint, yErr1, yErr2)
            iPoint += 1
    return out


def go(spec1={}, spec2={}, mode=None):
    canvas = r.TCanvas(mode, mode, 800, 600)

    assert mode in ["yields", "ratios", "scatter"], mode

    fileName = {"yields": "yields.pdf",
                "ratios": "yields_ratios.pdf",
                "scatter": "yields_scatter.pdf",
                }[mode]

    label1 = spec1["label"]
    if spec1["byLumi"]:
        label1 += "/L"
    label2 = spec2["label"]
    if spec2["byLumi"]:
        label2 += "/L"
    
    canvas.Print(fileName+"[")
    misc = []

    line = r.TLine()

    for name in ["0b_le3j", "1b_le3j", "2b_le3j", "3b_le3j",
                 "0b_ge4j", "1b_ge4j", "2b_ge4j", "3b_ge4j",
                 "ge4b_ge4j"]:

        canvas.cd(0)
        canvas.Clear()
        canvas.Divide(2, 2)

        card1 = getattr(spec1["mod"], "data_%s" % name)()
        card2 = getattr(spec2["mod"], "data_%s" % name)()
        #print dir(card1)
        #print card.htBinLowerEdges()
        for iKey, key in enumerate(["nHad", "nMuon", "nMumu", "nPhot"]):
            if ("2b" in name) or ("3b" in name) or ("ge4b" in name):
                if key in ["nMumu", "nPhot"]:
                    continue
            lumiKey = key[1:].lower()

            lumi1 = card1.lumi()[lumiKey]*spec1["lumiFactor"]
            lumi2 = card2.lumi()[lumiKey]*spec2["lumiFactor"]
            h1 = histo("%s_%s_1" % (name, key),
                       card1.htBinLowerEdges(),
                       card1.observations()[key])
            h2 = histo("%s_%s_2" % (name, key),
                       card2.htBinLowerEdges(),
                       card2.observations()[key])

            if spec1["byLumi"]:
                h1.Scale(1.0 / lumi1)
            if spec2["byLumi"]:
                h2.Scale(1.0 / lumi2)

            canvas.cd(1 + iKey)

            if mode == "yields":
                h1.Draw()
                h1.SetStats(False)
                h2.SetLineColor(r.kRed)
                h2.SetMarkerColor(r.kRed)
                h2.Draw("same")

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

                null = r.TH2D("null_"+gr.GetTitle(), gr.GetTitle(), 1, 0.5, 20.0e3, 1, 0.5, 20.0e3)
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


            r.gPad.SetTickx()
            r.gPad.SetTicky()

            misc.append(h1)
            misc.append(h2)

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
