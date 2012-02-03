#! /usr/bin/env python

import ROOT as r
from array import array

import DataFactory as DF

import inspect

def makeFile() :
    xbins = array('d', [ 275, 325, 375, 475, 575, 675, 775, 875 ] )
    ybins = array('d', [ 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57 ] )
    nxbins = len(xbins)
    nybins = len(ybins)
    nbins = (nxbins+1) * (nybins+1)
    bins = range( 1, nbins+1 )

    f = r.TFile.Open( "data_factory_test.root", "UPDATE" )
    histo = r.TH2D("photMC", "DataFactory Test", nxbins-1, xbins, nybins-1, ybins)
    rn = r.TRandom()
    for bin in bins :
        histo.SetBinContent(bin, rn.Rndm()*1000. )
    directory = "phot"
    if not f.cd( directory ) : 
        print "--> Creating directory: %s" % ( directory )
        f.mkdir( directory ).cd()
        f.cd( directory )
    histo.Write("",r.TObject.kOverwrite)
    f.Close()

r.gROOT.SetBatch(True)

mF = False
if mF: makeFile()

#d = { "data_factory_test.root" : { "phot" : [ "photMC" ] } }
d = { "~/Documents/RA1/RA1_Stats_baseline.root" :
        { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
          "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
          "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
         },
     }

e = { "~/Documents/RA1/RA1_Stats_Btagged.root" :
        { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
          "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
          "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
         },
     }


dsf = DF.DataSliceFactory( d )
ds_52_53 = dsf.makeSlice("x",55.5,55.6)

dsf_b = DF.DataSliceFactory( e )
ds_52_53_b = dsf_b.makeSlice("x",55.5,55.6)

for slice in [ ds_52_53_b, ds_52_53 ] :
    mems = dir( slice )
    for attr in mems :
        if not "__" in attr:
            x = getattr( ds_52_53, attr )
            print "%s.%s = %s" % ( "self", attr, x )
    print
    print
    print
