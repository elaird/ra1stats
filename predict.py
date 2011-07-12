#!/usr/bin/env python

from inputData import data2011
import math,array
import ROOT as r

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
    return h

data = data2011()

htBins    = data.htBinLowerEdges()
constR    = data.constantMcRatioAfterHere()
nMuon     = data.observations()["nMuon2Jet"]
mcMuon    = data.mcExpectations()["mcMuon2Jet"]
mcMuonErr = data.mcStatError()["mcMuon2JetErr"]
nPhot     = data.observations()["nPhot2Jet"]
mcPhot    = data.mcExpectations()["mcPhot2Jet"]
mcPhotErr = data.mcStatError()["mcPhot2JetErr"]
syst      = data.fixedParameters()["sigmaPhotZ"]

muon = fill(histo(data, name = "mcMuon2Jet", title = "mcMuon2Jet"), mcMuon, mcMuonErr)
phot = fill(histo(data, name = "mcPhot2Jet", title = "mcPhot2Jet"), mcPhot, mcPhotErr)
muon.Divide(phot)

print     "HT   nPhoton    MC ratio(err)       prediction                                            nMuon"
print     "-----------------------------------------------------------------------------------------------"
rFinal = None
for i,ht,nPh,mcPh,nMu,mcMu in zip(range(len(htBins)), htBins, nPhot, mcPhot, nMuon, mcMuon) :
    mcRatio    = muon.GetBinContent(1+i)
    mcRatioErr = muon.GetBinError(1+i)
    out  = "%3d     %4d  *     %4.2f(+-%4.2f) = %5.1f "%(ht, nPh, mcRatio, mcRatioErr, nPh*mcRatio)
    out += "+- %4.1f (stat) "%(math.sqrt(nPh)*mcRatio)
    out += "+- %4.1f (mcStat) "%(nPh*mcRatioErr)
    out += "+- %5.1f (syst)"%(syst*nPh*mcRatio)
    out += "; %5d"%nMu
    print out
