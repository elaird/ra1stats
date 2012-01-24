#! /usr/bin/env python

import histogramProcessing as hP

def getMultiHists( d ) : 
    # d is a dictionary: structured:
    #   "filename_as_key" : { "phot" : [ "obs", "purity", "" ] }

    # h is local list of histograms to use with checkHistoBinning
    h = []
    
    histo_dict = {}
    for file in d.keys() :
        for dir in d[file].keys() :
            for histo_name in d[file][dir] :
                # create new entry in dictionary at directory level
                h_temp  = hP.oneHisto(file, dir, histo_name)
                histo_dict[dir][histo_name] =  h_temp
                if h_temp.ClassName()[:3] == "TH2" :
                    h.append( h_temp )

    hP.checkHistoBinning( h )
    return histo_dict
            


# might use this....
class inputData( object ) :
    """ Skeleton class for new approach to inputData """
    def __init__( self, d ) :

        histo_dict = getMultiHists( d )
        # hist_dict contains { "phot"       : [ histos ]
        #                      "phot_names" : [ "phot", "obs" ]


        h = 0
        i = 0
        while h.ClassName()[:3] != "TH2" :
            # lol wut
            h = histo_dict[ histo_dict.keys().sorted()[0] ].keys().sorted()[i]
            i+=1


        nxbins =  h.GetXaxis().GetNbins()
        nybins =  h.GetYaxis().GetNbins()

        # save repeated calls
        xbins   = xrange(1,nxbins+1) # probably unnecessary use of xrange but..
        ybins   = xrange(1,nybins+1)

        self._htBinLowerEdges = [ h.GetXaxis().GetBinLowEdge(bin) for bin in xbins ]
        self._atBinLowerEdges = [ h.GetXaxis().GetBinLowEdge(bin) for bin in ybins ]

        self._htMaxForPlot = h.GetXaxis().GetBinUpEdge( nxbins )
        self._atMaxForPlot = h.GetXaxis().GetBinUpEdge( nybins )

        #self._mergeBins = None
        #self._constantMcRatioAfterHere =  [ ] 

        self._htMeans = [ histo_dict["hadBulk"]["Htmeans"].GetXaxis().GetBinContent(bin) for bin in xbins ]

        #self._sigEffCorr =    (
        # this was apparently a hack

        dirs = hist_dict.keys(
        for objName in histo_dict.keys() :
            objKeys = histo_dict[objName].keys()
            if "obs" in objKeys :
                self._observations[ "n"+objName ]       = 
                    tuple( [ [ histo_dict[objName]["obs"].GetBinContent(xbin,ybin)        for xbin in xbins ] for ybin in ybins ] )
            if objName in objKeys :
                self._mcExpectations[ "mc"+objName ]    =
                    tuple( [ [ histo_dict[objName][objName].GetBinContent(xbin,ybin)      for xbin in xbins ] for ybin in ybins ] )
                self._mcStatError[ "mc"+objName+"Err" ] = 
                    tuple( [ [ histo_dict[objName][objName].GetBinError(xbin,ybin)        for xbin in xbins ] for ybin in ybins ] )
            if "purity" in objKeys :
                self._purities[ objName ]               = 
                    tuple( [ [ histo_dict[objName]["purity"].GetBinError(xbin,ybin)       for xbin in xbins ] for ybin in ybins ] )
            if "atTriggerEff" in objKeys :
                self._HtTriggerEff[dir] = 
                    tuple( [ [ histo_dict[objName]["atTriggerEff"].GetBinError(xbin,ybin) for xbin in xbins ] for ybin in ybins ] )
            if "HtTriggerEff" in objKeys :
                self._HtTriggerEff[dir] = 
                    tuple( [ histo_dict[objName]["HtTriggerEff"].GetBinError(xbin,ybin)   for xbin in xbins ] )
            if "lumiData" in objKeys :
                self._lumi[dir] = histo_dict[dir]["lumiData"]
            if "lumiMc" in objKeys :
                self._lumi["mc"+dir] = histo_dict[dir]["lumiMc"]


        self._mcExtra["mcHad"]  = tuple([(ttw+zinv if ttw!=None and zinv!=None else None) for ttw,zinv in zip(self._mcExpectations["mcTtw"], self._mcExpectations["mcZinv"])])
        self._mcExtra["mcPhot"] = tuple([(gJet/purity if (gJet and purity) else None) for gJet,purity in zip(self._mcExpectations["mcGjets"], self._purities["phot"])])
        self._mcExtra["mcMumu"] = tuple([(zMumu/purity if (zMumu and purity) else None) for zMumu,purity in zip(self._mcExpectations["mcZmumu"], self._purities["mumu"])])
                               
        #self._mcExtra = {}
        #self._mcExtra["mcHad"] 
        #self._mcExtra["mcPhot"]
        #self._mcExtra["mcMumu"]

        self._fixedParameters =
            "sigmaLumiLike": ut
            #"sigmaLumiLike": 0
            "sigmaPhotZ": 0.40,
            "sigmaMuonW": 0.30,
            "sigmaMumuZ": 0.20,
            "k_qcd_nom"     : 3
            "k_qcd_unc_inp" : 0
