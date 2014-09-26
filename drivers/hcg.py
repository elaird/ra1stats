import os
import calc
import likelihood
import plotting
import workspace

import ROOT as r


class driver(object):
    def __init__(self, llkName="", whiteList=[],
                 ignoreHad=False, separateSystObs=True,
                 signalToTest=None, signalExampleToStack=None, signalToInject=None,
                 trace=False):

        for item in ["signalToTest", "signalExampleToStack", "signalToInject"]:
            setattr(self, item, eval(item))

        self.likelihoodSpec = likelihood.spec(name=llkName,
                                              whiteList=whiteList,
                                              ignoreHad=ignoreHad,
                                              separateSystObs=separateSystObs)

        self.checkInputs()  # FIXME: move to likelihoodSpec
        r.gROOT.SetBatch(True)
        r.gErrorIgnoreLevel = r.kWarning
        r.gPrintViaErrorHandler = True
        r.RooRandom.randomGenerator().SetSeed(1)

        r.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
        print "FIXME: rewrite __init__"


        #UNCOMMENTED HERE DON'T REALLY KNOW WHAT IT DOES

        self.wspace = r.RooWorkspace("Workspace")

        args = {}
        args["w"] = self.wspace
        args["smOnly"] = self.smOnly()
        args["injectSignal"] = self.injectSignal()

        for item in ["separateSystObs", "poi", "REwk", "RQcd", "nFZinv",
                     "constrainQcdSlope", "qcdParameterIsYield",
                     "initialValuesFromMuonSample", "initialFZinvFromMc"] :
            args[item] = getattr(self.likelihoodSpec, item)()

        if not self.smOnly():
            args["sigMcUnc"] = self.signalToTest.sigMcUnc
            if self.signalToTest.binaryExclusion:
                ini, min, max = self.likelihoodSpec.poi()["f"]
                assert min <= 1.0, min
                assert 1.0 <= max, max

            args["rhoSignalMin"] = self.likelihoodSpec.rhoSignalMin()
            workspace.startLikelihood(w=self.wspace,
                                      xs=self.signalToTest.xs,
                                      sumWeightIn=self.signalToTest.sumWeightIn,
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


    def compute(self, attr="", ch="", verbose=False):
        allX = getattr(self.wspace, attr)()
        it = allX.createIterator()
        while it.Next():
            n = it.GetName()
            self.translate_fZinv(ch, n)
            self.translate_norms(ch, n)
            self.clone_nobs(it, ch, n)
            self.clone_exp(it, ch, n)


    def clone_nobs(self, it=None, ch="", n=""):
        for box in ["had", "muon", "mumu", "phot"]:
            old = "n_obs_bin%s%s" % (ch, box)
            new = "n%s%s" % (box.capitalize(), ch)
            if n.startswith(old):
                    a = it.Clone(n.replace(old, new))
                    workspace.wimport(self.wspace, a)


    def clone_exp(self, it=None, ch="", n=""):
        d = {"n_exp_bin%shad"  % ch: "hadB%s"    % ch,  # FIXME: s + b
             "n_exp_bin%smuon" % ch: "muonB%s"   % ch,  # FIXME: s + b
             "n_exp_bin%smumu" % ch: "mumuExp%s" % ch,
             "n_exp_bin%sphot" % ch: "photExp%s" % ch,
             }
        for old, new in d.iteritems():
            if n.startswith(old):
                a = it.Clone(n.replace(old, new))
                workspace.wimport(self.wspace, a)


    def translate_fZinv(self, ch="", n=""):
        prefix = "n_exp_bin%shad" % ch
        suffix = "_proc_zinv"
        if n.startswith(prefix) and n.endswith(suffix):
            fZinv = r.RooFormulaVar(n.replace(prefix, "fZinv%s" % ch).replace(suffix, ""),
                                    "(@0)/((@0) + (@1))",
                                    r.RooArgList(self.wspace.function(n),
                                                 self.wspace.function(n.replace("_zinv", "_ttw")),
                                                 ),
                                    )
            workspace.wimport(self.wspace, fZinv)


    def translate_norms(self, ch="", n=""):
        for varPrefix, funcPrefix in [("normTtw%s" % ch, "ttw%s" % ch),
                                      ("normZinv%s" % ch, "zInv%s" % ch),
                                      ("normEwk%s" % ch, "ewk%s" % ch),  # when sel.muonForFullEwk
                                      ]:
            if n.startswith(varPrefix):
                f = r.RooFormulaVar(n.replace(varPrefix, funcPrefix),
                                    "TMath::Exp((@0)*TMath::Log(%g))" % self.likelihoodSpec.lnUMax(),
                                    r.RooArgList(self.wspace.var(n)),
                                    )
                workspace.wimport(self.wspace, f)



    def addBulkYields(self, selection):
        for i, y in enumerate(selection.data.observations()["nHadBulkTriggerCorrected"]):
            b = workspace.ni("nHadBulk", selection.name, i)
            workspace.wimport(self.wspace, r.RooRealVar(b, b, y))


    def rooFitResults(self, cardName="card.txt"):
        cmd = ["combineCards.py"]
        for iFileName, fileName in enumerate(self.likelihoodSpec.dumpHcgCards()):
            cat = fileName[1 + fileName.find("/"):fileName.find(".txt")]
            cmd.append("_%s=%s" % (cat, fileName))  # note leading underscore
        cmd.append("> %s" % cardName)
        os.system(" ".join(cmd))
        
        #exit(cmd)

        fit = ["combine",
               "-M MaxLikelihoodFit",
               "--saveWorkspace",
               #"--saveNLL",
               #"--plots",
               "--rMin 0.0",
               "--rMax 1.0e-6",
               "--preFitValue 0.0",
               #"-v -1",
               cardName,
               #"| grep -v 'has no signal processes contributing to it'",
               ]
        os.system(" ".join(fit))

        f1 = r.TFile("mlfit.root")
        results = f1.Get("fit_b")
        f1.Close()
        return results


    def setWspace(self):
        results = self.rooFitResults()
        f = r.TFile("MaxLikelihoodFitResult.root")
        self.wspace = f.Get("MaxLikelihoodFitResult")
        f.Close()
        return results


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
                msgThreshold=None):

        results = self.setWspace()

        note = self.note() + "_hcg"
        if self.injectSignal():
            note += "_SIGNALINJECTED"

        for selection in self.likelihoodSpec.selections():
            self.addBulkYields(selection)  #  FIXME: move to data cards

            ch = "_%s_" % selection.name
            self.compute(attr="allVars", ch=ch)
            self.compute(attr="allFunctions", ch=ch)

            args = self.plotterArgs(selection)
            args.update({"results": results,
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

    def checkInputs(self):
        pass

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
