#!/usr/bin/env python

import ROOT as r

r.RooRandom.randomGenerator().SetSeed(1)

def wimport(wspace, name = None, value = None, lower = None, upper = None) :
    assert name and value!=None
    assert (lower==None==upper) or (lower!=None!=upper)
    if lower==upper==None : getattr(wspace, "import")(r.RooRealVar(name, name, value))
    else :                  getattr(wspace, "import")(r.RooRealVar(name, name, value, lower, upper))

def observables() :
    return {
        "nSel": 13, 
        "nPhot": 7,
        "tauNom":6.5/4.1,
        }

def fixedParameters() :
    return {"sigmaPhot": 0.4}

def importVarsAndDefineSets(wspace) :

    #fit parameters
    nSel = observables()["nSel"]
    for comp in ["Zinv","s"] :
        wimport(wspace = wspace, name = comp, value = 0.5*nSel, lower = 1.0e-2, upper = 5*nSel)

    #(nuisance)
    tauNom = observables()["tauNom"]
    wimport(wspace = wspace, name = "tau", value = tauNom, lower = 0.0, upper = 5*tauNom)

    #observations
    for key,value in observables().iteritems() :
        wimport(wspace = wspace, name = key, value = value)

    #fixed parameters
    for key,value in fixedParameters().iteritems() :
        wimport(wspace = wspace, name = key, value = value)

    #sets
    wspace.defineSet("poi","s")
    #wspace.defineSet("nuis","tau")
    wspace.defineSet("obs", "nSel,nPhot,tauNom")

def modelConfiguration(w) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(w.pdf("model"))
    modelConfig.SetParametersOfInterest(w.set("poi"))
    #modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def dataset(obsSet) :
    out = r.RooDataSet("dataName","title", obsSet)
    out.add(obsSet)
    #out.Print("v")
    return out

def setupLikelihood(w) :
    w.factory("Poisson::pHadr(nSel,sum::bPlusS(Zinv,s))")
    w.factory("Poisson::pPhot(nPhot,prod::tauZ(tau,Zinv))")
    w.factory("Gaussian::gTau(tauNom,tau,prod::tauSigma(tauNom,sigmaPhot))")
    w.factory("PROD::model(pHadr,pPhot,gTau)")

def computeInterval(dataset, modelconfig) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()
    print "UpperLimit=",plInt.UpperLimit(wspace.var("s"))

wspace = r.RooWorkspace("Workspace")
importVarsAndDefineSets(wspace)
data = dataset(wspace.set("obs"))
setupLikelihood(wspace)
modelConfig = modelConfiguration(wspace)
computeInterval(data, modelConfig)
