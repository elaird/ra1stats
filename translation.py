#!/usr/bin/env python

import ROOT as r
from array import array

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

def oneDataset(canvas = None, factors = None, data = None, name = "", iDataset = 0, color = None, afterTrigger = False) :
    htMeans = data.htMeans()

    if htMeans[-1]<1000. :
        htMax = 1045.
        print "WARNING: hacking HT mean %g  -->  %g for dataset %d"%(htMeans[-1], htMax, iDataset)
        htMeans = tuple(list(htMeans[:-1])+[htMax])

    graphs = []
    for i,tr in enumerate(factors) :
        canvas.cd(1+i)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

        trFactor,trFactorErr = data.translationFactor(tr, afterTrigger = afterTrigger)
        assert len(set([len(htMeans), len(trFactor), len(trFactorErr)]))==1

        gr = r.TGraphErrors()
        gr.SetName("%s%s%s"%(name, tr, "%d"%iDataset if iDataset else ""))
        gr.SetMarkerStyle(20)
        gr.SetLineColor(color)
        gr.SetMarkerColor(color)
        gr.SetTitle("%s: %s;<H_{T}> in bin (GeV); translation factor (%s trigger)"%(name, tr, "after" if afterTrigger else "before"))
        iGraph = 0
        for h,t,tE in zip(htMeans, trFactor, trFactorErr) :
            if t is None : continue
            gr.SetPoint(iGraph, h, t)
            gr.SetPointError(iGraph, 0.0, tE if tE else 0.0)
            iGraph += 1

        gr.Draw("psame" if iDataset else "ap")
        hist = gr.GetHistogram()
        for axis in [hist.GetXaxis(), hist.GetYaxis()] :
            axis.SetTitleSize(1.4*axis.GetTitleSize())
        hist.SetMinimum(0.0)
        graphs.append(gr)

    return graphs

def plot(datasets = []) :
    canvas = r.TCanvas("canvas", "canvas", 600, 800)

    fileName = "translation_factors.pdf"
    canvas.Print(fileName+"[")
    misc = []
    slices = datasets[0]["slices"] #assume first list of slices contains the subsequent ones
    for name in slices :
        canvas.cd(0)
        canvas.Clear()
        canvas.Divide(1, 3)
        leg = r.TLegend(0.6, 0.9, 0.85, 0.98)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)

        for iDataset,dct in enumerate(datasets) :
            attr = "data_%s"%name
            module = dct["module"]
            if not hasattr(module, attr) :
                continue
            data = getattr(module, attr)()
            graphs = oneDataset(canvas = canvas,
                                factors = ["gZ", "mumuZ", "muW"] if name!="ge3b" else ["muHad"],
                                data = getattr(module, "data_%s"%name)(),
                                name = name,
                                iDataset = iDataset,
                                color = dct["color"],
                                )
            leg.AddEntry(graphs[0], dct["label"], "lp")
            misc += graphs

        canvas.cd(0)
        leg.Draw()
        canvas.Print(fileName)
    canvas.Print(fileName+"]")


#2011
from inputData.data2011reorg import take3

#2012
from inputData.data2012 import take5,take5a,take5_capped,take5_unweighted
from inputData.data2012 import take6,take6_capped,take6_unweighted

datasets = [ {"module": take5,            "slices": ["0b_no_aT", "0b", "1b", "2b", "ge3b"], "color":1+r.kGray,  "label": "2012 (fully weighted; raw)"},
             {"module": take5a,           "slices": ["0b_no_aT", "0b", "1b", "2b", "ge3b"], "color":r.kBlack,   "label": "2012 (fully weighted; hacked)"},
             {"module": take5_capped,     "slices": ["0b", "1b", "2b", "ge3b"],             "color":r.kBlue,    "label": "2012 (weights capped at 5)"},
             {"module": take5_unweighted, "slices": ["0b", "1b", "2b", "ge3b"],             "color":r.kCyan,    "label": "2012 (unweighted)"},
             {"module": take3,            "slices": ["0b", "1b", "2b", "ge3b"],             "color":r.kMagenta, "label": "2011"},
             ]

datasets = [ {"module": take6,            "slices": ["0b_no_aT", "0b", "1b", "2b", "ge3b"], "color":1+r.kGray,  "label": "2012 (fully weighted; raw)"},
             {"module": take6_capped,     "slices": ["0b", "1b", "2b", "ge3b"],             "color":r.kBlue,    "label": "2012 (weights capped at 5)"},
             {"module": take6_unweighted, "slices": ["0b", "1b", "2b", "ge3b"],             "color":r.kCyan,    "label": "2012 (unweighted)"},
             #{"module": take3,            "slices": ["0b", "1b", "2b", "ge3b"],             "color":r.kMagenta, "label": "2011"},
             ]

#todo: what to minimize in a fit?
setup()
plot(datasets)
