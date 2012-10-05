#!/usr/bin/env python

import ROOT as r

x     = r.RooRealVar("x", "x", 1.0, 0.0, 10.0) #desire to be fixed
mu    = r.RooRealVar("mu","mean of gaussian", 1.0, 0.0, 3.0) #floating paramter in range [0-3]

sigmaValues = [0.1, 0.2, 0.26, 0.4]
canvas = r.TCanvas()
canvas.Divide(len(sigmaValues), 1)

keep = []
text = r.TLatex()
text.SetNDC()

color = {"gauss":r.kRed,
         "lognormal":r.kBlue,
         }

for i,sigmaValue in enumerate(sigmaValues) :
    canvas.cd(1+i)
    sigma = r.RooRealVar("sigma","width of gaussian", sigmaValue) #fixed
    k     = r.RooRealVar("k","shape param. for log-normal", r.TMath.Exp(sigmaValue)) #fixed

    gauss     = r.RooGaussian("gauss","gaussian PDF", x, mu, sigma)
    lognormal = r.RooLognormal("lognormal","lognormal PDF", x, mu, k)

    xframe = x.frame(0.0, 3.0) #specify range

    for item in [gauss, lognormal] :
        item.plotOn(xframe)
        xframe.getAttLine().SetLineColor(color[item.GetName()])

    xframe.Draw()

    text.SetTextColor(r.kBlack)
    keep.append( text.DrawLatex(0.5, 0.8, "#mu = 1.0,   #sigma = %4.2f"%sigmaValue) )

    for i,item in enumerate([gauss, lognormal]) :
        name = item.GetName()
        text.SetTextColor(color[name])
        keep.append( text.DrawLatex(0.5, 0.8-0.04*(1+i), name) )

    r.gPad.SetTickx()
    r.gPad.SetTicky()

canvas.cd(0)
canvas.Print("lognormal.pdf")
