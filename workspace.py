import collections,math
import utils,plotting,calc
from common import obs,pdf,note
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
                     
def parametrizedExp(w = None, sample = "", i = None) :
    return r.RooFormulaVar(ni(name = sample, i = i), "(@0)*(@1)*exp(-(@2)*(@3))",
                           r.RooArgList(w.var(ni(name = "nHadBulk", i = i)), w.var("A_%s"%sample), w.var("k_%s"%sample), w.var(ni(name = "htMean", i = i)))
                           )
    
def parametrizedExpA(w = None, sample = "", i = None) :
    return r.RooFormulaVar(ni(name = sample, i = i), "(@0)*exp((@1)-(@2)*(@3))",
                           r.RooArgList(w.var(ni(name = "nHadBulk", i = i)), w.var("A_%s"%sample), w.var("k_%s"%sample), w.var(ni(name = "htMean", i = i)))
                           )
    
def parametrizedLinearEwk(w = None, ewk = "", i = None, iLast = None) :
    return r.RooFormulaVar(ni(name = ewk, i = i), "(@0)*(@1)*(1 + (@2)*((@3)-(@4))/((@5)-(@4)))",
                           r.RooArgList(w.var(ni(name = "nHadBulk", i = i)), w.var("A_%s"%ewk), w.var("k_%s"%ewk),
                                        w.var(ni(name = "htMean", i = i)), w.var(ni(name = "htMean", i = 0)), w.var(ni(name = "htMean", i = iLast))
                                        )
                           )

def importEwk(w = None, REwk = None, name = "", i = None, iLast = None, nHadValue = None, A_ini = None) :
    A = "A_%s"%name
    k = "k_%s"%name

    if REwk and not i :
        wimport(w, r.RooRealVar(A, A, A_ini, 0.0, 1.0))
        wimport(w, r.RooRealVar(k, k, 0.0,  -1.0, 1.0))
    if REwk=="Constant" and not i :
        w.var(k).setVal(0.0)
        w.var(k).setConstant()
    
    if REwk=="Linear" : wimport(w, parametrizedLinearEwk(w = w, ewk = name, i = i, iLast = iLast))
    elif (REwk=="FallingExp" or  REwk=="Constant") : wimport(w, parametrizedExp(w = w, sample = name, i = i))
    else : wimport(w, r.RooRealVar(ni(name = name, i = i), ni(name = name, i = i), max(1, nHadValue), 0.0, 10.0*max(1, nHadValue)))
    return varOrFunc(w, name, i)

def importFZinv(w = None, nFZinv = "", name = "", i = None, iLast = None) :
    first = ni(name = name, i = 0)
    this  = ni(name = name, i = i)
    last  = ni(name = name, i = iLast)
    
    if nFZinv=="All" :
        wimport(w, r.RooRealVar(this, this, 0.5, 0.2, 0.8))
    elif nFZinv=="One" :
        if not i : wimport(w, r.RooRealVar(this, this, 0.5, 0.0, 1.0))
        else     : wimport(w, r.RooFormulaVar(this, "(@0)", r.RooArgList(w.var(first))))
    elif nFZinv=="Two" :
        if not i :
            wimport(w, r.RooRealVar(this, this, 0.5, 0.0, 1.0))
            wimport(w, r.RooRealVar(last, last, 0.5, 0.0, 1.0))
        elif i!=iLast :
            argList = r.RooArgList(w.var(first), w.var(last),
                                   w.var(ni(name = "htMean", i = i    )),
                                   w.var(ni(name = "htMean", i = 0    )),
                                   w.var(ni(name = "htMean", i = iLast))
                                   )
            wimport(w, r.RooFormulaVar(this, "(@0)+((@2)-(@3))*((@1)-(@0))/((@4)-(@3))", argList))
    return varOrFunc(w, name, i)

def ni(name = "", label = "", i = None) :
    out = name
    if label : out += "_%s"%label
    if i!=None : out +="%d"%i
    return out

def hadTerms(w = None, inputData = None, REwk = None, RQcd = None, nFZinv = None, smOnly = None, label = "", qcdSearch = None) :
    obs = inputData.observations()
    trg = inputData.triggerEfficiencies()
    htMeans = inputData.htMeans()
    terms = []

    assert not qcdSearch
    assert RQcd!="FallingExpA"

    #QCD variables
    A = ni(name = "A_qcd", label = label); wimport(w, r.RooRealVar(A, A, 1.5e-5, 0.0, 100.0))
    k = ni(name = "k_qcd", label = label); wimport(w, r.RooRealVar(k, k, 1.0e-5, 0.0,   1.0))

    #inital values
    A_ewk_ini = 1.3e-5
    if RQcd=="Zero" :
        w.var(A).setVal(0.0)
        w.var(A).setConstant()
        w.var(k).setVal(0.0)
        w.var(k).setConstant()
    else :
        #as in past
        factor = 0.7
        w.var(k).setVal( initialkQcd(inputData, factor, A_ewk_ini) )
        w.var(A).setVal( initialAQcd(inputData, factor, A_ewk_ini, w.var(k).getVal()) )

    #observed "constants", not depending upon slice
    for i,htMeanValue,nHadBulkValue,hadTrgEffValue in zip(range(len(htMeans)), htMeans, obs["nHadBulk"], trg["had"]) :
        m = ni(name = "htMean", i = i)
        if not w.var(m) : wimport(w, r.RooRealVar(m, m, htMeanValue))
        b = ni(name = "nHadBulk", i = i)
        if not w.var(b) : wimport(w, r.RooRealVar(b, b, nHadBulkValue*hadTrgEffValue))

    #more
    iLast = len(htMeans)-1
    for i,nHadValue in enumerate(obs["nHad"]) :
        qcdName = ni(name = "qcd", label = label)
        if RQcd=="FallingExpA" : wimport(w, parametrizedExpA(w = w, sample = qcdName, i = i))
        else :                   wimport(w, parametrizedExp (w = w, sample = qcdName, i = i))
        qcd = w.function(ni(name = qcdName, i = i))
        
        ewk   = importEwk(  w = w, REwk   = REwk,   name = ni(name = "ewk",   label = label), i = i, iLast = iLast, nHadValue = nHadValue, A_ini = A_ewk_ini)
        fZinv = importFZinv(w = w, nFZinv = nFZinv, name = ni(name = "fZinv", label = label), i = i, iLast = iLast)

        wimport(w, r.RooFormulaVar(ni(name = "zInv", label = label, i = i), "(@0)*(@1)",       r.RooArgList(ewk, fZinv)))
        wimport(w, r.RooFormulaVar(ni(name = "ttw",  label = label, i = i), "(@0)*(1.0-(@1))", r.RooArgList(ewk, fZinv)))

        hadB    = ni(name = "hadB",    label = label, i = i)
        hadS    = ni(name = "hadS",    label = label, i = i)
        nHad    = ni(name = "nHad",    label = label, i = i)
        hadPois = ni(name = "hadPois", label = label, i = i)
        hadExp  = ni(name = "hadExp",  label = label, i = i)
        
        wimport(w, r.RooFormulaVar(hadB, "(@0)+(@1)", r.RooArgList(ewk, qcd)))
        wimport(w, r.RooRealVar(nHad, nHad, nHadValue))
        if smOnly :
            wimport(w, r.RooPoisson(hadPois, hadPois, w.var(nHad), w.function(hadB)))
        else :
            wimport(w, r.RooProduct(hadS, hadS, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("hadLumi"), w.var("signalEffHad%d"%i))))
            wimport(w, r.RooAddition(hadExp, hadExp, r.RooArgSet(w.function(hadB), w.function(hadS))))
            wimport(w, r.RooPoisson(hadPois, hadPois, w.var(nHad), w.function(hadExp)))
        terms.append(hadPois)

    w.factory("PROD::%s(%s)"%(ni(name = "hadTerms", label = label), ",".join(terms)))

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

def mumuTerms(w = None, inputData = None, label = "", smOnly = None) :
    terms = []
    wimport(w, r.RooRealVar("rhoMumuZ", "rhoMumuZ", 1.0, 1.0e-3, 3.0))
    wimport(w, r.RooRealVar("oneMumu", "oneMumu", 1.0))
    wimport(w, r.RooRealVar("sigmaMumuZ", "sigmaMumuZ", inputData.fixedParameters()["sigmaMumuZ"]))
    wimport(w, r.RooGaussian("mumuGaus", "mumuGaus", w.var("oneMumu"), w.var("rhoMumuZ"), w.var("sigmaMumuZ")))
    terms.append("mumuGaus")

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
        wimport(w, r.RooRealVar("nMumu%d"%i, "nMumu%d"%i, nMumuValue))
        wimport(w, r.RooRealVar("rMumu%d"%i, "rMumu%d"%i, (mcZmumuValue/mcZinvValue if not rFinal else rFinal)/purity))
        wimport(w, r.RooFormulaVar("mumuExp%d"%i, "(@0)*(@1)*(@2)",
                                   r.RooArgList(w.var("rhoMumuZ"), w.var("rMumu%d"%i), w.function(ni(name = "zInv", i = i)))
                                   ))
        wimport(w, r.RooPoisson("mumuPois%d"%i, "mumuPois%d"%i, w.var("nMumu%d"%i), w.function("mumuExp%d"%i)))
        terms.append("mumuPois%d"%i)
    
    w.factory("PROD::mumuTerms(%s)"%",".join(terms))

def photTerms(w = None, inputData = None, label = "", smOnly = None) :
    terms = []
    wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 1.0e-3, 3.0))
    wimport(w, r.RooRealVar("onePhot", "onePhot", 1.0))
    wimport(w, r.RooRealVar("sigmaPhotZ", "sigmaPhotZ", inputData.fixedParameters()["sigmaPhotZ"]))
    wimport(w, r.RooGaussian("photGaus", "photGaus", w.var("onePhot"), w.var("rhoPhotZ"), w.var("sigmaPhotZ")))
    terms.append("photGaus")

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
        wimport(w, r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue))
        wimport(w, r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, (mcGjetValue/mcZinvValue if not rFinal else rFinal)/purity))
        wimport(w, r.RooFormulaVar("photExp%d"%i, "(@0)*(@1)*(@2)",
                                   r.RooArgList(w.var("rhoPhotZ"), w.var("rPhot%d"%i), w.function(ni(name = "zInv", i = i)))
                                   ))
        wimport(w, r.RooPoisson("photPois%d"%i, "photPois%d"%i, w.var("nPhot%d"%i), w.function("photExp%d"%i)))
        terms.append("photPois%d"%i)
    
    w.factory("PROD::photTerms(%s)"%",".join(terms))

def muonTerms(w = None, inputData = None, label = "", smOnly = None) :
    terms = []
    wimport(w, r.RooRealVar("rhoMuonW", "rhoMuonW", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("oneMuon", "oneMuon", 1.0))
    wimport(w, r.RooRealVar("sigmaMuonW", "sigmaMuonW", inputData.fixedParameters()["sigmaMuonW"]))
    wimport(w, r.RooGaussian("muonGaus", "muonGaus", w.var("oneMuon"), w.var("rhoMuonW"), w.var("sigmaMuonW")))
    terms.append("muonGaus")

    rFinal = None
    for i,nMuonValue,mcMuonValue,mcTtwValue,stopHere in zip(range(len(inputData.observations()["nMuon"])),
                                                            inputData.observations()["nMuon"],
                                                            inputData.mcExpectations()["mcMuon"],
                                                            inputData.mcExpectations()["mcTtw"],
                                                            inputData.constantMcRatioAfterHere(),
                                                            ) :
        if nMuonValue==None : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcMuon"][i:])/sum(inputData.mcExpectations()["mcTtw"][i:])
        wimport(w, r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue))
        wimport(w, r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue if not rFinal else rFinal))
        wimport(w, r.RooFormulaVar("muonB%d"%i, "(@0)*(@1)*(@2)",
                                   r.RooArgList(w.var("rhoMuonW"), w.var("rMuon%d"%i), w.function(ni(name = "ttw", i = i)))
                                   ))
        if smOnly :
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonB%d"%i)))
        else :
            wimport(w, r.RooProduct("muonS%d"%i, "muonS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("muonLumi"), w.var("signalEffMuon%d"%i))))
            wimport(w, r.RooAddition("muonExp%d"%i, "muonExp%d"%i, r.RooArgSet(w.function("muonB%d"%i), w.function("muonS%d"%i))))
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonExp%d"%i)))
        
        terms.append("muonPois%d"%i)
    
    w.factory("PROD::muonTerms(%s)"%",".join(terms))

def qcdTerms(w = None, inputData = None, label = "", smOnly = None) :
    k_qcd_nom = ni(name = "k_qcd_nom", label = label)
    k_qcd_unc_inp = ni(name = "k_qcd_unc_inp", label = label)
    k_qcd = ni(name = "k_qcd", label = label)
    A_qcd = ni(name = "A_qcd", label = label)
    qcdGaus = ni(name = "qcdGaus", label = label)
    qcdTerms = ni(name = "qcdTerms", label = label)

    wimport(w, r.RooRealVar(k_qcd_nom, k_qcd_nom, inputData.fixedParameters()["k_qcd_nom"]))
    wimport(w, r.RooRealVar(k_qcd_unc_inp, k_qcd_unc_inp, inputData.fixedParameters()["k_qcd_unc_inp"]))
    wimport(w, r.RooGaussian(qcdGaus, qcdGaus, w.var(k_qcd_nom), w.var(k_qcd), w.var(k_qcd_unc_inp)))
    w.var(A_qcd).setVal(1.0e-2)
    w.var(k_qcd).setVal(inputData.fixedParameters()["k_qcd_nom"])
    w.factory("PROD::%s(%s)"%(qcdTerms, qcdGaus))

def signalTerms(w = None, inputData = None, label = "", smOnly = None, #smOnly not used
                signalDict = {}, extraSigEffUncSources = [], rhoSignalMin = None) :
    wimport(w, r.RooRealVar("xs", "xs", signalDict["xs"]))
    wimport(w, r.RooRealVar("f", "f", 1.0, 0.0, 2.0))
    
    for item in ["had", "muon"] :
        lumi = ni(item+"Lumi", label = label)
        wimport(w, r.RooRealVar(lumi, lumi, inputData.lumi()[item]))
    
    wimport(w, r.RooRealVar("oneRhoSignal", "oneRhoSignal", 1.0))
    wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0, rhoSignalMin, 2.0))
    deltaSignal = utils.quadSum([inputData.fixedParameters()["sigmaLumiLike"]]+[signalDict[item] for item in extraSigEffUncSources])
    wimport(w, r.RooRealVar("deltaSignal", "deltaSignal", deltaSignal))
    wimport(w, r.RooGaussian("signalGaus", "signalGaus", w.var("oneRhoSignal"), w.var("rhoSignal"), w.var("deltaSignal")))

    for key,value in signalDict.iteritems() :
        if "eff"!=key[:3] : continue
        if type(value) not in [list,tuple] : continue
        for iBin,eff,corr in zip(range(len(value)), value, inputData.sigEffCorr()) :
            name = ni(name = "signal%s"%(key.replace("eff","Eff")), label = label, i = iBin)
            wimport(w, r.RooRealVar(name, name, eff*corr))

    w.factory("PROD::signalTerms(%s)"%",".join(["signalGaus"]))

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

def varOrFunc(w = None, name = "", i = None) :
    s = ni(name = name, i = i)
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

def setupLikelihood(wspace = None, selection = None, smOnly = None, extraSigEffUncSources = [], rhoSignalMin = 0.0,
                    REwk = None, RQcd = None, nFZinv = None, qcdSearch = None, constrainQcdSlope = None, signalDict = {}, simpleOneBin = {}) :

    terms = []
    obs = []
    nuis = []
    multiBinObs = []
    multiBinNuis = []

    w = wspace
    samples = selection.samplesAndSignalEff.keys()
    inputData = selection.data
    label = selection.name

    args = {}
    for item in ["w", "inputData", "label", "smOnly"] :
        args[item] = eval(item)

    hadArgs = {}
    for item in ["REwk", "RQcd", "nFZinv", "qcdSearch"] :
        hadArgs[item] = eval(item)
    hadArgs.update(args)

    sigArgs = {}
    for item in ["signalDict", "extraSigEffUncSources", "rhoSignalMin"] :
        sigArgs[item] = eval(item)
    sigArgs.update(args)

    if not smOnly :
        signalTerms(**sigArgs)
        terms.append("signalTerms")
        obs.append("oneRhoSignal")
        nuis.append("rhoSignal")

    if simpleOneBin :
        simpleOneBinTerm(varDict = simpleOneBin, **args)
        terms.append("simpleOneBinTerm")
        multiBinObs.append("nHad")
    else :
        if "FallingExp" in RQcd :
            nuis += [ni("k_qcd", label)]
            if not qcdSearch : nuis += [ni("A_qcd", label)]
        if REwk :
            nuis += [ni("A_ewk", label)]
            if REwk!="Constant" :
                nuis += [ni("k_ewk", label)]

        for item in ["muon", "phot", "mumu"] :
            if item in samples :
                multiBinNuis += [ni("fZinv", label)]
                break

        hadTerms(**hadArgs)
        photTerms(**args)
        muonTerms(**args)
        if "mumu" in inputData.lumi() :
            mumuTerms(**args)
        if constrainQcdSlope :
            qcdTerms(**args)
            terms.append(ni("qcdTerms", label))
            obs.append(ni("k_qcd_nom", label))
            nuis.append(ni("k_qcd_unc_inp", label))
        
    if "had" in samples :
        terms.append(ni(name = "hadTerms", label = label))
        multiBinObs.append(ni(name = "nHad", label = label))

    if "phot" in samples :
        terms.append("photTerms")
        obs.append("onePhot")
        multiBinObs.append("nPhot")
        nuis.append("rhoPhotZ")
        
    if "muon" in samples :
        terms.append("muonTerms")
        obs.append("oneMuon")
        multiBinObs.append("nMuon")
        nuis.append("rhoMuonW")
        
    if "mumu" in samples :
        terms.append("mumuTerms")
        obs.append("oneMumu")
        multiBinObs.append("nMumu")
        nuis.append("rhoMumuZ")

    obs += multi(w, multiBinObs, inputData)
    nuis += multi(w, multiBinNuis, inputData)

    out = {}
    for item in ["terms", "obs", "nuis"] :
        out[item] = eval(item)
    return out

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
        args["smOnly"] = self.smOnly()
        args.update(self.likelihoodSpec)
        del args["selections"]#pass only local slice info

        for item in ["wspace", "extraSigEffUncSources", "rhoSignalMin"] :
            args[item] = getattr(self, item)

        assert len(self.likelihoodSpec["selections"])==1, "Multiple selections not yet supported."

        total = collections.defaultdict(list)
        for sel in self.likelihoodSpec["selections"] :
            args["selection"] = sel
            args["signalDict"] = self.signal[sel.name] if sel.name in self.signal else {}
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
        
        for sel in l["selections"] :
            bins = sel.data.htBinLowerEdges()
            for dct in [self.signal, self.signalExampleToStack] :
                if sel.name not in dct : continue
                for key,value in dct[sel.name].iteritems() :
                    if type(value) is list : assert len(value)==len(bins)
            
    def smOnly(self) :
        return not self.signal

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
        for selection in self.likelihoodSpec["selections"] :
            example = self.signalExampleToStack[selection.name] if selection.name in self.signalExampleToStack else {}
            args = {"wspace": self.wspace, "results": utils.rooFitResults(pdf(self.wspace), self.data),
                    "lumi": selection.data.lumi(), "htBinLowerEdges": selection.data.htBinLowerEdges(),
                    "htMaxForPlot": selection.data.htMaxForPlot(), "smOnly": self.smOnly(), "note": self.note(),
                    "signalExampleToStack": example, "printPages": printPages, "drawMc": drawMc}
            for item in ["REwk", "RQcd"] :
                args[item] = self.likelihoodSpec[item]

            plotter = plotting.validationPlotter(args)
            plotter.inputData = selection.data #temporary
            plotter.go()

    def qcdPlot(self) :
        plotting.errorsPlot(self.wspace, utils.rooFitResults(pdf(self.wspace), self.data))
