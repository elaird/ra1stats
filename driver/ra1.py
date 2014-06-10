import os

import calc
import ensemble
import likelihood
import plotting
import workspace
import utils

import ROOT as r


class driver(object):
    def __init__(self, llkName="", rhoSignalMin=0.0, fIniFactor=1.0,
                 whiteList=[], ignoreHad=False, separateSystObs=True,
                 signalToTest=None, signalExampleToStack=None, signalToInject=None,
                 trace=False):

        for item in ["rhoSignalMin", "signalToTest",
                     "signalExampleToStack", "signalToInject"]:
            setattr(self, item, eval(item))

        self.likelihoodSpec = likelihood.spec(name=llkName,
                                              whiteList=whiteList,
                                              ignoreHad=ignoreHad,
                                              separateSystObs=separateSystObs)

        self.checkInputs()
        r.gROOT.SetBatch(True)
        r.gErrorIgnoreLevel = r.kWarning
        r.gPrintViaErrorHandler = True
        r.RooRandom.randomGenerator().SetSeed(1)

        self.wspace = r.RooWorkspace("Workspace")

        args = {}
        args["w"] = self.wspace
        args["smOnly"] = self.smOnly()
        args["injectSignal"] = self.injectSignal()

        for item in ["separateSystObs", "poi", "REwk", "RQcd", "nFZinv",
                     "constrainQcdSlope", "qcdParameterIsYield",
                     "initialValuesFromMuonSample", "initialFZinvFromMc"] :
            args[item] = getattr(self.likelihoodSpec, item)()

        for item in ["rhoSignalMin"] :
            args[item] = getattr(self, item)

        if not self.smOnly():
            args["sigMcUnc"] = self.signalToTest.sigMcUnc
            workspace.startLikelihood(w=self.wspace,
                                      xs=self.signalToTest.xs,
                                      sumWeightIn=self.signalToTest.sumWeightIn,
                                      effUncRel=self.signalToTest.effUncRel,
                                      fIniFactor=fIniFactor,
                                      poi=self.likelihoodSpec.poi())

        total = {}
        for sel in self.likelihoodSpec.selections():
            args["selection"] = sel
            args["signalToTest"] = self.signalToTest.effs(sel.name) if self.signalToTest else {}
            args["signalToInject"] = self.signalToInject.effs(sel.name) if self.signalToInject else {}
            args["systematicsLabel"] = self.systematicsLabel(sel.name)
            args["kQcdLabel"] = self.kQcdLabel(sel.name)

            d = workspace.setupLikelihood(**args)
            for key, value in d.iteritems():
                if key not in total:
                    total[key] = []
                total[key] += value

        workspace.finishLikelihood(w=self.wspace,
                         smOnly=self.smOnly(),
                         standard=self.likelihoodSpec.standardPoi(),
                         poiDict=self.likelihoodSpec.poi(),
                         **total)

        self.data = workspace.dataset(workspace.obs(self.wspace))
        self.modelConfig = workspace.modelConfiguration(self.wspace)

        if trace :
            #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
            #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
            r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    def checkInputs(self):
        l = self.likelihoodSpec
        assert l.REwk() in ["", "FallingExp", "Linear", "Constant"]
        assert l.RQcd() in ["FallingExp", "Zero"]
        assert l.nFZinv() in ["One", "Two", "All"]
        assert len(l.poi()) == 1, len(l.poi())
        if not l.standardPoi():
            assert self.smOnly()
            if "qcd" in l.poi().keys()[0]:
                assert "FallingExp" in l.RQcd()
            #assert len(l.selections())==1,"%d!=1"%len(l.selections())

        if l.initialValuesFromMuonSample():
            if l.RQcd() != "Zero":
                assert l.qcdParameterIsYield()

        if l.constrainQcdSlope():
            assert l.RQcd() == "FallingExp","%s!=FallingExp" % l.RQcd()
        if any([sel.universalKQcd for sel in l.selections()]):
            assert "FallingExp" in l.RQcd()
        for sel in l.selections():
            assert sel.boxes, sel.name
            if sel.muonForFullEwk:
                for box in ["phot", "mumu"]:
                    assert box not in sel.boxes, box
            bins = sel.data.htBinLowerEdges()
            for obj in [self.signalToTest, self.signalExampleToStack, self.signalToInject]:
                if not obj:
                    continue
                effs = obj.effs(sel.name)
                if not effs:
                    continue
                for key, value in effs.iteritems():
                    if type(value) is list:
                        assert len(value) == len(bins), "key %s: %d != %d" % (key, len(value), len(bins))

    def smOnly(self) :
        return not self.signalToTest

    def injectSignal(self) :
        return bool(self.signalToInject)

    def systematicsLabel(self, name) :
        selections = self.likelihoodSpec.selections()
        syst = [s.universalSystematics for s in selections]
        assert sum(syst)<2
        if any(syst) : assert not syst.index(True)
        return name if sum(syst)!=1 else selections[syst.index(True)].name

    def kQcdLabel(self, name) :
        selections = self.likelihoodSpec.selections()
        k = [s.universalKQcd for s in selections]
        assert sum(k)<2
        if any(k) : assert not k.index(True)
        return name if sum(k)!=1 else selections[k.index(True)].name

    def note(self) :
        return self.likelihoodSpec.note()+("_signal" if not self.smOnly() else "")

    def rooFitResults(self):
        return utils.rooFitResults(workspace.pdf(self.wspace), self.data)

    def debug(self) :
        self.wspace.Print("v")
        plotting.writeGraphVizTree(self.wspace)
        #pars = utils.rooFitResults(workspace.pdf(wspace), data).floatParsFinal(); pars.Print("v")
        self.rooFitResults().Print("v")
        #wspace.Print("v")

    def writeMlTable(self, fileName = "mlTables.tex", categories = []) :
        def pars() :
            self.rooFitResults()
            return workspace.floatingVars(self.wspace)

        def renamed(v, cat = "") :
            out = v
            out = out.replace("_"+cat, "")
            for i in range(20,-1,-1) :
                out = out.replace("_%d"%i, "^{%d}"%i)
            out = out.replace("ewk", r'\mathrm{EWK}')
            out = out.replace("qcd", r'\mathrm{QCD}')
            out = out.replace("rho", r'\rho_')
            out = out.replace("MumuZ", r'{\mu\mu Z}')
            out = out.replace("MuonW", r'{\mu W}')
            out = out.replace("PhotZ", r'{\gamma Z}')
            out = out.replace("Zinv", r'_\mathrm{Zinv}')
            return r'$%s$'%out

        p = pars()
        s  = "\n".join([r'\documentclass{article}',
                        r'\begin{document}'])

        for cat in categories :
            if not any([cat in d["name"] for d in p]) : continue
            s += "\n".join(['', '',
                            r'\begin{table}\centering',
                            r'\caption{SM-only maximum-likelihood parameter values (%s).}'%cat.replace("_", " "),
                            r'\label{tab:mlParameterValues%s}'%cat,
                            r'\begin{tabular}{lcc}',
                            ])
            s += r'name & value & error \\ \hline'+'\n'

            for d in sorted(p, key = lambda d: utils.naturalSortKey(d["name"])) :
                if cat not in d["name"] : continue
                cols = [r'{\tt %9.2e}', r'{\tt %8.1e}']
                if "rho" in d["name"] or "fZinv" in d["name"] :
                    cols = [r'{\tt %3.2f}', r'{\tt %3.2f}']
                spec = ' & '.join(['%s']+cols)+r'\\'+'\n'
                s += spec%(renamed(d["name"], cat), d["value"], d["error"])
            s += "\n".join([r'\hline', r'\end{tabular}', r'\end{table}'])

        s += "\n".join(['',r'\end{document}'])
        import makeTables as mt
        mt.write(s, fileName)

    def profile(self) :
        calc.profilePlots(self.data, self.modelConfig, self.note())


    def expandPoiRange(self, allowNegative=True, nIterationsMax=1):
        s = self.wspace.set("poi")
        assert s.getSize() == 1
        poi = s.first()

        r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING)
        nIterations = 0

        for i in range(nIterationsMax):
            results = self.rooFitResults()
            #results.Print()
            #poi.Print()

            again = False
            nIterations += 1
            if nIterationsMax <= nIterations:
                break
            if poi.getMax() < poi.getVal() + 2.0 * poi.getError():
                poi.setMax(poi.getMax() + 2.0 * (poi.getMax() - poi.getMin()))
                poi.setMin(0.0)
                again = True
            if allowNegative and (poi.getVal() - 2.0 * poi.getError() <  poi.getMin()):
                poi.setMin(poi.getMin() - 1.0 * (poi.getMax() - poi.getMin()))
                again = True
            if not again:
                break
        return nIterations, poi

    def interval(self, cl = 0.95, method = "profileLikelihood", makePlots = False,
                 nIterationsMax = 1, lowerItCut = 0.1, upperItCut = 0.9, itFactor = 3.0) :

        hack = False
        if hack :
            print "HACK!"
            d = self.intervalSimple(cl = cl, method = method, makePlots = makePlots)
            d["nIterations"] = 1
            s = self.wspace.set("poi"); assert s.getSize()==1
            s.first().setMax(40.0)
            s.first().setMin(0.0)
            return d

        for i in range(nIterationsMax) :
            d = self.intervalSimple(cl = cl, method = method, makePlots = makePlots)
            d["nIterations"] = i+1
            if nIterationsMax==1 : return d

            s = self.wspace.set("poi"); assert s.getSize()==1
            m = s.first().getMax()
            if d["upperLimit"]>upperItCut*m :
                s.first().setMax(m*itFactor)
                s.first().setMin(m/itFactor)
                s.first().setMin(0.0); print "HACK: setting min to zero"
            elif d["upperLimit"]<lowerItCut*m :
                s.first().setMax(m/itFactor)
            else :
                break
        return d

    def intervalSimple(self, cl = None, method = "", makePlots = None) :
        if method=="profileLikelihood" :
            return calc.plInterval(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(),
                                   cl = cl, poiList = self.likelihoodSpec.poiList(), makePlots = makePlots)
        elif method=="feldmanCousins" :
            return fcExcl(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)

    def cppDrive(self, tool = ["", "valgrind", "igprof"][0]) :
        workspace.wimport(self.wspace, self.data)
        workspace.wimport(self.wspace, self.modelConfig)
        fileName = "workspace.root"
        self.wspace.writeToFile(fileName)
        cmd = {"":"",
               "valgrind":"valgrind --tool=callgrind",
               "igprof":"igprof",
               }[tool]
        os.system(cmd+" cpp/drive %s"%fileName)

    def cls(self, cl = 0.95, nToys = 300, calculatorType = "", testStatType = 3, plusMinus = {}, makePlots = False, nWorkers = 1, plSeedParams = {}) :
        args = {}
        out = {}
        if plSeedParams["usePlSeed"] :
            plUpperLimit = self.interval(cl = cl, nIterationsMax = plSeedParams["plNIterationsMax"])["upperLimit"]
            out["PlUpperLimit"] = plUpperLimit
            args["nPoints"] = plSeedParams["nPoints"]
            args["poiMin"] = plUpperLimit*plSeedParams["minFactor"]
            args["poiMax"] = plUpperLimit*plSeedParams["maxFactor"]

            s = self.wspace.set("poi"); assert s.getSize()==1
            if s.first().getMin() : s.first().setMin(0.0)
            if args["poiMax"]>s.first().getMax() : s.first().setMax(args["poiMax"])

        out2 = calc.cls(dataset = self.data, modelconfig = self.modelConfig, wspace = self.wspace, smOnly = self.smOnly(),
                        cl = cl, nToys = nToys, calculatorType = calculatorType, testStatType = testStatType,
                        plusMinus = plusMinus, nWorkers = nWorkers, note = self.note(), makePlots = makePlots, **args)
        out.update(out2)
        return out

    def clsCustom(self, nToys = 200, testStatType = 3) :
        return calc.clsCustom(self.wspace, self.data, nToys = nToys, testStatType = testStatType, smOnly = self.smOnly(), note = self.note())

    def plotterArgs(self, selection) :
        def activeBins(selection) :
            out = {}
            for key,value in selection.data.observations().iteritems() :
                out[key] = map(lambda x:x!=None, value)
            return out

        args = {}
        args["activeBins"] = activeBins(selection)
        args["systematicsLabel"] = self.systematicsLabel(selection.name)

        for item in ["smOnly", "note"] :
            args[item] = getattr(self, item)()

        for item in ["wspace", "signalExampleToStack", "signalToTest"] :
            args[item] = getattr(self, item)

        for arg,member in {"selNote": "note", "label":"name", "inputData":"data",
                           "muonForFullEwk":"muonForFullEwk", "yAxisLogMinMax":"yAxisLogMinMax"}.iteritems() :
            args[arg] = getattr(selection, member)

        for item in ["lumi", "htBinLowerEdges", "htMaxForPlot"] :
            args[item] = getattr(selection.data, item)()

        for item in ["REwk", "RQcd", "legendTitle", "ignoreHad"] :
            args[item] = getattr(self.likelihoodSpec, item)()

        return args

    def ensemble(self, nToys = 200, stdout = False, reuseResults = False) :
        assert nToys
        args = {"note":self.note(), "nToys":nToys}
        if not reuseResults :
            ensemble.writeHistosAndGraphs(self.wspace, self.data, **args)
        else :
            print "WARNING: ensemble plots/tables are being created from previous results."

        args.update({"plotsDir":"plots", "stdout":stdout, "selections":self.likelihoodSpec.selections()})
        plotting.ensemblePlotsAndTables(**args)

    def bestFitToy(self, nToys = 200) :
        #obs,results,i = ntupleOfFitToys(self.wspace, self.data, nToys, cutVar = ("var", "A_qcd"), cutFunc = lambda x:x>90.0); return toys,i
        #obs,results,i = ntupleOfFitToys(self.wspace, self.data, nToys, cutVar = ("var", "rhoPhotZ"), cutFunc = lambda x:x>2.0); return toys,i
        for selection in self.likelihoodSpec.selections() :
            args = self.plotterArgs(selection)
            args.update({"results": results, "note": self.note()+"_toy%d"%i, "obsLabel":"Toy %d"%i,
                         "printPages": False, "drawMc": True, "printNom":False, "drawComponents":True, "printValues":True
                         })
            plotter = plotting.validationPlotter(args)
            plotter.inputData = selection.data
            plotter.go()

    def expectedLimit(self, cl = 0.95, nToys = 200, plusMinus = {}, makePlots = False) :
        return expectedLimit(self.data, self.modelConfig, self.wspace, smOnly = self.smOnly(), cl = cl, nToys = nToys,
                             plusMinus = plusMinus, note = self.note(), makePlots = makePlots)

    def bestFit(self,
                printPages=False,
                drawMc=True,
                printValues=False,
                printNom=False,
                drawComponents=True,
                errorsFromToys=0,
                drawRatios=False,
                significance=False,
                pullPlotMax=3.5,
                pullThreshold=2.0,
                msgThreshold=r.RooFit.DEBUG):
        #calc.pullPlots(workspace.pdf(self.wspace))

        r.RooMsgService.instance().setGlobalKillBelow(msgThreshold)
        results = self.rooFitResults()
        out = {}
        out["numInvalidNll"] = utils.checkResults(results)

        poisKey = "simple"
        lognKey = "kMinusOne"
        pulls = calc.pulls(pdf=workspace.pdf(self.wspace),
                           poisKey=poisKey,
                           lognKey=lognKey)

        title = "_".join([x.name for x in self.likelihoodSpec.selections()])
        calc.pullPlots(pulls=pulls,
                       poisKey=poisKey,
                       lognKey=lognKey,
                       note=self.note(),
                       plotsDir="plots",
                       yMax=pullPlotMax,
                       threshold=pullThreshold,
                       title=title)

        for selection in self.likelihoodSpec.selections():
            args = self.plotterArgs(selection)
            args.update({"results": results,
                         "note": self.note() if not self.injectSignal() else self.note()+"_SIGNALINJECTED",
                         "nSelections": len(self.likelihoodSpec.selections()),
                         "obsLabel": "Data" if not self.injectSignal() else "Data (SIGNAL INJECTED)",
                         "printPages": printPages,
                         "drawMc": drawMc,
                         "printNom": printNom,
                         "drawComponents": drawComponents,
                         "printValues": printValues,
                         "errorsFromToys": errorsFromToys,
                         "drawRatios": drawRatios,
                         "significance": significance,
                         })
            plotter = plotting.validationPlotter(args)
            plotter.go()

        # gather stats
        out.update(calc.pullStats(pulls=pulls,
                                  nParams=len(workspace.floatingVars(self.wspace)),
                                  ),
                   )

        # key change
        out["chi2ProbSimple"] = out["prob"]
        del out["prob"]

        if errorsFromToys:
            pvalues = plotting.ensembleResults(note=self.note(),
                                               nToys=errorsFromToys)
            for dct in pvalues:
                out[dct["key"]] = utils.ListFromTGraph(dct["pValue"])[-1]

        return out


    def translate(self, w, attr="", verbose=False):
        d = {"n_obs_binhad":  "nHad_",
             "n_obs_binmuon": "nMuon_",
             "n_obs_binmumu": "nMumu_",
             "n_obs_binphot": "nPhot_",
             "n_exp_binhad":  "hadB_",  # FIXME: s + b
             "n_exp_binmuon": "muonB_",  # FIXME: s + b
             "n_exp_binmumu": "mumuExp_",
             "n_exp_binphot": "photExp_",
             }

        allX = getattr(w, attr)()
        it = allX.createIterator()
        while it.Next():
            n = it.GetName()
            for old, new in d.iteritems():
                if n.startswith(old):
                    n2 = n.replace(old, new)
                    a = it.Clone(n2)
                    workspace.wimport(w, a)
                    if verbose:
                        print n, n2
                        a.Print()


    def compute(self, w, attr="", label="", verbose=False):
        allX = getattr(w, attr)()
        it = allX.createIterator()
        while it.Next():
            n = it.GetName()
            if n.startswith("n_exp_binhad") and n.endswith("_proc_zinv"):
                fZinv = r.RooFormulaVar(n.replace("n_exp_binhad", "fZinv_%s_" % label).replace("_proc_zinv", ""),
                                        "(@0)/((@0) + (@1))",
                                        r.RooArgList(w.function(n), w.function(n.replace("_zinv", "_ttw"))),
                                        )
                workspace.wimport(w, fZinv)
                if verbose:
                    fZinv.Print()

            for varPrefix, funcPrefix in [("normTtw", "ttw"),
                                          ("normZinv", "zInv"),
                                          ]:
                if n.startswith(varPrefix):
                    f = r.RooFormulaVar(n.replace(varPrefix, funcPrefix),
                                        "TMath::Exp((@0)*TMath::Log(%g))" % self.likelihoodSpec.lnUMax(),
                                        r.RooArgList(w.var(n)),
                                        )
                    workspace.wimport(w, f)
                    if verbose:
                        f.Print()


    def addBulkYields(self, w, selection):
        for i, y in enumerate(selection.data.observations()["nHadBulkTriggerCorrected"]):
            b = workspace.ni("nHadBulk", selection.name, i)
            workspace.wimport(w, r.RooRealVar(b, b, y))


    def hcgBestFit(self,
                   printPages=False,
                   drawMc=True,
                   printValues=False,
                   printNom=False,
                   drawComponents=True,
                   errorsFromToys=0,
                   drawRatios=False,
                   significance=False,
                   pullPlotMax=3.5,
                   pullThreshold=2.0,
                   msgThreshold=None):

        if msgThreshold:
            r.RooMsgService.instance().setGlobalKillBelow(msgThreshold)

        for fileName in self.likelihoodSpec.dumpHcgCards():
            cmd = ["combine",
                   "-M MaxLikelihoodFit",
                   "--saveWorkspace",
                   #"--saveNLL",
                   #"--plots",
                   "--rMin 0.0",
                   "--rMax 1.0e-6",
                   "--preFitValue 0.0",
                   #"-v -1",
                   fileName,
                   ]
            os.system(" ".join(cmd))

        r.gSystem.Load("libHiggsAnalysisCombinedLimit.so")

        f1 = r.TFile("mlfit.root")
        results = f1.Get("fit_b")
        f1.Close()

        f = r.TFile("MaxLikelihoodFitResult.root")
        wspace = f.Get("MaxLikelihoodFitResult")
        self.translate(wspace, attr="allVars")
        self.translate(wspace, attr="allFunctions")

        self.compute(wspace, attr="allVars")
        self.compute(wspace, attr="allFunctions", label="0b_ge4j")

        note = self.note() + "_hcg"
        if self.injectSignal():
            note += "_SIGNALINJECTED"

        for selection in self.likelihoodSpec.selections():
            self.addBulkYields(wspace, selection)  #  FIXME: move to data cards
            args = self.plotterArgs(selection)
            args.update({"results": results,
                         "wspace": wspace,
                         "note": note,
                         "nSelections": len(self.likelihoodSpec.selections()),
                         "obsLabel": "Data" if not self.injectSignal() else "Data (SIGNAL INJECTED)",
                         "printPages": printPages,
                         "drawMc": drawMc,
                         "printNom": printNom,
                         "drawComponents": drawComponents,
                         "printValues": printValues,
                         "errorsFromToys": errorsFromToys,
                         "drawRatios": drawRatios,
                         "significance": significance,
                         "hcg": True,
                         })
            plotter = plotting.validationPlotter(args)
            plotter.go()

        f.Close()


    def qcdPlot(self):
        plotting.errorsPlot(self.wspace,
                            utils.rooFitResults(workspace.pdf(self.wspace), self.data),
                            )
