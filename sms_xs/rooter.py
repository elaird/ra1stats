#!/usr/bin/env python

import ROOT as r
from collections import defaultdict

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
    histosOut = defaultdict(dict)
    for fileName,histName in {"gluglu_decoupled7TeV.txt":"gluino",
                              "sqsq_decoupled7TeV.txt":"squark",
                              "stst_decoupled7TeV.txt":"stop_or_sbottom",
                              }.iteritems() :
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
        histosOut[histName]['hist'] = histo
        histosOut[histName]['com'] = fileName[-8:-4]
    return histosOut


def makeRootFile(fileName = "", xsFile=None) :
    outFile = r.TFile(fileName, "RECREATE")

    canvas = r.TCanvas()
    pdfFile = "sms_xs.pdf"

    hs = histos()

    leg = r.TLegend(0.5, 0.7, 0.88, 0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    for iHisto,(hname,props) in enumerate(hs.iteritems()):
        h = props['hist']
        h.Write()
        h.SetStats(False)
        h.SetTitle("")
        h.GetXaxis().SetRangeUser(300,1200)
        h.SetMinimum(2e-4)
        h.SetMaximum(2e+1)
        baseOpts = "c"
        h.Draw("%s%s"%(baseOpts, "same" if iHisto else ""))
        lineColor = props.get('lineColor',4+iHisto)
        markerColor = props.get('markerColor',1+iHisto)
        lineStyle = props.get('lineStyle',1)
        lineWidth = props.get('lineWidth',1)
        h.SetLineColor(lineColor)
        h.SetMarkerColor(markerColor)
        h.SetLineStyle(lineStyle)
        h.SetLineWidth(lineWidth)
        entry = " ".join([props['com'].replace("TeV", " TeV"),
                          h.GetName().replace("_"," "),
                          "pair"])
        leg.AddEntry(h, entry, "l")
    leg.Draw()
    canvas.SetLogy()
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(pdfFile)
    outFile.Close()

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

setup()
makeRootFile(fileName = "sms_xs.root")
