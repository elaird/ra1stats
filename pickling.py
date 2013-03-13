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
def effHistos(okMerges=[None,
                        (0, 1, 2, 3, 4, 5, 6, 7, 7, 7),
                        (0, 1, 2, 2, 2, 2, 2, 2, 2, 2),
                        (0, 1, 2, 2, 2, 2, 2, 2),
                        ]):
    model = conf.signal.model()
    out = {}
    for sel in likelihoodSpec.likelihoodSpec(model).selections():
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

            d[item] = [hp.effHisto(box=box,
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


def eventsInRange(switches=None, nEventsIn=None):
    minEventsIn, maxEventsIn = conf.signal.nEventsIn(conf.signal.model())
    out = True
    if minEventsIn is not None:
        out &= (minEventsIn <= nEventsIn)
    if maxEventsIn is not None:
        out &= (nEventsIn <= maxEventsIn)
    return out


def signalModel(point=None, eff=None, xs=None, xsLo=None,
                nEventsIn=None, switches=None):
    out = common.signal(xs=xs.GetBinContent(*point), label="%d_%d_%d" % point,
                        effUncRel=conf.signal.effUncRel(conf.signal.model()),
                        )

    if xsLo:
        out["xs_LO"] = xsLo.GetBinContent(*point)

    out["xs"] = out.xs
    out["x"] = xs.GetXaxis().GetBinLowEdge(point[0])
    out["y"] = xs.GetYaxis().GetBinLowEdge(point[1])
    out["nEventsIn"] = nEventsIn.GetBinContent(*point)
    out["eventsInRange"] = eventsInRange(switches, out["nEventsIn"])
    if not out["eventsInRange"]:
        return out

    for selName, dct in eff.iteritems():
        d = {}
        for box, effHistos in dct.iteritems():
            if not all([hasattr(item, "GetBinContent") for item in effHistos]):
                continue

            d[box] = map(lambda x: x.GetBinContent(*point), effHistos)

            d[box+"Sum"] = sum(d[box])
            key = box.replace("eff", "nEvents")
            d[key] = d[box+"Sum"]*out["nEventsIn"]
            if d[key] > 0.0:
                d[box+"SumUncRelMcStats"] = 1.0/math.sqrt(d[key])
            elif d[key] < 0.0:
                print "ERROR: negative value: ", point, d[key], box
        out[selName] = d
    return out


def stuffVars(switches=None, binsMerged=None, signal=None):
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
    args = {"switches": conf.switches(),
            "eff": effHistos(),
            "xs": hp.xsHisto(),
            "nEventsIn": hp.nEventsInHisto(),
            }
    hp.checkHistoBinning([args["xs"]]+histoList(args["eff"]))
    for point in points:
        signal = signalModel(point=point, **args)
        stem = conf.pickledFileName(*point)
        writeNumbers(fileName=stem+".in", d=signal)
        if not outFilesAlso:
            continue
        writeNumbers(fileName=stem+".out", d=signal)
        #stuffVars(switches,
        #          binsMerged=args["data"].htBinLowerEdges(),
        #          signal=signal)


##merge functions
def mergedFile():
    model = conf.signal.model()
    return "%s_%s.root" % (conf.mergedFileStem(),
                           common.note(likelihoodSpec.likelihoodSpec(model))
                           )


#note: improve this data format
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


def mergePickledFiles(printExample=False):
    example = hp.xsHisto()
    if printExample:
        print "Here are the example binnings:"
        for c in ["X", "Y", "Z"]:
            print " ".join(["%s:" % c,
                            getattr(example, "GetNbins%s" % c)(),
                            getattr(example, "Get%saxis" % c)().GetXmin(),
                            getattr(example, "Get%saxis" % c)().GetXmax(),
                            ])
    histos = {}
    zTitles = {}

    for point in hp.points():
        fileName = conf.pickledFileName(*point)+".out"
        if not os.path.exists(fileName):
            print "skipping file", fileName
            continue

        d = readNumbers(fileName)
        contents = {}
        for key, value in d.iteritems():
            flatten(contents, key, value)

        for key, value in contents.iteritems():
            if key not in histos:
                histos[key] = example.Clone(key)
                histos[key].Reset()
            histos[key].SetBinContent(point[0], point[1], point[2], value[0])
            zTitles[key] = value[1]

        os.remove(fileName)
        os.remove(fileName.replace(".out", ".in"))

    for key, histo in histos.iteritems():
        histo.GetZaxis().SetTitle(zTitles[key])

    f = r.TFile(mergedFile(), "RECREATE")
    for histo in histos.values():
        histo.Write()
    f.Close()
