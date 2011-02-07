#!/usr/bin/env python

def switches() :
    d = {}

    d["method"] = "profileLikelihood"
    #d["method"] = "feldmanCousins"

    d["nlo"] = True
    d["fixQcdToZero"] = True
    d["constrainParameters"] = False

    d["testPointsOnly"] = True
    d["printCovarianceMatrix"] = False
    d["writeWorkspaceFile"] = False
    d["signalFreeMode"] = False
    
    d["twoHtBins"] = True
    d["tanBeta"] = 10

    return d

def histoSpecs() :
    dir = "/afs/cern.ch/user/e/elaird/public/20_yieldHistograms"

    d = {}

    #v4
    f = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta%dFall10v1.root"%switches()["tanBeta"]
    d["sig10"]  = {"file": "%s/v4/had/%s"%(dir,f)}
    d["muon"]   = {"file": "%s/v4/muon/%s"%(dir,f)}
    d["sig05"]  = {"file": "%s/v4/had/%s"%(dir,f)}
    d["sig20"]  = {"file": "%s/v4/had/%s"%(dir,f)}
    d["ht"]     = {"file": "%s/v4/ht/QcdBkgdEst_tanbeta%d.root"%(dir,switches()["tanBeta"])}

    for key in d :
        tag = key[-2:]
        d[key]["beforeDir"] = "mSuGraScan_beforeAll_%s"%tag
        d[key]["250Dirs"  ] = []
        d[key]["300Dirs"  ] = []
        d[key]["350Dirs"  ] = ["mSuGraScan_350_%s"%tag]
        d[key]["450Dirs"  ] = ["mSuGraScan_450_%s"%tag]
        d[key]["loYield"  ] = "m0_m12_mChi_0"

    d["muon"]["beforeDir"] = "mSuGraScan_beforeAll_10"
    d["muon"]["350Dirs"] = ["mSuGraScan_350_10"]
    d["muon"]["450Dirs"] = ["mSuGraScan_450_10"]

    d["ht"]["beforeDir"] = None
    d["ht"]["250Dirs"]   = ["Reco_Bin_250_HT_300"]
    d["ht"]["300Dirs"]   = ["Reco_Bin_300_HT_350"]
    d["ht"]["350Dirs"]   = ["Reco_Bin_350_HT_400", "Reco_Bin_400_HT_450"]
    d["ht"]["450Dirs"]   = ["Reco_Bin_450_HT_500", "Reco_Bin_500_HT_Inf"]
    
    return d

def stringsNoArgs() :
    d = {}

    #internal names
    if switches()["twoHtBins"] :
        d["pdfName"] = "TopLevelPdf"
        d["dataName"] = "ObservedNumberCountingDataWithSideband"
        d["signalVar"] = "masterSignal"
    else :
        d["pdfName"] = "total_model"
        d["dataName"] = "obsDataSet"
        d["signalVar"] = "s"

    #output name options
    d["outputDir"]      = "output"
    d["logDir"]         = "log"
    d["plotStem"]       = "%s/Significance"%d["outputDir"]
    d["workspaceStem"]  = "%s/Combine"%d["outputDir"]
    d["logStem"]        = "%s/job"%d["logDir"]
    d["mergedFile"]     = "%s/Significance_%s_tanBeta%d_%s_%s.root"%(d["outputDir"],
                                                                     switches()["method"],
                                                                     switches()["tanBeta"],
                                                                     "nlo" if switches()["nlo"] else "lo",
                                                                     "2HtBins" if switches()["twoHtBins"] else "1HtBin",
                                                                     )
    return d

def strings(xBin, yBin, zBin) :
    d = stringsNoArgs()
    #output name options
    d["tag"]               = "m0_%d_m12_%d_mZ_%d"%(xBin, yBin, zBin)
    d["plotFileName"]      = "%s_%s.pickled"%(d["plotStem"], d["tag"])
    d["workspaceFileName"] = "%s_%s.root"%(d["workspaceStem"], d["tag"])
    return d

