import cPickle
import math
import os

import common
import configuration as conf
import histogramProcessing as hp
import likelihoodSpec
import utils

import ROOT as r


##I/O
def writeNumbers(fileName=None, d=None):
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()


def readNumbers(fileName):
    inFile = open(fileName)
    d = cPickle.load(inFile)
    inFile.close()
    return d


##number collection
def effHistos(model=None,
              okMerges=[None,
                        (0, 1, 2, 2, 2, 2, 2, 2),  # 8 --> 3
                        (0, 1, 2, 3, 3, 3, 3, 3, 3, 3),  # 10 --> 4
                        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9),  # 11 --> 10
                        ],
              allCategories=False,
              ):
    out = {}
    for sel in likelihoodSpec.likelihoodSpec(model.name,
                                             allCategories=allCategories,
                                             ).selections():
        badMerge = " ".join(["bin merge",
                             str(sel.data._mergeBins),
                             "not yet supported:",
                             sel.name,
                             ])

        assert sel.data._mergeBins in okMerges, badMerge
        bins = sel.data.htBinLowerEdges()
        htThresholds = zip(bins, list(bins[1:])+[None])

        d = {}
        for box, considerSignal in sel.samplesAndSignalEff.iteritems():
            item = "eff%s" % box.capitalize()
            if not considerSignal:
                d[item] = [0.0]*len(bins)
                continue

            d[item] = [hp.effHisto(model=model,
                                   box=box,
                                   htLower=l,
                                   htUpper=u,
                                   bJets=sel.bJets,
                                   jets=sel.jets) for l, u in htThresholds]

            item = "%s" % box + "Weights"
            d[item] = [hp.histoWeights(model=model,
                                          box=box,
                                          htLower=l,
                                          htUpper=u,
                                          bJets=sel.bJets,
                                          jets=sel.jets) for l, u in htThresholds]


        out[sel.name] = d
    return out


def histoList(histos={}):
    out = []
    for key, value in histos.iteritems():
        for item in value:
            if not hasattr(item, "GetBinContent"):
                continue
            out.append(item)
    return out


def eventsInRange(model="", nEventsIn=None):
    minEventsIn, maxEventsIn = conf.signal.nEventsIn(model)
    out = True
    if minEventsIn is not None:
        out &= (minEventsIn <= nEventsIn)
    if maxEventsIn is not None:
        out &= (nEventsIn <= maxEventsIn)
    return out


def signalModel(model="", point3=None, eff=None, xs=None, xsLo=None,
                nEventsIn=None, weightsIn=None):
    out = common.signal(xs=xs.GetBinContent(*point3),
                        label="%s_%d_%d_%d" % ((model,)+point3),
                        effUncRel=conf.signal.effUncRel(model),
                        )

    if xsLo:
        out["xs_LO"] = xsLo.GetBinContent(*point3)

    out["xs"] = out.xs
    out["x"] = xs.GetXaxis().GetBinLowEdge(point3[0])
    out["y"] = xs.GetYaxis().GetBinLowEdge(point3[1])
    out["nEventsIn"] = nEventsIn.GetBinContent(*point3)
    out["weightsIn"] = weightsIn.GetBinContent(*point3)
    out["eventsInRange"] = eventsInRange(model=model,
                                         nEventsIn=out["nEventsIn"])
    if not out["eventsInRange"]:
        return out

    for selName, dct in eff.iteritems():
        d = {}
        for box, effHistos in dct.iteritems():
            if not all([hasattr(item, "GetBinContent") for item in effHistos]):
                continue
            d[box] = map(lambda x: x.GetBinContent(*point3), effHistos)
            if "Weights" not in box:
                d["relUnc"] = map(lambda x: 1/math.sqrt(x.GetBinContent(*point3)*out["nEventsIn"]) if x.GetBinContent(*point3) else 2, effHistos) 
                d["relErr"] = map(lambda x: x.GetBinError(*point3)/x.GetBinContent(*point3) if x.GetBinContent(*point3) else 2, effHistos) 
                d[box+"Sum"] = sum(d[box])
                key = box.replace("eff", "nEvents")
                d[key] = d[box+"Sum"]*out["nEventsIn"]
                if d[key] > 0.0:
                    d[box+"SumUncRelMcStats"] = 1.0/math.sqrt(d[key])
                elif d[key] < 0.0:
                    print "ERROR: negative value: ", point3, d[key], box
        out[selName] = d
    return out


def stuffVars(binsMerged=None, signal=None):
    titles = {"xs": "#sigma (pb)",
              "nEventsIn": "N events in",
              "effHadSum": "eff. of hadronic selection (all bins summed)",
              "nEventsHad": "N events after selection (all bins summed)",
              "effHadSumUncRelMcStats": "rel.unc.on tot.had.eff. from MC stat",
              }

    out = {}
    for key, value in signal.iteritems():
        if type(value) is list:
            continue
        out[key] = (value, titles[key] if key in titles else "")

    for i, bin in enumerate(binsMerged):
        sels = []
        for item in conf.likelihood()["alphaT"].keys():
            sels += ["effHad%s" % item, "effMuon%s" % item]

        for sel in sels:
            if sel not in signal:
                continue
            l = [signal[sel][i],
                 "#epsilon of %s %d selection" % (sel.replace("eff", ""), bin),
                 ]
            out["%s%d" % (sel, bin)] = tuple(l)

    return out


def writeSignalFiles(points=[], outFilesAlso=False):
    args = {}
    for model in conf.signal.models():
        name = model.name
        args[name] = {"eff": effHistos(model),
                      "xs": hp.xsHisto(model),
                      "nEventsIn": hp.nEventsInHisto(model),
                      "weightsIn": hp.weightsInHisto(model),
                      }
        hp.checkHistoBinning([args[name]["xs"]]+histoList(args[name]["eff"]))

    for point in points:
        name = point[0]
        signal = signalModel(model=name, point3=point[1:], **args[name])
        stem = conf.directories.pickledFileName(*point)
        writeNumbers(fileName=stem+".in", d=signal)
        if not outFilesAlso:
            continue
        writeNumbers(fileName=stem+".out", d=signal)


##merge functions
def mergedFile(model=None):
    tags = [conf.limit.method()]
    if "CLs" in conf.limit.method():
        tags += [conf.limit.calculatorType(),
                 "TS%d" % conf.limit.testStatistic()
                 ]
    if conf.limit.binaryExclusion():
        tags.append("binaryExcl")
    tags.append(model.name)
    if not model.isSms:
        tags.append(model.xsVariation)

    tags.append(common.note(likelihoodSpec.likelihoodSpec(model.name)))
    return "".join([conf.directories.mergedFile()+"/",
                    "_".join(tags),
                    ".root"
                    ])


# FIXME: improve this data format
def flatten(target={}, key=None, obj=None):
    if type(obj) == dict:
        for k, v in obj.iteritems():
            flatten(target, "%s_%s" % (key, k), v)
    elif type(obj) == list:
        for i, x in enumerate(obj):
            flatten(target, "%s_%d" % (key, i), x)
    elif type(obj) in [float, int, bool]:
        flatten(target, key, (obj, ''))
    elif type(obj) == tuple and len(obj) == 2 and type(obj[1]) == str:
        assert key not in target, key
        target[key] = obj
    else:
        assert False, type(obj)


def mergePickledFiles(printExamples=False):
    examples = {}
    histos = {}
    zTitles = {}

    for model in conf.signal.models():
        name = model.name
        examples[name] = hp.xsHisto(model)
        histos[name] = {}
        zTitles[name] = {}
        if printExamples:
            print "Here are the example binnings for %s:" % name
            for c in ["X", "Y", "Z"]:
                print " ".join(["%s:" % c,
                                str(getattr(examples[name],
                                            "GetNbins%s" % c)()),
                                str(getattr(examples[name],
                                            "Get%saxis" % c)().GetXmin()),
                                str(getattr(examples[name],
                                            "Get%saxis" % c)().GetXmax()),
                                ])

    for name, iX, iY, iZ in hp.points():
        fileName = conf.directories.pickledFileName(name, iX, iY, iZ)+".out"
        if not os.path.exists(fileName):
            print "skipping file", fileName
            continue

        d = readNumbers(fileName)
        contents = {}
        for key, value in d.iteritems():
            flatten(contents, key, value)

        for key, value in contents.iteritems():
            if key not in histos[name]:
                histos[name][key] = examples[name].Clone(name+"_"+key)
                histos[name][key].Reset()
            histos[name][key].SetBinContent(iX, iY, iZ, value[0])
            zTitles[name][key] = value[1]

        os.remove(fileName)
        os.remove(fileName.replace(".out", ".in"))

    for model in conf.signal.models():
        f = r.TFile(mergedFile(model=model), "RECREATE")
        for key, histo in histos[model.name].iteritems():
            histo.GetZaxis().SetTitle(zTitles[model.name][key])
            histo.Write()
        f.Close()
