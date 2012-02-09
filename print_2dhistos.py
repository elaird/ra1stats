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
            "/vols/cms02/samr/Correct_Baseline_Root_File.root" :
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
dsf  = DF.DataSliceFactory( baseline )
ds_55_up_baseline = dsf.makeSlice("x",55.5,55.6)
ds_52_53_baseline = dsf.makeSlice("x",52.5,52.6)
ds_53_55_baseline = dsf.makeSlice("x",53.5,53.6)

slices = { 
          "baseline aT0.55" : ds_55_up_baseline,
          "baseline aT0.53" : ds_53_55_baseline,
          "baseline aT0.52" : ds_52_53_baseline,
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
