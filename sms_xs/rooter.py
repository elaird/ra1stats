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
    for fileName,histName in {#"gluglu_decoupled7TeV.txt":"gluino",
                              "sqsq_decoupled7TeV.txt":"squark",
                              #"stst_decoupled7TeV.txt":"stop_or_sbottom",
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
        for mass,(xs,xsErr) in dct.iteritems() :
            histo.SetBinContent(histo.FindBin(mass), xs)
        histosOut.append(histo)
        comsOut.append(fileName[-8:-4])
    return histosOut,comsOut

def exclusionHisto(xsFile='T2tt_xs.root', xsHistoName='UpperLimit_2D',
                   yMinMax=(50,50), doScale=True) :

    rfile = r.TFile(xsFile,'READ')
    xsHisto = rfile.Get(xsHistoName)

    minYBin = xsHisto.GetYaxis().FindBin(yMinMax[0])
    maxYBin = xsHisto.GetYaxis().FindBin(yMinMax[1])

    xsProj = xsHisto.ProjectionX('T2tt',minYBin,maxYBin)
    xsProj.Print()

    #if doScale:
        #xsProj *= 1000.

    xsProj.SetDirectory(0)
    rfile.Close()
    return xsProj, "excluded"


def makeRootFile(fileName = "") :
    xsH, xsC = exclusionHisto()

    outFile = r.TFile(fileName, "RECREATE")

    canvas = r.TCanvas()
    pdfFile = "sms_xs.pdf"

    hs,coms = histos()
    hs.append(xsH)
    coms.append(xsC)

    leg = r.TLegend(0.5, 0.7, 0.88, 0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    for iHisto,(h,com) in enumerate(zip(hs,coms)) :
        isExcl = (com == "excluded")
        h.Write()
        h.SetStats(False)
        h.SetTitle("")
        h.GetXaxis().SetRangeUser(300,1200)
        baseOpts = "c" if not isExcl else "]["
        h.Draw("%s%s"%(baseOpts, "same" if iHisto else ""))
        h.SetLineColor(1+iHisto)
        h.SetMarkerColor(1+iHisto)
        entry = " ".join([com.replace("TeV", " TeV"),
                          h.GetName().replace("_"," "),
                          "pair" if not isExcl else ""])
        leg.AddEntry(h, entry, "lp")
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
