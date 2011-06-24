#!/usr/bin/env python

import array,math,utils
from inputData import data2011
import ROOT as r

def setupRoot() :
    r.gROOT.SetBatch(True)
    r.gROOT.SetStyle("Plain")

def histo(inputData, name, title = "") :
    bins = array.array('d', list(inputData.htBinLowerEdges())+[inputData.htMaxForPlot()])
    out = r.TH1D(name, "%s;H_{T} (GeV);ratio"%title, len(bins)-1, bins)
    out.Sumw2()
    out.SetStats(False)
    return out

def fill(h, contents, errors) :
    h.Reset()
    for i,c,e in zip(range(len(contents)), contents, errors) :
        h.SetBinContent(1+i, c)
        h.SetBinError(1+i, e)

def go(label = None, yLabel = "", title = "", minMax = (0.0, 2.0), mcPhot = None, mcPhotErr = None, mcZinv = None, mcZinvErr = None, scale = 1.0) :
    ph = histo(data, "ph")
    fill(ph, mcPhot, mcPhotErr)
    
    z = histo(data, "z", title = title)
    fill(z, mcZinv, mcZinvErr)
    
    z.Divide(ph)
    z.Scale(scale)
    z.GetYaxis().SetTitle(yLabel)
    z.GetYaxis().SetRangeUser(*minMax)
    z.Draw()
    
    fileName = "%s.eps"%label
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Print(fileName)
    utils.epsToPdf(fileName)

setupRoot()
data = data2011()

go(label = "photons",
   yLabel = "Z#rightarrow #nu#bar{#nu} + jets / #gamma + jets",
   title = "Spring '11 MadGraph MC#semicolon RA1 selection",
   #minMax = (0.0, 1.5),
   mcPhot = data.mcExpectations()["mcPhot"],
   mcPhotErr = data.mcStatError()["mcPhotErr"],
   mcZinv = data.mcExpectations()["mcZinv"],
   mcZinvErr = data.mcStatError()["mcZinvErr"],
   scale = data.lumi()["phot"]/data.lumi()["had"]
   )

go(label = "muons",
   yLabel = "W#rightarrow #mu#nu + jets / W + jets (had. selection)",
   title = "Spring '11 MadGraph MC#semicolon RA1 selection",
   #minMax = (0.0, 1.5),
   mcPhot = data.mcExpectations()["mcMuon"],
   mcPhotErr = data.mcStatError()["mcMuonErr"],
   mcZinv = data.mcExpectations()["mcTtw"],
   mcZinvErr = data.mcStatError()["mcTtwErr"],
   scale = data.lumi()["muon"]/data.lumi()["had"]
   )
