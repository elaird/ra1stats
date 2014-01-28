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
                      default=0,
                      metavar="N",
                      help="number of pseudo-experiments to generate/use")

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

    parser.add_option("--ensemble",
                      dest="ensemble",
                      default=False,
                      action="store_true",
                      help="generate an ensemble of pseudo-data")

    parser.add_option("--reuse",
                      dest="reuse",
                      default=False,
                      action="store_true",
                      help="reuse results of a previous --ensemble")
    options, _ = parser.parse_args()

    options.nToys = int(options.nToys)
    options.bestFit = not options.interval
    if options.ensemble:
        assert options.nToys
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
    elif options.bestFit or options.ensemble:
        kargs["signalExampleToStack"] = None  # signal
    return kargs


def hMapInit(nBins=0):
    out = {}
    for key in ["chi2ProbSimple", "chi2Prob", "lMax"]:
        out[key] = r.TH1D("pValueMap_%s" % key,
                          ";category;p-value",
                          nBins, 0.0, nBins)
    return out


def go(selections=[], options=None, hMap=None, report=None):
    nCategories = 0
    for iSel, sel in enumerate(selections):
        if options.category and sel.name != options.category:
            continue
        nCategories += 1

        whiteList = [sel.name] if sel.name else []

        f = driver.driver(llkName=options.llk,
                          whiteList=whiteList,
                          ignoreHad=options.ignoreHad,
                          separateSystObs=not options.ensemble,
                          #trace=True
                          #rhoSignalMin=0.1,
                          #fIniFactor=0.1,
                          **signalArgs(whiteList, options)
                          )

        if options.ensemble:
            f.ensemble(nToys=options.nToys,
                       stdout=True,
                       reuseResults=options.reuse)

        if options.interval:
            cl = 0.95 if f.likelihoodSpec.standardPoi() else 0.68
            print f.interval(cl=cl,
                             method=["profileLikelihood", "feldmanCousins"][0],
                             makePlots=True,
                             )
            #f.profile()

        if options.bestFit:
            dct = f.bestFit(drawMc=False,
                            drawComponents=False,
                            errorsFromToys=options.nToys,
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
    return nCategories


if __name__ == "__main__":
    # before other imports so that --help is not stolen by pyROOT
    options = opts()

    import driver
    import likelihood
    import plotting
    from signals import t2, two, t2cc
    import ROOT as r

    if options.simultaneous:
        selections = [""]
    else:
        selections = likelihood.spec(name=options.llk).selections()

    report = {}
    hMap = hMapInit(nBins=len(selections))
    nCategories = go(selections=selections,
                     options=options,
                     hMap=hMap,
                     report=report)

    plotting.pValueCategoryPlots(hMap, )  # logYMinMax=(1.0e-4, 1.0e2))
    printReport(report)
    if not nCategories:
        print "WARNING: category %s not found." % options.category
