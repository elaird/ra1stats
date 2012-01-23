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
            h = hist_dict[ hist_dict.keys().sorted()[0] ].keys()[i]
            i+=1


        nxbins =  h.GetXaxis().GetNbins()
        nybins =  h.GetYaxis().GetNbins()

        # save repeated calls
        xbins   = range(1,nxbins+1)
        ybins   = range(1,nxbins+1)

        self._htBinLowerEdges = [ h.GetXaxis().GetBinLowEdge(bin) for bin in xbins ]
        self._atBinLowerEdges = [ h.GetXaxis().GetBinLowEdge(bin) for bin in ybins ]

        self._htMaxForPlot = h.GetXaxis().GetBinUpEdge( nxbins )
        self._atMaxForPlot = h.GetXaxis().GetBinUpEdge( nybins )

        #self._mergeBins = None
        #self._constantMcRatioAfterHere =  [ ] 

        for dir in histo_dict.keys() :
            self._lumi[dir] = histo_dict[dir]["lumiData"]
            self._lumi["mc"+dir] = histo_dict[dir]["lumiMc"]

        self._htMeans = [ histo_dict["hadBulk"]["Htmeans"].GetXaxis().GetBinContent(bin) for bin in xbins ]

        #self._sigEffCorr =    (
        # this was apparently a hack

        # this needs fixing: it's unsafe on dictionary being invalid at second layer i.e. top level "phot" dir doesn't contain corresponding TH2D names "phot"
        for objName in hist_dict.keys() :
            objKeys = hist_dict[objName].keys()
            if "obs" in objKeys :
                self._observations[ "n"+objName ]       = 
                    tuple( [ [ histo_dict[objName]["obs"].GetBinContent(xbin,ybin)   for xbin in xbins ] for ybin in ybins ] )
            if objName in objKeys :
                self._mcExpectations[ "mc"+objName ]    =
                    tuple( [ [ histo_dict[objName][objName].GetBinContent(xbin,ybin) for xbin in xbins ] for ybin in ybins ] )
                self._mcStatError[ "mc"+objName+"Err" ] = 
                    tuple( [ [ histo_dict[objName][objName].GetBinError(xbin,ybin)   for xbin in xbins ] for ybin in ybins ] )
            if "purity" in objKeys :
                self._purities[ objName ]               = 
                    tuple( [ [ histo_dict[objName]["purity"].GetBinError(xbin,ybin)  for xbin in xbins ] for ybin in ybins ] )

                               
        self._triggerEfficienci
            "hadBulk":       ( 
            "had":           ( 
            "phot":          ( 
            "mumu":          ( 
            }
                               


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
