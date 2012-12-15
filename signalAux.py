#joint SMS-CMSSM
def xsHistoSpec(model = "", cmssmProcess = "", xsVariation = "") :
    if not cmssmProcess :
        if xsVariation!="default":
            print 'WARNING: variation "%s" for SMS %s will need to use error bars in xs file.'%(xsVariation, model)
    else :
        print "WARNING: using 7 TeV xs for model %s, process %s"%(model, cmssmProcess)

    base = "xs"
    #seven = "%s/v5/7TeV.root"%base
    eight = "%s/v5/8TeV.root"%base;
    tgqFile = "%s/v1/TGQ_xSec.root"%base
    tanBeta10 = "%s/v5/7TeV_cmssm.root"%base
    d = {"T2":          {"histo": "squark", "factor": 1.0,  "file": eight},
         "T2tt":        {"histo": "stop_or_sbottom","factor": 1.0,  "file": eight},
         "T2bb":        {"histo": "stop_or_sbottom","factor": 1.0,  "file": eight},
         "tanBeta10":   {"histo": "%s_%s"%(cmssmProcess, xsVariation),  "factor": 1.0,  "file": tanBeta10},
         }

    for item in ["T1", "T1bbbb", "T1tttt", "T5zz"] :
        d[item] = {"histo":"gluino", "factor":1.0,  "file":eight}

    for item in ["TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8"] :
        d[item] = {"histo":"clone", "factor":1.0, "file":tgqFile}

    assert model in d,"model=%s"%model
    return d[model]

def effHistoSpec(model = "", box = None, scale = None, htLower = None, htUpper = None,
                 bJets = None, jets = None, xsVariation = None) :
    #xsVariation is ignored
    base = "ra1e/2012/"

    cmssm = {"tanBeta10":  {"cmssw":"rw", "had":"v2", "muon":"v2"},
             #"tanBeta10":  {"cmssw":"42", "had":"v8", "muon":"v8"},
             "tanBeta40":  {"cmssw":"42", "had":"v2", "muon":"v2"},
             }

    sms = {"T1":          {"had": "v5"},
           "T2":          {"had": "v1"},
           "T2tt":        {"had": "v1", "muon": "v1"},
           "T2bb":        {"had": "v3", "muon": "v3"},
           "T2bw":        {"had": "mchi0.75", "muon": "mchi0.75"},
           "T5zz":        {"had": "v1", "muon": "v1"},
           "T1bbbb":      {"had": "v3", "muon": "v3"},
           "T1tttt":      {"had": "v1", "muon": "v1"},
           "T1tttt_ichep":{"had": "2012full", "muon": "2012full"},
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
    tags = []
    if model in cmssm :
        oldBase = base
        base = "ra1e/2011/"
        print 'WARNING: modifying base "%s" to "%s" for model %s.'%(oldBase, base, model)
        assert box in ["had", "muon"]
        if scale not in ["1", "05", "2"] :
            print "WARNING: assuming scale=1"
            scale="1"
        d = cmssm[model]
        out["file"] = "/".join([base, "%s_scan"%d["cmssw"], model, box, d[box], box+"%s.root"%thresh])
        out["beforeDir"] = "mSuGraScan_before_scale%s"%scale
        tags.append("mSuGraScan")
    elif model in sms :
        assert box in ["had","muon"]
        out["file"] = "/".join([base, "sms", model, box, sms[model][box], box+"%s.root"%thresh])
        out["beforeDir"] = "smsScan_before"
        tags.append("smsScan")
    else :
        assert False, "model %s not in list"%model

    if bJets :
        tags.append(bJets)
    if jets :
        tags.append(jets)

    if box=="had":
        tags.append("AlphaT55")
    else:
        tags.append("NoAlphaT")

    if htLower :
        tags.append("%d"%htLower)
    if htUpper :
        tags.append("%d"%htUpper)
    if model in cmssm :
        tags.append("scale%s"%scale)

    out["afterDir"] = "_".join(tags)
    return out

#SMS
def ranges(model) :
    x = {"T1":   ( 287.5, 1400), #(min, max)
         "T2":   ( 287.5, 1000),
         "T2tt": ( 300.0, 800.0),
         "T2bb": ( 287.5, 900.0),
         "T1bbbb": ( 287.5, 1400),
         "T1tttt": ( 400.0, 1400),
         "T1tttt_2012": ( 375.0, 1200.0),
         "tanBeta10": (0.0, 4000.0),
         }
    y = {"T5zz":   (50.0, 999.9), #(min, max)
         "T1":     ( 0.0, 1225),
         "T2":     ( 0.0,  825),
         "T2tt":   ( 0.0,  600),
         "T2bb":   ( 0.0,  725),
         "T1bbbb": ( 0.0, 1225),
         "T1tttt": ( 0.0, 1050),
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
            "T2tt": [ 12, 4, 0 ],
            "T1bbbb": [ 10, 4, 0 ],
            "T1tttt": [ 10, 4, 0 ],
            "T1tttt_2012": [ 8, 4, 0 ]
            }

    d = {}
    d["xRange"] = x.get(model, (50.0, 1499.9))
    d["yRange"] = y.get(model, (50.0, 1224.9))

    d["xDivisions"] = xDivisions.get(model, None)
    d["yDivisions"] = yDivisions.get(model, None)

    d["xsZRangeLin"] = (0.0,      2.0, 20) #(zMin, zMax, nContours)
    d["xsZRangeLog"] = (1.0e-3,  10.0, 20)
    d["effZRange"]   = (0.0, 0.35, 35)

    d["effUncExpZRange"] = (0.0, 0.20, 20)
    d["effUncThZRange"] = (0.0, 0.40, 40)
    return d

def chi() :
    return "#tilde{#chi}^{0}_{1}"

def processStamp(key = "") :
    dct = {
        ''     : {
        'text': "",
        'xpos': 0.4250,
        },
        'T2'     : {
        'text': "pp #rightarrow #tilde{q} #tilde{q}, #tilde{q} #rightarrow q %s; m(#tilde{g})>>m(#tilde{q})"%chi(),
        'xpos': 0.4250,
        },
        'T2bb'   : {
        'text': "pp #rightarrow #tilde{b} #tilde{b}, #tilde{b} #rightarrow b %s; m(#tilde{g})>>m(#tilde{b})"%chi(),
        'xpos': 0.425,
        },
        'T2tt'   : {
        'text': "pp #rightarrow #tilde{t} #tilde{t}, #tilde{t} #rightarrow t %s; m(#tilde{g})>>m(#tilde{t})"%chi(),
        'xpos': 0.41,
        },
        'T1'     : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow q #bar{q} %s; m(#tilde{q})>>m(#tilde{g})"%chi(),
        'xpos': 0.4325,
        },
        'T1bbbb' : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow b #bar{b} %s; m(#tilde{b})>>m(#tilde{g})"%chi(),
        'xpos': 0.43,
        },
        'T1tttt' : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow t #bar{t} %s; m(#tilde{t})>>m(#tilde{g})"%chi(),
        'xpos': 0.425,
        },
        }
    return dct.get(key, dct[""])

def histoTitle(model = "") :
    d = {"T1"           : ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T2"           : ";m_{squark} (GeV);m_{LSP} (GeV)",
         "T2tt"         : ";m_{stop} (GeV);m_{LSP} (GeV)",
         "T2bb"         : ";m_{sbottom} (GeV);m_{LSP} (GeV)",
         "T2bw"         : ";m_{UKNOWN} (GeV);m_{UNKNOWN_2} (GeV)",
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

#CMSSM
def benchmarkPoints() :
    out = {}
    fields =                       [  "m0",  "m12",  "A0", "tanBeta", "sgn(mu)"]
    #out["LM0" ] = dict(zip(fields, [   200,    160,  -400,        10,         1]))
    #out["LM1" ] = dict(zip(fields, [    60,    250,     0,        10,         1]))
    out["LM2" ] = dict(zip(fields, [   185,    350,     0,        35,         1]))
    out["LM3" ] = dict(zip(fields, [   330,    240,     0,        20,         1]))
    #out["LM4" ] = dict(zip(fields, [   210,    285,     0,        10,         1]))
    #out["LM5" ] = dict(zip(fields, [   230,    360,     0,        10,         1]))
    #out["LM6" ] = dict(zip(fields, [    85,    400,     0,        10,         1]))
    out["LM7" ] = dict(zip(fields, [  3000,    230,     0,        10,         1]))
    out["LM8" ] = dict(zip(fields, [   500,    300,  -300,        10,         1]))
    out["LM9" ] = dict(zip(fields, [  1450,    175,     0,        50,         1]))
    out["LM10"] = dict(zip(fields, [  3000,    500,     0,        10,         1]))
    out["LM11"] = dict(zip(fields, [   250,    325,     0,        35,         1]))
    out["LM12"] = dict(zip(fields, [  2545,    247,  -866,        48,         1]))
    out["LM13"] = dict(zip(fields, [   270,    218,  -553,        40,         1]))

    #out["IM1" ] = dict(zip(fields, [   100,    510,     0,        10,         1]))
    #out["IM2" ] = dict(zip(fields, [   180,    510,     0,        10,         1]))
    #out["IM3" ] = dict(zip(fields, [   260,    450,     0,        10,         1]))
    out["IM4" ] = dict(zip(fields, [   820,    390,     0,        10,         1]))

    out["RM1" ] = dict(zip(fields, [   320,    520,     0,        10,         1]))
    out["RM2" ] = dict(zip(fields, [  1800,    280,     0,        10,         1]))
    return out

def scanParameters() :
    out = {}
    fields =                            ["A0", "tanBeta", "sgn(mu)"]
    out["tanBeta3" ] = dict(zip(fields, [   0,         3,         1]))
    out["tanBeta10"] = dict(zip(fields, [   0,        10,         1]))
    out["tanBeta50"] = dict(zip(fields, [   0,        50,         1]))
    return out

def processes() :
    return ["gg", "sb", "ss", "sg", "ll", "nn", "ng", "bb", "tb", "ns"]
