import directories


class mod(object):
    def __init__(self, dataset="", tag="", com=None, had="", muon=""):
        for item in ["dataset", "tag", "com", "had", "muon"]:
            setattr(self, item, eval(item))

    @property
    def name(self):
        return self.dataset+("" if not self.tag else "_"+self.tag)


def model():
    assert len(models()) == 1
    return models()[0].name


def models():
    return [
        #mod(dataset="T1", com=8, had="v5"),
        #mod(dataset="T2", com=8, had="v1"),
        mod(dataset="T2cc", com=8, had="v4_ISRReweighted"),
        #mod(dataset="T2tt", com=8, had="v1", muon="v1"),
        #mod(dataset="T2bb", com=8, had="v3", muon="v3"),
        #mod(dataset="T1bbbb", com=8, had="v3", muon="v3"),
        #mod(dataset="T1tttt", com=8, had="v1", muon="v1"),
        #
        #mod(dataset="T2bb", com=8, tag="ct6l1", had="v6_yossof_cteq61"),
        #mod(dataset="T2bb", com=8, tag="ct10", had="v6_yossof_ct10_normalized"),
        #mod(dataset="T2bb", com=8, tag="ct66", had="v6_yossof_cteq66_normalized"),
        #mod(dataset="T2bb", com=8, tag="mstw08", had="v6_yossof_mst08_normalized"),
        #mod(dataset="T2bb", com=8, tag="nnpdf21", had="v6_yossof_nnpdf21_normalized"),
        #
        #mod(dataset="T1bbbb", com=8, tag="ct6l1", had="v6_yossof_cteq61"),
        #mod(dataset="T1bbbb", com=8, tag="ct10", had="v6_yossof_ct10_normalized"),
        #mod(dataset="T1bbbb", com=8, tag="ct66", had="v6_yossof_cteq66_normalized"),
        #mod(dataset="T1bbbb", com=8, tag="mstw08", had="v6_yossof_mstw08_normalized"),
        #mod(dataset="T1bbbb", com=8, tag="nnpdf21", had="v6_yossof_nnpdf21_normalized"),
        #
        #mod(dataset="T1tttt", com=8, tag="ichep", had="2012full", muon="2012full"),
        #
        #mod(dataset="T5zz", com=7, had="v1", muon="v1"),
        #mod(dataset="TGQ_0p0", com=7, had="v1"),
        #mod(dataset="TGQ_0p2", com=7, had="v1"),
        #mod(dataset="TGQ_0p4", com=7, had="v1"),
        #mod(dataset="TGQ_0p8", com=7, had="v1"),
        #
        #mod(dataset="tanBeta10", com=7, had="v2", muon="v2"),
        #mod(dataset="tanBeta10", com=7, tag="42", had="v8", muon="v8"),
        #mod(dataset="tanBeta40", com=7, tag="42", had="v2", muon="v2"),
        ]


def xsVariation():
    variations = ["default", "up", "down"]
    return dict(zip(variations, variations))["default"]


def isSms(model=""):
    assert model
    return "tanBeta" not in model


def ignoreEff(model=""):
    return {"T1": ["muon"], "T1bbbb": [], "T1tttt": [],
            "T2": ["muon"], "T2bb": ["muon"], "T2tt": [], "T2cc": ["muon"],
            }[model]


def effUncRel(model=""):
    return {"T1": 0.140, "T1bbbb": 0.160, "T1tttt": 0.230,
            "T2": 0.134, "T2bb": 0.131, "T2tt": 0.139, "T2cc": 0.20,
            }[model]


def nEventsIn(model=""):
    return {"T5zz":      (5.0e3, None),
            "tanBeta10": (9.0e3, 11.0e3),
            }.get(model, (1, None))


def interBin(model=""):
    assert model
    return "LowEdge"


def whiteListOfPoints(model="", respect=False):
    if not respect:
        return []

    # in GeV
    return {"T1": [(700.0, 300.0)],
            "T1bbbb": [(900.0, 500.0)],
            "T1tttt": [(850.0, 250.0)],
            "T2tt": [(450.0,  20.0)],
            #"T2tt": [(550.0,  20.0)],
            #"T2tt": [(400.0,   0.0)],
            #"T2tt": [(410.0,  20.0)],
            #"T2tt": [(420.0,  20.0)],
            "T2bb": [(500.0, 150.0)],
            "T2": [(600.0, 250.0)],
            "T2cc": [(175.0, 95.0)],
            #"T2cc": [(175.0, 165.0)],
            }[model]


def xsHistoSpec(model="", cmssmProcess="", xsVariation=""):
    if not cmssmProcess:
        if xsVariation != "default":
            print 'WARNING: variation "%s" (%s)' % (xsVariation, model) + \
                  ' will need to use error bars in xs file.'
    else:
        print "WARNING: using 7 TeV xs for " + \
              "model %s, process %s" % (model, cmssmProcess)

    base = directories.xs()
    #seven = "%s/v5/7TeV.root"%base
    eight = "%s/v5/8TeV.root" % base
    tgqFile = "%s/v1/TGQ_xSec.root" % base
    tanBeta10 = "%s/v5/7TeV_cmssm.root" % base
    d = {"T2":      {"histo": "squark", "factor": 1.0, "file": eight},
         "T2tt":    {"histo": "stop_or_sbottom", "factor": 1.0, "file": eight},
         "T2bb":    {"histo": "stop_or_sbottom", "factor": 1.0, "file": eight},
         "T2cc":    {"histo": "stop_or_sbottom", "factor": 1.0, "file": eight},
         "tanBeta10": {"histo": "%s_%s" % (cmssmProcess, xsVariation),
                       "factor": 1.0, "file": tanBeta10},
         }

    for item in ["T1", "T1bbbb", "T1tttt", "T5zz"]:
        d[item] = {"histo": "gluino", "factor": 1.0, "file": eight}

    for item in ["TGQ_0p0", "TGQ_0p2", "TGQ_0p4", "TGQ_0p8"]:
        d[item] = {"histo": "clone", "factor": 1.0, "file": tgqFile}

    assert model in d, "model=%s" % model
    return d[model]


def effHistoSpec(model="", box=None, htLower=None, htUpper=None,
                 bJets=None, jets=None):

    assert box in ["had", "muon"], box

    # FIXME: remove these hard-coded numbers
    if htLower == 275:
        fileName = "%s0.root" % box
    elif htLower == 325:
        fileName = "%s1.root" % box
    else:
        fileName = "%s.root" % box

    tags = []

    # FIXME: improve
    dct = {}
    for m in models():
        if m.name == model:
            dct = {"tag": m.tag,
                   "had": m.had,
                   "muon": m.muon,
                   }

    if not isSms(model):
        dir2 = "rw_scan" if not dct["tag"] else "%s_scan" % dct["tag"]
        subDirs = ["2011", dir2]
        beforeDir = "mSuGraScan_before_scale1"
        tags.append("mSuGraScan")
    else:
        subDirs = ["2012", "sms"]
        beforeDir = "smsScan_before"
        tags.append("smsScan")

    if bJets:
        tags.append(bJets)
    if jets:
        tags.append(jets)

    if box == "had":
        tags.append("AlphaT55")
    else:
        tags.append("NoAlphaT")

    if htLower:
        tags.append("%d" % htLower)
    if htUpper:
        tags.append("%d" % htUpper)
    if not isSms(model):
        tags.append("scale1")

    return {"beforeDir": beforeDir,
            "afterDir": "_".join(tags),
            "file": "/".join([directories.eff()] + subDirs + [model,
                                                              box,
                                                              dct[box],
                                                              fileName]
                             )
            }


#SMS
def ranges(model):
    x = {"T1":   (287.5, 1400),  # (min, max)
         "T2":   (287.5, 1000),
         "T2tt": (300.0, 800.0),
         "T2bb": (287.5, 900.0),
         "T2cc":   (87.5, 300.0),
         "T1bbbb": (287.5, 1400),
         "T1tttt": (387.5, 1400),
         "T1tttt_2012": (375.0, 1200.0),
         "tanBeta10": (0.0, 4000.0),
         }

    y = {"T5zz":   (50.0, 999.9),  # (min, max)
         "T1":      (0.0, 1225),
         "T2":      (0.0,  825),
         "T2tt":    (0.0,  600),
         "T2bb":    (0.0,  725),
         "T2cc":    (0.0,  300),
         "T1bbbb":  (0.0, 1225),
         "T1tttt":  (0.0, 1050),
         "T1tttt_2012":  (50.0, 800.0),
         "tanBeta10": (0.0, 4000.0),
         }

    z = {"T2cc": (1.0, 200.0, 20),
         }

    xMaxDiag = {"T1":     800.0,
                "T2":     550.0,
                "T2tt":   400.0,
                "T2bb":   500.0,
                "T2cc":   300.0,
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
    return {'T2': {'text': sqProc("q"), 'xpos': 0.4250},
            'T2bb': {'text': sqProc("b"), 'xpos': 0.425},
            'T2tt': {'text': sqProc("t"), 'xpos': 0.41},
            'T2cc': {'text': sqProc("t", "c"), 'xpos': 0.425},
            'T1': {'text': glProc("q"), 'xpos': 0.4325},
            'T1bbbb': {'text': glProc("b"), 'xpos': 0.43},
            'T1tttt': {'text': glProc("t"), 'xpos': 0.425},
            }[model]


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
