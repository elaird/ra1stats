#!/usr/bin/env python

from inputData import data2011
import math

data = data2011()

htBins   = data.htBinLowerEdges()
constR   = data.constantMcRatioAfterHere()
nMuon    = data.observations()["nMuon2Jet"]
mcMuon   = data.mcExpectations()["mcMuon2Jet"]
nPhot    = data.observations()["nPhot2Jet"]
mcPhot   = data.mcExpectations()["mcPhot2Jet"]

print     "HT   nPhoton    MC ratio       prediction                         nMuon"
print     "-----------------------------------------------------------------------"
rFinal = None
for i,ht,stopHere,nPh,mcPh,nMu,mcMu in zip(range(len(htBins)), htBins, constR, nPhot, mcPhot, nMuon, mcMuon) :
    if stopHere :
        rFinal = sum(mcMuon[i:])/sum(mcPhot[i:])
        #rFinal = 0.38
    ratio = rFinal if rFinal else mcMu/mcPh
    print "%3d     %4d  *     %4.2g  = %5.1f +- %4.1f (stat) +- %5.1f (syst); %5d"%(ht, nPh, ratio, nPh*ratio, math.sqrt(nPh)*ratio, 0.4*nPh*ratio, nMu)
