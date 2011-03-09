#!/usr/bin/env python

import os
import configuration as conf
import histogramProcessing as hp
import ROOT as r

def fetchHisto(file, dir, histo) :
    f = r.TFile(file)
    hOld = f.Get("%s/%s"%(dir,histo))
    h = hOld.Clone("%s_clone"%hOld.GetName())
    h.SetDirectory(0)
    f.Close()
    return h

def collectHistos(model = None, dir = "/vols/cms02/elaird1/24_sms_isr_from_riccardo/v2", subDir = "") :
    out = {}
    dir = "%s/%s"%(dir, subDir)
    for file in os.listdir(dir) :
        fields = file.split("_")
        if model!=fields[0] : continue
        key = (float(fields[1]), float(fields[2]))
        out[key] = fetchHisto("%s/%s"%(dir,file), "lastPt", "last_pT")
    return out

def model() :
    def isSimplifiedModel(model) : return len(model)==2
    out = conf.switches()["signalModel"]
    assert isSimplifiedModel(out),"%s is not a simplified model"%out
    return out

def example2DHisto(item = "sig10") :
    spec = conf.histoSpecs()[item]
    return hp.loYieldHisto(spec, spec["350Dirs"], lumi = 1.0)

def example1DHisto(collection) :
    return collection[collection.keys()[0]]

def output3DHisto(sms, numCollection = None, denCollection = None) :
    def initHisto(exampleCollection) :
        xy = example2DHisto()
        z = example1DHisto(exampleCollection)
        name = "%s_weight"%sms
        return r.TH3F(name, name,
                      xy.GetNbinsX(), xy.GetXaxis().GetXmin(), xy.GetXaxis().GetXmax(),
                      xy.GetNbinsY(), xy.GetYaxis().GetXmin(), xy.GetYaxis().GetXmax(),
                      z.GetNbinsX(),   z.GetXaxis().GetXmin(),  z.GetXaxis().GetXmax())

    out = initHisto(numCollection)
    for iBinX in range(1, 1+out.GetNbinsX()) :
        x = out.GetXaxis().GetBinLowEdge(iBinX)
        for iBinY in range(1, 1+out.GetNbinsY()) :
            y = out.GetYaxis().GetBinLowEdge(iBinY)
            fake = False
            if (x,y) not in numCollection : continue
            if (x,y) not in denCollection : continue
            for iBinZ in range(1, 1+out.GetNbinsZ()) :
                num = numCollection[(x,y)].GetBinContent(iBinZ)
                den = denCollection[(x,y)].GetBinContent(iBinZ)
                content = num/den if (den and num) else 1.0
                out.SetBinContent(iBinX, iBinY, iBinZ, content)
    return out

def weights1DHisto(threeD) :
    out = r.TH1D("weights", "weights", 100, 0.0, 2.0)
    for iBinX in range(1, 1+threeD.GetNbinsX()) :
        for iBinY in range(1, 1+threeD.GetNbinsY()) :
            for iBinZ in range(1, 1+threeD.GetNbinsZ()) :
                out.Fill(threeD.GetBinContent(iBinX, iBinY, iBinZ))
    return out

def weights2DHisto(threeD) :
    out = r.TH2D("weights", "weights",
                 threeD.GetNbinsX(), threeD.GetXaxis().GetXmin(), threeD.GetXaxis().GetXmax(),
                 threeD.GetNbinsY(), threeD.GetYaxis().GetXmin(), threeD.GetYaxis().GetXmax())

    for iBinX in range(1, 1+threeD.GetNbinsX()) :
        for iBinY in range(1, 1+threeD.GetNbinsY()) :
            mean = 0.0
            for iBinZ in range(1, 1+threeD.GetNbinsZ()) :
                mean += threeD.GetBinContent(iBinX, iBinY, iBinZ)
            mean/=threeD.GetNbinsZ()
            out.SetBinContent(iBinX, iBinY, mean)
    return out

def threeDHisto(sms) :
    histos0 = collectHistos(sms, subDir = "gen0")
    histos3 = collectHistos(sms, subDir = "gen3")
    return output3DHisto(sms, numCollection = histos3, denCollection = histos0)

def fileName(sms) :
    return "%s_weights.root"%sms

def writeHisto(fileName, histo) :
    f = r.TFile(fileName, "RECREATE")
    histo.Write()
    f.Close()

def weightPlot1D(epsFileName, threeD) :
    canvas = r.TCanvas("canvas")
    canvas.SetLogy()
    r.gStyle.SetOptStat(111111)
    oneD = weights1DHisto(threeD)
    oneD.SetTitle(";weight;entries / bin")
    oneD.Draw()
    canvas.Print(epsFileName)
    os.system("epstopdf %s"%epsFileName)
    os.remove(epsFileName)

def weightPlot2D(epsFileName, threeD) :
    canvas = r.TCanvas("canvas")
    canvas.SetRightMargin(0.15)
    twoD = weights2DHisto(threeD)
    twoD.SetTitle(";m_{mother} (GeV);m_{LSP} (GeV);mean weight from ISR variation")
    twoD.SetStats(False)
    twoD.Draw("colz")
    twoD.GetZaxis().SetRangeUser(0.5, 1.5)
    canvas.Print(epsFileName)
    os.system("epstopdf %s"%epsFileName)
    os.remove(epsFileName)

sms = model()
threeD = threeDHisto(sms)
writeHisto(fileName(sms), threeD)
weightPlot1D(fileName(sms).replace(".root","_1D.eps"), threeD)
weightPlot2D(fileName(sms).replace(".root","_2D.eps"), threeD)
