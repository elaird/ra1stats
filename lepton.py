#!/usr/bin/env python
import ROOT as r
import math,array,cPickle
import histogramProcessing as hp

def modelConfiguration(wspace, pdfName)  :
    modelConfig = r.RooStats.ModelConfig("Combine")
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

        poipar = r.RooArgList(wspace.set("poi"))
        for i in range(poipar.getSize()) :
            spar = poipar[i]
            spar.setMin( newMin(par) )
            spar.setMax( newMin(par) )

def profileLikelihood(modelConfig, wspace, dataName, signalVar) :
    plc = r.RooStats.ProfileLikelihoodCalculator(wspace.data(dataName), modelConfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()
    print "Profile Likelihood interval on s = [%g, %g]"%(plInt.LowerLimit(wspace.var(signalVar)), plInt.UpperLimit(wspace.var(signalVar)))
    #lrplot = r.RooStats.LikelihoodIntervalPlot(plInt)
    #lrplot.Draw();
    return plInt.UpperLimit(wspace.var(signalVar))

def feldmanCousins(modelConfig, wspace, dataName, signalVar) :
    fc = r.RooStats.FeldmanCousins(wspace.data(dataName), modelConfig)
    fc.SetConfidenceLevel(0.95)
    fc.FluctuateNumDataEntries(False) #number counting: dataset always has 1 entry with N events observed
    fc.UseAdaptiveSampling(True)
    fc.AdditionalNToysFactor(4)
    fc.SetNBins(40)

    fcInt = fc.GetInterval()
    print "Feldman Cousins interval on s = [%g, %g]"%(fcInt.LowerLimit(wspace.var(signalVar)), fcInt.UpperLimit(wspace.var(signalVar)))
    return fcInt.UpperLimit(wspace.var(signalVar))

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

def yields(specs, nlo, twoHtBins, lumi, m0, m12, mChi) :
    func = hp.nloYieldHisto if nlo else hp.loYieldHisto
    out = {}
    for item in specs :
        if item!="ht" :
            if twoHtBins :
                for tag,dir in zip(["1", "2"],["350Dirs", "450Dirs"]) :
                    histo = func(specs[item], specs[item][dir], lumi)
                    if histo : out["%s_%s"%(item,tag)] = histo.GetBinContent(m0, m12, mChi)
            else :
                histo = func(specs[item], specs[item]["350Dirs"] + specs[item]["450Dirs"], lumi)
                if histo : out["%s_2"%item] = histo.GetBinContent(m0, m12, mChi)

        else :
            for tag,dir in zip(["1", "2"],["250Dirs", "300Dirs"]) :
                histo = func(specs[item], specs[item][dir], lumi, beforeSpec = specs["sig10"])
                if histo : out["%s_%s"%(item,tag)] = histo.GetBinContent(m0, m12, mChi)
    return out

def setSFrac(wspace, sFrac) :
    wspace.var("BR_1").setVal(sFrac[0])
    wspace.var("BR_2").setVal(sFrac[1])
    
def setSignalVars(y, switches, specs, strings, wspace, sigma_SigEff, pdfUncertainty) :
    def d_s(y, tag, twoHtBins) :
        if twoHtBins : return y["%s_1"%tag] + y["%s_2"%tag]
        else :         return y["%s_2"%tag]

    def signalSys(init, y, twoHtBins) :
        ds       = d_s(y, "sig10", twoHtBins)
        ds_sys05 = d_s(y, "sig05", twoHtBins)
        ds_sys2  = d_s(y, "sig20", twoHtBins)
        masterPlus =  abs(max((max((ds_sys2 - ds),(ds_sys05 - ds))),0.))
        masterMinus = abs(max((max((ds - ds_sys2),(ds - ds_sys05))),0.))
        return math.sqrt( math.pow( max(masterMinus,masterPlus)/ds,2) + pow(init,2) + pow(pdfUncertainty, 2) )

    ds = d_s(y, "sig10", switches["twoHtBins"])

    if ds>0.0 :
        wspace.var("signal_sys").setVal(sigma_SigEff if not switches["nlo"] else signalSys(sigma_SigEff, y, switches["twoHtBins"]))
        wspace.var("muon_cont_2").setVal(y["muon_2"]/ds)
        wspace.var("lowHT_cont_1").setVal(y["ht_1"]/ds)
        wspace.var("lowHT_cont_2").setVal(y["ht_2"]/ds)
        
        if switches["twoHtBins"] :
            wspace.var("BR_1").setVal(y["sig10_1"]/ds)
            wspace.var("BR_2").setVal(y["sig10_2"]/ds)
            wspace.var("muon_cont_1").setVal(y["muon_1"]/ds)

    return ds

def writeNumbers(fileName = None, m0 = None, m12 = None, mChi = None, upperLimit = None, ds = None, y = None) :
    def insert(name, value) :
        assert name not in y
        y[name] = value

    insert("UpperLimit", upperLimit)
    insert("ExclusionLimit", 2*(ds<upperLimit)-1)

    outFile = open(fileName, "w")
    cPickle.dump([m0, m12, mChi, y], outFile)
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

def accXeff(switches, specs, inputData, m0, m12, mChi) :
    if len(switches["signalModel"])==2 :
        s = specs["sig10"]
        num = hp.loYieldHisto(s, s["350Dirs"] + s["450Dirs"], inputData["lumi"])
        den = hp.loYieldHisto(s, [s["beforeDir"]]           , inputData["lumi"])
        num.Divide(den)
        return num.GetBinContent(m0, m12, mChi)
    else :
        return inputData["_accXeff"]

def lumi(switches, inputData) :
    if len(switches["signalModel"])==2 :
        return inputData["lumi"]
    else :
        return 1.0

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
    wspace = r.RooWorkspace("Combine")
    loadLibraries(strings["sourceFiles"])
    r.AddModel(lumi(switches, inputData),
               inputData["_lumi_sys"],
               accXeff(switches, specs, inputData, m0, m12, mChi),
               inputData["_accXeff_sys"],
               
               inputData["sigma_ttW"],
               inputData["sigma_Zinv"],
               
               inputData["_lowHT_sys_1"],
               inputData["_lowHT_sys_2"],
               
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
    
    r.AddDataSideband_Combi(array.array('d', summedData["n_htcontrol"]),
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
    
    modelConfig = modelConfiguration(wspace, strings["pdfName"])

    if switches["writeWorkspaceFile"] : wspace.writeToFile(strings["outputWorkspaceFileName"])
    if switches["constrainParameters"] : constrainParams(wspace, strings["pdfName"], strings["dataName"])
    
    if switches["ignoreSignalContamination"] :
        y = {}
        ds = None
        setSFrac(wspace, inputData["sFrac"])
    else :
        y = yields(specs, switches["nlo"], switches["twoHtBins"], inputData["lumi"], m0, m12, mChi)
        ds = setSignalVars(y, switches, specs, strings, wspace, inputData["sigma_SigEff"], inputData["pdfUncertainty"])

    func = eval(switches["method"])
    upperLimit = func(modelConfig, wspace, strings["dataName"], strings["signalVar"])
    writeNumbers(fileName = strings["plotFileName"], m0 = m0, m12 = m12, mChi = mChi, upperLimit = upperLimit, ds = ds, y = y)
    #printStuff(y, m0, m12, mChi)
