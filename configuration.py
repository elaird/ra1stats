#!/usr/bin/env python

def switches() :
    d = {}
    d["doBayesian"] = False
    d["doFeldmanCousins"] = False
    d["doMCMC"] = False

    d["testPointsOnly"] = True
    d["printCovarianceMatrix"] = False
    d["writeWorkspaceFile"] = False

    return d

def strings(m0, m12) :
    d = {}
    d["sourceFile"] = "Lepton2.C"
    
    d["signalFile"] = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_nlo.root"
    d["signalDir1"] = "mSuGraScan_beforeAll"
    d["signalDir2"] = "mSuGraScan_350"
    d["signalHistExample"] = "m0_m12_0"

    d["muonControlFile"] = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_muon.root"
    d["muonControlDir"]  = "mSuGraScan_350"
    d["muonControlHist"] = "m0_m12_0"

    d["sys05File"]       = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"
    d["sys2File"]        = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"

    #output name options
    d["outputDir"]         = "output"
    d["logDir"]            = "log"
    d["tag"]               = "m0_%d_m12_%d"%(m0, m12)
    d["plotStem"]          = "%s/Significance"%d["outputDir"]
    d["plotFileName"]      = "%s_%s.root"%(d["plotStem"], d["tag"])
    d["workspaceStem"]     = "%s/Combine"%d["outputDir"]
    d["workspaceFileName"] = "%s_%s.root"%(d["workspaceStem"], d["tag"])
    d["logStem"]           = "%s/job"%d["logDir"]

    return d

