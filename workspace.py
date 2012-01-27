import collections,math
import utils,plotting,calc
from common import obs,pdf,note,ni
import ROOT as r

def modelConfiguration(w, smOnly, qcdSearch) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(pdf(w))
    modelConfig.SetObservables(w.set("obs"))
    if (not smOnly) or qcdSearch :
        modelConfig.SetParametersOfInterest(w.set("poi"))
        modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def q0q1(inputData, factor, A_ewk_ini) :
    def thing(i) :
        return (obs["nHad"][i] - obs["nHadBulk"][i]*A_ewk_ini*factor)
    obs = inputData.observations()
    return thing(0)/thing(1)

def initialkQcd(inputData, factor, A_ewk_ini) :
    obs = inputData.observations()
    htMeans = inputData.htMeans()    
    out = q0q1(inputData, factor, A_ewk_ini)
    out *= obs["nHadBulk"][1]/float(obs["nHadBulk"][0])
    out = math.log(out)
    out /= (htMeans[1] - htMeans[0])
    return out

def initialAQcd(inputData, factor, A_ewk_ini, kQcd) :
    obs = inputData.observations()
    htMeans = inputData.htMeans()
    out = math.exp(kQcd)
    out *= (obs["nHad"][0]/float(obs["nHadBulk"][0]) - A_ewk_ini*factor)
    return out
                     
def parametrizedExp(w = None, name = "", label = "", kLabel = "", i = None) :
    A = ni("A_%s"%name, label)
    k = ni("k_%s"%name, kLabel)
    bulk = ni("nHadBulk", label, i)
    mean = ni("htMean", label, i)
    varName = ni(name, label, i)
    return r.RooFormulaVar(varName, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var(bulk), w.var(A), w.var(k), w.var(mean)))
    
def parametrizedExpA(w = None, name = "", label = "", kLabel = "", i = None) :
    A = ni("A_%s"%name, label)
    k = ni("k_%s"%name, kLabel)
    bulk = ni("nHadBulk", label, i)
    mean = ni("htMean", label, i)
    varName = ni(name, label, i)
    return r.RooFormulaVar(varName, "(@0)*exp((@1)-(@2)*(@3))", r.RooArgList(w.var(bulk), w.var(A), w.var(k), w.var(mean)))
    
def parametrizedLinear(w = None, name = "", label = "", kLabel = "", i = None, iLast = None) :
    def mean(j) : return ni("htMean", label, j)
    A = ni("A_%s"%name, label)
    k = ni("k_%s"%name, kLabel)
    bulk = ni("nHadBulk", label, i)
    varName = ni(name, label, i)
    return r.RooFormulaVar(varName, "(@0)*(@1)*(1 + (@2)*((@3)-(@4))/((@5)-(@4)))",
                           r.RooArgList(w.var(bulk), w.var(A), w.var(k), w.var(mean(i)), w.var(mean(0)), w.var(mean(iLast)))
                           )

def importEwk(w = None, REwk = None, name = "", label = "", i = None, iLast = None, nHadValue = None, A_ini = None) :
    A = ni("A_%s"%name, label)
    k = ni("k_%s"%name, label)

    if REwk and not i :
        wimport(w, r.RooRealVar(A, A, A_ini, 0.0, 1.0))
        wimport(w, r.RooRealVar(k, k, 0.0,  -1.0, 1.0))
    if REwk=="Constant" and not i :
        w.var(k).setVal(0.0)
        w.var(k).setConstant()
    
    if REwk=="Linear" : wimport(w, parametrizedLinear(w = w, name = name, label = label, kLabel = label, i = i, iLast = iLast))
    elif (REwk=="FallingExp" or  REwk=="Constant") : wimport(w, parametrizedExp(w = w, name = name, label = label, kLabel = label, i = i))
    else :
        varName = ni(name, label, i)
        wimport(w, r.RooRealVar(varName, varName, max(1, nHadValue), 0.0, 10.0*max(1, nHadValue)))
    return varOrFunc(w, name, label, i)

def importFZinv(w = None, nFZinv = "", name = "", label = "", i = None, iLast = None) :
    def mean(j) : return ni("htMean", label, j)
    def fz(j) : return ni(name, label, j)
    
    if nFZinv=="All" :
        wimport(w, r.RooRealVar(fz(i), fz(i), 0.5, 0.2, 0.8))
    elif nFZinv=="One" :
        if not i : wimport(w, r.RooRealVar(fz(i), fz(i), 0.5, 0.0, 1.0))
        else     : wimport(w, r.RooFormulaVar(fz(i), "(@0)", r.RooArgList(w.var(fz(0)))))
    elif nFZinv=="Two" :
        if not i :
            wimport(w, r.RooRealVar(fz(i),     fz(i),     0.5, 0.0, 1.0))
            wimport(w, r.RooRealVar(fz(iLast), fz(iLast), 0.5, 0.0, 1.0))
        elif i!=iLast :
            argList = r.RooArgList(w.var(fz(0)), w.var(fz(iLast)), w.var(mean(i)), w.var(mean(0)), w.var(mean(iLast)))
            wimport(w, r.RooFormulaVar(fz(i), "(@0)+((@2)-(@3))*((@1)-(@0))/((@4)-(@3))", argList))
    return varOrFunc(w, name, label, i)

def hadTerms(w = None, inputData = None, label = "", systematicsLabel = "", kQcdLabel = "", smOnly = None,
             REwk = None, RQcd = None, nFZinv = None, qcdSearch = None) :

    obs = inputData.observations()
    trg = inputData.triggerEfficiencies()
    htMeans = inputData.htMeans()
    terms = []
    out = collections.defaultdict(list)

    assert not qcdSearch
    assert RQcd!="FallingExpA"

    #QCD variables
    A = ni("A_qcd", label)
    wimport(w, r.RooRealVar(A, A, 1.5e-5, 0.0, 100.0))

    k = ni("k_qcd", kQcdLabel)
    if label==kQcdLabel :
        wimport(w, r.RooRealVar(k, k, 1.0e-5, 0.0, 1.0))

    #inital values
    A_ewk_ini = 1.3e-5
    if RQcd=="Zero" :
        w.var(A).setVal(0.0)
        w.var(A).setConstant()
        w.var(k).setVal(0.0)
        w.var(k).setConstant()
    else :
        out["nuis"].append(k)
        if not qcdSearch : out["nuis"].append(A)
        factor = 0.7
        w.var(k).setVal( initialkQcd(inputData, factor, A_ewk_ini) )
        w.var(A).setVal( initialAQcd(inputData, factor, A_ewk_ini, w.var(k).getVal()) )

    #observed "constants", not depending upon slice
    for i,htMeanValue,nHadBulkValue,hadTrgEffValue in zip(range(len(htMeans)), htMeans, obs["nHadBulk"], trg["had"]) :
        m = ni("htMean", label, i)
        if not w.var(m) : wimport(w, r.RooRealVar(m, m, htMeanValue))
        b = ni("nHadBulk", label, i)
        if not w.var(b) : wimport(w, r.RooRealVar(b, b, nHadBulkValue*hadTrgEffValue))

    #more
    iLast = len(htMeans)-1
    for i,nHadValue in enumerate(obs["nHad"]) :
        if RQcd=="FallingExpA" : wimport(w, parametrizedExpA(w = w, name = "qcd", label = label, kLabel = kQcdLabel, i = i))
        else :                   wimport(w, parametrizedExp (w = w, name = "qcd", label = label, kLabel = kQcdLabel, i = i))
        qcd = w.function(ni("qcd", label, i))
        
        ewk   = importEwk(  w = w, REwk   = REwk,   name = "ewk",   label = label, i = i, iLast = iLast, nHadValue = nHadValue, A_ini = A_ewk_ini)
        fZinv = importFZinv(w = w, nFZinv = nFZinv, name = "fZinv", label = label, i = i, iLast = iLast)

        wimport(w, r.RooFormulaVar(ni("zInv", label, i), "(@0)*(@1)",       r.RooArgList(ewk, fZinv)))
        wimport(w, r.RooFormulaVar(ni("ttw",  label, i), "(@0)*(1.0-(@1))", r.RooArgList(ewk, fZinv)))

        hadB    = ni("hadB",    label, i)
        hadS    = ni("hadS",    label, i)
        nHad    = ni("nHad",    label, i)
        hadPois = ni("hadPois", label, i)
        hadExp  = ni("hadExp",  label, i)
        
        wimport(w, r.RooFormulaVar(hadB, "(@0)+(@1)", r.RooArgList(ewk, qcd)))
        wimport(w, r.RooRealVar(nHad, nHad, nHadValue))
        if smOnly :
            wimport(w, r.RooPoisson(hadPois, hadPois, w.var(nHad), w.function(hadB)))
        else :
            lumi = ni("hadLumi", label)
            eff = ni("signalEffHad", label, i)
            rho = ni("rhoSignal", systematicsLabel)
            wimport(w, r.RooProduct(hadS, hadS, r.RooArgSet(w.var("f"), w.var(rho), w.var("xs"), w.var(lumi), w.var(eff))))
            wimport(w, r.RooAddition(hadExp, hadExp, r.RooArgSet(w.function(hadB), w.function(hadS))))
            wimport(w, r.RooPoisson(hadPois, hadPois, w.var(nHad), w.function(hadExp)))
        terms.append(hadPois)

    hadTermsName = ni("hadTerms", label)
    w.factory("PROD::%s(%s)"%(hadTermsName, ",".join(terms)))

    out["terms"].append(hadTermsName)
    out["multiBinObs"].append(ni("nHad", label))
    if REwk :
        out["nuis"].append(ni("A_ewk", label))
        if REwk!="Constant" : out["nuis"].append(ni("k_ewk", label))
    return out

def simpleOneBinTerm(w = None, inputData = None, label = "", smOnly = None, varDict = {}) :
    assert not smOnly
    obs = inputData.observations()
    terms = []

    i = len(obs["nHad"])-1
    nHad = obs["nHad"][i]

    wimport(w, r.RooRealVar("nHad%d"%i, "nHad%d"%i, nHad))
    wimport(w, r.RooRealVar("hadB%d"%i, "hadB%d"%i, varDict["b"]))
    wimport(w, r.RooProduct("hadS%d"%i, "hadS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("hadLumi"), w.var("signalEffHad%d"%i))))
    wimport(w, r.RooAddition("hadExp%d"%i, "hadExp%d"%i, r.RooArgSet(w.function("hadB%d"%i), w.function("hadS%d"%i))))
    wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadExp%d"%i)))
    terms.append("hadPois%d"%i)
    
    w.factory("PROD::simpleOneBinTerm(%s)"%",".join(terms))

def mumuTerms(w = None, inputData = None, label = "", systematicsLabel = "", kQcdLabel = "", smOnly = None) :
    terms = []
    out = collections.defaultdict(list)

    if label==systematicsLabel :
        rho = ni("rhoMumuZ", label)
        one = ni("oneMumu", label)
        sigma = ni("sigmaMumuZ", label)
        gaus = ni("mumuGaus", label)
        wimport(w, r.RooRealVar(rho, rho, 1.0, 1.0e-3, 3.0))
        wimport(w, r.RooRealVar(one, one, 1.0))
        wimport(w, r.RooRealVar(sigma, sigma, inputData.fixedParameters()["sigmaMumuZ"]))
        wimport(w, r.RooGaussian(gaus, gaus, w.var(one), w.var(rho), w.var(sigma)))
        out["obs"].append(one)
        out["nuis"].append(rho)
        terms.append(gaus)

    rFinal = None
    for i,nMumuValue,purity,mcZmumuValue,mcZinvValue,stopHere in zip(range(len(inputData.observations()["nMumu"])),
                                                                     inputData.observations()["nMumu"],
                                                                     inputData.purities()["mumu"],
                                                                     inputData.mcExpectations()["mcZmumu"],
                                                                     inputData.mcExpectations()["mcZinv"],
                                                                     inputData.constantMcRatioAfterHere(),
                                                                     ) :
        if nMumuValue==None : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcZmumu"][i:])/sum(inputData.mcExpectations()["mcZinv"][i:])
        nMumu = ni("nMumu", label, i)
        rMumu = ni("rMumu", label, i)
        wimport(w, r.RooRealVar(nMumu, nMumu, nMumuValue))
        wimport(w, r.RooRealVar(rMumu, rMumu, (mcZmumuValue/mcZinvValue if not rFinal else rFinal)/purity))

        mumuExp = ni("mumuExp", label, i)
        rhoMumuZ = ni("rhoMumuZ", systematicsLabel)
        wimport(w, r.RooFormulaVar(mumuExp, "(@0)*(@1)*(@2)",
                                   r.RooArgList(w.var(rhoMumuZ), w.var(rMumu), w.function(ni("zInv", label, i)))
                                   )
                )

        mumuPois = ni("mumuPois", label, i)
        wimport(w, r.RooPoisson(mumuPois, mumuPois, w.var(nMumu), w.function(mumuExp)))
        terms.append(mumuPois)

    mumuTermsName = ni("mumuTerms", label)
    w.factory("PROD::%s(%s)"%(mumuTermsName, ",".join(terms)))

    out["terms"].append(mumuTermsName)
    out["multiBinObs"].append(ni("nMumu", label))
    return out

def photTerms(w = None, inputData = None, label = "", systematicsLabel = "", kQcdLabel = "", smOnly = None) :
    out = collections.defaultdict(list)

    terms = []
    if label==systematicsLabel :
        rho = ni("rhoPhotZ", label)
        one = ni("onePhot", label)
        sigma = ni("sigmaPhotZ", label)
        gaus = ni("photGaus", label)
        wimport(w, r.RooRealVar(rho, rho, 1.0, 1.0e-3, 3.0))
        wimport(w, r.RooRealVar(one, one, 1.0))
        wimport(w, r.RooRealVar(sigma, sigma, inputData.fixedParameters()["sigmaPhotZ"]))
        wimport(w, r.RooGaussian(gaus, gaus, w.var(one), w.var(rho), w.var(sigma)))
        terms.append(gaus)
        out["obs"].append(one)
        out["nuis"].append(rho)

    rFinal = None
    for i,nPhotValue,purity,mcGjetValue,mcZinvValue,stopHere in zip(range(len(inputData.observations()["nPhot"])),
                                                                    inputData.observations()["nPhot"],
                                                                    inputData.purities()["phot"],
                                                                    inputData.mcExpectations()["mcGjets"],
                                                                    inputData.mcExpectations()["mcZinv"],
                                                                    inputData.constantMcRatioAfterHere(),
                                                                    ) :
        if nPhotValue==None : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcGjets"][i:])/sum(inputData.mcExpectations()["mcZinv"][i:])
        nPhot = ni("nPhot", label, i)
        rPhot = ni("rPhot", label, i)
        wimport(w, r.RooRealVar(nPhot, nPhot, nPhotValue))
        wimport(w, r.RooRealVar(rPhot, rPhot, (mcGjetValue/mcZinvValue if not rFinal else rFinal)/purity))

        rho = ni("rhoPhotZ", systematicsLabel)
        photExp = ni("photExp", label, i)
        wimport(w, r.RooFormulaVar(photExp, "(@0)*(@1)*(@2)",
                                   r.RooArgList(w.var(rho), w.var(rPhot), w.function(ni("zInv", label, i)))
                                   )
                )

        photPois = ni("photPois", label, i)
        wimport(w, r.RooPoisson(photPois, photPois, w.var(nPhot), w.function(photExp)))
        terms.append(photPois)

    photTermsName = ni("photTerms", label)
    w.factory("PROD::%s(%s)"%(photTermsName, ",".join(terms)))

    out["terms"].append(photTermsName)
    out["multiBinObs"].append(ni("nPhot", label))
    return out

def muonTerms(w = None, inputData = None, label = "", systematicsLabel = "", kQcdLabel = "", smOnly = None) :
    terms = []
    out = collections.defaultdict(list)

    if label==systematicsLabel :
        rho = ni("rhoMuonW", label)
        one = ni("oneMuonW", label)
        sigma = ni("sigmaMuonW", label)
        gaus = ni("muonGaus", label)
        wimport(w, r.RooRealVar(rho, rho, 1.0, 0.0, 2.0))
        wimport(w, r.RooRealVar(one, one, 1.0))
        wimport(w, r.RooRealVar(sigma, sigma, inputData.fixedParameters()["sigmaMuonW"]))
        wimport(w, r.RooGaussian(gaus, gaus, w.var(one), w.var(rho), w.var(sigma)))
        terms.append(gaus)
        out["obs"].append(one)
        out["nuis"].append(rho)

    rFinal = None
    for i,nMuonValue,mcMuonValue,mcTtwValue,stopHere in zip(range(len(inputData.observations()["nMuon"])),
                                                            inputData.observations()["nMuon"],
                                                            inputData.mcExpectations()["mcMuon"],
                                                            inputData.mcExpectations()["mcTtw"],
                                                            inputData.constantMcRatioAfterHere(),
                                                            ) :
        if nMuonValue==None : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcMuon"][i:])/sum(inputData.mcExpectations()["mcTtw"][i:])
        nMuon = ni("nMuon", label, i)
        rMuon = ni("rMuon", label, i)
        wimport(w, r.RooRealVar(nMuon, nMuon, nMuonValue))
        wimport(w, r.RooRealVar(rMuon, rMuon, mcMuonValue/mcTtwValue if not rFinal else rFinal))

        muonB = ni("muonB", label, i)
        rhoMuonW = ni("rhoMuonW", systematicsLabel)
        wimport(w, r.RooFormulaVar(muonB, "(@0)*(@1)*(@2)",
                                   r.RooArgList(w.var(rhoMuonW), w.var(rMuon), w.function(ni("ttw", label, i)))
                                   )
                )

        muonPois = ni("muonPois", label, i)
        if smOnly :
            wimport(w, r.RooPoisson(muonPois, muonPois, w.var(nMuon), w.function(muonB)))
        else :
            muonS = ni("muonS", label, i)
            muonExp = ni("muonExp", label, i)
            lumi = ni("muonLumi", label)
            eff = ni("signalEffMuon", label, i)
            rhoSignal = ni("rhoSignal", systematicsLabel)
            wimport(w, r.RooProduct(muonS, muonS, r.RooArgSet(w.var("f"), w.var(rhoSignal), w.var("xs"), w.var(lumi), w.var(eff))))
            wimport(w, r.RooAddition(muonExp, muonExp, r.RooArgSet(w.function(muonB), w.function(muonS))))
            wimport(w, r.RooPoisson(muonPois, muonPois, w.var(nMuon), w.function(muonExp)))
        terms.append(muonPois)

    muonTermsName = ni("muonTerms", label)
    w.factory("PROD::%s(%s)"%(muonTermsName, ",".join(terms)))

    out["terms"].append(muonTermsName)
    out["multiBinObs"].append(ni("nMuon", label))
    return out

def qcdTerms(w = None, inputData = None, label = "", systematicsLabel = "", kQcdLabel = "", smOnly = None) :
    out = collections.defaultdict(list)

    if label!=kQcdLabel : return out

    k_qcd_nom = ni("k_qcd_nom", label)
    k_qcd_unc_inp = ni("k_qcd_unc_inp", label)
    k_qcd = ni("k_qcd", label)
    A_qcd = ni("A_qcd", label)
    qcdGaus = ni("qcdGaus", label)
    qcdTerms = ni("qcdTerms", label)

    wimport(w, r.RooRealVar(k_qcd_nom, k_qcd_nom, inputData.fixedParameters()["k_qcd_nom"]))
    wimport(w, r.RooRealVar(k_qcd_unc_inp, k_qcd_unc_inp, inputData.fixedParameters()["k_qcd_unc_inp"]))
    wimport(w, r.RooGaussian(qcdGaus, qcdGaus, w.var(k_qcd_nom), w.var(k_qcd), w.var(k_qcd_unc_inp)))
    w.var(A_qcd).setVal(1.0e-2)
    w.var(k_qcd).setVal(inputData.fixedParameters()["k_qcd_nom"])
    w.factory("PROD::%s(%s)"%(qcdTerms, qcdGaus))

    out["terms"].append(qcdTerms)
    out["obs"].append(k_qcd_nom)
    out["nuis"].append(k_qcd_unc_inp)
    return out

def signalTerms(w = None, inputData = None, label = "", systematicsLabel = "", kQcdLabel = "", smOnly = None, #kQcdLabel,smOnly not used
                signalDict = {}, extraSigEffUncSources = [], rhoSignalMin = None) :

    for item in ["had", "muon"] :
        lumi = ni(item+"Lumi", label = label)
        wimport(w, r.RooRealVar(lumi, lumi, inputData.lumi()[item]))
    
    for key,value in signalDict.iteritems() :
        if "eff"!=key[:3] : continue
        if type(value) not in [list,tuple] : continue
        for iBin,eff,corr in zip(range(len(value)), value, inputData.sigEffCorr()) :
            name = ni(name = "signal%s"%(key.replace("eff","Eff")), label = label, i = iBin)
            wimport(w, r.RooRealVar(name, name, eff*corr))

    out = collections.defaultdict(list)
    if label==systematicsLabel :
        deltaSignalValue = utils.quadSum([inputData.fixedParameters()["sigmaLumiLike"]]+[signalDict[item] for item in extraSigEffUncSources])
        one = ni("oneRhoSignal", label)
        rho = ni("rhoSignal", label)
        delta = ni("deltaSignal", label)
        gaus = ni("signalGaus", label)

        wimport(w, r.RooRealVar(one, one, 1.0))
        wimport(w, r.RooRealVar(rho, rho, 1.0, rhoSignalMin, 2.0))
        wimport(w, r.RooRealVar(delta, delta, deltaSignalValue))
        wimport(w, r.RooGaussian(gaus, gaus, w.var(one), w.var(rho), w.var(delta)))

        signalTermsName = ni("signalTerms", label)
        w.factory("PROD::%s(%s)"%(signalTermsName, gaus))
        out["terms"].append(signalTermsName)
        out["obs"].append(one)
        out["nuis"].append(rho)
    return out

def multi(w, variables, inputData) :
    out = []
    bins = range(len(inputData.observations()["nHad"]))
    for item in variables :
        for i in bins :
            name = ni(name = item, i = i)
            if not w.var(name) :
                print "multi:",name
                continue
            out.append(name)
    return out

def varOrFunc(w = None, name = "", label = "", i = None) :
    s = ni(name, label, i)
    return w.var(s) if w.var(s) else w.function(s)

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def setupLikelihood(w = None, selection = None, systematicsLabel = None, kQcdLabel = None, smOnly = None, extraSigEffUncSources = [], rhoSignalMin = 0.0,
                    REwk = None, RQcd = None, nFZinv = None, qcdSearch = None, constrainQcdSlope = None, signalDict = {}, simpleOneBin = {}) :

    variables = {"terms": [],
                 "obs": [],
                 "nuis": [],
                 "multiBinObs": [],
                 "multiBinNuis": [],
                 }

    samples = selection.samplesAndSignalEff.keys()

    if simpleOneBin :
        assert False
        simpleOneBinTerm(varDict = simpleOneBin, **args)
        variables["terms"].append("simpleOneBinTerm")
        variables["multiBinObs"].append("nHad")

    boxes = ["had", "phot", "muon", "mumu"]
    items = [] if smOnly else ["signal"]
    items += boxes
    if constrainQcdSlope : items.append("qcd")

    args = {}
    for item in items :
        args[item] = {}
        args[item]["inputData"] = selection.data
        args[item]["label"] = selection.name
        for x in ["w", "systematicsLabel", "kQcdLabel", "smOnly"] :
            args[item][x] = eval(x)

    for x in ["REwk", "RQcd", "nFZinv", "qcdSearch"] :
        args["had"][x] = eval(x)

    if "signal" in args :
        for x in ["signalDict", "extraSigEffUncSources", "rhoSignalMin"] :
            args["signal"][x] = eval(x)

    for item in ["muon", "phot", "mumu"] :
        if item in samples :
            variables["multiBinNuis"] += [ni("fZinv", args[item]["label"])]
            break

    for item in items :
        if (item in boxes) and (item not in selection.data.lumi()) : continue
        func = eval("%sTerms"%item)
        d = func(**(args[item]))
        if (item in boxes) and (item not in samples) : continue
        for key in variables : #include terms, obs, etc. in likelihood
            variables[key] += d[key]

    out = {}
    for item in ["terms", "obs", "nuis"] : out[item] = variables[item]
    out["obs"]  += multi(w, variables["multiBinObs"], selection.data)
    out["nuis"] += multi(w, variables["multiBinNuis"], selection.data)
    return out

def startLikelihood(w = None, signal = {}) :
    wimport(w, r.RooRealVar("xs", "xs", signal["xs"]))
    wimport(w, r.RooRealVar("f", "f", 1.0, 0.0, 2.0))

def finishLikelihood(w = None, smOnly = None, qcdSearch = None, terms = [], obs = [], nuis = []) :
    w.factory("PROD::model(%s)"%",".join(terms))

    if not smOnly :
        w.defineSet("poi", "f")
    elif qcdSearch :
        w.defineSet("poi", "A_qcd,k_qcd")

    w.defineSet("obs", ",".join(obs))
    w.defineSet("nuis", ",".join(nuis))

class foo(object) :
    def __init__(self, likelihoodSpec = {}, extraSigEffUncSources = [], rhoSignalMin = 0.0,
                 signal = {}, signalExampleToStack = {}, trace = False) :
                 
        for item in ["likelihoodSpec", "extraSigEffUncSources", "rhoSignalMin", "signal", "signalExampleToStack"] :
            setattr(self, item, eval(item))

        self.checkInputs()
        r.gROOT.SetBatch(True)
        r.RooRandom.randomGenerator().SetSeed(1)

        self.wspace = r.RooWorkspace("Workspace")

        args = {}
        args["w"] = self.wspace
        args["smOnly"] = self.smOnly()
        args.update(self.likelihoodSpec)
        del args["selections"]#pass only local slice info

        for item in ["extraSigEffUncSources", "rhoSignalMin"] :
            args[item] = getattr(self, item)

        print "fix signal format"
        if not self.smOnly() :
            startLikelihood(w = self.wspace, signal = self.signal[self.signal.keys()[0]])

        total = collections.defaultdict(list)
        for sel in self.likelihoodSpec["selections"] :
            args["selection"] = sel
            args["signalDict"] = self.signal[sel.name] if sel.name in self.signal else {}
            args["systematicsLabel"] = self.systematicsLabel(sel.name)
            args["kQcdLabel"] = self.kQcdLabel(sel.name)
            d = setupLikelihood(**args)
            for key,value in d.iteritems() :
                total[key] += value
        finishLikelihood(w = self.wspace, smOnly = self.smOnly(), qcdSearch = self.likelihoodSpec["qcdSearch"], **total)

        self.data = dataset(obs(self.wspace))
        self.modelConfig = modelConfiguration(self.wspace, self.smOnly(), self.likelihoodSpec["qcdSearch"])

        if trace :
            #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
            #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
            r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    def checkInputs(self) :
        l = self.likelihoodSpec
        assert l["REwk"] in ["", "FallingExp", "Linear", "Constant"]
        assert l["RQcd"] in ["FallingExp", "FallingExpA", "Zero"]
        assert l["nFZinv"] in ["One", "Two", "All"]
        if l["simpleOneBin"] : 
            for item in ["hadTerms", "muonTerms", "photTerms", "mumuTerms"] :
                assert not l[item]
        if l["qcdSearch"] :
            assert self.smOnly()
            assert "FallingExp" in l["RQcd"]
        if l["constrainQcdSlope"] :
            assert l["RQcd"] == "FallingExp","%s!=FallingExp"%l["RQcd"]
        if any([sel.universalKQcd for sel in l["selections"]]) :
            assert "FallingExp" in l["RQcd"]
        for sel in l["selections"] :
            assert sel.samplesAndSignalEff,sel.name
            bins = sel.data.htBinLowerEdges()
            for dct in [self.signal, self.signalExampleToStack] :
                if sel.name not in dct : continue
                for key,value in dct[sel.name].iteritems() :
                    if type(value) is list : assert len(value)==len(bins)
            
    def smOnly(self) :
        return not self.signal

    def systematicsLabel(self, name) :
        selections = self.likelihoodSpec["selections"]
        syst = [s.universalSystematics for s in selections]
        assert sum(syst)<2
        if any(syst) : assert not syst.index(True)
        return name if sum(syst)!=1 else selections[syst.index(True)].name

    def kQcdLabel(self, name) :
        selections = self.likelihoodSpec["selections"]
        k = [s.universalKQcd for s in selections]
        assert sum(k)<2
        if any(k) : assert not k.index(True)
        return name if sum(k)!=1 else selections[k.index(True)].name

    def note(self) :
        return note(likelihoodSpec = self.likelihoodSpec)
    
    def debug(self) :
        self.wspace.Print("v")
        plotting.writeGraphVizTree(self.wspace)
        #pars = utils.rooFitResults(pdf(wspace), data).floatParsFinal(); pars.Print("v")
        utils.rooFitResults(pdf(self.wspace), self.data).Print("v")
        #wspace.Print("v")

    def profile(self) :
        calc.profilePlots(self.data, self.modelConfig, self.note(), self.smOnly(), self.likelihoodSpec["qcdSearch"])

    def interval(self, cl = 0.95, method = "profileLikelihood", makePlots = False,
                 nIterationsMax = 1, lowerItCut = 0.1, upperItCut = 0.9, itFactor = 3.0) :
        
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
        if self.likelihoodSpec["qcdSearch"] :
            return plIntervalQcd(self.data, self.modelConfig, self.wspace, self.note(), cl = cl, makePlots = makePlots)
        elif method=="profileLikelihood" :
            return plInterval(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)
        elif method=="feldmanCousins" :
            return fcExcl(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)

    def cls(self, cl = 0.95, nToys = 300, calculatorType = 0, testStatType = 3, plusMinus = {}, makePlots = False, nWorkers = 1,
            plSeed = False, plNIterationsMax = None) :
        args = {}
        out = {}
        if plSeed :
            plUpperLimit = self.interval(cl = cl, nIterationsMax = plNIterationsMax)["upperLimit"]
            out["PlUpperLimit"] = plUpperLimit

            #args["nPoints"] = 3
            #args["poiMin"] = plUpperLimit*0.5
            #args["poiMax"] = plUpperLimit*1.5
            args["nPoints"] = 7
            args["poiMin"] = plUpperLimit*0.5
            args["poiMax"] = plUpperLimit*2.0

            s = self.wspace.set("poi"); assert s.getSize()==1
            if s.first().getMin() : s.first().setMin(0.0)
            if args["poiMax"]>s.first().getMax() : s.first().setMax(args["poiMax"])
            
        out2 = cls(dataset = self.data, modelconfig = self.modelConfig, wspace = self.wspace, smOnly = self.smOnly(),
                   cl = cl, nToys = nToys, calculatorType = calculatorType, testStatType = testStatType,
                   plusMinus = plusMinus, nWorkers = nWorkers, note = self.note(), makePlots = makePlots, **args)
        out.update(out2)
        return out

    def clsCustom(self, nToys = 200, testStatType = 3) :
        return calc.clsCustom(self.wspace, self.data, nToys = nToys, testStatType = testStatType, smOnly = self.smOnly(), note = self.note())

    def pValue(self, nToys = 200) :
        calc.pValue(self.wspace, self.data, nToys = nToys, note = self.note())

    def ensemble(self, nToys = 200) :
        out = calc.ensemble(self.wspace, self.data, nToys = nToys, note = self.note())
        if out :
            results,i = out
            args = {"wspace": self.wspace, "results": results, "lumi": self.inputData.lumi(),
                    "htBinLowerEdges": self.inputData.htBinLowerEdges(), "htMaxForPlot": self.inputData.htMaxForPlot(),
                    "smOnly": self.smOnly(), "note": self.note()+"_toy%d"%i, "signalExampleToStack": self.signalExampleToStack,
                    "printPages": False, "toyNumber":i}

            for item in ["REwk", "RQcd"] : args[item] = self.likelihoodSpec[item]
                    
            plotter = plotting.validationPlotter(args)
            plotter.inputData = self.inputData
            plotter.go()

    def expectedLimit(self, cl = 0.95, nToys = 200, plusMinus = {}, makePlots = False) :
        return expectedLimit(self.data, self.modelConfig, self.wspace, smOnly = self.smOnly(), cl = cl, nToys = nToys,
                             plusMinus = plusMinus, note = self.note(), makePlots = makePlots)

    def bestFit(self, printPages = False, drawMc = True) :
        results = utils.rooFitResults(pdf(self.wspace), self.data)
        for selection in self.likelihoodSpec["selections"] :
            example = self.signalExampleToStack[selection.name] if selection.name in self.signalExampleToStack else {}
            args = {"wspace": self.wspace, "results": results,
                    "lumi": selection.data.lumi(), "htBinLowerEdges": selection.data.htBinLowerEdges(),
                    "htMaxForPlot": selection.data.htMaxForPlot(), "smOnly": self.smOnly(), "note": self.note(),
                    "signalExampleToStack": example, "label":selection.name, "systematicsLabel":self.systematicsLabel(selection.name),
                    "printPages": printPages, "drawMc": drawMc}
            for item in ["REwk", "RQcd"] :
                args[item] = self.likelihoodSpec[item]

            plotter = plotting.validationPlotter(args)
            plotter.inputData = selection.data #temporary
            plotter.go()

    def qcdPlot(self) :
        plotting.errorsPlot(self.wspace, utils.rooFitResults(pdf(self.wspace), self.data))
