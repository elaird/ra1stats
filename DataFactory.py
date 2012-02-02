#! /usr/bin/env python

import histogramProcessing as hP

import utils
from data import data,scaled,excl,trig

from math import sqrt
from collections import defaultdict

def projectHistogram( histo, axis, amin, amax, suffix, name, addOverFlow = True,
                      addUnderFlow = False) :
    ax = histo.GetXaxis() if axis == "y" else histo.GetYaxis()
    Projection = histo.ProjectionX if axis == "x" else histo.ProjectionY

    firstbin = 1
    lastbin  = ax.GetNbins()
    if amin is not None :
        firstbin = ax.FindBin( amin )
    if amax is not None :
        lastbin  = ax.FindBin( amax )

    h_options = "e"
    h_proj = Projection( name+suffix, firstbin, lastbin, h_options )

    nbins = h_proj.GetNbinsX()
    maxBinContent = h_proj.GetBinContent( nbins )
    minBinContent = h_proj.GetBinContent( 1 )
    maxBinErr     = h_proj.GetBinError( nbins )
    minBinErr     = h_proj.GetBinError( 1 )
    overflow      = h_proj.GetBinContent( nbins+1 )
    underflow     = h_proj.GetBinContent( 0 )
    overflowErr   = h_proj.GetBinError( nbins+1 )
    underflowErr  = h_proj.GetBinError( 0 )

    if addOverFlow :
        h_proj.SetBinContent( nbins, maxBinContent + overflow )
        h_proj.SetBinError(   nbins, sqrt(maxBinErr**2 + overflowErr**2)  )
    if addUnderFlow :
        h_proj.SetBinContent( 1,     minBinContent + overflow )
        h_proj.SetBinError(   1,     sqrt(minBinErr**2 + underflowErr**2) )
    return h_proj
    

def getMultiHists( d ) :
    # d is a dictionary: structured:
    #   "filename_as_key" : { "phot" : [ "obs", "purity", "" ] }

    # h is local list of histograms to use with checkHistoBinning
    h = []

    histo_dict = defaultdict(dict)
    for file in d.keys() :
        for dir in d[file].keys() :
            for histo_name in d[file][dir] :
                # create new entry in dictionary at directory level
                # ideally we should add hP.getMultiHistos( file, list )
                # then we can avoid the overhead in the function calls
                h_temp  = hP.oneHisto(file, dir, histo_name)
                histo_dict[dir][histo_name] =  h_temp
                if h_temp.ClassName()[:3] == "TH2" :
                    h.append( h_temp )
    hP.checkHistoBinning( h )
    return histo_dict

# ok from here: 
#   - we want a class the *just* holds the histograms: this means any sort of
#   import of this module cannot accidently cause huge overhead. This is the
#   only reason to do a class rather than a function here

class DataSliceFactory( object ) :
    def __init__( self, d ) :
        self._histos = getMultiHists( d )


    def makeSlice( self, axis="x", a1 = None, a2 = None ) :
        amin = min( a1, a2 )
        amax = max( a1, a2 )
        # want to operator on hists (second level of the dictionary) and turn them into cuts with the appropriate at values
        h = defaultdict(dict) # h is going to be used to hold the tempory 1Ds used to instantiate a DataSlice
        h_suffix = "_%d-%d" % ( int(amin*100), int(amax*100) )

        for dir in self._histos.keys() :
            for histo_name in self._histos[dir].keys() :
                histo = self._histos[dir][histo_name]
                # set some sensible defaults
                # how is ProjectionX defined in the binning varies across slices.  Should probably put some check on this
                cName = histo.ClassName()
                if cName[:3] == "TH2" : 
                    h[dir][histo_name] = projectHistogram( histo, axis,  amin, amax, h_suffix, histo_name )
                elif cName[:3] == "TH1" : # only the lumi hists are 1D
                    h[dir][histo_name] = histo 
        return DataSlice( h, h_suffix )
        

class DataSlice( object ) :
    # this class *checks* that everything souhld be a TH1D as otherwise makes no
    # sense for it
    def __init__( self, histo_dict, suffix = "" ) :
        for obj in [ "_mcExpectations", "_mcStatError", "_observations",
            "_purities", "_atTriggerEff", "_HtTriggerEff", "_lumi", "_mcExtra",
            "_fixedParameters", "_htMeans" ] :
            setattr(self, obj, {} )
        for dir in histo_dict.keys() :
            for name in histo_dict[dir] :
                if histo_dict[dir][name].ClassName()[:3] != "TH1" :
                    assert False, "Attempted to take a 1D histogram slice without providing 1D histos"

        i = 0 
        hname = histo_dict[ histo_dict.keys()[0] ].keys()[i]
        h = histo_dict[ histo_dict.keys()[0] ][hname]
        while h.GetName().find("lumi") > 0 :
            i+=1
            hname = histo_dict[ histo_dict.keys()[0] ].keys()[i]
            h = histo_dict[ histo_dict.keys()[0] ][hname]

        nxbins =  h.GetXaxis().GetNbins()

        # save repeated calls
        xbins   = xrange(1,nxbins+1) # probably unnecessary use of xrange but..

        self._htBinLowerEdges = [ h.GetXaxis().GetBinLowEdge(bin) for bin in xbins ]

        self._htMaxForPlot = h.GetXaxis().GetBinUpEdge( nxbins )

        # called from data.py mergeEfficiency
        self._mergeBins = None
        self._constantMcRatioAfterHere =  [ ]

        try :
            self._htMeans = tuple( [ histo_dict["hadBulk"]["Htmeans"].GetXaxis().GetBinContent(bin) for bin in xbins ] )
        except KeyError :
            print "hadBulk/Htmeans histogram not defined"

        self._sigEffCorr =  (       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0,       1.0)

        for objName in histo_dict.keys() :
            objKeys = histo_dict[objName].keys()

            if objName+"MC" in objKeys :
                self._mcExpectations[ "mc"+objName ] = \
                    tuple( [ histo_dict[objName][objName+"MC"].GetBinContent(xbin)      for xbin in xbins ] )
                self._mcStatError[ "mc"+objName+"Err" ] = \
                    tuple( [ histo_dict[objName][objName+"MC"].GetBinError(xbin)        for xbin in xbins ] )

            if "obs" in objKeys :
                self._observations[ "n"+objName ] = \
                    tuple( [ histo_dict[objName]["obs"].GetBinContent(xbin)        for xbin in xbins ] )
            if "purity" in objKeys :
                self._purities[ objName ] = \
                    tuple( [ histo_dict[objName]["purity"].GetBinError(xbin)       for xbin in xbins ] )
            if "atTriggerEff" in objKeys :
                self._atTriggerEff[dir] = \
                    tuple( [ histo_dict[objName]["atTriggerEff"].GetBinError(xbin) for xbin in xbins ] )
            if "HtTriggerEff" in objKeys :
                self._HtTriggerEff[dir] = \
                    tuple( [ histo_dict[objName]["HtTriggerEff"].GetBinError(xbin) for xbin in xbins ] )
            if "lumiData" in objKeys :
                self._lumi[dir] = histo_dict[dir]["lumiData"].GetBinContent(1)
            if "lumiMc" in objKeys :
                self._lumi["mc"+dir] = histo_dict[dir]["lumiMc"].GetBinContent(1)

        if histo_dict.get("had") :
            hadKeys = histo_dict["had"].keys()
            for obj in [ "tt", "W", "Z", "t", "QCD" ] :
                if obj in hadKeys :
                    self._mcExpectations[ "mc" + obj ] = \
                        tuple( [ histo_dict["had"][obj].GetBinContent(xbin) for xbin in xbins ] )

# need to update this to 2D
        try : 
            self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
            self._mcExtra["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectations["mcGjets"], self._purities["phot"])])
            self._mcExtra["mcMumu"] = tuple([(zMumu/purity if (zMumu and purity) else None) for zMumu,purity in zip(self._mcExpectations["mcZmumu"], self._purities["mumu"])])
        except KeyError,e :
            print "Missing %s required for mcExtra" % ( e )

        self._fixedParameters = {
            "sigmaLumiLike": utils.quadSum({"lumi": 0.06, "deadEcal": 0.03, "lepVetoes": 0.025, "jesjer": 0.025, "pdf": 0.10}.values()),
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,
            "k_qcd_nom"     : 3.3e-2,
            "k_qcd_unc_inp" : 0.66e-2,
            }

       #print self._mcExpectations
       #print self._htBinLowerEdges
       #print self._htMaxForPlot
