from configuration import locations

def smsRanges(model) :
    x = {"":     ( 50.0, 1499.9), #(min, max)
         "T1":   ( 50.0, 1224.9),
         "T5zz": (400.0, 1224.9),
         }
    y = {"":     ( 50.0, 1224.9), #(min, max)
         "T5zz": ( 50.0,  999.9),
         }
    
    d = {}

    d["smsXRange"] = x[model if model in x else ""]
    d["smsYRange"] = y[model if model in y else ""]
    d["smsXsZRangeLin"] = (0.0,      2.0, 20) #(zMin, zMax, nContours)
    d["smsXsZRangeLog"] = (1.0e-3, 100.0, 20)
    d["smsEffZRange"]   = (0.0, 0.35, 35)

    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.40, 40)
    return d

def histoSpec(model = "", box = None, scale = None, htLower = None, htUpper = None, alphaTLower = None, alphaTUpper = None, bTag = None, nbTag = None, bTagLower = None) :
    assert not ( nbTag and bTagLower ), "cannot specify both an exact number of btags and a lower limit"

    base = locations()["eff"]

    cmssm = {"tanBeta10":  {"cmssw":"42", "had":"v6", "muon":"v6"},
             "tanBeta40":  {"cmssw":"42", "had":"v2", "muon":"v2"},
             #"tanBeta10": {"cmssw":"38", "had":"v2", "muon":"v5"},
             }

    sms = {"T1":      {"had": "v4"},
           "T2":      {"had": "v4"},
           "T2tt":    {"had": "v6", "muon": "v6"},
           "T2bb":    {"had": "v1", "muon": "v1"},
           "T5zz":    {"had": "v1", "muon": "v1"},
           "TGQ_0p0": {"had": "v1"},
           "TGQ_0p2": {"had": "v1"},
           "TGQ_0p4": {"had": "v1"},
           "TGQ_0p8": {"had": "v1"},
           }

    #remove these hard-coded numbers
    thresh = ""
    if htLower==275 : thresh = "0"
    if htLower==325 : thresh = "1"

    out = {}
    if model in cmssm :
        assert box in ["had", "muon"]
        assert scale in ["1", "05", "2"]
        d = cmssm[model]
        out["file"] = "/".join([base, "%s_scan"%d["cmssw"], model, box, d[box], box+"%s.root"%thresh])
        out["beforeDir"] = "mSuGraScan_before_scale%s"%scale
        out["afterDir"] = "mSuGraScan"
    elif model in sms :
        assert box in ["had","muon"]
        out["file"] = "/".join([base, "sms", model, box, sms[model][box], box+"%s.root"%thresh])
        out["beforeDir"] = "smsScan_before"
        out["afterDir"] = "smsScan"
    else :
        assert False, "model %s not in list"%model
    
    if bTag           : out["afterDir"] += "_btag"
    if nbTag          : out["afterDir"] += "_==_%d"%nbTag
    if bTagLower      : out["afterDir"] += "_>_%d"%bTagLower
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
         "T2bb"    : ";m_{sbottom} (GeV);m_{LSP} (GeV)",
         "T5zz"    : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "TGQ_0p0" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p2" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p4" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p8" : ";m_{gluino} (GeV);m_{squark} (GeV)",
         ""        : ";m_{0} (GeV);m_{1/2} (GeV)",
         }
    return d[model] if model in d else d[""]
