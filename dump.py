#!/usr/bin/env python

from inputData import afterAlphaT,mixedMuons_b
#data = afterAlphaT.data_55_v1()
data = mixedMuons_b.data_55_v1()

for func in ["observations", "mcExpectations", "purities", "mcExtra", "mcStatError"] :
    print func
    print "--------------------"
    d = getattr(data, func)()
    for key in sorted(d.keys()) :
        print key,d[key]
    print

notes = r'''
NOTES
-----

- all numbers are after the trigger, i.e.
-- the observations are integers (except for nMumu, to be updated)
-- the appropriate MC samples are scaled down to emulate trigger inefficiency

- mcGJets is the true gamma+jets component of the MC
- mcPhot is what is to be compared to data; (GJets + QCD contamination)
- they are related by the photon purity

similarly:
- mcZmumu is the true Z->mumu component of the MC
- mcMumu is what is to be compared to data (Z->mumu + ttbar contamination)
- they are related by the mumu purity

'''

print notes
