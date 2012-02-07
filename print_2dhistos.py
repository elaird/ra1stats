#! /usr/bin/env python

import ROOT as r
from array import array

import DataFactory as DF

import inspect

baseline = { "~/Documents/RA1/RA1_Stats_baseline.root" :
               { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
               },
           }

btagged = { "~/Documents/RA1/RA1_Stats_Btagged.root" :
               { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
               },
          } 

r.gROOT.SetBatch(1)

dsf = DF.DataSliceFactory( d )
ds_52_53 = dsf.makeSlice("x",55.5,55.6)

dsf_b = DF.DataSliceFactory( e )
ds_52_53_b = dsf_b.makeSlice("x",55.5,55.6)

for slice in [ ds_52_53_b, ds_52_53 ] :
    mems = dir( slice )
    for attr in mems :
        if not "__" in attr:
            x = getattr( slice, attr )
            print "%s.%s = %s" % ( "self", attr, x )
