#!/usr/bin/env python

from inputData import mixedMuons_b_sets_reweighted,mixedMuons_b_sets_aT_reweighted

#data = mixedMuons_b_sets_aT_reweighted.data_55_0btag()
data = mixedMuons_b_sets_reweighted.data_55_1btag()

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
-- the observations are integers
-- the appropriate MC samples are scaled down to emulate trigger inefficiency

- mcGJets is the true gamma+jets component of the MC
- mcPhot is what is to be compared to data; (GJets + QCD contamination)
- they are related by the photon purity
'''

print notes
