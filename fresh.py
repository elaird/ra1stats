import math,array,copy,collections
import utils
import plotting as plotting
import ROOT as r
from runInverter import RunInverter

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
                     
def initialkQcdControl(inputData, label) :
    obs = inputData.observations()
    out = float(obs["nHadControl%s"%label][0]*obs["nHadBulk"][1])/float(obs["nHadControl%s"%label][1]*obs["nHadBulk"][0])
    out = math.log(out)
    htMeans = inputData.htMeans()    
    out /= (htMeans[1] - htMeans[0])
    return out

def initialAQcdControl(inputData, label) :
    obs = inputData.observations()
    htMeans = inputData.htMeans()
    out = math.exp( initialkQcdControl(inputData, label)*htMeans[0] )
    out *= (obs["nHadControl%s"%label][0]/float(obs["nHadBulk"][0]))
    return out

def parametrizedExp(w = None, sample = "", i = None) :
    return r.RooFormulaVar("%s%d"%(sample, i), "(@0)*(@1)*exp(-(@2)*(@3))",
                           r.RooArgList(w.var("nHadBulk%d"%i), w.var("A_%s"%sample), w.var("k_%s"%sample), w.var("htMean%d"%i)))
    
def parametrizedExpA(w = None, sample = "", i = None) :
    return r.RooFormulaVar("%s%d"%(sample, i), "(@0)*exp((@1)-(@2)*(@3))",
                           r.RooArgList(w.var("nHadBulk%d"%i), w.var("A_%s"%sample), w.var("k_%s"%sample), w.var("htMean%d"%i)))
    
def parametrizedLinearEwk(w = None, ewk = "", i = None, iLast = None) :
    return r.RooFormulaVar("%s%d"%(ewk, i), "(@0)*(@1)*(1 + (@2)*((@3)-(@4))/((@5)-(@4)))",
                           r.RooArgList(w.var("nHadBulk%d"%i), w.var("A_%s"%ewk), w.var("d_%s"%ewk),
                                        w.var("htMean%d"%i), w.var("htMean0"), w.var("htMean%d"%iLast)))

def importEwk(w = None, REwk = None, name = "", i = None, iLast = None, nHadValue = None, A_ini = None) :
    if REwk and not i :
        wimport(w, r.RooRealVar("A_%s"%name, "A_%s"%name, A_ini, 0.0, 1.0))
        wimport(w, r.RooRealVar("k_%s"%name, "k_%s"%name, 0.0,  -1.0, 1.0))
    if REwk=="Constant" and not i :
        w.var("k_%s"%name).setVal(0.0)
        w.var("k_%s"%name).setConstant()
    
    if REwk=="Linear" : wimport(w, parametrizedLinearEwk(w = w, ewk = name, i = i, iLast = iLast))
    elif (REwk=="Exp" or  REwk=="Constant") : wimport(w, parametrizedExp(w = w, sample = name, i = i))
    else : wimport(w, r.RooRealVar("%s%d"%(name, i), "%s%d"%(name, i), 0.5*max(1, nHadValue), 0.0, 10.0*max(1, nHadValue)))
    return varOrFunc(w, name, i)

def importFZinv(w = None, nFZinv = "", name = "", i = None, iLast = None) :
    if nFZinv=="All" :
        wimport(w, r.RooRealVar("%s%d"%(name, i), "%s%d"%(name, i), 0.5, 0.2, 0.8))
    elif nFZinv=="One" :
        if not i : wimport(w, r.RooRealVar("%s%d"%(name, i), "%s%d"%(name, i), 0.5, 0.0, 1.0))
        else     : wimport(w, r.RooFormulaVar("%s%d"%(name, i), "(@0)", r.RooArgList(w.var("%s0"%name))))
    elif nFZinv=="Two" :
        if not i :
            wimport(w, r.RooRealVar("%s%d"%(name, i),     "%s%d"%(name, i),     0.5, 0.0, 1.0))
            wimport(w, r.RooRealVar("%s%d"%(name, iLast), "%s%d"%(name, iLast), 0.5, 0.0, 1.0))
        elif i!=iLast :
            argList = r.RooArgList(w.var("%s%d"%(name, 0)), w.var("%s%d"%(name, iLast)), w.var("htMean%d"%i), w.var("htMean0"), w.var("htMean%d"%iLast))
            wimport(w, r.RooFormulaVar("%s%d"%(name, i), "(@0)+((@2)-(@3))*((@1)-(@0))/((@4)-(@3))", argList))
    return varOrFunc(w, name, i)

def varOrFunc(w = None, name = "", i = None) :
    return w.var("%s%d"%(name, i)) if w.var("%s%d"%(name, i)) else w.function("%s%d"%(name, i))

def hadTerms(w, inputData, REwk, RQcd, nFZinv, smOnly, qcdSearch, hadControlSamples = []) :
    obs = inputData.observations()
    trg = inputData.triggerEfficiencies()
    htMeans = inputData.htMeans()
    terms = []

    A_ewk_ini = 1.3e-5
    if not qcdSearch :
        if RQcd=="FallingExpA" :
            wimport(w, r.RooRealVar("A_qcd", "A_qcd", math.log(1.5e-5), -20.0, math.log(100.0)))
        else :
            wimport(w, r.RooRealVar("A_qcd", "A_qcd", 1.5e-5, 0.0, 100.0))
            #wimport(w, r.RooRealVar("A_qcd", "A_qcd", 1.5e-5, -100.0, 100.0))
        wimport(w, r.RooRealVar("k_qcd", "k_qcd", 1.0e-5, 0.0,   1.0))
        #wimport(w, r.RooRealVar("k_qcd", "k_qcd", 1.0e-5, -1.0,   1.0))
    else :
        if RQcd=="FallingExpA" :
            wimport(w, r.RooRealVar("A_qcd", "A_qcd", math.log(1.5e-5), -20.0, math.log(2.0)))
        else :
            wimport(w, r.RooRealVar("A_qcd", "A_qcd", 1.5e-5, 0.0, 5.0))
        #wimport(w, r.RooRealVar("k_qcd", "k_qcd", 1.0e-5, 0.0, 1.0))
        #wimport(w, r.RooRealVar("k_qcd", "k_qcd", 4.7e-2, 3.7e-2, 5.7e-2))
        wimport(w, r.RooRealVar("k_qcd", "k_qcd", 4.7e-2, 4.5e-2, 4.9e-2))
        #wimport(w, r.RooRealVar("k_qcd", "k_qcd", 4.7e-2, 3.5e-2, 4.9e-2))
    
    if RQcd=="Zero" :
        w.var("A_qcd").setVal(0.0)
        w.var("A_qcd").setConstant()
        w.var("k_qcd").setVal(0.0)
        w.var("k_qcd").setConstant()
    else :
        factor = 0.7
        if not hadControlSamples :
            w.var("k_qcd").setVal(initialkQcd(inputData, factor, A_ewk_ini))
        else :
            w.var("k_qcd").setVal(initialkQcdControl(inputData, "_"+hadControlSamples[0]))
        value = initialAQcd(inputData, factor, A_ewk_ini, w.var("k_qcd").getVal())
        w.var("A_qcd").setVal(value if RQcd=="FallingExp" else math.log(value))

    for i,htMeanValue,nHadBulkValue,hadTrgEffValue in zip(range(len(htMeans)), htMeans, obs["nHadBulk"], trg["had"]) :
        wimport(w, r.RooRealVar("htMean%d"%i, "htMean%d"%i, htMeanValue))
        wimport(w, r.RooRealVar("nHadBulk%d"%i, "nHadBulk%d" %i, nHadBulkValue*hadTrgEffValue))

    iLast = len(htMeans)-1
    for i,nHadValue in enumerate(obs["nHad"]) :
        if RQcd=="FallingExpA" : wimport(w, parametrizedExpA(w = w, sample = "qcd", i = i))            
        else :                   wimport(w, parametrizedExp (w = w, sample = "qcd", i = i))
        
        ewk = importEwk(w = w, REwk = REwk, name = "ewk", i = i, iLast = iLast, nHadValue = nHadValue, A_ini = A_ewk_ini)
        fZinv = importFZinv(w = w, nFZinv = nFZinv, name = "fZinv", i = i, iLast = iLast)

        wimport(w, r.RooFormulaVar("zInv%d"%i, "(@0)*(@1)",       r.RooArgList(ewk, fZinv)))
        wimport(w, r.RooFormulaVar("ttw%d"%i,  "(@0)*(1.0-(@1))", r.RooArgList(ewk, fZinv)))

        wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)", r.RooArgList(ewk, w.function("qcd%d"%i))))
        wimport(w, r.RooRealVar("nHad%d"%i, "nHad%d"%i, nHadValue))
        if smOnly :
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadB%d"%i)))
        else :
            wimport(w, r.RooProduct("hadS%d"%i, "hadS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("hadLumi"), w.var("signalEffHad%d"%i))))
            wimport(w, r.RooAddition("hadExp%d"%i, "hadExp%d"%i, r.RooArgSet(w.function("hadB%d"%i), w.function("hadS%d"%i))))
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadExp%d"%i)))
        terms.append("hadPois%d"%i)
    
    w.factory("PROD::hadTerms(%s)"%",".join(terms))

def simpleOneBinTerm(w, inputData, smOnly, varDict) :
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

def hadControlTerms(w, inputData, REwk, RQcd, smOnly, label = "") :
    def s(i = None) : return ("_%s%s"%(label, "_%d"%i if i!=None else ""))
    obs = inputData.observations()
    htMeans = inputData.htMeans()
    terms = []

    assert (REwk and ("FallingExp" in RQcd))
    wimport(w, r.RooRealVar("A_qcdControl%s"%s(), "A_qcdControl%s"%s(), initialAQcdControl(inputData, s()), 0.0, 100.0))
    wimport(w, r.RooRealVar("A_ewkControl%s"%s(), "A_ewkControl%s"%s(), 10.0e-6, 0.0, 1.0))
    wimport(w, r.RooRealVar("d_ewkControl%s"%s(), "d_ewkControl%s"%s(), 0.0, -1.0, 1.0))
    w.var("d_ewkControl%s"%s()).setVal(0.0)
    w.var("d_ewkControl%s"%s()).setConstant()

    for i,htMeanValue,nHadBulkValue,nControlValue in zip(range(len(htMeans)), htMeans, obs["nHadBulk"], obs["nHadControl%s"%s()]) :
        wimport(w, r.RooFormulaVar("qcdControl%s"%s(i), "(@0)*(@1)*exp(-(@2)*(@3))",
                                   r.RooArgList(w.var("nHadBulk%d"%i), w.var("A_qcdControl%s"%s()), w.var("k_qcd"), w.var("htMean%d"%i))))

        wimport(w, parametrizedLinearEwk(w = w, ewk = "ewkControl", i = i, iLast = iLast))
        wimport(w, r.RooFormulaVar("hadControlB%s"%s(i), "(@0)+(@1)", r.RooArgList(w.function("ewkControl%s"%s(i)), w.function("qcdControl%s"%s(i)))))
        wimport(w, r.RooRealVar("nHadControl%s"%s(i), "nHadControl%s"%s(i), nControlValue))
        if smOnly :
            wimport(w, r.RooPoisson("hadControlPois%s"%s(i), "hadControlPois%s"%s(i), w.var("nHadControl%s"%s(i)), w.function("hadControlB%s"%s(i))))
        else :
            wimport(w, r.RooPoisson("hadControlPois%s"%s(i), "hadControlPois%s"%s(i), w.var("nHadControl%s"%s(i)), w.function("hadControlB%s"%s(i))))            
        terms.append("hadControlPois%s"%s(i))
    
    w.factory("PROD::hadControlTerms%s(%s)"%(s(), ",".join(terms)))

def mumuTerms(w, inputData) :
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
        if nMumuValue<0 : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcZmumu"][i:])/sum(inputData.mcExpectations()["mcZinv"][i:])
        wimport(w, r.RooRealVar("nMumu%d"%i, "nMumu%d"%i, nMumuValue))
        wimport(w, r.RooRealVar("rMumu%d"%i, "rMumu%d"%i, (mcZmumuValue/mcZinvValue if not rFinal else rFinal)/purity))
        wimport(w, r.RooFormulaVar("mumuExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMumuZ"), w.var("rMumu%d"%i), w.function("zInv%d"%i))))
        wimport(w, r.RooPoisson("mumuPois%d"%i, "mumuPois%d"%i, w.var("nMumu%d"%i), w.function("mumuExp%d"%i)))
        terms.append("mumuPois%d"%i)
    
    w.factory("PROD::mumuTerms(%s)"%",".join(terms))

def photTerms(w, inputData) :
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
        if nPhotValue<0 : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcGjets"][i:])/sum(inputData.mcExpectations()["mcZinv"][i:])
        wimport(w, r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue))
        wimport(w, r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, (mcGjetValue/mcZinvValue if not rFinal else rFinal)/purity))
        wimport(w, r.RooFormulaVar("photExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoPhotZ"), w.var("rPhot%d"%i), w.function("zInv%d"%i))))
        wimport(w, r.RooPoisson("photPois%d"%i, "photPois%d"%i, w.var("nPhot%d"%i), w.function("photExp%d"%i)))
        terms.append("photPois%d"%i)
    
    w.factory("PROD::photTerms(%s)"%",".join(terms))

def muonTerms(w, inputData, smOnly) :
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
        if nMuonValue<0 : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcMuon"][i:])/sum(inputData.mcExpectations()["mcTtw"][i:])
        wimport(w, r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue))
        wimport(w, r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue if not rFinal else rFinal))
        wimport(w, r.RooFormulaVar("muonB%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMuonW"), w.var("rMuon%d"%i), w.function("ttw%d"%i))))

        if smOnly :
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonB%d"%i)))
        else :
            wimport(w, r.RooProduct("muonS%d"%i, "muonS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("muonLumi"), w.var("signalEffMuon%d"%i))))
            wimport(w, r.RooAddition("muonExp%d"%i, "muonExp%d"%i, r.RooArgSet(w.function("muonB%d"%i), w.function("muonS%d"%i))))
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonExp%d"%i)))
        
        terms.append("muonPois%d"%i)
    
    w.factory("PROD::muonTerms(%s)"%",".join(terms))

def signalTerms(w, inputData, signalDict) :
    wimport(w, r.RooRealVar("hadLumi", "hadLumi", inputData.lumi()["had"]))
    wimport(w, r.RooRealVar("muonLumi", "muonLumi", inputData.lumi()["muon"]))
    wimport(w, r.RooRealVar("xs", "xs", signalDict["xs"]))
    wimport(w, r.RooRealVar("f", "f", 1.0, 0.0, 2.0))

    wimport(w, r.RooRealVar("oneRhoSignal", "oneRhoSignal", 1.0))
    #wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0))
    wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0, 0.0, 2.0))
    #wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0, 0.8, 1.2))
    wimport(w, r.RooRealVar("deltaSignal", "deltaSignal", inputData.fixedParameters()["sigmaLumiLike"]))
    wimport(w, r.RooGaussian("signalGaus", "signalGaus", w.var("oneRhoSignal"), w.var("rhoSignal"), w.var("deltaSignal")))

    for key,value in signalDict.iteritems() :
        if key=="xs" : continue
        if "NLO_over_LO" in key : continue
        for iBin,eff,corr in zip(range(len(value)), value, inputData.sigEffCorr()) :
            name = "signal%s%d"%(key.replace("eff","Eff"), iBin)
            wimport(w, r.RooRealVar(name, name, eff*corr))

    w.factory("PROD::signalTerms(%s)"%",".join(["signalGaus"]))

def multi(w, variables, inputData) :
    out = []
    bins = range(len(inputData.observations()["nHad"]))
    for item in variables :
        for i in bins :
            if item.count("_") < 2 : name = "%s%d"%(item,i)
            else : name = "%s_%d"%(item,i)
            if not w.var(name) : continue
            out.append(name)
    return out

def setupLikelihood(wspace = None, inputData = None, REwk = None, RQcd = None, nFZinv = None,
                    qcdSearch = None, signal = {}, smOnly = None, simpleOneBin = {},
                    includeHadTerms = None, hadControlSamples = [],
                    includeMuonTerms = None, includePhotTerms = None, includeMumuTerms = None) :
    terms = []
    obs = []
    nuis = []
    multiBinObs = []
    multiBinNuis = []

    w = wspace

    if not smOnly :
        signalTerms(w, inputData, signal)
        terms.append("signalTerms")
        obs.append("oneRhoSignal")
        nuis.append("rhoSignal")

    if simpleOneBin :
        simpleOneBinTerm(w, inputData, smOnly, simpleOneBin)
        terms.append("simpleOneBinTerm")
        multiBinObs.append("nHad")
    else :
        if "FallingExp" in RQcd :
            nuis += ["k_qcd"]
            if not qcdSearch : nuis += ["A_qcd"]
        if REwk :
            nuis += ["A_ewk"]
            if REwk!="Constant" :
                nuis += ["k_ewk"]
        if includeMuonTerms or includePhotTerms or includeMumuTerms :
            multiBinNuis += ["fZinv"]

        hadTerms(w, inputData, REwk, RQcd, nFZinv, smOnly, qcdSearch, hadControlSamples)
        photTerms(w, inputData)
        muonTerms(w, inputData, smOnly)
        mumuTerms(w, inputData)
        
    if includeHadTerms :
        terms.append("hadTerms")
        multiBinObs.append("nHad")

    for item in hadControlSamples :
        hadControlTerms(w, inputData, REwk, RQcd, smOnly, item)
        terms.append("hadControlTerms_%s"%item)
        multiBinObs.append("nHadControl_%s"%item)

    if includePhotTerms :
        terms.append("photTerms")
        obs.append("onePhot")
        multiBinObs.append("nPhot")
        nuis.append("rhoPhotZ")
        
    if includeMuonTerms :
        terms.append("muonTerms")
        obs.append("oneMuon")
        multiBinObs.append("nMuon")
        nuis.append("rhoMuonW")
        
    if includeMumuTerms :
        terms.append("mumuTerms")
        obs.append("oneMumu")
        multiBinObs.append("nMumu")
        nuis.append("rhoMumuZ")
        
    w.factory("PROD::model(%s)"%",".join(terms))

    if not smOnly :
        w.defineSet("poi", "f")
    elif qcdSearch :
        w.defineSet("poi", "A_qcd,k_qcd")

    obs += multi(w, multiBinObs, inputData)
    nuis += multi(w, multiBinNuis, inputData)
    w.defineSet("obs", ",".join(obs))
    w.defineSet("nuis", ",".join(nuis))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out

def plInterval(dataset, modelconfig, wspace, note, smOnly, cl = None, makePlots = True) :
    assert not smOnly
    out = {}
    calc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()
    out["upperLimit"] = lInt.UpperLimit(wspace.var("f"))
    out["lowerLimit"] = lInt.LowerLimit(wspace.var("f"))

    if makePlots :
        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        psFile = "intervalPlot_%s_%g.ps"%(note, 100*cl)
        plot = r.RooStats.LikelihoodIntervalPlot(lInt)
        plot.Draw(); print
        canvas.Print(psFile)
        utils.ps2pdf(psFile)

    utils.delete(lInt)
    return out

def plIntervalQcd(dataset, modelconfig, wspace, note, cl = None, makePlots = True) :
    out = {}
    calc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()
    out["upperLimit"] = lInt.UpperLimit(wspace.var("A_qcd"))
    out["lowerLimit"] = lInt.LowerLimit(wspace.var("A_qcd"))

    lInt.Print()
    if makePlots :
        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        psFile = "intervalPlot_%s_%g.ps"%(note, 100*cl)
        plot = r.RooStats.LikelihoodIntervalPlot(lInt)
        plot.Draw(); print
        canvas.Print(psFile)
        utils.ps2pdf(psFile)

    utils.delete(lInt)
    return out

def fcExcl(dataset, modelconfig, wspace, note, smOnly, cl = None, makePlots = True) :
    assert not smOnly

    f = r.RooRealVar("f", "f", 1.0)
    poiValues = r.RooDataSet("poiValues", "poiValues", r.RooArgSet(f))
    r.SetOwnership(poiValues, False) #so that ~FeldmanCousins() can delete it
    points = [1.0]
    for point in [0.0] + points :
        f.setVal(point)
        poiValues.add(r.RooArgSet(f))
        
    out = {}
    calc = r.RooStats.FeldmanCousins(dataset, modelconfig)
    calc.SetPOIPointsToTest(poiValues)
    calc.FluctuateNumDataEntries(False)
    calc.UseAdaptiveSampling(True)
    #calc.AdditionalNToysFactor(4)
    #calc.SetNBins(40)
    #calc.GetTestStatSampler().SetProofConfig(r.RooStats.ProofConfig(wspace, 1, "workers=4", False))
    
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()

    out["upperLimit"] = lInt.UpperLimit(wspace.var("f"))
    return out

def ts1(wspace = None, data = None, snapSb = None, snapB = None, snapfHat = None, verbose = False) :
        wspace.loadSnapshot(snapSb)
        nll = pdf(wspace).createNLL(data)
        sbLl = -nll.getVal()
        utils.delete(nll)
        
        wspace.loadSnapshot(snapB)
        nll = pdf(wspace).createNLL(data)
        bLl = -nll.getVal()
        utils.delete(nll)

        return -2.0*(sbLl-bLl)

def ts10(wspace = None, data = None, snapSb = None, snapB = None, snapfHat = None, verbose = False) :
        wspace.loadSnapshot(snapSb)
        results = utils.rooFitResults(pdf(wspace), data)
        if verbose :
            print "S+B"
            print "---"            
            results.Print("v")
        sbLl = -results.minNll()
        utils.delete(results)
        
        wspace.loadSnapshot(snapB)
        results = utils.rooFitResults(pdf(wspace), data)
        if verbose :
            print " B "
            print "---"            
            results.Print("v")        
        bLl = -results.minNll()
        utils.delete(results)

        out = -2.0*(sbLl-bLl)
        if verbose : print "TS:",out
        return out

def ts4(wspace = None, data = None, snapSb = None, snapB = None, snapfHat = None, verbose = False) :
        wspace.loadSnapshot(snapB)
        nll = pdf(wspace).createNLL(data)
        bLl = -nll.getVal()
        utils.delete(nll)
        return bLl

def ts40(wspace = None, data = None, snapSb = None, snapB = None, snapfHat = None, verbose = False) :
        wspace.loadSnapshot(snapB)
        results = utils.rooFitResults(pdf(wspace), data)
        if verbose :
            print " B "
            print "---"            
            results.Print("v")        
        out = -results.minNll()
        utils.delete(results)

        if verbose : print "TS:",out
        return out

def ts(testStatType = None, **args) :
    if testStatType==1 : return ts1(**args)
    if testStatType==2 : return ts2(**args)
    if testStatType==3 : return ts3(**args)
    if testStatType==4 : return ts4(**args)

def clsCustom(wspace, data, nToys = 100, smOnly = None, testStatType = None, note = "", plots = True) :
    assert not smOnly

    toys = {}
    for label,f in {"b":0.0, "sb":1.0, "fHat":None}.iteritems() :
        if f!=None :
            wspace.var("f").setVal(f)
            wspace.var("f").setConstant()
        else :
            wspace.var("f").setVal(1.0)
            wspace.var("f").setConstant(False)
        results = utils.rooFitResults(pdf(wspace), data)
        wspace.saveSnapshot("snap_%s"%label, wspace.allVars())
        toys[label] = pseudoData(wspace, nToys)
        utils.delete(results)

    args = {"wspace": wspace, "testStatType": testStatType, "snapSb": "snap_sb", "snapB": "snap_b", "snapfHat": "snap_fHat"}
    obs = ts(data = data, **args)

    out = {}
    values = collections.defaultdict(list)
    for label in ["b", "sb"] :
        for toy in toys[label] : 
            values[label].append(ts(data = toy, **args))
        out["CL%s"%label] = 1.0-indexFraction(obs, values[label])
    if plots : plotting.clsCustomPlots(obs = obs, valuesDict = values, note = "TS%d_%s"%(testStatType, note))

    out["CLs"] = out["CLsb"]/out["CLb"] if out["CLb"] else 9.9
    return out

def cls(dataset = None, modelconfig = None, wspace = None, smOnly = None, cl = None, nToys = None, calculatorType = None, testStatType = None,
        plusMinus = {}, note = "", makePlots = None, nWorkers = None) :
    assert not smOnly

    npoints = 1
    poimin = 1.0
    poimax = 1.0
    
    wimport(wspace, dataset)
    wimport(wspace, modelconfig)
    result = RunInverter(w = wspace, modelSBName = "modelConfig", dataName = "dataName",
                         nworkers = nWorkers, ntoys = nToys, type = calculatorType, testStatType = testStatType,
                         npoints = npoints, poimin = poimin, poimax = poimax, debug = False)

    #r.gROOT.LoadMacro("StandardHypoTestInvDemo.C+")
    #result = r.RunInverter(wspace, "modelConfig", "", "dataName", calculatorType, testStatType, 1, 1.0, 1.0, nToys, True)

    iPoint = result.FindIndex(1.0)
    if iPoint<0 :
        print "WARNING: No index for POI value 1.0.  Will use 0."
        iPoint = 0

    out = {}
    out["CLb"] = result.CLb(iPoint)
    out["CLs+b"] = result.CLsplusb(iPoint)
    out["CLs"] = result.CLs(iPoint)
    out["CLsError"] = result.CLsError(iPoint)

    values = result.GetExpectedPValueDist(iPoint).GetSamplingDistribution()
    q,hist = quantiles(values, plusMinus, histoName = "expected_CLs_distribution",
                       histoTitle = "expected CLs distribution;CL_{s};toys / bin",
                       histoBins = (205, -1.0, 1.05), cutZero = False)

    for key,value in q.iteritems() :
        assert not (key in out),"%s %s"%(key, str(out))
        out[key] = value

    if makePlots :
        ps = "cls_%s_TS%d.ps"%(note, testStatType)
        canvas = r.TCanvas()
        canvas.Print(ps+"[")
        
        resultPlot = r.RooStats.HypoTestInverterPlot("HTI_Result_Plot", "", result)
        resultPlot.Draw("CLb 2CL")
        canvas.Print(ps)

        text = r.TText()
        text.SetNDC()

        for i in range(npoints) :
            tsPlot = resultPlot.MakeTestStatPlot(i)
            #tsPlot.SetLogYaxis(True)
            tsPlot.Draw()
        
            text.DrawText(0.1, 0.95, "Point %d"%i)
            canvas.Print(ps)

        leg = plotting.drawDecoratedHisto(quantiles = q, hist = hist, obs = out["CLs"])
        text.DrawText(0.1, 0.95, "Point %d"%iPoint)
        canvas.Print(ps)
        
        canvas.Print(ps+"]")
        utils.ps2pdf(ps)
    return out

def profilePlots(dataset, modelconfig, note, smOnly, qcdSearch) :
    assert (not smOnly) or qcdSearch

    canvas = r.TCanvas()
    canvas.SetTickx()
    canvas.SetTicky()
    psFile = "profilePlots_%s.ps"%note
    canvas.Print(psFile+"[")

    plots = r.RooStats.ProfileInspector().GetListOfProfilePlots(dataset, modelconfig); print
    for i in range(plots.GetSize()) :
        plots.At(i).Draw("al")
        canvas.Print(psFile)
    canvas.Print(psFile+"]")
    utils.ps2pdf(psFile)

def pseudoData(wspace, nToys) :
    out = []
    #make pseudo experiments with current parameter values
    dataset = pdf(wspace).generate(obs(wspace), nToys)
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        data = r.RooDataSet("pseudoData%d"%i, "title", argSet)
        data.add(argSet)
        out.append(data)
    return out

def limits(wspace, snapName, modelConfig, smOnly, cl, datasets, makePlots = False) :
    out = []
    for i,dataset in enumerate(datasets) :
        wspace.loadSnapshot(snapName)
        #dataset.Print("v")
        interval = plInterval(dataset, modelConfig, wspace, note = "", smOnly = smOnly, cl = cl, makePlots = makePlots)
        out.append(interval["upperLimit"])
    return sorted(out)

def quantiles(values = [], plusMinus = {}, histoName = "", histoTitle = "", histoBins = [], cutZero = None) :
    def histoFromList(l, name, title, bins, cutZero = False) :
        h = r.TH1D(name, title, *bins)
        for item in l :
            if cutZero and (not item) : continue
            h.Fill(item)
        return h
    
    def probList(plusMinus) :
        def lo(nSigma) : return ( 1.0-r.TMath.Erf(nSigma/math.sqrt(2.0)) )/2.0
        def hi(nSigma) : return 1.0-lo(nSigma)
        out = []
        out.append( (0.5, "Median") )
        for key,n in plusMinus.iteritems() :
            out.append( (lo(n), "MedianMinus%s"%key) )
            out.append( (hi(n), "MedianPlus%s"%key)  )
        return sorted(out)

    def oneElement(i, l) :
        return map(lambda x:x[i], l)
    
    pl = probList(plusMinus)
    probs = oneElement(0, pl)
    names = oneElement(1, pl)
    
    probSum = array.array('d', probs)
    q = array.array('d', [0.0]*len(probSum))

    h = histoFromList(values, name = histoName, title = histoTitle, bins = histoBins, cutZero = cutZero)
    h.GetQuantiles(len(probSum), q, probSum)
    return dict(zip(names, q)),h
    
def expectedLimit(dataset, modelConfig, wspace, smOnly, cl, nToys, plusMinus, note = "", makePlots = False) :
    assert not smOnly
    
    #fit to SM-only
    wspace.var("f").setVal(0.0)
    wspace.var("f").setConstant(True)
    results = utils.rooFitResults(pdf(wspace), dataset)

    #generate toys
    toys = pseudoData(wspace, nToys)

    #restore signal model
    wspace.var("f").setVal(1.0)
    wspace.var("f").setConstant(False)

    #save snapshot
    snapName = "snap"
    wspace.saveSnapshot(snapName, wspace.allVars())

    #fit toys
    l = limits(wspace, snapName, modelConfig, smOnly, cl, toys)

    q,hist = quantiles(l, plusMinus, histoName = "upperLimit", histoTitle = ";upper limit on XS factor;toys / bin", histoBins = (50, 1, -1), cutZero = True) #enable auto-range
    nSuccesses = hist.GetEntries()

    obsLimit = limits(wspace, snapName, modelConfig, smOnly, cl, [dataset])[0]

    if makePlots : plotting.expectedLimitPlots(quantiles = q, hist = hist, obsLimit = obsLimit, note = note)
    return q,nSuccesses

def indexFraction(item, l) :
    totalList = sorted(l+[item])
    i1 = totalList.index(item)
    totalList.reverse()
    i2 = len(totalList)-totalList.index(item)-1
    return (i1+i2)/2.0/len(l)

def collect(wspace, results, extraStructure = False) :
    def lMax(results) :
        #return math.exp(-results.minNll())
        return -results.minNll()

    out = {}
    out["lMax"] = lMax(results)
    funcBestFit,funcLinPropError = utils.funcCollect(wspace)
    parBestFit,parError,parMin,parMax = utils.parCollect(wspace)

    if extraStructure :
        out["funcBestFit"] = funcBestFit
        out["parBestFit"] = parBestFit
        out["parError"] = parError
        return out
    
    assert set(funcBestFit.keys()).isdisjoint(set(parBestFit.keys()))
    for d in [funcBestFit, parBestFit] :
        for key,value in d.iteritems() :
            out[key] = value
    return out

def ntupleOfFitToys(wspace = None, data = None, nToys = None, cutVar = ("",""), cutFunc = None ) :
    results = utils.rooFitResults(pdf(wspace), data)
    wspace.saveSnapshot("snap", wspace.allVars())

    obs = collect(wspace, results, extraStructure = True)

    toys = []
    for dataSet in pseudoData(wspace, nToys) :
        wspace.loadSnapshot("snap")
        #dataSet.Print("v")
        results = utils.rooFitResults(pdf(wspace), dataSet)

        if all(cutVar) and cutFunc and cutFunc(getattr(wspace,cutVar[0])(cutVar[1]).getVal()) :
            wspace.allVars().assignValueOnly(dataSet.get())
            wspace.saveSnapshot("snapA", wspace.allVars())
            return obs,results
        
        toys.append( collect(wspace, results) )
        utils.delete(results)
    return obs,toys

def pValue(wspace, data, nToys = 100, note = "", plots = True) :
    graph = r.TGraph()
    lMaxs = []

    obs,toys = ntupleOfFitToys(wspace, data, nToys)
    lMaxData = obs["lMax"]
    for i,toy in enumerate(toys) :
        lMaxs.append(toy["lMax"])
        graph.SetPoint(i, i, indexFraction(lMaxData, lMaxs))
    
    out = indexFraction(lMaxData, lMaxs)
    if plots : plotting.pValuePlots(pValue = out, lMaxData = lMaxData, lMaxs = lMaxs, graph = graph, note = note)
    return out

def ensemble(wspace, data, nToys = None, note = "", plots = True) :
    def parHistos(pars = None, shift = True) :
        histos = {}
        factor = 2.0
        for par in pars :
            mean  = obs["parBestFit"][par]
            error = obs["parError"][par]
            h = histos[par] = r.TH1D(par, par, 100, mean - factor*error, mean + factor*error)
            h.Sumw2()
            for toy in toys : h.Fill(toy[par])
        if shift : utils.shiftUnderAndOverflows(1, histos.values())
        return histos
    
    def funcHistos(funcs = None, shift = True) :
        histos = {}
        factor = 3.0
        for func in funcs :
            mean  = obs["funcBestFit"][func]
            error = math.sqrt(mean)
            h = histos[func] = r.TH1D(func, func, 100, mean - factor*error, mean + factor*error)
            h.Sumw2()
            for toy in toys : h.Fill(toy[func])
        if shift : utils.shiftUnderAndOverflows(1, histos.values())
        return histos

    def otherHistos(keys = [], shift = True) :
        histos = {}
        for key in keys :
            h = histos[key] = r.TH1D(key, key, 100, 1.0, -1.0)
            h.Sumw2()
            for toy in toys : h.Fill(toy[key])
        if shift : utils.shiftUnderAndOverflows(1, histos.values())
        return histos

    def parHistos2D(pairs = [], suffix = "") :
        histos = {}

        for pair in pairs :
            name = "_".join(pair)
            name += suffix
            title = ";".join([""]+list(pair))
            h = histos[name] = r.TH2D(name, title, 100, 1.0, -1.0, 100, 1.0, -1.0)
            h.Sumw2()
            h.SetStats(False)
            h.SetTitleOffset(1.3)
            for toy in toys : h.Fill(toy[pair[0]], toy[pair[1]])
        return histos

    obs,toys = ntupleOfFitToys(wspace, data, nToys, cutVar = ("var", "A_qcd"), cutFunc = lambda x:x>90.0); return toys

    obs,toys = ntupleOfFitToys(wspace, data, nToys)
    
    pHistos = parHistos(pars = utils.parCollect(wspace)[0].keys())
    fHistos = funcHistos(funcs = utils.funcCollect(wspace)[0].keys())
    oHistos = otherHistos(keys = ["lMax"])
    pHistos2 = parHistos2D(pairs = [("A_qcd","k_qcd"), ("A_ewk","A_qcd"), ("A_ewk","k_qcd"), ("A_ewk","fZinv0")])

    canvas = utils.numberedCanvas()
    psFileName = "ensemble_%s.ps"%note
    canvas.Print(psFileName+"[")
    plotting.cyclePlot(d = pHistos, f = plotting.histoLines, canvas = canvas, psFileName = psFileName,
                       args = {"bestColor":r.kGreen, "quantileColor":r.kRed, "bestDict":obs["parBestFit"], "errorDict":obs["parError"], "errorColor":r.kGreen})
    plotting.cyclePlot(d = fHistos, f = plotting.histoLines, canvas = canvas, psFileName = psFileName,
                       args = {"bestColor":r.kGreen, "quantileColor":r.kRed, "bestDict":obs["funcBestFit"], "errorColor":r.kGreen, "print":True})
    plotting.cyclePlot(d = oHistos, canvas = canvas, psFileName = psFileName)
    plotting.cyclePlot(d = pHistos2, canvas = canvas, psFileName = psFileName)
        
    canvas.Print(psFileName+"]")        
    utils.ps2pdf(psFileName)
    
def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def pdf(w) :
    return w.pdf("model")

def obs(w) :
    return w.set("obs")

def noteArgs() : return ["REwk", "RQcd", "nFZinv", "qcdSearch", "simpleOneBin", "hadTerms", "hadControlSamples", "muonTerms", "photTerms", "mumuTerms"]

def note(REwk = None, RQcd = None, nFZinv = None, qcdSearch = None, ignoreSignalContaminationInMuonSample = None,
         simpleOneBin = None, hadTerms = None, hadControlSamples = [], muonTerms = None, photTerms = None, mumuTerms = None) :
    out = ""
    if simpleOneBin : return "simpleOneBin"
    
    if REwk : out += "REwk%s_"%REwk
    out += "RQcd%s"%RQcd
    out += "_fZinv%s"%nFZinv
    if qcdSearch :        out += "_qcdSearch"
    if hadTerms :        out += "_had"
    if ignoreSignalContaminationInMuonSample :  out += "_ignoreMuContam"
    for item in hadControlSamples : out += "_hadControl_%s"%item
    if muonTerms :       out += "_muon"
    if photTerms :       out += "_phot"
    if mumuTerms :       out += "_mumu"
    return out

class foo(object) :
    def __init__(self, inputData = None, REwk = None, RQcd = None, nFZinv = None, qcdSearch = False, signal = {}, signalExampleToStack = ("", {}), trace = False,
                 simpleOneBin = {}, hadTerms = True, hadControlSamples = [], muonTerms = True, photTerms = True, mumuTerms = False) :
        for item in ["inputData", "REwk", "RQcd", "nFZinv", "qcdSearch", "signal", "signalExampleToStack",
                     "simpleOneBin", "hadTerms", "hadControlSamples", "muonTerms", "photTerms", "mumuTerms"] :
            setattr(self, item, eval(item))

        self.checkInputs()
        r.gROOT.SetBatch(True)
        r.RooRandom.randomGenerator().SetSeed(1)

        self.wspace = r.RooWorkspace("Workspace")

        args = {}
        for item in ["wspace", "inputData", "REwk", "RQcd", "nFZinv", "qcdSearch", "signal", "simpleOneBin", "hadControlSamples"] :
            args[item] = getattr(self, item)
        for item in ["had", "muon", "phot", "mumu"] :
            args["include%s%sTerms"%(item[0].capitalize(),item[1:])] = getattr(self,"%sTerms"%item)
        args["smOnly"] = self.smOnly()
        setupLikelihood(**args)
        
        self.data = dataset(obs(self.wspace))
        self.modelConfig = modelConfiguration(self.wspace, self.smOnly(), self.qcdSearch)

        if trace :
            #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
            #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
            r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    def checkInputs(self) :
        assert self.REwk in ["", "Exp", "Linear", "Constant"]
        assert self.RQcd in ["FallingExp", "FallingExpA", "Zero"]
        assert self.nFZinv in ["One", "Two", "All"]
        if self.simpleOneBin : 
            for item in ["hadTerms", "hadControlSamples", "muonTerms", "photTerms", "mumuTerms"] :
                assert not getattr(self,item),item
        if self.qcdSearch :
            assert self.smOnly()
            assert "FallingExp" in self.RQcd
        bins = self.inputData.htBinLowerEdges()
        for d in [self.signal, self.signalExampleToStack[1]] :
            for key,value in d.iteritems() :
                if "xs" in key : continue
                assert ("effHad" in key) or ("effMuon" in key)
                assert len(value)==len(bins)
            
    def smOnly(self) :
        return not self.signal

    def note(self) :
        d = {}
        for item in noteArgs() :
            d[item] = getattr(self, item)
        return note(**d)
    
    def debug(self) :
        self.wspace.Print("v")
        plotting.writeGraphVizTree(self.wspace)
        #pars = utils.rooFitResults(pdf(wspace), data).floatParsFinal(); pars.Print("v")
        utils.rooFitResults(pdf(self.wspace), self.data).Print("v")
        #wspace.Print("v")

    def profile(self) :
        profilePlots(self.data, self.modelConfig, self.note(), self.smOnly(), self.qcdSearch)

    def interval(self, cl = 0.95, method = "profileLikelihood", makePlots = False) :
        if self.qcdSearch :
            return plIntervalQcd(self.data, self.modelConfig, self.wspace, self.note(), cl = cl, makePlots = makePlots)
        elif method=="profileLikelihood" :
            return plInterval(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)
        elif method=="feldmanCousins" :
            return fcExcl(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)

    def cls(self, cl = 0.95, nToys = 300, calculatorType = 0, testStatType = 3, plusMinus = {}, makePlots = False, nWorkers = 1) :
        return cls(dataset = self.data, modelconfig = self.modelConfig, wspace = self.wspace, smOnly = self.smOnly(),
                   cl = cl, nToys = nToys, calculatorType = calculatorType, testStatType = testStatType,
                   plusMinus = plusMinus, nWorkers = nWorkers, note = self.note(), makePlots = makePlots)

    def clsCustom(self, nToys = 200, testStatType = 3) :
        return clsCustom(self.wspace, self.data, nToys = nToys, testStatType = testStatType, smOnly = self.smOnly(), note = self.note())

    def pValue(self, nToys = 200) :
        pValue(self.wspace, self.data, nToys = nToys, note = self.note())

    def ensemble(self, nToys = 200) :
        results = ensemble(self.wspace, self.data, nToys = nToys, note = self.note())
        if results :
            args = {"wspace": self.wspace, "results": results, "lumi": self.inputData.lumi(), "htBinLowerEdges": self.inputData.htBinLowerEdges(),
                    "htMaxForPlot": self.inputData.htMaxForPlot(), "REwk": self.REwk, "RQcd": self.RQcd, "hadControlLabels": self.hadControlSamples,
                    "mumuTerms": self.mumuTerms, "smOnly": self.smOnly(), "note": self.note(), "signalExampleToStack": self.signalExampleToStack, "printPages": False}
            plotter = plotting.validationPlotter(args)
            plotter.inputData = self.inputData
            plotter.go()

    def expectedLimit(self, cl = 0.95, nToys = 200, plusMinus = {}, makePlots = False) :
        return expectedLimit(self.data, self.modelConfig, self.wspace, smOnly = self.smOnly(), cl = cl, nToys = nToys,
                             plusMinus = plusMinus, note = self.note(), makePlots = makePlots)

    def bestFit(self, printPages = False) :
        args = {"wspace": self.wspace, "results": utils.rooFitResults(pdf(self.wspace), self.data),
                "lumi": self.inputData.lumi(), "htBinLowerEdges": self.inputData.htBinLowerEdges(),
                "htMaxForPlot": self.inputData.htMaxForPlot(), "REwk": self.REwk, "RQcd": self.RQcd,
                "hadControlLabels": self.hadControlSamples, "mumuTerms": self.mumuTerms, "smOnly": self.smOnly(), "note": self.note(),
                "signalExampleToStack": self.signalExampleToStack, "printPages": printPages}
        plotter = plotting.validationPlotter(args)
        plotter.inputData = self.inputData
        plotter.go()

    def qcdPlot(self) :
        plotting.errorsPlot(self.wspace, utils.rooFitResults(pdf(self.wspace), self.data))
