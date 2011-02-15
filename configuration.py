#!/usr/bin/env python
import os

def checkAndAdjust(d) :
    assert d["signalModel"] in ["T1", "T2", "tanBeta3", "tanBeta10", "tanBeta50"]
    if len(d["signalModel"])==2 :
        d["nlo"] = False
        d["minSignalEventsForConsideration"] = None
        d["maxSignalEventsForConsideration"] = None

def singleJobOnly() :
    d = switches()
    return any([d[item] for item in ["hardCodedSignalContamination"]])

def switches() :
    d = {}

    d["method"] = "profileLikelihood"
    #d["method"] = "feldmanCousins"

    d["nlo"] = True
    #d["signalModel"] = "T1"
    d["signalModel"] = "tanBeta3"

    d["debugOutput"] = False
    d["testPointOnly"] = True
    d["twoHtBins"] = True
    d["exponentialBkg"] = False

    d["computeExpectedLimit"] = False
    d["nToys"] = 200

    d["hardCodedSignalContamination"] = False
    d["assumeUncorrelatedLowHtSystematics"] = True
    d["constrainParameters"] = False

    d["Ra2SyncHack"] = False
    d["printCovarianceMatrix"] = False
    d["writeWorkspaceFile"] = False
    d["writeGraphVizTree"] = False

    d["CL"] = 0.95
    d["minSignalEventsForConsideration"] =  1.0
    d["maxSignalEventsForConsideration"] = 50.0

    checkAndAdjust(d)
    return d

def isCern() :
    return ("cern.ch" in os.environ["HOSTNAME"])

def histoSpecs() :
    dir = "/afs/cern.ch/user/e/elaird/public/20_yieldHistograms" if isCern() else "/vols/cms02/elaird1/20_yieldHistograms"

    d = {}
    for model in ["tanBeta3", "tanBeta10", "tanBeta50"] :
        d[model] = {}
    
        f = "AK5Calo_PhysicsProcesses_mSUGRA_%s.root"%(model.lower())
        d[model]["sig10"]  = {"file": "%s/v5/Signal/%s"%(dir, f)}
        d[model]["muon"]   = {"file": ("%s/v5/muon/%s"%(dir, f) ).replace(".root", "_Muon.root")}
        d[model]["sig05"]  = {"file": "%s/v5/Signal/%s"%(dir, f)}
        d[model]["sig20"]  = {"file": "%s/v5/Signal/%s"%(dir, f)}
        d[model]["ht"]     = {"file": "%s/v5/QCD/QcdBkgdEst_%s.root"%(dir, model.lower())}

        for key in d[model] :
            tag = key[-2:]
            d[model][key]["beforeDir"] = "mSuGraScan_beforeAll_%s"%tag
            d[model][key]["250Dirs"  ] = []
            d[model][key]["300Dirs"  ] = []
            d[model][key]["350Dirs"  ] = ["mSuGraScan_350_%s"%tag]
            d[model][key]["450Dirs"  ] = ["mSuGraScan_450_%s"%tag]
            d[model][key]["loYield"  ] = "m0_m12_mChi_0"

        d[model]["muon"]["beforeDir"] = "mSuGraScan_beforeAll_10"
        d[model]["muon"]["350Dirs"] = ["mSuGraScan_350_10"]
        d[model]["muon"]["450Dirs"] = ["mSuGraScan_450_10"]
            
        d[model]["ht"]["beforeDir"] = None
        d[model]["ht"]["250Dirs"]   = ["Reco_Bin_250_HT_300"]
        d[model]["ht"]["300Dirs"]   = ["Reco_Bin_300_HT_350"]
        d[model]["ht"]["350Dirs"]   = ["Reco_Bin_350_HT_400", "Reco_Bin_400_HT_450"]
        d[model]["ht"]["450Dirs"]   = ["Reco_Bin_450_HT_500", "Reco_Bin_500_HT_Inf"]

    for model in ["T1", "T2"] :
        d[model] = {}
    
        d[model]["sig10"]  = {"file": "%s/v5/SMSFinal/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir,model)}
        d[model]["muon"]   = {"file": "%s/v5/MuonSMSsamples/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir,model)}
        d[model]["ht"]     = {"file": "%s/v5/QCD/QcdBkgdEst_%s.root"%(dir, model.lower())}
        
        for key in d[model] :
            tag = key[-2:]
            d[model][key]["beforeDir"] = "mSuGraScan_beforeAll_%s"%tag
            d[model][key]["250Dirs"  ] = []
            d[model][key]["300Dirs"  ] = []
            d[model][key]["350Dirs"  ] = ["mSuGraScan_350_%s"%tag]
            d[model][key]["450Dirs"  ] = ["mSuGraScan_450_%s"%tag]
            d[model][key]["loYield"  ] = "m0_m12_mChi_0"
            
            d[model]["muon"]["beforeDir"] = "mSuGraScan_beforeAll"
            d[model]["muon"]["350Dirs"] = ["mSuGraScan_350"]
            d[model]["muon"]["450Dirs"] = ["mSuGraScan_450"]
            
        d[model]["ht"]["beforeDir"] = None
        d[model]["ht"]["250Dirs"]   = ["Reco_Bin_250_HT_300"]
        d[model]["ht"]["300Dirs"]   = ["Reco_Bin_300_HT_350"]
        d[model]["ht"]["350Dirs"]   = ["Reco_Bin_350_HT_400", "Reco_Bin_400_HT_450"]
        d[model]["ht"]["450Dirs"]   = ["Reco_Bin_450_HT_500", "Reco_Bin_500_HT_Inf"]

    return d[switches()["signalModel"]]

def histoTitle() :
    if switches()["signalModel"]=="T1" :
        return ";m_{gluino} (GeV);m_{LSP} (GeV)"
    if switches()["signalModel"]=="T2" :
        return ";m_{squark} (GeV);m_{LSP} (GeV)"
    else :
        return ";m_{0} (GeV);m_{1/2} (GeV)"

def mergedFile(outputDir, switches) :
    out  = "%s/"%outputDir
    out += "_".join([switches["method"],
                     switches["signalModel"],
                     "nlo" if switches["nlo"] else "lo",
                     "2HtBins" if switches["twoHtBins"] else "1HtBin",
                     "expR" if switches["exponentialBkg"] else "constantR",
                     ])
    for item in ["Ra2SyncHack", "computeExpectedLimit"] :
        if switches[item] : out += "_%s"%item
    out += ".root"
    return out

def stringsNoArgs() :
    d = {}

    d["sourceFiles"] = ["RooMyPdf.cxx", "SlimPdfFactory.C"]
    d["subCmd"] = "bsub" if isCern() else "qsub"
    d["envScript"] = "env.sh" if isCern() else "envIC.sh"

    #internal names
    d["workspaceName"]   = "Combine"
    d["modelConfigName"] = "Combine"
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
    d["workspaceStem"]  = "%s/%s"%(d["outputDir"], d["workspaceName"])
    d["logStem"]        = "%s/job"%d["logDir"]
    d["mergedFile"]     = mergedFile(d["outputDir"], switches())
    return d

def strings(xBin, yBin, zBin) :
    d = stringsNoArgs()
    #output name options
    d["tag"]               = "m0_%d_m12_%d_mZ_%d"%(xBin, yBin, zBin)
    d["pickledFileName"]   = "%s_%s.pickled"%(d["plotStem"], d["tag"])
    d["workspaceFileName"] = "%s_%s.root"%(d["workspaceStem"], d["tag"])
    return d

