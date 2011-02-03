#!/usr/bin/env python

def switches() :
    d = {}
    d["doBayesian"] = False
    d["doFeldmanCousins"] = False
    d["doMCMC"] = False

    d["nlo"] = True
    d["testPointsOnly"] = True
    d["printCovarianceMatrix"] = False
    d["writeWorkspaceFile"] = False

    return d

def strings(m0, m12) :
    d = {}
    d["sourceFile"] = "Lepton.C"
    #d["sourceFile"] = "SplitSignal.C"

    d["signalFile"]      = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_nlo.root"
    d["muonControlFile"] = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_muon.root"
    d["sys05File"]       = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"
    d["sys2File"]        = "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"

    for item in ["muonControl", "signal", "sys05", "sys2"] :
        d["%sDir1"%item]    = "mSuGraScan_beforeAll"
        d["%sDir2"%item]    = "mSuGraScan_350"
        d["%sLoYield"%item] = "m0_m12_0"

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

