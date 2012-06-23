#! /usr/bin/env python

import ROOT as r
from collections import Iterable
from array import array
from socket import gethostname
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

r.gROOT.SetBatch(1)

base_histos = [ "lumiData", "lumiMc", "WJets", "Zinv", "t", "ZZ",
                "DY", "tt", "obs" ] #"WW", "WZ" ]

std_selections = { "had"  : base_histos,
                   "muon" : base_histos,
                   "mumu" : base_histos,
                   "phot" : [ "lumiData", "lumiMc", "obs", "Phot" ],
                 }

base_dir = { 'phosphorus' : '~/116_numbers/',
             'kinitos'    : '~/public_html/03_RA1/07_ra1stats_numbers/'
           }[gethostname()]

d_set = "08_23_06_2012"
#file_names = [ "{0}b.root".format(i) for i in range(0,4) ]
file_names = [ "RA1_Stats_{0}_btags.root".format(s) for s in "Zero", "One",
                                                             "Two",
                                                             "More_Than_Two" ]

fullfiles = [ "{base}/{set}/{file}".format(base=base_dir, set=d_set, file=f) for f in file_names ]


names = [ "btag0", "btag1", "btag2", "btag3", ]

selections  = [ { rfile : std_selections } for rfile in fullfiles ]

dsfs = [ DF.DataSliceFactory( selection ) for selection in selections ]
dss  = [ dsf.makeSlice("x",55.5,55.6) for dsf in dsfs ]

slices = dict( zip( names, dss ) )

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
