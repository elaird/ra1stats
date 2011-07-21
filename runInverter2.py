##from http://root.cern.ch/root/html/tutorials/roostats/StandardHypoTestInvDemo.C.html
##
##    type = 0 Freq calculator 
##    type = 1 Hybrid 
##
##    testStatType = 0 LEP
##                 = 1 Tevatron 
##                 = 2 Profile Likelihood
##                 = 3 Profile Likelihood one sided (i.e. = 0 if mu < mu_hat)
##
##    useCLs          scan for CLs (otherwise for CLs+b)    
##
##    npoints:        number of points to scan , for autoscan set npoints = -1 
##
##    poimin,poimax:  min/max value to scan in case of fixed scans 
##                    (if min >= max, try to find automatically)                           
##
##    ntoys:         number of toys to use 
##
##    extra options are available as global paramters of the macro. They are: 
##

import ROOT as r

def RunInverter(w = None, modelSBName = "", modelBName = "",
                dataName = "", type = None, testStatType = None, 
                npoints = None, poimin = None, poimax = None, 
                ntoys = 1000, useCls = True, CL = 0.95, 
                nworkers = 1, optimize = False, debug = False, initialFit = True) :

    if debug : w.Print()

    data = w.data(dataName)
    assert data, "Dataset %s does not exist."%dataName
    if debug : print "Using dataset '%s'"%dataName

    bModel, sbModel = buildModels(w = w, modelBName = modelBName, modelSBName = modelSBName, debug = debug)
    testStat = testStatistic(bModel = bModel, sbModel = bModel, testStatType = testStatType, optimize = optimize)
    calc = calculator(data = data, bModel = bModel, sbModel = sbModel,
                      type = type, testStat = testStat, ntoys = ntoys, optimize = optimize, initialFit = initialFit)

    tester = r.RooStats.HypoTestInverter(calc)
    tester.SetConfidenceLevel(CL)
    tester.UseCLs(useCls)
    tester.SetVerbose(True)
    
    if nworkers>1 : calc.GetTestStatSampler().SetProofConfig(r.RooStats.ProofConfig(w, nworkers, "", r.kFALSE))
    if npoints>=1 :
        if debug : print "Doing a fixed scan  in interval : %g , %g"%(poimin, poimax)
        tester.SetFixedScan(npoints, poimin, poimax)
    else :
        if debug : print "Doing an  automatic scan  in interval : %g , %g"%(poi.getMin(), poi.getMax())
    return tester.GetInterval()

def buildModels(w = None, modelBName = None, modelSBName = None, debug = None) :
    bModel = w.obj(modelBName)
    sbModel = w.obj(modelSBName)

    assert sbModel, "ModelConfig '%s' does not exist."%modelSBName
    assert sbModel.GetPdf(), "Model '%s' has no pdf."%modelSBName
    assert sbModel.GetParametersOfInterest(), "Model %s has no poi."%modelSBName
    if not sbModel.GetSnapshot() :
        if debug : print "Model '%s' has no snapshot.  Make one using model POI:"%modelSBName
        sbModel.SetSnapshot(sbModel.GetParametersOfInterest())
        if debug : sbModel.GetSnapshot().Print("v")

    if (not bModel) or (bModel==sbModel) :
        if debug :
            print "The background model '%s' does not exist"%modelBName
            print "Copy it from ModelConfig '%s' and set POI to zero:"%modelSBName

        bModel = sbModel.Clone()
        bModel.SetName(modelSBName+"_with_poi_0")
        assert bModel.GetParametersOfInterest().getSize()==1,"bModel.GetParametersOfInterest().getSize()=%d"%bModel.GetParametersOfInterest().getSize()
        var = bModel.GetParametersOfInterest().first()
        assert var
        oldval = var.getVal()
        var.setVal(0)
        bModel.SetSnapshot(r.RooArgSet(var))
        var.setVal(oldval)
        if debug : bModel.GetSnapshot().Print("v")
    elif not bModel.GetSnapshot() :
        if debug : print "Model '%s' has no snapshot.  Make one using model POI set to 0:"%modelBName
        assert bModel.GetParametersOfInterest().getSize()==1,"bModel.GetParametersOfInterest().getSize()=%d"%bModel.GetParametersOfInterest().getSize()
        var = bModel.GetParametersOfInterest().first()
        assert var, "Model '%s' has no valid POI."%modelBName
        oldval = var.getVal()
        var.setVal(0)
        bModel.SetSnapshot(r.RooArgSet(var))
        var.setVal(oldval)
        if debug : bModel.GetSnapshot().Print("v")
    return bModel,sbModel

def testStatistic(bModel = None, sbModel = None, testStatType = None, optimize = None) :    
    slrts = r.RooStats.SimpleLikelihoodRatioTestStat(sbModel.GetPdf(), bModel.GetPdf())
    slrts.SetNullParameters(sbModel.GetSnapshot())
    slrts.SetAltParameters(bModel.GetSnapshot())

    # ratio of profile likelihood - need to pass snapshot for the alt
    ropl = r.RooStats.RatioOfProfiledLikelihoodsTestStat(sbModel.GetPdf(), bModel.GetPdf(), bModel.GetSnapshot())
    ropl.SetSubtractMLE(False)
   
    profll = r.RooStats.ProfileLikelihoodTestStat(sbModel.GetPdf())
    if (testStatType == 3) : profll.SetOneSided(1)
    if optimize : profll.SetReuseNLL(True)

    testStat = slrts
    if (testStatType == 1) : testStat = ropl
    if (testStatType == 2 or testStatType == 3) : testStat = profll
    if testStatType == 4 :
        assert False, "NumEventsTestStat is not implemented."
        testStat = r.RooStats.NumEventsTestStat(sbModel.GetPdf())
    return testStat

def calculator(data = None, bModel = None, sbModel = None, type = None, testStat = None, ntoys = None, optimize = None, initialFit = None) :
    if type==0 : hc = r.RooStats.FrequentistCalculator(data, bModel, sbModel)
    else       : hc = r.RooStats.HybridCalculator(data, bModel, sbModel)
    
    toymcs = hc.GetTestStatSampler()
    toymcs.SetNEventsPerToy(1)
    toymcs.SetTestStatistic(testStat)
    if optimize : toymcs.SetUseMultiGen(true)

    if (type == 1) :
        hc.SetToys(ntoys,ntoys)

        # check for nuisance prior pdf 
        if (bModel.GetPriorPdf() and sbModel.GetPriorPdf()) :
            hc.ForcePriorNuisanceAlt(bModel.GetPriorPdf())
            hc.ForcePriorNuisanceNull(sbModel.GetPriorPdf())
        else :
            assert not (bModel.GetNuisanceParameters() or sbModel.GetNuisanceParameters()),\
                   "Cannnot run Hybrid calculator because no prior on the nuisance parameter is specified."

    else : 
        hc.SetToys(ntoys,ntoys)

    # Get the result
    r.RooMsgService.instance().getStream(1).removeTopic(r.RooFit.NumIntegration)

    if initialFit :
        poi = sbModel.GetParametersOfInterest().first()
        sbModel.GetPdf().fitTo(data)
        poihat = poi.getVal()

    return hc
