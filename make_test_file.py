#! /usr/bin/env python

import ROOT as r
from array import array

import inputData_x as iDx


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

d = { "data_factory_test.root" : { "phot" : [ "photMC" ] } }

dsf = iDx.DataSliceFactory( d )

ds_52_53 = dsf.makeSlice(0.52,0.53)
