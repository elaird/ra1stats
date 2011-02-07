#!/usr/bin/env python
import ROOT as r
import math,array,cPickle
import histogramProcessing as hp

def setupLikelihoodOneBin(wspace, switches) :
    
    def makeSignalModel() :
        splusb = "sum::splusb(%s,%s)" % ("prod::SigUnc(s,ratioSigEff[1,0.3,1.9])",
                                         "sum::b(%s)" % (','.join(["prod::ttW(ratioBkgdEff_1[1.0,0.,5.],TTplusW)",
                                                                   "prod::Zinv(ratioBkgdEff_2[1.0,0.,5.],ZINV)",
                                                                   "QCD"][:-1 if switches["fixQcdToZero"] else None])))
        wspace.factory("Poisson::signal(%s,%s)" % ("n_signal",splusb))
    
        wspace.factory("Gaussian::sigConstraint(1.,ratioSigEff,sigma_SigEff)")  # Systematic: signal acceptance*efficiency*luminosity
        wspace.factory("Gaussian::mcCons_ttW(1.,ratioBkgdEff_1,sigma_ttW)")     # Systematic:  ttw background estimate
        wspace.factory("Gaussian::mcCons_Zinv(1.,ratioBkgdEff_2,sigma_Zinv)")   # Systematic: Zinv background estimate

        wspace.factory("PROD::signal_model(%s,%s,%s,%s)" % ("signal","sigConstraint","mcCons_ttW","mcCons_Zinv"))

    def makePhotonMuonControls() :
        wspace.factory("Poisson::photoncontrol(%s,%s)" % ("n_photoncontrol",
                                                          "prod::sideband_photon(tau_photon,ZINV)"))

        wspace.factory("Poisson::muoncontrol(%s,%s)" % ("n_muoncontrol",
                                                        "sum::MuSPlusB(%s,%s)"%("prod::TTWside(tau_mu,TTplusW)",
                                                                                "prod::smu(tau_s_mu[0.001],s)") ))
    def makeQcdModel() :
        if switches["fixQcdToZero"] : return
        wspace.factory("Gaussian::xConstraint(1.,f,sigma_x)") # Systematic: uncertainty on assumption that rhoprime = rho*rho
        #likelihood for the low HT and/or low alphaT auxiliary measurements
        wspace.factory("Poisson::bar_signal(n_bar_signal,bbar)") #alphaT < 0.55 && HT > 350 GeV
        wspace.factory("Poisson::control_1(n_control_1,prod::taub(tau,b,rho))") #alphaT > 0.55 && 300 < HT < 350 GeV
        wspace.factory("Poisson::bar_control_1(n_bar_control_1,prod::taubar(tau,bbar))") #alphaT < 0.55 && 300 < HT << 350 GeV
        wspace.factory("Poisson::control_2(n_control_2,prod::taub_2(tauprime,b,prod::rhoprime(f[1.,0.,2.],rho,rho)))") #alphaT > 0.55 && 250 < HT < 300 GeV
        wspace.factory("Poisson::bar_control_2(n_bar_control_2,prod::taubar_2(tauprime,bbar))") #alphaT < 0.55 && 250 < HT < 300 GeV

        wspace.factory("PROD::QCD_model(%s)" % (','.join(["xConstraint","bar_signal",
                                                          "control_1",  "bar_control_1",
                                                          "control_2",  "bar_control_2"]) ) )
    makeSignalModel()
    makePhotonMuonControls()
    makeQcdModel()

    wspace.factory("PROD::total_model(%s)" % (','.join(["muoncontrol", "signal_model",
                                                        "photoncontrol",  "QCD_model"][:-1 if switches["fixQcdToZero"] else None])))


    observe = ["n_signal","n_muoncontrol","n_photoncontrol",
               "n_bar","n_bar_signal","n_control_1","n_bar_control_1","n_control_2","n_bar_control_2"
               ][:3 if switches["fixQcdToZero"] else None]

    nuisance = ["ratioBkgdEff_1","ratioBkgdEff_2","ratioSigEff","TTplusW","ZINV",
                "QCD"][:-1 if switches["fixQcdToZero"] else None]

    ## for bayesian methods
    #wspace.factory("Uniform::prior_nuis({%s})"%(','.join(nuisance)))
    #wspace.factory("Uniform::prior_poi({s})")
    #wspace.factory("PROD::prior(prior_poi,prior_nuis)")

    #for later use (plots)
    wspace.defineSet( "poi","s")
    wspace.defineSet( "obs",','.join(observe))
    wspace.defineSet("nuis",','.join(nuisance))
    return

def importVarsOneBin(wspace, inputData, switches, dataName) :
    for item in ["sigma_Zinv","sigma_ttW","sigma_x","sigma_SigEff"] :
        globals()[item] = inputData[item]  # maybe use a class?
        
    for item in ["n_signal",
                 "n_muoncontrol",  "mc_muoncontrol",  "mc_ttW",
                 "n_photoncontrol","mc_photoncontrol","mc_Zinv"] :
        globals()[item] = sum(inputData[item][:2]) # maybe use a class?

    tau_mu     = mc_muoncontrol   / mc_ttW    
    tau_photon = mc_photoncontrol / mc_Zinv
    
    n_control_2,     n_control_1     = inputData["n_htcontrol"][:2]
    n_bar_control_2, n_bar_control_1 = inputData["n_bar_htcontrol"][:2]
    n_bar_signal = sum(inputData["n_bar_htcontrol"][2:4])

    def wimport(name = None, value = None, lower = None, upper = None) :
        assert name and value!=None
        assert (lower==None==upper) or (lower!=None!=upper)
        if lower==upper==None : getattr(wspace, "import")(r.RooRealVar(name, name, value))
        else :                  getattr(wspace, "import")(r.RooRealVar(name, name, value, lower, upper))

    wimport("n_signal", n_signal, n_signal/10, n_signal*10)
    wimport("n_muoncontrol", n_muoncontrol, 0.001, n_muoncontrol*10)
    wimport("n_photoncontrol", n_photoncontrol, 0.001, n_photoncontrol*10)

    wimport("n_bar_signal", n_bar_signal, n_bar_signal/10, r.RooNumber.infinity())
    wimport("n_control_1", n_control_1, 0.001, r.RooNumber.infinity())
    wimport("n_bar_control_1", n_bar_control_1, n_bar_control_1/10, r.RooNumber.infinity())
    wimport("n_control_2", n_control_2, n_control_2/10, r.RooNumber.infinity())
    wimport("n_bar_control_2", n_bar_control_2, n_bar_control_2/10,r.RooNumber.infinity())

    #Parameter of interest; the number of (SUSY) signal events above the Standard Model background
    wimport("s", 2.5, 0.0001, n_signal*3) #expected numer of (SUSY) signal events above background

    #Nuisance parameters
    wimport("TTplusW", n_signal/2, 0.01, n_signal*10)#expected tt+W background in signal-like region
    wimport("ZINV", n_signal/2, 0.001, n_signal*10)#expected Zinv background in signal-like region
    wimport("QCD", 0.001, 0, n_signal*10)#expected QCD background in signal-like region

    #Nuisance parameter for low HT inclusive background estimation method
    wimport("bbar", n_bar_signal, n_bar_signal/10, n_bar_signal*10)#expected total background in alphaT<0.55 and HT>350 GeV
    wimport("tau", 1.0, 0.001, 4.)#factor which relates expected background in alphaT > 0.55 for HT > 350 GeV and 300 < HT < 350 GeV
    wimport("tauprime", 2.515, 0, 5.)#factor which relates expected background in alphaT > 0.55 for HT > 350 GeV and 250 < HT < 300 GeV
    wimport("rho", 1.18, 0., 2.)#factor rho which takes into account differences between alphaT > 0.55 and alphaT < 0.55 in the signal yield development with HT    
    
    for item in ["sigma_x",                # uncertainty on Monte Carlo estimation of X
                 "tau_mu","sigma_ttW",     # Nuisance par tt+w
                 "tau_photon","sigma_Zinv",# Nuisance par Zinv
                 "sigma_SigEff"            # Systematic : uncertainty on signal*acceptance*efficiency*lumi
                 ] : wimport(item, eval(item))
    
    setupLikelihoodOneBin(wspace, switches)

    #set values of observables
    lolArgSet = wspace.set("obs")
    newSet = r.RooArgSet(wspace.set("obs"))
    for item in ["n_signal","n_muoncontrol","n_photoncontrol",
                 "n_control_1","n_bar_control_1",
                 "n_control_2","n_bar_control_2","n_bar_signal"
                 ][:3 if switches["fixQcdToZero"] else None] :
        newSet.setRealValue(item, eval(item))
    
    data = r.RooDataSet(dataName, "title", lolArgSet)
    data.Print()
    data.add(lolArgSet)
    getattr(wspace, "import")(data)
    return data

def modelConfiguration(wspace, pdfName)  :
    modelConfig = r.RooStats.ModelConfig("Combine")
    modelConfig.SetWorkspace(wspace)
    modelConfig.SetPdf(wspace.pdf(pdfName))
    #modelConfig.SetPriorPdf(wspace.pdf("prior"))
    modelConfig.SetParametersOfInterest(wspace.set("poi"))
    modelConfig.SetNuisanceParameters(wspace.set("nuis"))
    getattr(wspace,"import")(modelConfig)
    return modelConfig

def printCovMat(wspace, data) :
    ratioSigEff = wspace.var("ratioSigEff")
    ratioBkgdEff_1 = wspace.var("ratioBkgdEff_1")
    ratioBkgdEff_2 = wspace.var("ratioBkgdEff_2")
    constrainedParams = r.RooArgSet(ratioBkgdEff_1, ratioBkgdEff_2, ratioSigEff)
  
    assert data
    wspace.pdf("total_model").fitTo(data, RooFit.Constrain(constrainedParams))

def constrainParams(wspace) :
    nuispar = r.RooArgList(wspace.set("nuis"))
    for i in range(nuispar.getSize()) :
        par = nuispar[i]
        par.setMin(max(par.getVal()-10*par.getError(), par.getMin() ) )
        par.setMax(min(par.getVal()+10*par.getError(), par.getMax() ) )

        poipar = r.RooArgList(wspace.set("poi"))
        for i in range(poipar.getSize()) :
            spar = poipar[i]
            spar.setMin(max(spar.getVal()-10*spar.getError(), spar.getMin() ) )
            spar.setMax(min(spar.getVal()+10*spar.getError(), spar.getMax() ) )

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
    for item in ["sig10", "sig05", "sig20", "muon"] :
        if twoHtBins :
            for tag,dir in zip(["1", "2"],["350Dirs", "450Dirs"]) :
                histo = func(specs[item], specs[item][dir], lumi)
                if histo : out["%s_%s"%(item,tag)] = histo.GetBinContent(m0, m12, mChi)
        else :
            histo = func(specs[item], specs[item]["350Dirs"] + specs[item]["450Dirs"], lumi)
            if histo : out["%s"%item] = histo.GetBinContent(m0, m12, mChi)

    for item in ["ht"] :
        for tag,dir in zip(["1", "2"],["250Dirs", "300Dirs"]) :
            histo = func(specs[item], specs[item][dir], lumi, beforeSpec = specs["sig10"])
            if histo : out["%s_%s"%(item,tag)] = histo.GetBinContent(m0, m12, mChi)
    return out

def setSignalVars(y, switches, specs, strings, wspace, sigma_SigEff_, pdfUncertainty) :
    def signalSys(init, y) :
        d_s       = y["sig10_1"]+y["sig10_2"]
        d_s_sys05 = y["sig05_1"]+y["sig05_2"]
        d_s_sys2  = y["sig20_1"]+y["sig20_2"]
        masterPlus =  abs(max((max((d_s_sys2 - d_s),(d_s_sys05 - d_s))),0.))
        masterMinus = abs(max((max((d_s - d_s_sys2),(d_s - d_s_sys05))),0.))
        return math.sqrt( math.pow( max(masterMinus,masterPlus)/d_s,2) + pow(init,2) + pow(pdfUncertainty, 2) )

    def d_s(y) :
        return y["sig10_1"] + y["sig10_2"]

    def frac(y, tag, index) :
        return y["%s_%d"%(tag, index)] / d_s(y)

    ds = d_s(y)
    if ds>0.0 :
        wspace.var("BR1").setVal(frac(y, "sig10", 1))
        wspace.var("BR2").setVal(frac(y, "sig10", 2))
        
        wspace.var("muon_cont_1").setVal(frac(y, "muon", 1))
        wspace.var("muon_cont_2").setVal(frac(y, "muon", 2))
        wspace.var("lowHT_cont_1").setVal(frac(y, "ht", 1))
        wspace.var("lowHT_cont_2").setVal(frac(y, "ht", 2))
        wspace.var("signal_sys").setVal(sigma_SigEff_ if not switches["nlo"] else signalSys(sigma_SigEff_, y))
    return ds

def setSignalVarsOneBin(y, switches, specs, strings, wspace, sigma_SigEff_) :
    tau_s_muon = 1
    d_s        = y["sig10"]
    d_muon     = y["muon"]
    signal_sys = sigma_SigEff_
    
    if d_s>0.0 : tau_s_muon = d_muon / d_s

    if switches["nlo"] and d_s>0.0 :
        d_s_sys05 = y["sig05"]
        d_s_sys2  = y["sig20"]
        masterPlus =  abs(max((max((d_s_sys2 - d_s),(d_s_sys05 - d_s))),0.))
        masterMinus = abs(max((max((d_s - d_s_sys2),(d_s - d_s_sys05))),0.))
        signal_sys = math.sqrt( math.pow( max(masterMinus,masterPlus)/d_s,2) + pow(sigma_SigEff_,2)  )

    #set background contamination
    wspace.var("tau_s_mu").setVal(tau_s_muon);
    wspace.var("sigma_SigEff").setVal(signal_sys);
    return d_s

def prepareCanvas(doBayesian, doMCMC) :
    c1 = r.TCanvas("c1")
    if doBayesian and doMCMC :
        c1.Divide(3)
        c1.cd(1)
    elif doBayesian or doMCMC :
        c1.Divide(2)
        c1.cd(1)

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
        num = hp.loYieldHisto(specs["sig10"], ["350Dirs", "450Dirs"], inputData["lumi"])
        den = hp.loYieldHisto(specs["sig10"], ["beforeDir"], inputData["lumi"])
        num.Divide(den)
        return num.GetBinContent(m0, m12, mChi)
    else :
        return inputData["_accXeff"]

def lumi(switches, inputData) :
    if len(switches["signalModel"])==2 :
        return inputData["lumi"]
    else :
        return 1.0

def Lepton(switches, specs, strings, inputData,
           m0, m12, mChi) :

    r.RooRandom.randomGenerator().SetSeed(inputData["seed"]) #set RooFit random seed for reproducible results
    wspace = r.RooWorkspace("Combine")
    
    #import variables and set up total likelihood function
    data = None
    modelConfig = None
    
    if not switches["twoHtBins"] :
        data = importVarsOneBin( wspace, inputData, switches, strings["dataName"])
    else :
        r.gSystem.Load("SlimPdfFactory_C.so")
        r.AddModel_Lin_Combi(array.array('d',inputData["sFrac"]),
                             lumi(switches, inputData),
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

                             wspace,
                             strings["pdfName"],
                             strings["signalVar"],
                             )

        r.AddDataSideband_Combi( array.array('d', inputData["n_htcontrol"]),
                                 array.array('d', inputData["n_bar_htcontrol"]),
                                 len(inputData["n_bar_htcontrol"]),

                                 array.array('d', inputData["n_muoncontrol"]),
                                 array.array('d', inputData["n_photoncontrol"]),

                                 taus(inputData["mc_muoncontrol"], inputData["mc_ttW"]),
                                 taus(inputData["mc_photoncontrol"], inputData["mc_Zinv"]),
                                 
                                 len(inputData["n_muoncontrol"]),
                                 wspace,
                                 strings["dataName"]
                                 )

    modelConfig = modelConfiguration(wspace, strings["pdfName"])

    if switches["writeWorkspaceFile"] : wspace.writeToFile(strings["outputWorkspaceFileName"])
    if switches["printCovarianceMatrix"] : printCovMat(wspace, data)
    if switches["constrainParameters"] : constrainParams(wspace)
    
    prepareCanvas(switches["method"]=="doBayesian", switches["method"]=="doMCMC")

    if not switches["signalFreeMode"] :
        y = yields(specs, switches["nlo"], switches["twoHtBins"], inputData["lumi"], m0, m12, mChi)
        if switches["twoHtBins"] : ds = setSignalVars(      y, switches, specs, strings, wspace, inputData["sigma_SigEff"], inputData["pdfUncertainty"])
        else :                     ds = setSignalVarsOneBin(y, switches, specs, strings, wspace, inputData["sigma_SigEff"])
    
    func = eval(switches["method"])
    upperLimit = func(modelConfig, wspace, strings["dataName"], strings["signalVar"])
    writeNumbers(fileName = strings["plotFileName"], m0 = m0, m12 = m12, mChi = mChi, upperLimit = upperLimit, ds = ds, y = y)
    #printStuff(y, m0, m12, mChi)
