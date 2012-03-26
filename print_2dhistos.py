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

btag0 = {
            "~/public_html/03_RA1/07_numbers_from_darren/02_23_03_2012/RA1_Stats_Zero_Btags.root" :
            { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
            },
        }

btag1 = {
            "~/public_html/03_RA1/07_numbers_from_darren/02_23_03_2012/RA1_Stats_One_Btags.root" :
            { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
            },
        }

btag2 = {
            "~/public_html/03_RA1/07_numbers_from_darren/02_23_03_2012/RA1_Stats_Two_Btags.root" :
            { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
            },
        }

btag_gt2 = {
            "~/public_html/03_RA1/07_numbers_from_darren/02_23_03_2012/RA1_Stats_More_Than_Two.root" :
            { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                 "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
            },
        }

btag_gt0 = { 
            "~/public_html/03_RA1/07_numbers_from_darren/02_23_03_2012/RA1_Stats_More_Than_Zero.root":
            { 
                "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
                "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                         "DY", "tt", "obs", "WZ" ],
            },
        }

r.gROOT.SetBatch(1)

dsf_b0  = DF.DataSliceFactory( btag0 )
dsf_b1  = DF.DataSliceFactory( btag1 )
dsf_b2  = DF.DataSliceFactory( btag2 )
dsf_bgt2  = DF.DataSliceFactory( btag_gt2 )
dsf_bgt0  = DF.DataSliceFactory( btag_gt0 )

ds_b0 = dsf_b0.makeSlice("x",55.5,55.6)
ds_b1 = dsf_b1.makeSlice("x",55.5,55.6)
ds_b2 = dsf_b2.makeSlice("x",55.5,55.6)
ds_bgt2 = dsf_bgt2.makeSlice("x",55.5,55.6)
ds_bgt0 = dsf_bgt0.makeSlice("x",55.5,55.6)

slices = { 
         "btag0" : ds_b0,
         "btag1" : ds_b1,
         "btag2" : ds_b2,
         "btag_gt2" : ds_bgt2,
         "btag_gt0" : ds_bgt0,
         }


for name,slice in slices.iteritems() :
    print "="*len(name)
    print name
    print "="*len(name)
    mems = dir( slice )
    for attr_name in mems :
        if not "__" in attr_name :
            attr_data = getattr( slice, attr_name )
            print "{classname}.{obj} = ".format(classname="self", obj=attr_name),
            print_unpack( attr_data,1 )
            print
    print "\n"
