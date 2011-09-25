#!/usr/bin/env python

import array,math,utils
from inputData import data2011
import ROOT as r

def setupRoot() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    #r.gROOT.SetStyle("Plain")
    r.gStyle.SetOptStat(0)
    r.gStyle.SetOptFit(1011)

def histo(inputData, name, title = "") :
    bins = array.array('d', list(inputData.htBinLowerEdges())+[inputData.htMaxForPlot()])
    out = r.TH1D(name, "%s;H_{T} (GeV);ratio"%title, len(bins)-1, bins)
    out.Sumw2()
    #out.SetStats(False)
    return out

def fill(h, contents, errors) :
    h.Reset()
    for i,c,e in zip(range(len(contents)), contents, errors) :
        h.SetBinContent(1+i, c)
        h.SetBinError(1+i, e)

def go(label = None, yLabel = "", title = "", minMax = (0.0, 2.0), mcPhot = None, mcPhotErr = None, mcZinv = None, mcZinvErr = None, sysFactor = None, scale = 1.0) :
    ph = histo(data, "ph")
    fill(ph, mcPhot, mcPhotErr)
    
    z = histo(data, "z", title = title)
    fill(z, mcZinv, mcZinvErr)
    
    z.Divide(ph)
    z.Scale(scale)
    z.GetYaxis().SetTitle(yLabel)
    z.GetYaxis().SetRangeUser(*minMax)
    z.Draw()

    z.Fit("pol0", "fq")
    f = z.GetListOfFunctions().At(0)
    value = f.GetParameter(0)    
    f.SetLineColor(r.kBlue)
    f.SetLineWidth(2)

    b = r.TBox()
    b.SetFillStyle(1)
    b.SetLineColor(r.kRed)
    box = b.DrawBox(z.GetXaxis().GetXmin(), value*(1.0-sysFactor), z.GetXaxis().GetXmax(), value*(1.0+sysFactor))

    leg = r.TLegend(0.15, 0.85, 0.65, 0.65)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(z, "ratio from MC (error bars are from MC stats)", "pl")
    leg.AddEntry(f, "fit to constant", "l")
    leg.AddEntry(b, "systematic error band (theo. + exp.)", "l")

    leg.Draw()
    fileName = "%s.eps"%label
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.Print(fileName)
    utils.epsToPdf(fileName)

setupRoot()
data = data2011(requireFullImplementation = False)

go(label = "photons",
   yLabel = "Z#rightarrow #nu#bar{#nu} + jets / #gamma + jets",
   title = "Spring '11 MadGraph MC#semicolon RA1 selection",
   #minMax = (0.0, 1.5),
   mcPhot = data.mcExpectations()["mcGjets"],
   mcPhotErr = data.mcStatError()["mcGjetsErr"],
   mcZinv = data.mcExpectations()["mcZinv"],
   mcZinvErr = data.mcStatError()["mcZinvErr"],
   sysFactor = data.fixedParameters()["sigmaPhotZ"],
   scale = data.lumi()["phot"]/data.lumi()["had"]
   )

go(label = "muons",
   yLabel = "t#bar{t} + W (had. selection) / t#bar{t} + W (#mu selection)",
   title = "Summer '11 MadGraph MC#semicolon RA1 selection",
   minMax = (0.0, 2.5),
   mcPhot = data.mcExpectations()["mcMuon"],
   mcPhotErr = data.mcStatError()["mcMuonErr"],
   mcZinv = data.mcExpectations()["mcTtw"],
   mcZinvErr = data.mcStatError()["mcTtwErr"],
   sysFactor = data.fixedParameters()["sigmaMuonW"],   
   scale = data.lumi()["muon"]/data.lumi()["had"]
   )

go(label = "mumu",
   yLabel = "Z#rightarrow#nu#bar{#nu} / Z#rightarrow#mu#bar{#mu}",
   title = "Spring '11 MadGraph MC#semicolon RA1 selection",
   minMax = (0.0, 15),
   mcPhot = data.mcExpectations()["mcZmumu"],
   mcPhotErr = data.mcStatError()["mcZmumuErr"],
   mcZinv = data.mcExpectations()["mcZinv"],
   mcZinvErr = data.mcStatError()["mcZinvErr"],
   sysFactor = data.fixedParameters()["sigmaMumuZ"],   
   scale = data.lumi()["mumu"]/data.lumi()["had"]
   )

go(label = "photons_to_muons",
   yLabel = "MC muon selected / MC photon selected",
   title = "Spring '11 MadGraph MC#semicolon RA1 selection#semicolon Njets=2",
   minMax = (0.0, 2.0),
   mcPhot = data.mcExpectations()["mcPhot2Jet"],
   mcPhotErr = data.mcStatError()["mcPhot2JetErr"],
   mcZinv = data.mcExpectations()["mcMuon2JetSpring11Re"],
   mcZinvErr = data.mcStatError()["mcMuon2JetSpring11ReErr"],
   sysFactor = data.fixedParameters()["sigmaPhotZ"],
   scale = data.lumi()["muon"]/data.lumi()["phot"]
   )
