#!/usr/bin/env python

def switches() :
    d = {}

    d["method"] = "profileLikelihood"
    #d["method"] = "feldmanCousins"

    d["nlo"] = True
    #this is the list of valid signalModels: T1, T2, tanBeta3, tanBeta10, tanBeta50
    #d["signalModel"] = "T2"
    d["signalModel"] = "tanBeta3"

    d["testPointsOnly"] = True
    d["twoHtBins"] = True
    d["exponentialBkg"] = False

    d["ignoreSignalContamination"] = False
    d["assumeUncorrelatedLowHtSystematics"] = True
    d["constrainParameters"] = False

    d["printCovarianceMatrix"] = False
    d["writeWorkspaceFile"] = False
    
    if len(d["signalModel"])==2 : d["nlo"] = False
    return d

def histoSpecs() :
    dir = "/afs/cern.ch/user/e/elaird/public/20_yieldHistograms"

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
            d[model][key]["title"    ] = ";m_{0} (GeV);m_{1/2} (GeV)"

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
            if model=="T1" :
                d[model][key]["title"] = ";m_{gluino} (GeV);m_{LSP} (GeV)"
            elif model=="T2" :
                d[model][key]["title"] = ";m_{squark} (GeV);m_{LSP} (GeV)"
            
            d[model]["muon"]["beforeDir"] = "mSuGraScan_beforeAll"
            d[model]["muon"]["350Dirs"] = ["mSuGraScan_350"]
            d[model]["muon"]["450Dirs"] = ["mSuGraScan_450"]
            
        d[model]["ht"]["beforeDir"] = None
        d[model]["ht"]["250Dirs"]   = ["Reco_Bin_250_HT_300"]
        d[model]["ht"]["300Dirs"]   = ["Reco_Bin_300_HT_350"]
        d[model]["ht"]["350Dirs"]   = ["Reco_Bin_350_HT_400", "Reco_Bin_400_HT_450"]
        d[model]["ht"]["450Dirs"]   = ["Reco_Bin_450_HT_500", "Reco_Bin_500_HT_Inf"]

    return d[switches()["signalModel"]]

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
    d["mergedFile"]     = "%s/%s_%s_%s_%s_%s.root"%(d["outputDir"],
                                                    switches()["method"],
                                                    switches()["signalModel"],
                                                    "nlo" if switches()["nlo"] else "lo",
                                                    "2HtBins" if switches()["twoHtBins"] else "1HtBin",
                                                    "expR" if switches()["exponentialBkg"] else "constantR",
                                                    )
    return d

def strings(xBin, yBin, zBin) :
    d = stringsNoArgs()
    #output name options
    d["tag"]               = "m0_%d_m12_%d_mZ_%d"%(xBin, yBin, zBin)
    d["plotFileName"]      = "%s_%s.pickled"%(d["plotStem"], d["tag"])
    d["workspaceFileName"] = "%s_%s.root"%(d["workspaceStem"], d["tag"])
    return d

