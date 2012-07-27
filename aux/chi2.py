#!/usr/bin/env python

import utils
from math import sqrt
import ROOT as r

rand = r.TRandom3(1)

def chi2ProbList(nTerms = None, mu = None, distribution = "", nPseudoExperiments = None, debug = False) :
    assert distribution in ["Poisson"],distribution
    func = getattr(rand, distribution)
    args = (mu,) if distribution=="Poisson" else (mu, mu**0.5)

    out = []
    for iPseudo in range(nPseudoExperiments) :
        chi2 = 0.0
        if debug : print "iPseudo=%d"%iPseudo
        for iBin in range(nTerms) :
            n = func(*args)
            chi2 += (n-mu)**2/mu
            if debug : print "iBin=%d, n=%d"%(iBin,n)

        out.append(r.TMath.Prob(chi2, nTerms))
    return out

def histo(name = "", title = "", lst = []) :
    nBins = 20
    h = r.TH1D(name, title, nBins, 0.0, 1.0)
    h.Sumw2()
    h.SetStats(False)
    h.SetMinimum(0.0)
    h.SetMarkerStyle(20)
    h.SetMarkerSize(0.3*h.GetMarkerSize())
    h.GetYaxis().SetTitleOffset(1.5)
    h.GetXaxis().SetTitleOffset(1.3)
    for x in lst :
        h.Fill(x)
    return h

def go(mus = [], nTerms = 1, nPseudoExperiments = 1000) :
    dct = {}
    for mu in mus :
        lst = chi2ProbList(nTerms = nTerms, mu = mu, distribution = "Poisson", nPseudoExperiments = nPseudoExperiments)
        name = "#mu = %g"%mu
        title = ";".join([name,
                          "Prob(#chi^{2}, %d)#semicolon    #chi^{2} #equiv #Sigma_{i=0}^{%d}(n_{i}-#mu)^{2}/#mu"%(nTerms, nTerms),
                          "pseudo-experiments / bin"])
        dct[mu] = histo(name = name, title = title, lst = lst)

    #unify histo maxes
    histoMax = 1.1*max(h.GetMaximum() for h in dct.values())
    [h.SetMaximum(histoMax) for h in dct.values()]
        
    canvas = r.TCanvas("canvas","",2)
    utils.cyclePlot(d = dct, canvas = canvas, fileName = "chi2.pdf", divide = (2,2), goptions = "", ticks = True)

go(mus = [0.5, 3.0, 16.0, 400.0], nTerms = 100, nPseudoExperiments = 10000)
#go(mus = [0.5])
