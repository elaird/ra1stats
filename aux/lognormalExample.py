#!/usr/bin/env python

import ROOT as r

x     = r.RooRealVar("x", "observed value of rho", 1.0, 0.0, 10.0) #desire to be fixed
mu    = r.RooRealVar("mu","mean of gaussian", 1.0, 0.0, 3.0) #floating paramter in range [0-3]

sigmaValue = 0.3
sigma = r.RooRealVar("sigma","width of gaussian", sigmaValue) #fixed
k     = r.RooRealVar("k","shape param. for log-normal", r.TMath.Exp(sigmaValue)) #fixed

gauss     = r.RooGaussian("gauss","gaussian PDF", x, mu, sigma)
lognormal = r.RooLognormal("lognormal","lognormal PDF", x, mu, k)

x.Print()
mu.Print()
k.Print()
lognormal.Print()

xframe = x.frame(0.0, 5.0) #specify range
gauss.plotOn(xframe)
lognormal.plotOn(xframe)
xframe.Draw()
xframe.getAttLine().SetLineColor(r.kRed)
