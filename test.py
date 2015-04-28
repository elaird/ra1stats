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

    parser.add_option("--system",
                      dest="system",
                      default=False,
                      action="store_true",
                      help="do each category's computation in a separate system call (e.g. to work around memory leaks)")

    options, _ = parser.parse_args()

    options.nToys = int(options.nToys)
    if options.genBands:
        assert options.nToys
    exclusive = [options.interval, options.genBands, options.significances]
    assert exclusive.count(True) <= 1, exclusive
    options.bestFit = not any(exclusive)
    return options


def printReport(report={}):
    n = max([len(cat) for cat in ["cat"] + report.keys()])
    fmtCat = "%" + str(n) + "s"
    header = "  ".join([fmtCat % "cat",
                        "nBadEval",
                        "nTerms",
                        "nParams",
                        "nDof",
                        "  chi2",
                        " prob",
                        "  satc",
                        " satp",
                    ])
    print header
    print "-" * len(header)
    for cat, dct in sorted(report.iteritems()):
        print "  ".join([fmtCat % cat,
                         "%8d" % dct["numInvalidNll"],
                         "%6d" % dct["nTerms"],
                         "%7d"% dct["nParams"],
                         "%4d"% dct["nDof"],
                         "%6.1f" % dct["chi2Simple"],
                         "%5.3f" % dct["chi2ProbSimple"],
                         "%6.1f" % dct["chi2Sat"],
                         "%5.3f" % dct["chi2ProbSat"],
                        ])


def printNlls(nlls={}, scale=True):
    if not nlls:
        return

    n = max([len(c) for c in nlls.keys()])
    header = "  ".join(["cat".ljust(n), "iBin", "nIter", "(fMin", "       fHat +-     Err", "   fMax)",
                        "", "nll_(f=fHat)", "nll_(f=0)", " delta", "sqrt(2*delta)"])
    if scale:
        header = header.replace("f", "s")

    fmt = "  ".join(["%"+str(n)+"s", "  %2d", "   %2d", "%8.1e", "%8.1e +- %7.1e", "%7.1e",
                     "", "      %6.2f ", "  %6.2f ", "%6.2f", " %5.2f"])
    print header
    print "-" * len(header)

    labelpVal = []
    for cat, nllDct in sorted(nlls.iteritems()):
        chi2 = 0.0
        nDof = 0
        labelSig = []
        canvas = r.TCanvas("canvas_%s" % cat)
        canvas.SetTicks(0,1)
        for iBin, d in sorted(nllDct.iteritems()):
            values = [cat, iBin, d["nIterations"]]
            pois = [d["poiMin"], d["poiVal"], d["poiErr"], d["poiMax"]]
            if scale:
                pois = [x*d["s_nom"] for x in pois]
            values += pois
            values += [d["minNll_sHat"], d["minNll_s0"], d["deltaMinNll_s0_sHat"], d["nSigma_s0_sHat"]]

            print fmt % tuple(values)
            nDof += 1
            chi2 += d["nSigma_s0_sHat"]**2
            labelSig.append((iBin+1, d["nSigma_s0_sHat"]))
        pVal = r.TMath.Prob(chi2, nDof)
        print "%s: chi2=%g, nDof=%d, prob=%g" % (cat, chi2, nDof, pVal)

        labelpVal.append((cat,pVal))
        h = r.TH1D("sig_%s" % cat,"",len(labelSig),0,len(labelSig))
        for sig in labelSig:
            h.SetStats(0)
            h.SetBinContent(sig[0], float(sig[1]))
            h.SetTitle("significances (%s); HT Bin; Signficance (#sigma)" % cat)
        h.SetMaximum(3.0)
        h.SetMinimum(-3.0)
        h.SetMarkerStyle(20)
        h.Draw("P")
        canvas.Print("significances_%s.pdf" % cat)

    pHist = r.TH1D("pValues","",len(labelpVal),0,len(labelpVal))
    for ip,p in enumerate(labelpVal):
        pHist.GetXaxis().SetBinLabel(ip+1,p[0])
        pHist.SetBinContent(ip+1,p[1])
        pHist.SetStats(0)
        pHist.SetTitle("p-values;category;chi2Prob")
        pHist.SetMinimum(0.0)
        pHist.SetMaximum(1.0)
        pHist.SetMarkerStyle(20)
    c = r.TCanvas("c")
    c.SetTicks(True)
    pHist.Draw("P")
    c.Print("pValues.pdf")

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

    #examples = examples_paper
    #signal = examples[tuple(whiteList)] if tuple(whiteList) in examples else {}
    from signals.t2cc_2012dev import dm10_250
    signal = dm10_250

    kargs = {"signalToTest": None,
             "signalToInject": None,
             "signalExampleToStack": None,
             }
    if options.interval:
        kargs["signalToTest"] = signal
    elif options.bestFit or options.genBands:
        kargs["signalExampleToStack"] = None  # signal
        # kargs["signalToTest"] = signal
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
    lumi = sel.data.lumi()["had"]
    trigEff = sel.data.triggerEfficiencies()["had"]

    for iBin in range(nBins):
        # make xs fall vs. HT
        xs1 = 0.1*r.TMath.Exp(-iBin)
        xs2 = 1.0*(2+iBin)**-4.0

        model = signals.point(xs=xs2,
                              label="%s_ht%d" % (selName, iBin),
                              sumWeightIn=1.0, x=0.0, y=0.0,
                              )
        effs = [0.0] * nBins
        effs[iBin] = 0.5
        model.insert(selName, {"effHad": effs,
                               "effUncRel":0.01}) # dummy}

        f = driver(signalToTest=model,
                llkName=options.llk,
                whiteList=whiteList,
                ignoreHad=options.ignoreHad,
                separateSystObs=not options.genBands,
                )

        dct = f.nlls()
        dct["s_nom"] = effs[iBin] * model.xs * lumi * trigEff[iBin]
        out[iBin] = dct

    return out


def go(selections=[], options=None, hMap=None):
    nCategories = 0
    report = {}
    nlls = {}

    for iSel, sel in enumerate(selections):
        if options.category and sel.name != options.category:
            continue

        if options.system:
            cmd = ["time", "./test.py"]
            for item in dir(options):
                if item.startswith("_"):
                    continue
                if item in ['read_file', 'read_module', 'ensure_value']:
                    continue
                if item in ["system", "bestFit"]:
                    continue

                if item in ["genBands", "ignoreHad", "interval", "plotBands", "significances", "simultaneous"]:
                    if getattr(options, item):
                        cmd.append("--%s" % item)
                elif item == "category":
                    cmd.append("--category=%s" % sel.name)
                else:
                    cmd.append("--%s=%s" % (item, getattr(options, item)))
            cmd = " ".join(cmd)
            print cmd
            os.system(cmd)
            continue

        nCategories += 1

        whiteList = [sel.name] if sel.name else []

        if options.significances and sel:
            nlls[sel.name] = significances(whiteList=whiteList,
                                           selName=sel.name,
                                           options=options)
            continue

        f = driver(llkName=options.llk,
                whiteList=whiteList,
                ignoreHad=options.ignoreHad,
                separateSystObs=not options.genBands,
                #trace=True
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

    from driver import driver

    import os
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

    if options.significances:
        printNlls(nlls)
    else:
        plotting.pValueCategoryPlots(hMap, )  # logYMinMax=(1.0e-4, 1.0e2))
        printReport(report)

    if (not options.system) and (not nCategories):
        print "WARNING: category %s not found." % options.category
