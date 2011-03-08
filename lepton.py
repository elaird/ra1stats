#!/usr/bin/env python
import ROOT as r
import math,array,cPickle,os
import histogramProcessing as hp
import utils

def modelConfiguration(wspace, pdfName, modelConfigName)  :
    modelConfig = r.RooStats.ModelConfig(modelConfigName)
    modelConfig.SetWorkspace(wspace)
    modelConfig.SetPdf(wspace.pdf(pdfName))
    #modelConfig.SetPriorPdf(wspace.pdf("prior"))
    modelConfig.SetParametersOfInterest(wspace.set("poi"))
    modelConfig.SetNuisanceParameters(wspace.set("nuis"))
    getattr(wspace,"import")(modelConfig)
    return modelConfig

def constrainParams(wspace, pdfName, dataName) :
    def newMin(p) : return max(p.getVal()-10*p.getError(), p.getMin() )
    def newMax(p) : return min(p.getVal()+10*p.getError(), p.getMax() )

    wspace.pdf(pdfName).fitTo(wspace.data(dataName))
    
    nuispar = r.RooArgList(wspace.set("nuis"))
    for i in range(nuispar.getSize()) :
        par = nuispar[i]
        par.setMin( newMin(par) )
        par.setMax( newMax(par) )

   # poipar = r.RooArgList(wspace.set("poi"))
   # for i in range(poipar.getSize()) :
   #     spar = poipar[i]
   #     spar.setMin( newMin(spar) )
   #     spar.setMax( newMax(spar) )

def writeGraphVizTree(wspace, strings) :
    dotFile = "%s/%s.dot"%(strings["outputDir"], strings["pdfName"])
    wspace.pdf(strings["pdfName"]).graphVizTree(dotFile)
    cmd = "dot -Tps %s -o %s"%(dotFile, dotFile.replace(".dot", ".ps"))
    os.system(cmd)
    
def profileLikelihood(modelConfig, wspace, data, signalVar, switches) :
    plc = r.RooStats.ProfileLikelihoodCalculator(data, modelConfig)
    plc.SetConfidenceLevel(switches["CL"])
    plInt = plc.GetInterval()
    print "Profile Likelihood interval on s = [%g, %g]"%(plInt.LowerLimit(wspace.var(signalVar)), plInt.UpperLimit(wspace.var(signalVar)))
    #lrplot = r.RooStats.LikelihoodIntervalPlot(plInt)
    #lrplot.Draw();
    out = plInt.UpperLimit(wspace.var(signalVar))
    utils.delete(plInt)
    return out

def feldmanCousins(modelConfig, wspace, data, signalVar, switches) :
    fc = r.RooStats.FeldmanCousins(data, modelConfig)
    fc.SetConfidenceLevel(switches["CL"])
    fc.FluctuateNumDataEntries(False) #number counting: dataset always has 1 entry with N events observed
    fc.UseAdaptiveSampling(True)
    if "fcAdditionalNToysFactor" in switches : fc.AdditionalNToysFactor(switches["fcAdditionalNToysFactor"])
    if "fcSetNBins" in switches : fc.SetNBins(switches["fcSetNBins"])        
    if "fcUseProof" in switches and switches["fcUseProof"] :
        fc.GetTestStatSampler().SetProofConfig(r.RooStats.ProofConfig(wspace, 1, "workers=4", False))
    fcInt = fc.GetInterval()
    print "Feldman Cousins interval on s = [%g, %g]"%(fcInt.LowerLimit(wspace.var(signalVar)), fcInt.UpperLimit(wspace.var(signalVar)))
    out = fcInt.UpperLimit(wspace.var(signalVar))
    utils.delete(fcInt)
    return out

#void bayesian(RooDataSet* data, RooStats::ModelConfig* modelConfig, RooWorkspace* wspace) {
#  RooStats::BayesianCalculator bc(*data, *modelConfig);
#  bc.SetConfidenceLevel(0.95);
#  RooStats::SimpleInterval* bInt = NULL;
#  if(wspace.set("poi").getSize() == 1)   {
#    bInt = bc.GetInterval();
#  } else{
#    cout << "Bayesian Calc. only supports on parameter of interest" << endl;
#    return;
#  }
#
#  cout << "Bayesian interval on s = ["
#       << bInt.LowerLimit( ) << ", "
#       << bInt.UpperLimit( ) << "]" << endl;
#  bInt.UpperLimit( );
#}
#
#void mcmc(RooDataSet* data, RooStats::ModelConfig* modelConfig, RooWorkspace* wspace) {
#  // Want an efficient proposal function, so derive it from covariance
#  // matrix of fit
#  RooFitResult* fit = wspace.pdf("total_model").fitTo(*data, RooFit::Save());
#  RooStats::ProposalHelper ph;
#  ph.SetVariables((RooArgSet&)fit.floatParsFinal());
#  ph.SetCovMatrix(fit.covarianceMatrix());
#  ph.SetUpdateProposalParameters(kTRUE); // auto-create mean vars and add mappings
#  ph.SetCacheSize(100);
#  RooStats::ProposalFunction* pf = ph.GetProposalFunction();
#  
#  RooStats::MCMCCalculator mc(*data, *modelConfig);
#  mc.SetConfidenceLevel(0.95);
#  mc.SetProposalFunction(*pf);
#  mc.SetNumBurnInSteps(200); // first N steps to be ignored as burn-in
#  mc.SetNumIters(20000000);
#  mc.SetLeftSideTailFraction(0.5); // make a central interval
#  RooStats::MCMCInterval* mcInt = mc.GetInterval();
#
#  cout << "MCMC interval on s = ["
#       << mcInt.LowerLimit(*wspace.var("s") ) << ", "
#       << mcInt.UpperLimit(*wspace.var("s") ) << "]" << endl;
#  mcInt.UpperLimit(*wspace.var("s") );
#  //MCMC interval on s = [15.7628, 84.7266]
#}

def insert(y, name, value) :
    assert name not in y
    y[name] = value

def d_s(y, tag, twoHtBins) :
    if twoHtBins : return y["%s_1"%tag] + y["%s_2"%tag]
    else :         return y["%s_2"%tag]

#returns the relative systematic error on signal yield
def accXeff_sigma(y, switches, inputData) :
    def maxDiffRel(default, listOfVariations) :
        return max([abs(var-default) for var in listOfVariations])/default

    l = ["deadEcal_sigma","lepPhotVeto_sigma"]
    out = utils.quadSum([inputData[item] for item in l])

    #add jes/res uncertainty
    if not isSimplifiedModel(switches) :
        out = utils.quadSum([out, inputData["jesRes_sigma"]])
    else :
        default = d_s(y, "sig10", switches["twoHtBins"])
        if default<=0.0 : return out

        isr = maxDiffRel(default, [d_s(y, "isr-", switches["twoHtBins"])])
        jes = maxDiffRel(default, [d_s(y, "jes-", switches["twoHtBins"]),
                                   d_s(y, "jes+", switches["twoHtBins"])])
        insert(y, "effUncRelIsr", isr)
        insert(y, "effUncRelJes", jes)
        insert(y, "effUncExperimental", utils.quadSum([inputData["deadEcal_sigma"], inputData["lepPhotVeto_sigma"], jes]))
        insert(y, "effUncTheoretical", utils.quadSum([isr, y["effUncRelPdf"]]))
        out = utils.quadSum([out, jes, isr, y["effUncRelPdf"]])

    if not switches["nlo"] : return out

    #add scale uncertainty for k-factors and pdf uncertainty
    ds       = d_s(y, "sig10", switches["twoHtBins"])
    ds_sys05 = d_s(y, "sig05", switches["twoHtBins"])
    ds_sys2  = d_s(y, "sig20", switches["twoHtBins"])
    if ds==0.0 : return out

    return utils.quadSum([out, maxDiffRel(ds, [ds_sys05, ds_sys2]), inputData["pdfUncertainty"]])

def yields(specs, switches, inputData, m0, m12, mChi) :
    func = hp.nloYieldHisto if switches["nlo"] else hp.loYieldHisto
    out = {}
    for item in specs :
        if item=="ht" :
            for tag,dir in zip(["1", "2"],["250Dirs", "300Dirs"]) :
                histo = func(specs[item], specs[item][dir], inputData["lumi"], beforeSpec = specs["sig10"])
                if histo : out["%s_%s"%(item,tag)] = histo.GetBinContent(m0, m12, mChi)
        elif item=="effUncRelPdf" :
            histo = hp.pdfUncHisto(specs[item])
            if histo : out[item] = histo.GetBinContent(m0, m12, mChi)
        else :
            if switches["twoHtBins"] :
                for tag,dir in zip(["1", "2"],["350Dirs", "450Dirs"]) :
                    histo = func(specs[item], specs[item][dir], inputData["lumi"])
                    if histo : out["%s_%s"%(item,tag)] = histo.GetBinContent(m0, m12, mChi)
            else :
                histo = func(specs[item], specs[item]["350Dirs"] + specs[item]["450Dirs"], inputData["lumi"])
                if histo : out["%s_2"%item] = histo.GetBinContent(m0, m12, mChi)


    insert(out, "ds", d_s(out, "sig10", switches["twoHtBins"]))
    insert(out, "accXeff_sigma", accXeff_sigma(out, switches, inputData))
    return out

def setSFrac(wspace, sFrac) :
    wspace.var("BR_1").setVal(sFrac[0])
    wspace.var("BR_2").setVal(sFrac[1])
    
def setSignalVars(y, switches, specs, strings, wspace) :
    def setAndInsert(y, var, value) :
        wspace.var(var).setVal(value)
        insert(y, var, value)
        
    if y["ds"]>0.0 :
        wspace.var("accXeff_sigma").setVal(y["accXeff_sigma"])
        setAndInsert(y, "muon_cont_2", max(0.01, y["muon_2"]/y["ds"]))
        setAndInsert(y, "lowHT_cont_1", max(0.01, y["ht_1"]/y["ds"]))
        setAndInsert(y, "lowHT_cont_2", max(0.02, y["ht_2"]/y["ds"]))
        
        if switches["twoHtBins"] :
            setAndInsert(y, "BR_1", y["sig10_1"]/y["ds"])
            setAndInsert(y, "BR_2", y["sig10_2"]/y["ds"])
            setAndInsert(y, "muon_cont_1", max(0.01, y["muon_1"]/y["ds"]))

def upperLimit(modelConfig, wspace, strings, switches, dataIn = None) :
    data = wspace.data(strings["dataName"]) if not dataIn else dataIn
    func = eval(switches["method"])
    return func(modelConfig, wspace, data, strings["signalVar"], switches)

def computeExpectedLimit(modelConfig, wspace, strings, switches, lumi) :
    wspace.var(strings["signalVar"]).setVal(0.0)
    dataset = wspace.pdf(strings["pdfName"]).generate(wspace.set("obs"), switches["nToys"])
    
    h = r.TH1D("upperLimit", ";upper limit (events / %g/pb);toys / bin"%lumi, 98, 1, 50)
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        data = r.RooDataSet(strings["dataName"]+str(i),"title",argSet)
        data.add(argSet)
        if switches["debugOutput"] : data.Print("v")
        h.Fill(upperLimit(modelConfig, wspace, strings, switches, dataIn = data))

    oneSigmaFrac = r.TMath.Erf(1.0/math.sqrt(2.0)) #6.82689492137085852e-01
    twoSigmaFrac = r.TMath.Erf(2.0/math.sqrt(2.0)) #9.54499736103641583e-01

    xOne = (1.0-oneSigmaFrac)/2.0
    xTwo = (1.0-twoSigmaFrac)/2.0
    probSum = array.array('d', [xTwo, xOne, 0.5, 1.0-xOne, 1.0-xTwo])
    q = array.array('d', [0.0]*len(probSum))
    h.GetQuantiles(len(probSum), q, probSum)

    if switches["debugMedianHisto"] :
        hp.setupRoot()
        h.Draw()
        hp.printOnce(r.gPad, "expectedLimit.eps")
        print probSum
        print q
    return q
    
def writeNumbers(fileName = None, m0 = None, m12 = None, mChi = None, d = None) :
    outFile = open(fileName, "w")
    cPickle.dump([m0, m12, mChi, d], outFile)
    outFile.close()

def taus(num, den) :
    assert len(num)==len(den)
    out = array.array('d', [0.0]*len(num))
    for i in range(len(out)) :
        out[i] = num[i]/den[i]
    return out

def printStuff(y, m0, m12, mChi) :
    for key in sorted(y.keys()) :
        print key,y[key]
    print "m0",m0
    print "m12",m12
    print "mChi",mChi

def accXeff(specs, m0, m12, mChi) :
    s = specs["sig10"]
    num = hp.loYieldHisto(s, s["350Dirs"] + s["450Dirs"], lumi = 1.0) #dummy lumi; cancels in ratio
    den = hp.loYieldHisto(s, [s["beforeDir"]]           , lumi = 1.0) #dummy lumi; cancels in ratio
    num.Divide(den)
    return num.GetBinContent(m0, m12, mChi)

def isSimplifiedModel(switches) :
    return len(switches["signalModel"])==2

def xsLimitRatherThanYieldLimit(switches) :
    return isSimplifiedModel(switches)

def summed(inputData, twoHtBins) :
    if twoHtBins : return inputData
    out = {}
    for key,value in inputData.iteritems() :
        if type(value) is tuple :
            out[key] = tuple(list(value[:-2])+[value[-2]+value[-1]])
        else :
            out[key] = value
    return out

def loadLibraries(sourceFiles) :
    for file in sourceFiles :
        r.gSystem.Load(file.replace(".cxx", "_cxx.so").replace(".C", "_C.so"))

def Lepton(switches, specs, strings, inputData, m0, m12, mChi) :

    r.RooRandom.randomGenerator().SetSeed(inputData["seed"]) #set RooFit random seed for reproducible results
    wspace = r.RooWorkspace(strings["workspaceName"])
    loadLibraries(strings["sourceFiles"])
    r.AddModel(inputData["lumi"],
               inputData["lumi_sigma"],
               1.0 if switches["hardCodeAccXeffToOne"] else accXeff(specs, m0, m12, mChi),
              # accXeff(specs, m0, m12, mChi),
               inputData["_accXeff_sigma"],
               switches["masterSignalMax"],

               xsLimitRatherThanYieldLimit(switches),
               
               inputData["sigma_ttW"],
               inputData["sigma_Zinv"],
               
               inputData["lowHT_sys_1"],
               inputData["lowHT_sys_2"],
               
               inputData["_muon_cont_1"],
               inputData["_muon_cont_2"],
               
               inputData["_lowHT_cont_1"],
               inputData["_lowHT_cont_2"],
               
               switches["exponentialBkg"],
               switches["twoHtBins"],
               switches["assumeUncorrelatedLowHtSystematics"],
               
               wspace,
               strings["pdfName"],
               strings["signalVar"],
               )
    
    summedData = summed(inputData, switches["twoHtBins"])
    
    r.AddDataSideband_Combi(switches["debugOutput"],
                            array.array('d', summedData["n_htcontrol"]),
                            array.array('d', summedData["n_bar_htcontrol"]),
                            len(summedData["n_bar_htcontrol"]),
                            
                            array.array('d', summedData["n_muoncontrol"]),
                            array.array('d', summedData["n_photoncontrol"]),
                            
                            taus(summedData["mc_muoncontrol"], summedData["mc_ttW"]),
                            taus(summedData["mc_photoncontrol"], summedData["mc_Zinv"]),
                            
                            len(summedData["n_muoncontrol"]),
                            switches["twoHtBins"],
                            wspace,
                            strings["dataName"]
                            )
    
    modelConfig = modelConfiguration(wspace, strings["pdfName"], strings["modelConfigName"])

    if switches["writeWorkspaceFile"] : wspace.writeToFile(strings["outputWorkspaceFileName"])
    if switches["writeGraphVizTree"] : writeGraphVizTree(wspace, strings)
    if switches["constrainParameters"] : constrainParams(wspace, strings["pdfName"], strings["dataName"])

    if switches["hardCodedSignalContamination"] :
        setSFrac(wspace, inputData["_sFrac"])
        upperLimit(modelConfig, wspace, strings, switches)
    else :
        y = yields(specs, switches, inputData, m0, m12, mChi)
        setSignalVars(y, switches, specs, strings, wspace)
        #wspace.allVars().Print("v")
        if switches["computeExpectedLimit"] :
            dictToWrite = {}
            q = computeExpectedLimit(modelConfig, wspace, strings, switches, inputData["lumi"])
            for label,value in zip(["MedianMinusTwoSigma",
                                    "MedianMinusOneSigma",
                                    "Median",
                                    "MedianPlusOneSigma",
                                    "MedianPlusTwoSigma"], q) :
                insert(dictToWrite, label, value)
        else :
            ul = upperLimit(modelConfig, wspace, strings, switches)
            insert(y, "UpperLimit", ul)
            insert(y, "ExclusionLimit", 2*(y["ds"]<ul)-1)
            dictToWrite = y
        writeNumbers(fileName = strings["pickledFileName"], m0 = m0, m12 = m12, mChi = mChi, d = dictToWrite)
    printStuff(y, m0, m12, mChi)
