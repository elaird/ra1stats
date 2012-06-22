#!/usr/bin/env python

import ROOT as r
from array import array

##2011
#from inputData.data2011reorg import take3 as module
#slices = ["0b", "1b", "2b", "ge3b"]

#2012
from inputData.data2012 import take5a as module
slices = ["0b_no_aT", "0b", "1b", "2b", "ge3b"]

#todo: what to minimize in a fit?

r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000

canvas = r.TCanvas("canvas", "canvas", 600, 800)

afterTrigger = False
fileName = "tr.pdf"
canvas.Print(fileName+"[")
for dataset in slices :
    d = getattr(module, "data_%s"%dataset)()
    htMeans = d.htMeans()
    factors = ["gZ", "mumuZ", "muW"] if dataset!="ge3b" else ["muHad"]
    canvas.cd(0)
    canvas.Clear()
    canvas.Divide(1, 3)
    graphs = []
    for i,tr in enumerate(factors) :
        canvas.cd(1+i)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

        trFactor,trFactorErr = d.translationFactor(tr, afterTrigger = afterTrigger)
        assert len(set([len(htMeans), len(trFactor), len(trFactorErr)]))==1

        gr = r.TGraphErrors()
        gr.SetName("%s%s"%(dataset,tr))
        gr.SetMarkerStyle(20)
        gr.SetTitle("%s: %s;<H_{T}> in bin (GeV); translation factor (%s trigger)"%(dataset, tr, "after" if afterTrigger else "before"))
        iGraph = 0
        for h,t,tE in zip(htMeans, trFactor, trFactorErr) :
            if t is None : continue
            gr.SetPoint(iGraph, h, t)
            gr.SetPointError(iGraph, 0.0, tE)
            iGraph += 1

        gr.Draw("ap")
        hist = gr.GetHistogram()
        for axis in [hist.GetXaxis(), hist.GetYaxis()] :
            axis.SetTitleSize(1.4*axis.GetTitleSize())
        hist.SetMinimum(0.0)

        graphs.append(gr)
    canvas.Print(fileName)

canvas.Print(fileName+"]")
