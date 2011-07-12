#!/usr/bin/env python

import configuration as conf

def smsRanges() :
    d = {}

    d["smsXRange"] = (400.0, 999.9) #(min, max)
    d["smsYRange"] = (100.0, 999.9)
    d["smsXsZRangeLin"] = (0.0, 40.0, 40) #(zMin, zMax, nContours)
    d["smsXsZRangeLog"] = (0.4, 40.0, 40)
    d["smsEffZRange"]   = (0.0, 0.35, 35)

    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.40, 40)
    return d

def histoSpec(box = None, scale = None, htLower = None, htUpper = None) :
    assert box in ["had", "muon"]
    assert scale in ["1", "05", "2"]
    
    scan = [{"cmssw": "38", "had":"v2", "muon":"v1", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/38_scan/"},
            {"cmssw": "42", "had":"v1", "muon":"v1", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/42_scan/"},
            ][1]
    
    out = {}
    out["file"] = "/".join([scan["dir"], box, scan[box], box+".root"])
    out["beforeDir"] = "mSuGraScan_before_scale%s"%scale
    if htLower!=None :
        out["afterDir"] = "mSuGraScan_%d%s_scale%s"%(htLower, "_%d"%htUpper if htUpper else "",scale)
    return out
     
    #for model in ["T1", "T2"] :
    #    d[model] = {}
    #
    #model = "T1"
    #d[model]["sig10"]  = {"file": "%s/v5/SMSFinal/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir,model)}
    #d[model]["muon"]   = {"file": "%s/v5/MuonSMSsamples/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir,model)}
    #d[model]["ht"]     = {"file": "%s/v5/QCD/QcdBkgdEst_%s.root"%(dir, model.lower())}
    #d[model]["jes-"]   = {"file": "%s/v5/SMSFinal_JESMinus/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir, model)}
    #d[model]["jes+"]   = {"file": "%s/v5/SMSFinal_JESPlus/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir, model)}
    #d[model]["isr-"]   = {"file": "%s/v5/SMS_ISR_variation/v2/AK5Calo_mySUSYTopo%s_ISR.root"%(dir, model)}
    ##d[model]["isr-"]   = {"file": "%s/v7/ISR-nofilter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi.root"%(dir, model)}
    #
    #model = "T2"
    #d[model]["sig10"]  = {"file": "%s/v7/signal-filter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi_new.root"%(dir,model)}
    #d[model]["muon"]   = {"file": "%s/v5/MuonSMSsamples/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir,model)}
    #d[model]["ht"]     = {"file": "%s/v7/lowHT-filter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi_new.root"%(dir, model)}
    #d[model]["jes-"]   = {"file": "%s/v7/JESminus-filter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi_new.root"%(dir, model)}
    #d[model]["jes+"]   = {"file": "%s/v7/JESplus-filter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi_new.root"%(dir, model)}
    #d[model]["isr-"]   = {"file": "%s/v7/ISR-filter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi_new.root"%(dir, model)}
    #
    #for model in ["T1", "T2"] :
    #    
    #    for key in d[model] :
    #        tag = key[-2:]
    #        d[model][key]["beforeDir"] = "mSuGraScan_beforeAll_%s"%tag
    #        d[model][key]["250Dirs"  ] = []
    #        d[model][key]["300Dirs"  ] = []
    #        d[model][key]["350Dirs"  ] = ["mSuGraScan_350_%s"%tag]
    #        d[model][key]["450Dirs"  ] = ["mSuGraScan_450_%s"%tag]
    #        d[model][key]["loYield"  ] = "m0_m12_mChi_0"
    #        
    #    for key in ["jes-","jes+"] :
    #        d[model][key]["beforeDir"] = "mSuGraScan_beforeAll_10"
    #        d[model][key]["350Dirs"] = ["mSuGraScan_350_10"]
    #        d[model][key]["450Dirs"] = ["mSuGraScan_450_10"]
    #
    #    for key in ["isr-"] :
    #        d[model][key]["beforeDir"] = "isr_unc_before"
    #        d[model][key]["350Dirs"  ] = ["isr_unc_350"]
    #        d[model][key]["450Dirs"  ] = ["isr_unc_450"]
    #        d[model][key]["loYield"  ] = "m0_m12"
    #        
    #    #warning: non-intuitive keys chosen to use histo bin check "for free"
    #    d[model]["effUncRelPdf"] = {"file": "/vols/cms02/elaird1/27_pdf_unc_from_tanja/v7/Plots_%s.root"%model, "350Dirs": ["/"], "loYield": "final_pdf_unc_error"}
    #        
    #    d[model]["muon"]["beforeDir"] = "mSuGraScan_beforeAll"
    #    d[model]["muon"]["350Dirs"] = ["mSuGraScan_350"]
    #    d[model]["muon"]["450Dirs"] = ["mSuGraScan_450"]
    #
    #    d[model]["ht"]["beforeDir"] = None
    #    d[model]["ht"]["250Dirs"]   = ["Reco_Bin_250_HT_300"]
    #    d[model]["ht"]["300Dirs"]   = ["Reco_Bin_300_HT_350"]
    #    d[model]["ht"]["350Dirs"]   = ["Reco_Bin_350_HT_400", "Reco_Bin_400_HT_450"]
    #    d[model]["ht"]["450Dirs"]   = ["Reco_Bin_450_HT_500", "Reco_Bin_500_HT_Inf"]

    return d[modelIn]

def histoTitle() :
    if conf.switches()["signalModel"]=="T1" :
        return ";m_{gluino} (GeV);m_{LSP} (GeV)"
    if conf.switches()["signalModel"]=="T2" :
        return ";m_{squark} (GeV);m_{LSP} (GeV)"
    else :
        return ";m_{0} (GeV);m_{1/2} (GeV)"

