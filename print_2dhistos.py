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

base_dir = { 'phosphorus' : '~/132_2012_categories/',
             'kinitos'    : '~/public_html/03_RA1/07_ra1stats_numbers/'
           }[gethostname()]

d_set = ""

files = {"ge4b_le3j": "RA1_Stats_More_Than_Three_btag_category_2.root",
         "ge4b_ge4j": "RA1_Stats_More_Than_Three_btag_category_3.root",
         "ge4b_ge2j": "RA1_Stats_More_Than_Three_btag_category_all.root",
         "3b_le3j": "RA1_Stats_More_Than_Two_btag_category_2.root",
         "3b_ge4j": "RA1_Stats_More_Than_Two_btag_category_3.root",
         "3b_ge2j": "RA1_Stats_More_Than_Two_btag_category_all.root",
         "2b_le3j": "RA1_Stats_Two_btags_category_2.root",
         "2b_ge4j": "RA1_Stats_Two_btags_category_3.root",
         "2b_ge2j": "RA1_Stats_Two_btags_category_all.root",
         "1b_le3j": "RA1_Stats_One_btag_category_2.root",
         "1b_ge4j": "RA1_Stats_One_btag_category_3.root",
         "1b_ge2j": "RA1_Stats_One_btag_category_all.root",
         "0b_le3j": "RA1_Stats_Zero_btags_category_2.root",
         "0b_ge4j": "RA1_Stats_Zero_btags_category_3.root",
         "0b_ge2j": "RA1_Stats_Zero_btags_category_all.root",
         }

slices = {}
for tag,fileName in files.iteritems() :
    fullName = "{base}/{set}/{file}".format(base=base_dir, set=d_set, file=fileName)
    dsf = DF.DataSliceFactory({fullName: std_selections})
    slices[tag] = dsf.makeSlice("x",55.5,55.6)

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
