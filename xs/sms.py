#!/usr/bin/env python

import ROOT as r

def parsed(fileName = "") :
    dct = {}
    f = open(fileName)
    for iLine,line in enumerate(f) :
        if "GeV" not in line :
            assert ("(pb)" in line) or line=="\n",line
            continue
        try:
            mass,gev,xs,garbage,percentUnc = line.replace("|","").split()
            relUnc = float(percentUnc.replace("%",""))/100.0
            dct[int(mass)] = (float(xs), relUnc)
        except:
            print "Bad format on line %d of file %s:"%(1+iLine, fileName)
            print line
            exit()
    f.close()
    return dct

def histos() :
    histosOut = []
    comsOut = []
    for fileName,histName in sorted({"gluglu_decoupled8TeV.txt":"gluino",
                              "sqsq_decoupled8TeV.txt":"squark",
                              "stst_decoupled8TeV.txt":"stop_or_sbottom",
                              }.iteritems()) :
        dct = parsed(fileName)
        masses = sorted(dct.keys())
        nMasses = len(masses)
        assert nMasses>1,"%s: %d"%(histName,nMasses)

        deltas = [masses[i+1]-masses[i] for i in range(nMasses-1)]
        assert len(set(deltas))==1,set(deltas)

        minMass = min(masses)
        maxMass = max(masses)
        binWidth = (maxMass - minMass + 0.0) / (nMasses-1)
        histo = r.TH1D(histName, "%s; mass (GeV);#sigma (pb)"%histName, nMasses, minMass-binWidth/2.0, maxMass+binWidth/2.0)
        for mass,(xs,xsRelUnc) in dct.iteritems() :
            histo.SetBinContent(histo.FindBin(mass), xs)
            histo.SetBinError(histo.FindBin(mass), xs*xsRelUnc)
        histosOut.append(histo)
        comsOut.append(fileName[-8:-4])
    return histosOut,comsOut

def makeRootFile(fileName = "") :
    outFile = r.TFile(fileName, "RECREATE")
    
    canvas = r.TCanvas()
    pdfFile = "sms_xs.pdf"
    canvas.Print(pdfFile+"[")

    hs,coms = histos()
    leg = r.TLegend(0.5, 0.7, 0.88, 0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    for iHisto,(h,com) in enumerate(zip(hs,coms)) :
        h.Write()
        h.SetStats(False)
        h.SetTitle("")
        h.Draw("p%s"%("same" if iHisto else ""))
        h.SetLineColor(1+iHisto)
        h.SetMarkerColor(1+iHisto)
        entry = " ".join([com.replace("TeV", " TeV"), h.GetName().replace("_"," "), "pair"])
        leg.AddEntry(h, entry, "lp")
    leg.Draw()
    canvas.SetLogy()
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(pdfFile)

    for i in range(len(hs)-1):
        ratio = hs[i].Clone("ratio_%d" % i)
        den = hs[i].Clone("den_%d" % i)
        den.Reset()
        for iBin in range(1, 1+ratio.GetNbinsX()):
            x = ratio.GetBinCenter(iBin)
            den.SetBinContent(iBin, hs[i+1].GetBinContent(hs[i+1].FindBin(x)))
        ratio.Divide(den)
        ratio.Draw()
        ratio.GetYaxis().SetTitle("%s / %s" % (hs[i].GetName(), hs[i+1].GetName()))
        ratio.SetMinimum(0.0)
        r.gPad.SetLogy(False)
        canvas.Print(pdfFile)
    canvas.Print(pdfFile+"]")

    outFile.Close()


def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

setup()
makeRootFile(fileName = "sms_xs.root")
