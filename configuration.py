#!/usr/bin/env python

def switches() :
    d = {}
    d["doBayesian"] = False
    d["doFeldmanCousins"] = False
    d["doMCMC"] = False

    d["nlo"] = False
    d["fixQcdToZero"] = True
    d["constrainParameters"] = False

    d["testPointsOnly"] = True
    d["printCovarianceMatrix"] = False
    d["printByHandValues"] = False
    d["writeWorkspaceFile"] = False

    d["twoHtBins"] = False
    
    return d

def histoSpecs() :
    dir = "/afs/cern.ch/user/e/elaird/public/20_yieldHistograms"

    d = {}

    ##v1
    #d["signal"] = {"file": "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_nlo.root"%dir}
    #d["muon"]   = {"file": "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_muon.root"%dir}
    #d["sys05"]  = {"file": "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"%dir}
    #d["sys2"]   = {"file": "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"%dir}

    ##v2
    #sig = "AK5Calo_PhysicsProcesses_mSUGRA_TanBeta3.root"
    #d["sig10"]  = {"file": "%s/v2/Signal/%s"%(dir, sig)}
    #d["muon"]   = {"file": "%s/v2/Muon/AK5Calo_mSugra_TanBeta3.root"%dir}
    #d["sig05"]  = {"file": "%s/v2/Signal/%s"%(dir, sig)}
    #d["sig20"]  = {"file": "%s/v2/Signal/%s"%(dir, sig)}
    #d["ht"]     = {"file": "%s/v2/QCDBkgd/QcdBkgdEst_tanbeta3.root"%dir}

    #v3
    sig = "AK5Calo_PhysicsProcesses_mSUGRA_TanBeta3.root"
    d["sig10"]  = {"file": "%s/v3/had/%s"%(dir, sig)}
    d["muon"]   = {"file": "%s/v3/muon/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3.root"%dir}
    d["sig05"]  = {"file": "%s/v3/had/%s"%(dir, sig)}
    d["sig20"]  = {"file": "%s/v3/had/%s"%(dir, sig)}
    d["ht"]     = {"file": "%s/v3/ht/QcdBkgdEst_tanbeta3.root"%dir}

    for key in d :
        d[key]["beforeDir"] = "mSuGraScan_beforeAll"
        d[key]["250Dirs"  ] = []
        d[key]["300Dirs"  ] = []
        d[key]["350Dirs"  ] = ["mSuGraScan_350_%s"%key[-2:]]
        d[key]["450Dirs"  ] = ["mSuGraScan_450_%s"%key[-2:]]
        d[key]["loYield"  ] = "m0_m12_mChi_0"

    d["muon"]["350Dirs"] = ["mSuGraScan_350"]
    d["muon"]["450Dirs"] = ["mSuGraScan_450"]

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
    d["outputDir"]         = "output"
    d["logDir"]            = "log"
    d["plotStem"]          = "%s/Significance"%d["outputDir"]
    d["workspaceStem"]     = "%s/Combine"%d["outputDir"]
    d["logStem"]           = "%s/job"%d["logDir"]
    return d

def strings(xBin, yBin, zBin) :
    d = stringsNoArgs()
    #output name options
    d["tag"]               = "m0_%d_m12_%d_mZ_%d"%(xBin, yBin, zBin)
    d["plotFileName"]      = "%s_%s.root"%(d["plotStem"], d["tag"])
    d["workspaceFileName"] = "%s_%s.root"%(d["workspaceStem"], d["tag"])
    return d

