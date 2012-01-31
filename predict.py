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

def fill(constantR, h, contents, errors) :
    h.Reset()
    cFinal = None
    eFinal = None
    for i,c,e in zip(range(len(contents)), contents, errors) :
        if constantR[i] :
            cFinal = sum(contents[i:])
            eFinal = e
        content = c if cFinal is None else cFinal
        error   = e if eFinal is None else eFinal
        if content==None or error==None : continue
        h.SetBinContent(1+i, content)
        h.SetBinError(1+i, error)
    return h

data = data2011(requireFullImplementation = False)

htBins = data.htBinLowerEdges()
constantR = data.constantMcRatioAfterHere()

mode = 0

if mode==0 :
    print "photon to muon (2-jet)"
    nMuon     = data.observations()["nMuon2Jet"]
    mcMuon    = data.mcExpectations()["mcMuon2Jet"]
    mcMuonErr = data.mcStatError()["mcMuon2JetErr"]
    
    nPhot     = data.observations()["nPhot2Jet"]
    mcPhot    = data.mcExpectations()["mcPhot2Jet"]
    mcPhotErr = data.mcStatError()["mcPhot2JetErr"]
    
    syst      = data.fixedParameters()["sigmaPhotZ"]

    muon = fill(constantR, histo(data, name = "mcMuon2Jet", title = "mcMuon2Jet"), mcMuon, mcMuonErr)
    phot = fill(constantR, histo(data, name = "mcPhot2Jet", title = "mcPhot2Jet"), mcPhot, mcPhotErr)

if mode==1 :
    print "photon to muon (n-jet)"
    nMuon     = data.observations()["nMuon"]
    mcMuon    = data.mcExpectations()["mcMuon"]
    mcMuonErr = data.mcStatError()["mcMuonErr"]
    
    nPhot     = data.observations()["nPhot"]
    mcPhot    = data.mcExtra()["mcPhot"]
    mcPhotErr = data.mcStatError()["mcGjetsErr"]

    syst      = data.fixedParameters()["sigmaPhotZ"]

    muon = fill(constantR, histo(data, name = "mcMuon", title = "mcMuon"), mcMuon, mcMuonErr)
    phot = fill(constantR, histo(data, name = "mcPhot", title = "mcPhot"), mcPhot, mcPhotErr)

if mode==2 :
    print "photon to mumu (n-jet)"
    nMuon     = data.observations()["nMumu"]
    mcMuon    = data.mcExtra()["mcMumu"]
    mcMuonErr = data.mcStatError()["mcZmumuErr"]
    
    nPhot     = data.observations()["nPhot"]
    mcPhot    = data.mcExtra()["mcPhot"]
    mcPhotErr = data.mcStatError()["mcGjetsErr"]

    syst      = data.fixedParameters()["sigmaPhotZ"]

    muon = fill(constantR, histo(data, name = "mcMumu", title = "mcMumu"), mcMuon, mcMuonErr)
    phot = fill(constantR, histo(data, name = "mcPhot", title = "mcPhot"), mcPhot, mcPhotErr)

muon.Divide(phot)

print     "HT   nPhoton    MC ratio(err)       prediction                                            nMuon"
print     "-----------------------------------------------------------------------------------------------"
rFinal = None
for i,ht,nPh,mcPh,nMu,mcMu in zip(range(len(htBins)), htBins, nPhot, mcPhot, nMuon, mcMuon) :
    mcRatio    = muon.GetBinContent(1+i)
    mcRatioErr = muon.GetBinError(1+i)
    if nPh==None : continue
    out  = "%3d     %4d  *     %4.2f(+-%4.2f) = %5.1f "%(ht, nPh, mcRatio, mcRatioErr, nPh*mcRatio)
    out += "+- %4.1f (stat) "%(math.sqrt(nPh)*mcRatio)
    out += "+- %4.1f (mcStat) "%(nPh*mcRatioErr)
    out += "+- %5.1f (syst)"%(syst*nPh*mcRatio)
    out += "; %5d"%nMu
    print out
