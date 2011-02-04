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

def stringsNoArgs() :
    dir = "/afs/cern.ch/user/e/elaird/public/20_yieldHistograms"

    d = {}
    d["sourceFile"] = "Lepton.C"
    #d["sourceFile"] = "SplitSignal.C"

    ##v1
    #d["signalFile"]      = "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_nlo.root"%dir
    #d["muonControlFile"] = "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_muon.root"%dir
    #d["sys05File"]       = "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"%dir
    #d["sys2File"]        = "%s/v1/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"%dir
    #
    #for item in ["muonControl", "signal", "sys05", "sys2"] :
    #    d["%sDir1"%item]    = "mSuGraScan_beforeAll"
    #    d["%sDir2"%item]    = "mSuGraScan_350"
    #    d["%sLoYield"%item] = "m0_m12_0"

    #v2
    d["signalFile"]      = "%s/v2/Signal/AK5Calo_tanBeta3.root"%dir
    d["muonControlFile"] = "%s/v2/Muon/AK5Calo_mSugra_TanBeta3.root"%dir
    d["sys05File"]       = "%s/v2/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"%dir
    d["sys2File"]        = "%s/v2/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"%dir

    for item in ["muonControl", "signal", "sys05", "sys2"] :
        d["%sDir1"%item]    = "mSuGraScan_beforeAll"
        d["%sDir2"%item]    = "mSuGraScan_350"
        d["%sLoYield"%item] = "m0_m12_mChi_0"

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

