import directories
from . import modelList
models = modelList.models


def effUncRel(model=""):
    return {"T1": 0.140, "T1bbbb": 0.160, "T1tttt": 0.230,
            "T2": 0.134, "T2bb": 0.131, "T2tt": 0.139, "T2cc": 0.20,
            "T1tttt_ichep": 0.230, "tanBeta10_7": 0.1736,
            }[model]


def effUncRelModified(model="", raw=None):
    if raw < 0.05:
        return effUncRel(model)
    else:
        return raw


def whiteListOfPoints(model="", respect=False):
    if not respect:
        return []

    # in GeV
    return {"T1": [(700.0, 300.0)],
            "T1bbbb": [(900.0, 500.0)],
            "T1tttt": [(850.0, 250.0)],
            "T2tt": [(387.5, 12.5)],
            #"T2tt": [(550.0,  20.0)],
            #"T2tt": [(400.0,   0.0)],
            #"T2tt": [(410.0,  20.0)],
            #"T2tt": [(420.0,  20.0)],
            "T2bb": [(500.0, 150.0)],
            "T2": [(600.0, 250.0)],
            #"T2": [(750.0, 0.0)],
            #"T2": [(450.0, 0.0)],
            #"T2": [(350.0, 100.0)],
            #"T2": [(400.0, 25.0)],
            #"T2": [(400.0, 50.0)],
            #"T2": [(375.0, 50.0)],
            "T2cc": [(250.0, 240.0)],
            #"T2cc": [(175.0, 165.0)],
            }.get(model, [])


def xsHistoSpec(model=None, cmssmProcess=""):
    if model.isSms and (model.xsVariation != "default"):
        error = 'ERROR: variation "%s" (%s)' % (model.xsVariation, model.name)
        error += ' will need to use error bars in xs file.'
        assert False, error

    base = directories.xs()
    assert model.com in [7, 8], model.com
    sms = "%s/v5/%dTeV.root" % (base, model.com)

    d = {"T2":      {"histo": "squark", "file": sms},
         "T2tt":    {"histo": "stop_or_sbottom", "file": sms},
         "T2bb":    {"histo": "stop_or_sbottom", "file": sms},
         "T2cc":    {"histo": "stop_or_sbottom", "file": sms},
         "tanBeta10_7": {"histo": "%s_%s" % (cmssmProcess, model.xsVariation),
                         "file": "%s/v5/7TeV_cmssm.root" % base},
         }

    for item in ["T1", "T1bbbb", "T1tttt", "T5zz_7"]:
        d[item] = {"histo": "gluino", "file": sms}

    for item in ["TGQ_0p0_7", "TGQ_0p2_7", "TGQ_0p4_7", "TGQ_0p8_7"]:
        d[item] = {"histo": "clone", "file": "%s/v1/TGQ_xSec.root" % base}

    assert model.name in d, "model=%s" % model.name
    return d[model.name]


def effHistoSpec(model=None, box=None, htLower=None, htUpper=None,
                 bJets=None, jets=None):

    assert box in ["had", "muon"], box

    # FIXME: remove these hard-coded numbers
    if htLower and (htLower <= 275):
        fileName = "%s0.root" % box
    elif htLower == 325:
        fileName = "%s1.root" % box
    else:
        fileName = "%s.root" % box

    tags = []

    if model.isSms:
        subDirs = [directories.eff(), "sms_%d" % model.com]
        beforeDir = "smsScan_before"
        tags.append("smsScan")
    else:
        subDirs = [directories.eff(), "cmssm_%d" % model.com]
        beforeDir = "mSuGraScan_before_scale1"
        tags.append("mSuGraScan")

    if bJets:
        tags.append(bJets)
    if jets:
        tags.append(jets)
    if model.extraVars:
        tags.append(" ".join(model.extraVars))
    if box == "had":
        if model.aT:
            if htLower in model.aT:
                tags.append("AlphaT"+model.aT[htLower])
            else:
                tags.append("AlphaT"+model.aT[max(model.aT)])
        else:
            tags.append("AlphaT55")
    else:
        tags.append("NoAlphaT")

    if htLower:
        tags.append("%d" % htLower)
    if htUpper:
        tags.append("%d" % htUpper)
    if not model.isSms:
        tags.append("scale1")

    fileFields = [model.name, box, getattr(model, "_"+box), fileName]
    return {"beforeDir": beforeDir,
            "afterDir": "_".join(tags),
            "file": "/".join(subDirs + fileFields),
            "weightedHistName": model.weightedHistName,
            "unweightedHistName": model.unweightedHistName}


def effUncRelHistoSpec(model=None, box=None,
                       bJets=None, jets=None):
    assert box in ["had", "muon"], box

    if model.isSms:
        subDirs = [directories.eff(), "sms_%d" % model.com]
    fileName = "syst.root"
    tags = ["total", model.name]
    if bJets:
        tags.append(bJets)
    if jets:
        tags.append(jets)

    fileFields = [model.name, box, getattr(model, "_"+box), fileName]
    return {"histDir": "",
            "file": "/".join(subDirs + fileFields),
            "effUncRelHistName": ("_").join(tags+["incl"])}


def ranges(model):
    x = {"T1":   (287.5, 1400),  # (min, max)
         "T2":   (287.5, 1000),
         "T2tt": (100.0, 1000.0),
         "T2bb": (287.5, 900.0),
         "T2cc":   (87.5, 400.0),
         "T1bbbb": (287.5, 1400),
         "T1tttt": (387.5, 1400),
         "T1tttt_ichep": (375.0, 1200.0),
         "tanBeta10_7": (0.0, 4000.0),
         }

    y = {"T5zz_7":   (50.0, 999.9),  # (min, max)
         "T1":      (0.0, 1225),
         "T2":      (0.0,  825),
         "T2tt":    (0.0, 1000),
         "T2bb":    (0.0,  725),
         "T2cc":    (0.0,  400),
         "T1bbbb":  (0.0, 1225),
         "T1tttt":  (0.0, 1050),
         "T1tttt_ichep":  (50.0, 800.0),
         "tanBeta10_7": (0.0, 4000.0),
         }

    z = {"T2cc": (1.0, 200.0, 20),
         }

    xMaxDiag = {"T1":     800.0,
                "T2":     550.0,
                "T2tt":   400.0,
                "T2bb":   500.0,
                "T2cc":   400.0,
                "T1bbbb": 800.0,
                "T1tttt": 700.0,
                }

    # [ primary, secondary, tertiary ] divisions
    xDivisions = {"T1": [10, 4, 0],
                  "T2": [10, 4, 0],
                  "T2bb": [10, 4, 0],
                  "T2cc": [10, 4, 0],
                  "T2tt": [10, 4, 0],
                  "T1bbbb": [10, 4, 0],
                  "T1tttt":  [8, 4, 0],
                  "T1tttt_2012": [8, 4, 0],
                  }

    yDivisions = {"T1": [10, 4, 0],
                  "T2": [10, 4, 0],
                  "T2bb": [10, 4, 0],
                  "T2cc": [10, 4, 0],
                  "T2tt": [12, 4, 0],
                  "T1bbbb": [10, 4, 0],
                  "T1tttt": [10, 4, 0],
                  "T1tttt_2012": [8, 4, 0]
                  }

    d = {}
    d["xRange"] = x.get(model, (50.0, 1499.9))
    d["yRange"] = y.get(model, (50.0, 1224.9))

    d["xMaxDiag"] = xMaxDiag.get(model, d["xRange"][0])

    d["xDivisions"] = xDivisions.get(model, None)
    d["yDivisions"] = yDivisions.get(model, None)

    d["xsZRangeLin"] = (0.0, 2.0, 20)  # (zMin, zMax, nContours)
    d["xsZRangeLog"] = z.get(model, (1.0e-3,  10.0, 20))
    d["effZRange"] = (0.0, 0.35, 35)

    d["effUncExpZRange"] = (0.0, 0.20, 20)
    d["effUncThZRange"] = (0.0, 0.40, 40)
    return d


def chi():
    return "#tilde{#chi}^{0}_{1}"


def pruned(s=""):
    return s.split(";")[0]


def sqProc(q="", daughter=""):
    if not daughter:
        daughter = q
    out = "pp #rightarrow #tilde{%s} #tilde{%s}" % (q, q)
    out += ", #tilde{%s} #rightarrow %s %s" % (q, daughter, chi())
    out += "; m(#tilde{g})>>m(#tilde{%s})" % q
    return out


def glProc(q=""):
    out = "pp #rightarrow #tilde{g} #tilde{g}"
    out += ", #tilde{g} #rightarrow %s #bar{%s} %s" % (q, q, chi())
    out += "; m(#tilde{%s})>>m(#tilde{g})" % q
    return out


def processStamp(model=""):
    out = {'T2': {'text': sqProc("q"), 'xpos': 0.4250},
           'T2bb': {'text': sqProc("b"), 'xpos': 0.425},
           'T2tt': {'text': sqProc("t"), 'xpos': 0.41},
           'T2cc': {'text': sqProc("t", "c"), 'xpos': 0.425},
           'T1': {'text': glProc("q"), 'xpos': 0.4325},
           'T1bbbb': {'text': glProc("b"), 'xpos': 0.43},
           'T1tttt': {'text': glProc("t"), 'xpos': 0.425},
           }[model]
    out.update({'ypos': 0.78})
    return out


def histoTitle(model=""):
    d = {"T1": ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T2": ";m_{squark} (GeV);m_{LSP} (GeV)",
         "T2tt": ";m_{stop} (GeV);m_{LSP} (GeV)",
         "T2cc": ";m_{stop} (GeV);m_{LSP} (GeV)",
         "T2bb": ";m_{sbottom} (GeV);m_{LSP} (GeV)",
         "T2bw": ";m_{UKNOWN} (GeV);m_{UNKNOWN_2} (GeV)",
         "T5zz": ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T1bbbb": ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "T1tttt": ";m_{gluino} (GeV);m_{LSP} (GeV)",
         "TGQ_0p0": ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p2": ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p4": ";m_{gluino} (GeV);m_{squark} (GeV)",
         "TGQ_0p8": ";m_{gluino} (GeV);m_{squark} (GeV)",
         "": ";m_{0} (GeV);m_{1/2} (GeV)",
         }
    return d.get(model, d[""])


#CMSSM
def benchmarkPoints():
    out = {}
    fields = ["m0",  "m12",  "A0", "tanBeta", "sgn(mu)"]
    #out["LM0"]= dict(zip(fields,   [200,    160,  -400,        10,      1]))
    #out["LM1"]= dict(zip(fields,    [60,    250,     0,        10,      1]))
    out["LM2"] = dict(zip(fields,  [185,    350,     0,        35,      1]))
    out["LM3"] = dict(zip(fields,  [330,    240,     0,        20,      1]))
    #out["LM4"]= dict(zip(fields,   [210,    285,     0,        10,      1]))
    #out["LM5"]= dict(zip(fields,   [230,    360,     0,        10,      1]))
    #out["LM6"]= dict(zip(fields,   [85,     400,     0,        10,      1]))
    out["LM7"] = dict(zip(fields,  [3000,    230,     0,        10,     1]))
    out["LM8"] = dict(zip(fields,   [500,    300,  -300,        10,     1]))
    out["LM9"] = dict(zip(fields,  [1450,    175,     0,        50,     1]))
    out["LM10"] = dict(zip(fields, [3000,    500,     0,        10,     1]))
    out["LM11"] = dict(zip(fields,  [250,    325,     0,        35,     1]))
    out["LM12"] = dict(zip(fields, [2545,    247,  -866,        48,     1]))
    out["LM13"] = dict(zip(fields,  [270,    218,  -553,        40,     1]))

    #out["IM1"] = dict(zip(fields,   [100,    510,     0,        10,     1]))
    #out["IM2"] = dict(zip(fields,   [180,    510,     0,        10,     1]))
    #out["IM3"] = dict(zip(fields,   [260,    450,     0,        10,     1]))
    out["IM4"] = dict(zip(fields,   [820,    390,     0,        10,     1]))

    out["RM1"] = dict(zip(fields,   [320,    520,     0,        10,     1]))
    out["RM2"] = dict(zip(fields,  [1800,    280,     0,        10,     1]))
    return out


def scanParameters():
    out = {}
    fields = ["A0", "tanBeta", "sgn(mu)"]
    out["tanBeta3"] = dict(zip(fields,  [0,         3,         1]))
    out["tanBeta10"] = dict(zip(fields, [0,        10,         1]))
    out["tanBeta50"] = dict(zip(fields, [0,        50,         1]))
    return out


def processes():
    return ["gg", "sb", "ss", "sg", "ll", "nn", "ng", "bb", "tb", "ns"]


def checkModels():
    # check for duplicates
    names = [model.name for model in models()]
    assert len(names) == len(set(names)), names


checkModels()
