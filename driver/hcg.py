import os
import ra1
import likelihood
import plotting
import workspace

import ROOT as r


class driver(ra1.driver):
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

        # self.wspace = r.RooWorkspace("Workspace")
        # self.data = workspace.dataset(workspace.obs(self.wspace))
        # self.modelConfig = workspace.modelConfiguration(self.wspace)


    def compute(self, attr="", ch="", verbose=False):
        allX = getattr(self.wspace, attr)()
        it = allX.createIterator()
        while it.Next():
            n = it.GetName()
            self.translate_fZinv(ch, n)
            self.translate_zinvTtw(ch, n)
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


    def translate_zinvTtw(self, ch="", n=""):
        for varPrefix, funcPrefix in [("normTtw%s" % ch, "ttw%s" % ch),
                                      ("normZinv%s" % ch, "zInv%s" % ch),
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


