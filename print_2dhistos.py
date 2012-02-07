#! /usr/bin/env python

import ROOT as r

from collections import Iterable
from array import array

import DataFactory as DF

def print_unpack( item, level = 0, ending_comma = False ) :
    if not isinstance( item, dict) : 
        if not isinstance( item, Iterable ) :
            print "\t"*level,"{item:.4}".format(item=item),
            if ending_comma :
                print ","
            else:
                print
        else :
            s = "(" if isinstance( item,tuple ) else "[" 
            e = ")" if isinstance( item,tuple ) else "]" 
            print "\t"*level,s,
            for i in item :
                print "{i:.4},".format(i=i),
            print e,
            if ending_comma :
                print ","
    else :
        print "\t"*level,"{"
        for key,value in item.iteritems() :
            print "\t"*(level+1),
            keystring = '"%s"' % key
            print '{k:20} : '.format( k=keystring ),
            print_unpack( value, 0, True )
        print "\t"*level,"}"

baseline = { 
            "~/Documents/RA1/RA1_Stats_baseline.root" :
               { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
               },
           }

btagged =  { 
            "~/Documents/RA1/RA1_Stats_Btagged.root" :
               { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
               },
           } 

baseline_noMHT_ov_MET = { 
            "~/Documents/RA1/RA1_Stats_Baseline_No_MHT_ov_MET.root" :
               { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
               },
           }

btagged_noMHT_ov_MET =  { 
            "~/Documents/RA1/RA1_Stats_Btagged_No_MHT_ov_MET.root" :
               { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
               },
           } 

r.gROOT.SetBatch(1)
#
dsf  = DF.DataSliceFactory( baseline_noMHT_ov_MET )
dsf2 = DF.DataSliceFactory( btagged_noMHT_ov_MET )
ds_55_up_baseline = dsf.makeSlice("x",55.5,55.6)
ds_55_up_btagged  = dsf2.makeSlice("x",55.5,55.6)

slices = { 
          "baseline no MHT/MET" : ds_55_up_baseline,
          "btagged  no MHT/MET" : ds_55_up_btagged,
         }


for name,slice in slices.iteritems() :
    print "="*len(name)
    print name
    print "="*len(name)
    mems = dir( slice )
    for attr_name in mems :
        if not "__" in attr_name :
            attr_data = getattr( slice, attr_name )
            print "{classname}.{obj} = \n".format(classname="self", obj=attr_name),
            print_unpack( attr_data,1 )
            print
    print "\n"
