#!/usr/bin/env python

import optparse


def opts():
    parser = optparse.OptionParser("usage: %prog [options]")

    parser.add_option("--ignoreHad",
                      dest="ignoreHad",
                      default=False,
                      action="store_true",
                      help="remove the hadronic sample from the likelihood")

    parser.add_option("--nToys",
                      dest="nToys",
                      default=300,
                      metavar="N",
                      help="number of pseudo-experiments to generate/use")

    parser.add_option("--genBands",
                      dest="genBands",
                      default=False,
                      action="store_true",
                      help=r'''generate an ensemble of pseudo-data
                      (used for uncertainty bands)''')

    parser.add_option("--plotBands",
                      dest="plotBands",
                      default=False,
                      action="store_true",
                      help="plot results of a previous --genBands")

    parser.add_option("--simultaneous",
                      dest="simultaneous",
                      default=False,
                      action="store_true",
                      help=r'''fit all categories simultaneously
                      rather than looping over them''')

    parser.add_option("--category",
                      dest="category",
                      default="",
                      help="select only one category (defaults to all)")

    parser.add_option("--llk",
                      dest="llk",
                      default="2012dev",
                      help="likelihood (defaults to 2012dev)")

    parser.add_option("--interval",
                      dest="interval",
                      default=False,
                      action="store_true",
                      help="scan nll vs. likelihood/__init__.py:poi()")

    parser.add_option("--significances",
                      dest="significances",
                      default=False,
                      action="store_true",
                      help="print nll(poi=0) for each HT bin")

    options, _ = parser.parse_args()

    options.nToys = int(options.nToys)
    if options.genBands:
        assert options.nToys
    exclusive = [options.interval, options.genBands, options.significances]
    assert exclusive.count(True) <= 1, exclusive
    options.bestFit = not any(exclusive)
    return options


def printReport(report={}):
    header = None
    for cat, dct in sorted(report.iteritems()):
        if not header:
            keys = sorted(dct.keys())
            l = max([len(key) for key in keys])
            fmt = "%"+str(l)+"s"
            header = " ".join([fmt % "cat"] + [fmt % key for key in keys])
            print header
            print "-"*len(header)
        out = [fmt % cat]
        for key in keys:
            value = dct[key]
            sValue = str(value) if type(value) is int else "%6.4f" % value
            out.append(fmt % sValue)
        print " ".join(out)


def printNlls(nlls={}):
    n = max([len(c) for c in nlls.keys()])
    header = "  ".join(["cat".ljust(n), "iBin", "nIter", " (fMin", "  fHat+=   Err", "  fMax)",
                        "", "nll_fHat", "nll_f=0", " delta", "sqrt(2*delta)"])
    fmt = "  ".join(["%"+str(n)+"s", "  %2d", "   %2d", "%6.2f", "%6.2f+-%6.2f", "%6.2f ",
                     "", "  %6.2f", " %6.2f", "%6.2f", "%s"])
    print header
    print "-" * len(header)

    for cat, nllDct in sorted(nlls.iteritems()):
        for iBin, d in sorted(nllDct.iteritems()):
            delta = d["nllB"] - d["nllSb"]
            if 0.0 < delta:
                s = "-" if d["poiVal"] < 0.0 else " "
                s += "%5.2f" % (2.0*delta)**0.5
            else:
                s = "  -  "
            print fmt % (cat, iBin, d["nIterations"],
                         d["poiMin"], d["poiVal"], d["poiErr"], d["poiMax"],
                         d["nllSb"], d["nllB"], delta, s)


def signalArgs(whiteList=[], options=None):
    examples_paper = {("0b_le3j",): t2.a,
                      ("0b_ge4j",): two.t1,
                      ("1b_le3j",): two.t2bb,
                      ("1b_ge4j",): two.t2tt,
                      ("2b_le3j",): two.t2bb,
                      ("2b_ge4j",): two.t2tt,
                      ("3b_le3j",): {},
                      ("3b_ge4j",): two.t1bbbb,
                      ("ge4b_ge4j",): two.t1tttt,
                      }

    examples_t2cc = {("0b_le3j",): t2cc.testMcUnc1,
                     ("0b_ge4j",): t2cc.far10,
                     ("1b_le3j",): t2cc.far10,
                     ("1b_ge4j",): t2cc.far10,
                     ("2b_le3j",): {},
                     ("2b_ge4j",): {},
                     ("3b_le3j",): {},
                     ("3b_ge4j",): {},
                     ("ge4b_ge4j",): {},
                     }

    examples = examples_paper
    signal = examples[tuple(whiteList)] if tuple(whiteList) in examples else {}

    kargs = {"signalToTest": None,
             "signalToInject": None,
             "signalExampleToStack": None,
             }
    if options.interval:
        kargs["signalToTest"] = signal
    elif options.bestFit or options.genBands:
        kargs["signalExampleToStack"] = None  # signal
    return kargs


def hMapInit(nBins=0):
    out = {}
    for key in ["chi2ProbSimple", "chi2Prob", "lMax"]:
        out[key] = r.TH1D("pValueMap_%s" % key,
                          ";category;p-value",
                          nBins, 0.0, nBins)
    return out


def significances(whiteList=[], selName="", options=None):
    out = {}

    assert len(whiteList) == 1, whiteList
    ll = likelihood.spec(name=options.llk, whiteList=whiteList)
    sel = ll.selections()[0]
    nBins = len(sel.data.htBinLowerEdges())

    for iBin in range(nBins):
        # make xs fall vs. HT
        xs1 = 0.1*r.TMath.Exp(-iBin)
        xs2 = 1.0*(1+iBin)**-4.0
        model = signals.point(xs=xs2,
                              label="%s_ht%d" % (selName, iBin),
                              sumWeightIn=1.0, x=0.0, y=0.0, effUncRel=0.01,  # dummy
                              )
        effs = [0.0] * nBins
        effs[iBin] = 0.5
        model.insert(selName, {"effHad": effs})

        f = driver.driver(signalToTest=model,
                          llkName=options.llk,
                          whiteList=whiteList,
                          ignoreHad=options.ignoreHad,
                          separateSystObs=not options.genBands,
                          )

        nIterations, poi = f.expandPoiRange(allowNegative=True,
                                            nIterationsMax=10,
                                            )
        out[iBin] = {"nIterations": nIterations,
                     "poiVal": poi.getVal(),
                     "poiErr": poi.getError(),
                     "poiMin": poi.getMin(),
                     "poiMax": poi.getMax(),
                     }

        out[iBin]["nllSb"] = f.rooFitResults().minNll()

        # fix POI to zero
        poi.setMin(0.0)
        poi.setMax(0.0)
        poi.setVal(0.0)
        out[iBin]["nllB"] = f.rooFitResults().minNll()

    return out


def go(selections=[], options=None, hMap=None):
    nCategories = 0
    report = {}
    nlls = {}

    for iSel, sel in enumerate(selections):
        if options.category and sel.name != options.category:
            continue
        nCategories += 1

        whiteList = [sel.name] if sel.name else []

        if options.significances and sel:
            nlls[sel.name] = significances(whiteList=whiteList,
                                           selName=sel.name,
                                           options=options)
            continue

        f = driver.driver(llkName=options.llk,
                          whiteList=whiteList,
                          ignoreHad=options.ignoreHad,
                          separateSystObs=not options.genBands,
                          #trace=True
                          #rhoSignalMin=0.1,
                          #fIniFactor=0.1,
                          **signalArgs(whiteList, options)
                          )

        if options.genBands:
            f.ensemble(nToys=options.nToys,
                       stdout=True,
                       reuseResults=False)

        if options.interval:
            cl = 0.95 if f.likelihoodSpec.standardPoi() else 0.68
            print f.interval(cl=cl,
                             method=["profileLikelihood", "feldmanCousins"][0],
                             makePlots=True,
                             )
            #f.profile()

        if options.bestFit:
            errorsFromToys = options.nToys * bool(options.plotBands)
            dct = f.bestFit(drawMc=False,
                            drawComponents=False,
                            errorsFromToys=errorsFromToys,
                            printPages=False,
                            drawRatios=False,
                            significance=options.ignoreHad,
                            #msgThreshold=r.RooFit.DEBUG,
                            msgThreshold=r.RooFit.WARNING,
                            )
            if dct:
                report[sel.name] = dct
                for key, pValue in dct.iteritems():
                    if key not in hMap:
                        continue
                    hMap[key].GetXaxis().SetBinLabel(1+iSel, sel.name)
                    hMap[key].SetBinContent(1+iSel, pValue)

        #f.qcdPlot()
        #f.debug()
        #f.cppDrive(tool="")
        #
        #print f.cls(cl=cl,
        #            makePlots=True,
        #            testStatType=3,
        #            nToys=50,
        #            nWorkers=1,
        #            plusMinus={"OneSigma": 1.0,
        #                       "TwoSigma": 2.0},
        #            calculatorType=["frequentist",
        #                            "asymptotic",
        #                            "asymptoticNom"][1],
        #            #plSeedParams={"usePlSeed": True,
        #            #              "plNIterationsMax": 10,
        #            #              "nPoints": 7,
        #            #              "minFactor": 0.5,
        #            #              "maxFactor":2.0},
        #            plSeedParams={"usePlSeed": True,
        #                          "plNIterationsMax": 10,
        #                          "nPoints": 10,
        #                          "minFactor": 0.0,
        #                          "maxFactor":3.0},
        #            )
        #
        #f.writeMlTable(fileName="mlTables_%s.tex" % "_".join(whiteList),
        #               categories=sorted([x.name for x in selections]))
        #
    return nCategories, report, nlls


if __name__ == "__main__":
    # before other imports so that --help is not stolen by pyROOT
    options = opts()

    import driver
    import likelihood
    import plotting
    from signals import t2, two, t2cc
    import signals
    import ROOT as r
    r.gROOT.SetBatch(True)

    if options.simultaneous:
        selections = [""]
    else:
        selections = likelihood.spec(name=options.llk).selections()

    hMap = hMapInit(nBins=len(selections))
    nCategories, report, nlls = go(selections=selections,
                                   options=options,
                                   hMap=hMap,
                                   )

    if not options.significances:
        plotting.pValueCategoryPlots(hMap, )  # logYMinMax=(1.0e-4, 1.0e2))
        printReport(report)
    else:
        printNlls(nlls)

    if not nCategories:
        print "WARNING: category %s not found." % options.category
