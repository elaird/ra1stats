from configuration import locations

def ranges(model) :
    x = {"T1":   ( 312.5, 1200.0), #(min, max)
         "T2":   ( 312.5, 1200.0),
         "T2tt": ( 312.5, 1200.0),
         "T2bb": ( 312.5, 1200.0),
         "T1bbbb": ( 312.5, 1200.0),
         "T1tttt": ( 440.0, 1200.0),
         "T1tttt_2012": ( 375.0, 1200.0),
         "tanBeta10": (0.0, 4000.0),
         }
    y = {"T5zz": ( 50.0,  999.9), #(min, max)
         "T1":   ( 50.0, 1000.0),
         "T2":   ( 50.0, 1000.0),
         "T2tt": ( 50.0, 1000.0),
         "T2bb": ( 50.0, 1000.0),
         "T1bbbb": ( 50.0, 1000.0),
         "T1tttt": ( 50.0, 800.0),
         "T1tttt_2012": ( 50.0, 800.0),
         "tanBeta10": (0.0, 4000.0),
         }

    # [ primary, secondary, tertiary ] divisions
    xDivisions = {
            "T1": [ 10, 4, 0 ],
            "T2": [ 10, 4, 0 ],
            "T2bb": [ 10, 4, 0 ],
            "T2tt": [ 10, 4, 0 ],
            "T1bbbb": [ 10, 4, 0 ],
            "T1tttt": [ 8, 4, 0 ],
            "T1tttt_2012": [ 8, 4, 0 ],
            }

    yDivisions = {
            "T1": [ 10, 4, 0 ],
            "T2": [ 10, 4, 0 ],
            "T2bb": [ 10, 4, 0 ],
            "T2tt": [ 10, 4, 0 ],
            "T1bbbb": [ 10, 4, 0 ],
            "T1tttt_2012": [ 8, 4, 0 ]
            }

    d = {}
    d["xRange"] = x.get(model, (50.0, 1499.9))
    d["yRange"] = y.get(model, (50.0, 1224.9))

    d["xDivisions"] = xDivisions.get(model, None)
    d["yDivisions"] = yDivisions.get(model, None)

    d["xsZRangeLin"] = (0.0,      2.0, 20) #(zMin, zMax, nContours)
    d["xsZRangeLog"] = (1.0e-3, 100.0, 20)
    d["effZRange"]   = (0.0, 0.35, 35)

    d["effUncExpZRange"] = (0.0, 0.20, 20)
    d["effUncThZRange"] = (0.0, 0.40, 40)
    return d


def histoSpec(model = "", box = None, scale = None, htLower = None, htUpper = None, alphaTLower = None, alphaTUpper = None, nbTag = None, bTagLower = None) :
    assert not ( nbTag and bTagLower ), "cannot specify both an exact number of btags and a lower limit"

    base = locations()["eff"]

    cmssm = {"tanBeta10":  {"cmssw":"rw", "had":"v2", "muon":"v2"},
             #"tanBeta10":  {"cmssw":"42", "had":"v8", "muon":"v8"},
             "tanBeta40":  {"cmssw":"42", "had":"v2", "muon":"v2"},
             }

    sms = {"T1":          {"had": "rw_fix"},
           "T2":          {"had": "rw_fix"},
           "T2tt":        {"had": "rw_fix", "muon": "rw_fix"},
           "T2bb":        {"had": "rw_fix", "muon": "rw_fix"},
           "T5zz":        {"had": "v1", "muon": "v1"},
           "T1bbbb":      {"had": "rw_fix", "muon": "rw_fix"},
           "T1tttt":      {"had": "v3", "muon": "v3"},
           "T1tttt_2012": {"had": "2012full_newIDs", "muon": "2012full_newIDs"},
           "TGQ_0p0":     {"had": "v1"},
           "TGQ_0p2":     {"had": "v1"},
           "TGQ_0p4":     {"had": "v1"},
           "TGQ_0p8":     {"had": "v1"},
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

    if nbTag is not None     : out["afterDir"] += "_btag_==_%s"%nbTag
    if bTagLower is not None : out["afterDir"] += "_btag_>_%s"%bTagLower
    #if box == "muon":
        #if alphaTLower    : out["afterDir"] += "_NoAlphaT"
    #else:
        #if alphaTLower    : out["afterDir"] += "_AlphaT%s"%alphaTLower
    if alphaTLower    : out["afterDir"] += "_AlphaT%s"%alphaTLower
    if alphaTUpper    : out["afterDir"] += "_%s"%alphaTUpper
    if htLower        : out["afterDir"] += "_%d"%htLower
    if htUpper        : out["afterDir"] += "_%d"%htUpper
    if model in cmssm : out["afterDir"] += "_scale%s"%scale
    return out

def histoTitle(model = "") :
    d = {"T1"           : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T2"           : ";m_{squark} (GeV);m_{LSP} (GeV)",
         "T2tt"         : ";m_{stop} (GeV);m_{LSP} (GeV)",
         "T2bb"         : ";m_{sbottom} (GeV);m_{LSP} (GeV)",
         "T5zz"         : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T1bbbb"       : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T1tttt"       : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T1tttt_2012"  : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "TGQ_0p0"      : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p2"      : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p4"      : ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p8"      : ";m_{gluino} (GeV);m_{squark} (GeV)",
         ""             : ";m_{0} (GeV);m_{1/2} (GeV)",
         }
    return d[model] if model in d else d[""]
