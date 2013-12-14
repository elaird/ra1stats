#!/usr/bin/env python

import ROOT as r
from array import array

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

def plotRatio(canvas=None, factors=None, graphs=None, data=None, name=None, datasets=[], leg=None):
    htMeans = data.htMeans()
    nDataset = len(datasets)
    graphsToReturn = []

    for i,tr in enumerate(factors):
        canvas.cd(i+1)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

        grName = []
        grs = []
        for iDataset, dataset in enumerate(datasets):
            grName.append(name+tr+("%d"%iDataset if iDataset else ""))
            
        for gr in graphs:
            if gr.GetName() in grName: grs.append(gr)

        rgr = r.TGraphErrors()
        rgr.SetName("%s%s_ratios"%(name, tr))
        rgr.SetMarkerStyle(20)
        rgr.SetLineColor(r.kRed)
        rgr.SetMarkerColor(r.kRed)
        rgr.SetTitle("%s: %s;<H_{T}> in bin (GeV); translation factor ratio"%(name, tr))

        hPoint = 0
        hrPoint = 0
        for hPoint, ht in enumerate(htMeans):
            t=[]
            dPoint = 0
            for igr, gr in enumerate(grs) :
                tf = r.Double(0)
                Ht = r.Double(0)
                gr.GetPoint(hPoint, Ht, tf)
                t.append(tf)
            for itf, tf in enumerate(t):
                if not itf: continue
                if t[0] == 0.0: continue
                ratio = t[itf]/t[0]
                #print "itf",itf,"hrPoint",hrPoint,"Ht", Ht, "t[itf]",t[itf],"t[0]",t[0], "ratio", ratio
                rgr.SetPoint(hrPoint, Ht, ratio)
            hPoint += 1
            hrPoint += 1
        rgr.Draw("ap")
        hist = rgr.GetHistogram()
        for axis in [hist.GetXaxis(), hist.GetYaxis()] :
            axis.SetTitleSize(1.4*axis.GetTitleSize())
        graphsToReturn.append(rgr)
    return graphsToReturn

def oneDataset(canvas = None, factors = None, data = None, name = "", iDataset = 0, color = None, afterTrigger = False) :
    htMeans = data.htMeans()

    #if htMeans[-1]<1000. :
    #    htMax = 1045.
    #    print "WARNING: hacking HT mean %g  -->  %g for dataset %d"%(htMeans[-1], htMax, iDataset)
    #    htMeans = tuple(list(htMeans[:-1])+[htMax])

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

def plot(datasets = [], tag = "", factors = ["gZ", "mumuZ", "muW"]) :
    canvas = r.TCanvas("canvas", "canvas", 600, 800)


    fileName = "plots/translation_factors_%s.pdf"%tag
    canvas.Print(fileName+"[")
    misc = []
    slices = datasets[0]["slices"] #assume first list of slices contains the subsequent ones
    for name in slices :
        canvas.cd(0)
        canvas.Clear()
        canvas.Divide(1, 3)
        leg = r.TLegend(0.5, 0.92, 0.9, 0.98)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)

        for iDataset,dct in enumerate(datasets) :
            attr = "data_%s"%name
            module = dct["module"]
            if not hasattr(module, attr) :
                continue
            data = getattr(module, attr)()
            graphs = oneDataset(canvas = canvas,
                                factors = factors if name!="ge3b" else ["muHad"],
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
    canvas.Clear()

    ratioFileName = "plots/ratio_translation_factors_%s.pdf"%tag
    canvas.Print(ratioFileName+"[")
    for name in slices:
        canvas.cd(0)
        canvas.Clear()
        canvas.Divide(1, 3)
        rgr = plotRatio(canvas = canvas,
                        factors = factors if name!="ge3b" else ["muHad"],
                        graphs = misc,
                        data = getattr(module, "data_%s"%name)(),
                        name = name,
                        datasets = datasets,
                        leg = leg
                        )
        canvas.cd(0)
        canvas.Print(ratioFileName)    
    canvas.Print(ratioFileName+"]")
    canvas.Delete()


##########
from inputData.dataMisc import orig
from inputData.data2011reorg import take3
from inputData.data2012hcp import take5,take5a,take5_capped,take5_unweighted
from inputData.data2012hcp import take6,take6_capped,take6_unweighted
from inputData.data2012hcp import take12_weighted,take12_unweighted,take14
from inputData.data2012dev import take0,take1,take3,take5,take5_noMHTMET

setup()

d = ["2010", "2011eps", "2011", "2012ichep", "2012hcp", "2012dev"][-1]
if d=="2010" :
    datasets = [ {"module": orig, "slices": ["2010"], "color":r.kBlack,  "label": "2010"},
                 ]
    plot(datasets, tag = d, factors = ["gZ", "muW"])
elif d=="2011eps" :
    datasets = [ {"module": orig, "slices": ["2011_4"], "color":r.kBlue, "label": "2011 (EPS)"},
                 ]
    plot(datasets, tag = d, factors = ["gZ", "muW"])
elif d=="2011" :
    datasets = [ {"module": take3,            "slices": ["0b", "1b", "2b", "ge3b"],
                  "color":r.kMagenta, "label": "2011"},
                 ]
    plot(datasets, tag = d)
elif d=="2012ichep" :
    datasets = [ {"module": take5,            "slices": ["0b_no_aT", "0b", "1b", "2b", "ge3b"],
                  "color":1+r.kGray,  "label": "2012 (fully weighted; raw)"},
                 {"module": take5a,           "slices": ["0b_no_aT", "0b", "1b", "2b", "ge3b"],
                  "color":r.kBlack,   "label": "2012 (fully weighted; hacked)"},
                 {"module": take5_capped,     "slices": ["0b", "1b", "2b", "ge3b"],
                  "color":r.kBlue,    "label": "2012 (weights capped at 5)"},
                 {"module": take5_unweighted, "slices": ["0b", "1b", "2b", "ge3b"],
                  "color":r.kCyan,    "label": "2012 (unweighted)"},
                 {"module": take3,            "slices": ["0b", "1b", "2b", "ge3b"],
                  "color":r.kMagenta, "label": "2011"},
                 ]
    plot(datasets, tag = d)
elif d=="2012ichep_5fb" :
    datasets = [ {"module": take6,            "slices": ["0b_no_aT", "0b", "1b", "2b", "ge3b"],
                  "color":1+r.kGray,  "label": "2012 (fully weighted; raw)"},
                 {"module": take6_capped,     "slices": ["0b", "1b", "2b", "ge3b"],
                  "color":r.kBlue,    "label": "2012 (weights capped at 5)"},
                 {"module": take6_unweighted, "slices": ["0b", "1b", "2b", "ge3b"],
                  "color":r.kCyan,    "label": "2012 (unweighted)"},
                 #{"module": take3,            "slices": ["0b", "1b", "2b", "ge3b"],
                 # "color":r.kMagenta, "label": "2011"},
                 ]
    plot(datasets, tag = d)
elif d=="2012hcp" :
    color1 = {"ge2j":r.kBlack, "ge4j":r.kRed, "le3j":r.kBlue}
    color2 = {"ge2j":r.kGray, "ge4j":r.kOrange, "le3j":r.kCyan}

    for i,j in enumerate(["ge4j", "le3j"]) :
        bs = ["0b", "1b", "2b"]+(["3b", "ge4b"] if j!="le3j" else [])
        slices = ["%s_%s"%(b,j) for b in bs]
        datasets = [ {"module": take12_weighted, "slices": slices, "color":color1[j], "label": "2012 HCP (%s, weighted)"%j},
                     {"module": take12_unweighted, "slices": slices, "color":color2[j], "label": "2012 HCP (%s, unweighted)"%j},
                     ]
        #print datasets
        plot(datasets, tag = j)
elif d=="2012dev" :
    color1 = {"ge2j":r.kBlack, "ge4j":r.kRed,    "le3j":r.kBlue}
    color2 = {"ge2j":r.kGray,  "ge4j":r.kOrange, "le3j":r.kCyan}

    for i,j in enumerate(["ge4j", "le3j"]) :
        bs = ["0b", "1b", "2b", "3b"]+(["ge4b"] if j!="le3j" else [])
        slices = ["%s_%s"%(b,j) for b in bs]
        datasets = [ {"module": take5, "slices": slices, "color":color1[j], "label": "2012 dev (%s, weighted)"%j},
                     {"module": take5_noMHTMET, "slices": slices, "color":color2[j], "label": "2012 dev w/o MHT/MET sideband weights (%s, weighted)"%j},
                     ]
        #print datasets
        plot(datasets, tag = j)
else :
    print "ERROR: dataset not recognized."
