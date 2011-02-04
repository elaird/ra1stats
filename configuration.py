#!/usr/bin/env python

def switches() :
    d = {}
    d["doBayesian"] = False
    d["doFeldmanCousins"] = False
    d["doMCMC"] = False

    d["nlo"] = True
    d["fixQcdToZero"] = True
    
    d["testPointsOnly"] = True
    d["printCovarianceMatrix"] = False
    d["printByHandValues"] = False
    d["writeWorkspaceFile"] = False

    return d

def stringsNoArgs() :
    dir = "/afs/cern.ch/user/e/elaird/public/20_yieldHistograms"

    d = {}
    d["sourceFile"] = "Lepton.C"
    #d["sourceFile"] = "SplitSignal.C"

    d["signalFile"]      = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_nlo.root"
    d["muonControlFile"] = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_muon.root"
    d["sys05File"]       = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"
    d["sys2File"]        = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"

    #d["signalFile"]      = "%s/Signal/AK5Calo_tanBeta3.root"%dir
    #d["muonControlFile"] = "%s/Muon/AK5Calo_tanBeta3.root"%dir
    #d["sys05File"]       = "%s/QCDBkgd/QcdBkgdEst_tanbeta3.root"%dir
    #d["sys2File"]        = "%s/AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"%dir

    for item in ["muonControl", "signal", "sys05", "sys2"] :
        d["%sDir1"%item]    = "mSuGraScan_beforeAll"
        d["%sDir2"%item]    = "mSuGraScan_350"
        d["%sLoYield"%item] = "m0_m12_0"

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

