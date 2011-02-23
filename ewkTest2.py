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
        "rhoNom": 1.0,
        }

def fixedParameters() :
    return {
        "sigmaPhot": 0.4,
        "tauNom": 6.5/4.1,
        }

def importVarsAndDefineSets(wspace) :

    #fit parameters
    nSel = observables()["nSel"]
    for comp in ["Zinv","s"] :
        wimport(wspace = wspace, name = comp, value = 0.5*nSel, lower = 1.0e-2, upper = 5*nSel)

    #(nuisance)
    rhoNom = observables()["rhoNom"]
    wimport(wspace = wspace, name = "rho", value = rhoNom, lower = 0.0, upper = 5*rhoNom)

    #observations
    for key,value in observables().iteritems() :
        wimport(wspace = wspace, name = key, value = value)

    #fixed parameters
    for key,value in fixedParameters().iteritems() :
        wimport(wspace = wspace, name = key, value = value)

    #sets
    wspace.defineSet("poi","s")
    #wspace.defineSet("nuis","tau")
    wspace.defineSet("obs", "nSel,nPhot,rhoNom")

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
    w.factory("Poisson::pHadr(nSel,sum::bPlusS(prod::rhoZ(rho,Zinv),s))")
    w.factory("Poisson::pPhot(nPhot,prod::tauZ(tauNom,Zinv))")
    w.factory("Gaussian::gRho(rhoNom,rho,sigmaPhot)")
    w.factory("PROD::model(pHadr,pPhot,gRho)")

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
