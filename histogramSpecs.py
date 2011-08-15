#!/usr/bin/env python

import configuration as conf

def smsRanges() :
    d = {}

    #d["smsXRange"] = (400.0, 999.9) #(min, max)
    #d["smsYRange"] = (100.0, 999.9)
    d["smsXsZRangeLin"] = (0.0,      2.0, 20) #(zMin, zMax, nContours)
    d["smsXsZRangeLog"] = (1.0e-2, 200.0, 20)
    d["smsEffZRange"]   = (0.0, 0.35, 35)

    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.40, 40)
    return d

def histoSpec(box = None, scale = None, htLower = None, htUpper = None) :
    assert box in ["had", "muon"]
    assert scale in ["1", "05", "2"]
    
    scan = [{"cmssw": "38", "had":"v2", "muon":"v5", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/38_scan/"},
            {"cmssw": "42", "had":"v2", "muon":"v2", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/42_scan/"},
            ][1]
    
    out = {}
    out["file"] = "/".join([scan["dir"], box, scan[box], box+".root"])
    out["beforeDir"] = "mSuGraScan_before_scale%s"%scale
    if htLower!=None :
        out["afterDir"] = "mSuGraScan_%d%s_scale%s"%(htLower, "_%d"%htUpper if htUpper else "",scale)
    return out

def smsHistoSpec(model = "", box = None, htLower = None, htUpper = None) :
    assert model in ["T1", "T2"]
    assert box in ["had", "muon"]
    
    scan = {"had":"v2", "muon":"v1", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/sms/%s/"%model}
    thresh = ""
    if htLower==275 : thresh = "0"
    if htLower==325 : thresh = "1"
    
    out = {}
    out["file"] = "/".join([scan["dir"], box, scan[box], box+"%s.root"%thresh])
    out["beforeDir"] = "smsScan_before"
    if htLower!=None :
        out["afterDir"] = "smsScan_%d%s"%(htLower, "_%d"%htUpper if htUpper else "")
    return out

    #2010 spec comments
    #d[model]["jes-"]   = {"file": "%s/v5/SMSFinal_JESMinus/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir, model)}
    #d[model]["jes+"]   = {"file": "%s/v5/SMSFinal_JESPlus/AK5Calo_PhysicsProcesses_Topology%s.root"%(dir, model)}
    #d[model]["isr-"]   = {"file": "%s/v5/SMS_ISR_variation/v2/AK5Calo_mySUSYTopo%s_ISR.root"%(dir, model)}
    ##d[model]["isr-"]   = {"file": "%s/v7/ISR-nofilter/AK5Calo_PhysicsProcesses_Topology%s_38xFall10_spadhi.root"%(dir, model)}
    #warning: non-intuitive keys chosen to use histo bin check "for free"
    #d[model]["effUncRelPdf"] = {"file": "/vols/cms02/elaird1/27_pdf_unc_from_tanja/v7/Plots_%s.root"%model, "350Dirs": ["/"], "loYield": "final_pdf_unc_error"}

def histoTitle() :
    if conf.switches()["signalModel"]=="T1" :
        return ";m_{gluino} (GeV);m_{LSP} (GeV)"
    if conf.switches()["signalModel"]=="T2" :
        return ";m_{squark} (GeV);m_{LSP} (GeV)"
    else :
        return ";m_{0} (GeV);m_{1/2} (GeV)"

