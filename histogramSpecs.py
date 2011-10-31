import configuration as conf

def smsRanges() :
    d = {}

    d["smsXRange"] = ( 50.0, 1224.9) #(min, max)
    d["smsYRange"] = ( 50.0, 1224.9)
    d["smsXsZRangeLin"] = (0.0,      2.0, 20) #(zMin, zMax, nContours)
    d["smsXsZRangeLog"] = (0.5e-2, 500.0, 20)
    d["smsEffZRange"]   = (0.0, 0.35, 35)

    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.40, 40)
    return d

def cmssmHistoSpec(model = "", box = None, scale = None, htLower = None, htUpper = None, alphaTLower = None, alphaTUpper = None) :
    out = {}

    if model in ["tanBeta10", "tanBeta40"] :
        beforeDir = "mSuGraScan"
        scan = [{"cmssw": "38", "had":"v2", "muon":"v5", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/38_scan/"},
                {"cmssw": "42", "had":"v3", "muon":"v2", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/42_scan/"},
                ][1]
        if scan["had"] in ["v3"]: print "WARNING: using %s had spec; v2 is the stable one."%scan["had"]

        out["file"] = "/".join([scan["dir"], model, box, scan[box], box+".root"])
        out["beforeDir"] = "mSuGraScan_before_scale%s"%scale
        out["afterDir"] = "mSuGraScan"
        cmssm = True
    elif model in ["T1", "T2"] :
        scan = {"had":"v3", "muon":"v1", "dir":"/vols/cms02/elaird1/20_yieldHistograms/2011/sms/%s/"%model}
        thresh = ""
        if htLower==275 : thresh = "0"
        if htLower==325 : thresh = "1"
        out["file"] = "/".join([scan["dir"], box, scan[box], box+"%s.root"%thresh])
        out["beforeDir"] = "smsScan_before"
        out["afterDir"] = "smsScan"
        cmssm = False
    else :
        assert False, "model %s not in list"%model
    
    assert box in ["had", "muon"]
    assert scale in ["1", "05", "2"]
    
    if alphaTLower : out["afterDir"] += "_AlphaT%s"%alphaTLower
    if alphaTUpper : out["afterDir"] += "_%s"%alphaTUpper
    if htLower     : out["afterDir"] += "_%d"%htLower
    if htUpper     : out["afterDir"] += "_%d"%htUpper
    if cmssm       : out["afterDir"] += "_scale%s"%scale
    return out

def smsHistoSpec(**args) :
    return cmssmHistoSpec(**args)

def histoTitle() :
    if conf.switches()["signalModel"]=="T1" :
        return ";m_{gluino} (GeV);m_{LSP} (GeV)"
    if conf.switches()["signalModel"]=="T2" :
        return ";m_{squark} (GeV);m_{LSP} (GeV)"
    else :
        return ";m_{0} (GeV);m_{1/2} (GeV)"

