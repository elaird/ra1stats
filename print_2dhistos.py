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

base_dir = { 'phosphorus' : '~/140_updated_5fb_numbers_from_darren/v4_no_weights',
             'kinitos'    : '~/public_html/03_RA1/07_ra1stats_numbers/',
             'lx06.hep.ph.ic.ac.uk' : '/home/hep/elaird1/122_numbers_from_darren/v6_18fb',
             'lxplus433.cern.ch': '/tmp/elaird/root',
           }[gethostname()]

d_set = ""

files = {"ge4b_le3j": "RA1_Stats_btag_eq4_category_eq2_and_3.root",
         "ge4b_ge4j": "RA1_Stats_btag_eq4_category_greq4.root",
         #"ge4b_ge2j": "RA1_Stats_btag_eq4_category_inclusive.root",

         "3b_le3j": "RA1_Stats_btag_eq3_category_eq2_and_3.root",
         "3b_ge4j": "RA1_Stats_btag_eq3_category_greq4.root",
         #"3b_ge2j": "RA1_Stats_btag_eq3_category_inclusive.root",

         "2b_le3j": "RA1_Stats_btag_eq2_category_eq2_and_3.root",
         "2b_ge4j": "RA1_Stats_btag_eq2_category_greq4.root",
         #"2b_ge2j": "RA1_Stats_btag_eq2_category_inclusive.root",

         "1b_le3j": "RA1_Stats_btag_eq1_category_eq2_and_3.root",
         "1b_ge4j": "RA1_Stats_btag_eq1_category_greq4.root",
         #"1b_ge2j": "RA1_Stats_btag_eq1_category_inclusive.root",

         "0b_le3j": "RA1_Stats_btag_eq0_category_eq2_and_3.root",
         "0b_ge4j": "RA1_Stats_btag_eq0_category_greq4.root",
         #"0b_ge2j": "RA1_Stats_btag_eq0_category_inclusive.root",

         #"0b_le3j_alphaTmuon": "RA1_Stats_btag_eq0_category_eq2_and_3_alphaT.root",
         #"0b_ge4j_alphaTmuon": "RA1_Stats_btag_eq0_category_greq4_alphaT.root",
         ##"0b_ge2j_alphaTmuon": "RA1_Stats_btag_eq0_category_inclusive_alphaT.root",
         }

slices = {}
for tag,fileName in files.iteritems() :
    fullName = "{base}/{set}/{file}".format(base=base_dir, set=d_set, file=fileName)
    dsf = DF.DataSliceFactory({fullName: std_selections})
    slices[tag] = dsf.makeSlice("x",55.5,55.6)

for name in sorted(slices.keys()) :
    slice = slices[name]
    print "class data_%s(data) :"%name
    print "    def _fill(self) :"
    mems = dir( slice )
    for attr_name in mems :
        if not "__" in attr_name :
            attr_data = getattr( slice, attr_name )
            print "{space}{classname}.{obj} = ".format(space=" "*8, classname="self", obj=attr_name),
            print_unpack( attr_data,1 )
            print
    print "%scommon(self)"%(" "*8)
    print "\n"
