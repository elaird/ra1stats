#!/usr/bin/env python

import ROOT as r

def histo(inFile, histoName) :
    f = r.TFile(inFile)
    h = f.Get(histoName).Clone()
    h.SetDirectory(0)
    f.Close()
    return h

def patch(h, iBinX, iBinY) :
    avg = 0.0
    for i in [iBinX-1, iBinX+1] :
        for j in [iBinY-1, iBinY+1] :
            print i,j
            avg += h.GetBinContent(i, j)
    h.SetBinContent(11, 10, avg/4.0)

def writeHisto(h, histoName, outFile) :
    f = r.TFile(outFile, "RECREATE")
    h.Write(histoName)
    f.Close()

inFile = "/home/hep/elaird1/60_ra_comparison/ra1/v1/T2_effUncRelTh.root"
histoName = "effUncRelTheoretical_2D"

h = histo(inFile, histoName)
patch(h, 11, 10)
writeHisto(h, histoName, outFile = inFile.replace(".root", "_patched.root"))
