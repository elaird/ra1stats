def smsRanges() :
    d = {}

    d["smsXRange"] = ( 50.0, 1499.9) #(min, max)
    d["smsYRange"] = ( 50.0, 1224.9)
    d["smsXsZRangeLin"] = (0.0,      2.0, 20) #(zMin, zMax, nContours)
    d["smsXsZRangeLog"] = (0.5e-2, 500.0, 20)
    d["smsEffZRange"]   = (0.0, 0.35, 35)

    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.40, 40)
    return d

def histoSpec(model = "", box = None, scale = None, htLower = None, htUpper = None, alphaTLower = None, alphaTUpper = None) :
    base = "/vols/cms02/elaird1/20_yieldHistograms/2011/"

    cmssm = {"tanBeta10":  {"cmssw":"42", "had":"v3", "muon":"v2"},
             "tanBeta40":  {"cmssw":"42", "had":"v2", "muon":"v2"},
             #"tanBeta10": {"cmssw":"38", "had":"v2", "muon":"v5"},
             }

    sms = {"T1":      {"had": "v3"},
           "T2":      {"had": "v3"},
           "T2tt":    {"had": "v1"},
           "TGQ_0p0": {"had": "v1"},
           "TGQ_0p2": {"had": "v1"},
           "TGQ_0p4": {"had": "v1"},
           "TGQ_0p8": {"had": "v1"},
           }

    out = {}
    if model in cmssm :
        assert box in ["had", "muon"]
        assert scale in ["1", "05", "2"]
        d = cmssm[model]
        if d["had"] in ["v3"]: print "WARNING: using %s had spec; v2 is the stable one."%d["had"]
        out["file"] = "/".join([base, "%s_scan"%d["cmssw"], model, box, d[box], box+".root"])
        out["beforeDir"] = "mSuGraScan_before_scale%s"%scale
        out["afterDir"] = "mSuGraScan"
    elif model in sms :
        assert box in ["had"]
        thresh = ""
        if htLower==275 : thresh = "0"
        if htLower==325 : thresh = "1"
        out["file"] = "/".join([base, "sms", model, box, sms[model][box], box+"%s.root"%thresh])
        out["beforeDir"] = "smsScan_before"
        out["afterDir"] = "smsScan"
    else :
        assert False, "model %s not in list"%model
    
    if alphaTLower    : out["afterDir"] += "_AlphaT%s"%alphaTLower
    if alphaTUpper    : out["afterDir"] += "_%s"%alphaTUpper
    if htLower        : out["afterDir"] += "_%d"%htLower
    if htUpper        : out["afterDir"] += "_%d"%htUpper
    if model in cmssm : out["afterDir"] += "_scale%s"%scale
    return out

def histoTitle(model = "") :
    d = {"T1"      : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T2"      : ";m_{squark} (GeV);m_{LSP} (GeV)",
         "T2tt"    : ";m_{stop} (GeV);m_{LSP} (GeV)",
         "TGQ_0p0" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p2" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p4" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p8" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         ""        : ";m_{0} (GeV);m_{1/2} (GeV)",
         }
    return d[model] if model in d else d[""]
