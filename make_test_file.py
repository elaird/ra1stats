#! /usr/bin/env python

import ROOT as r
from array import array

import DataFactory as DF

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
d = { "/home/hyper/Documents/RA1/RA1_Status_baseline.root" :
        { "had"  : [ "lumiData", "lumiMc", "WW", "WJets", "Zinv", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
          "muon" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
          "mumu" : [ "lumiData", "lumiMc", "Zinv", "WW", "WJets", "t", "ZZ",
                     "DY", "tt", "obs", "WZ" ],
         },
     }

filename = "test2.pdf"

r.gStyle.SetOptStat(0)
canvas = r.TCanvas()
canvas.Print(filename+"[")

dsf = DF.DataSliceFactory( d )
canvas.Print(filename)
ds_52_53 = dsf.makeSlice("x",0.52,0.53)

canvas.Print(filename)
canvas.Print(filename+"]")
