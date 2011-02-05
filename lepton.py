#!/usr/bin/env python
import ROOT as r
import math

def loYieldHisto(spec, dirs, lumi) :
    f = r.TFile(spec["file"])
    assert not f.IsZombie()

    h = None
    for dir in dirs :
        hOld = f.Get("%s/%s"%(dir, spec["loYield"]))
        if not h :
            h = hOld.Clone("%s_%s_%s"%(spec["file"], dir, hOld.GetName()))
        else :
            h.Add(hOld)
            
    h.SetDirectory(0)
    h.Scale(lumi/100.0) #100/pb is the default normalization
    f.Close()
    return h

def nloYieldHisto(spec, dirs, lumi) :
    def numerator(name) :
        out = None
        for dir in dirs :
            if out is None :
                out = f.Get("%s/m0_m12_%s_0"%(dir, name))
            else :
                out.Add(f.Get("%s/m0_m12_%s_0"%(dir, name)))
        return out

    f = r.TFile(spec["file"])
    if f.IsZombie() : return None

    all = None
    for name in ["gg", "sb", "ss", "sg", "ll", "nn", "ng", "bb", "tb", "ns"] :
        den = f.Get("%s/m0_m12_%s_5"%(spec["beforeDir"], name))
        num = numerator(name)
        num.Divide(den)
        
        if all is None :
            all = num.Clone("%s_%s_%s"%(spec["file"], dirs[0], name))
        else :
            all.Add(num)

    all.SetDirectory(0)
    all.Scale(lumi)
    f.Close()
    return all

def workspace() : return r.RooWorkspace("Combine")

def setupLikelihoodOneBin(wspace, switches) :
    #likelihood for the signal region (Poisson to include the statistical uncertainty)
    if not switches["fixQcdToZero"] :
        wspace.factory("Poisson::signal(n_signal,sum::splusb(sum::b(prod::ttW(ratioBkgdEff_1[1.0,0.,5.],TTplusW),QCD,prod::Zinv(ratioBkgdEff_2[1.0,0.,5.],ZINV)),prod::SigUnc(s,ratioSigEff[1,0.3,1.9])))")
    else :
        wspace.factory("Poisson::signal(n_signal,sum::splusb(sum::b(prod::ttW(ratioBkgdEff_1[1.0,0.,5.],TTplusW),prod::Zinv(ratioBkgdEff_2[1.0,0.,5.],ZINV)),prod::SigUnc(s,ratioSigEff[1,0.3,1.9])))")

    if not switches["fixQcdToZero"] :
        #likelihood for the low HT and/or low alphaT auxiliary measurements
        wspace.factory("Poisson::bar_signal(n_bar_signal,bbar)") #alphaT < 0.55 && HT > 350 GeV
        wspace.factory("Poisson::control_1(n_control_1,prod::taub(tau,b,rho))") #alphaT > 0.55 && 300 < HT < 350 GeV
        wspace.factory("Poisson::bar_control_1(n_bar_control_1,prod::taubar(tau,bbar))") #alphaT < 0.55 && 300 < HT << 350 GeV
        wspace.factory("Poisson::control_2(n_control_2,prod::taub_2(tauprime,b,prod::rhoprime(f[1.,0.,2.],rho,rho)))") #alphaT > 0.55 && 250 < HT < 300 GeV
        wspace.factory("Poisson::bar_control_2(n_bar_control_2,prod::taubar_2(tauprime,bbar))") #alphaT < 0.55 && 250 < HT < 300 GeV
        #pdf for the systeamtic uncertainty on the assumption that rhoprime = rho*rho
        wspace.factory("Gaussian::xConstraint(1.,f,sigma_x)")
        wspace.factory("PROD::QCD_model(bar_signal,control_1,bar_control_1,control_2,bar_control_2,xConstraint)")

    #gaussians to include the systematic uncertainties on the background estimations and the signal acceptance*efficiency*luminosity
    wspace.factory("Gaussian::sigConstraint(1.,ratioSigEff,sigma_SigEff)");
    wspace.factory("Gaussian::mcCons_ttW(1.,ratioBkgdEff_1,sigma_ttW)"); 
    wspace.factory("Gaussian::mcCons_Zinv(1.,ratioBkgdEff_2,sigma_Zinv)");
    wspace.factory("PROD::signal_model(signal,sigConstraint,mcCons_ttW,mcCons_Zinv)");

    #set pdf for muon control 
    wspace.factory("Poisson::muoncontrol(n_muoncontrol,sum::MuSPlusB(prod::TTWside(tau_mu,TTplusW),prod::smu(tau_s_mu[0.001],s)))");

    #set pdf for photon control
    wspace.factory("Poisson::photoncontrol(n_photoncontrol,prod::sideband_photon(tau_photon,ZINV))");

    #combine the three
    if not switches["fixQcdToZero"] :
        wspace.factory("PROD::total_model(signal_model,QCD_model,muoncontrol,photoncontrol)")
    else :
        wspace.factory("PROD::total_model(signal_model,muoncontrol,photoncontrol)")
        
    #to use for bayesian methods
    wspace.factory("Uniform::prior_poi({s})")
    if not switches["fixQcdToZero"] :
        wspace.factory("Uniform::prior_nuis({TTplusW,QCD,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff})")
    else :
        wspace.factory("Uniform::prior_nuis({TTplusW,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff})")

    wspace.factory("PROD::prior(prior_poi,prior_nuis)")

    #define some sets to use later (plots)
    wspace.defineSet("poi","s")
    if not switches["fixQcdToZero"] :
        wspace.defineSet("obs","n_signal,n_muoncontrol,n_photoncontrol,n_bar_signal,n_control_1,n_bar_control_1,n_control_2,n_bar_control_2")
        wspace.defineSet("nuis","TTplusW,QCD,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff")
    else :
        wspace.defineSet("obs","n_signal,n_muoncontrol,n_photoncontrol")
        wspace.defineSet("nuis","TTplusW,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff")


def importVarsOneBin(wspace, inputData, switches, dataName) :
    def wimport(name = None, value = None, lower = None, upper = None) :
        assert name
        assert value
        if lower is None and upper is None :
            getattr(wspace, "import")(r.RooRealVar(name, name, value))
        else :
            assert lower!=None
            assert upper!=None
            getattr(wspace, "import")(r.RooRealVar(name, name, value, lower, upper))
            
    n_signal_ = inputData["n_signal"][0]+inputData["n_signal"][1]
    n_bar_signal_ = inputData["n_bar_htcontrol"][2]+inputData["n_bar_htcontrol"][3]

    n_muoncontrol_ = inputData["n_muoncontrol"][0]+inputData["n_muoncontrol"][1]
    tau_mu_ = (inputData["mc_muoncontrol"][0]+inputData["mc_muoncontrol"][1]) / (inputData["mc_ttW"][0]+inputData["mc_ttW"][1]);
    sigma_ttW_ = inputData["sigma_ttW"]
    
    n_photoncontrol_ = inputData["n_photoncontrol"][0]+inputData["n_photoncontrol"][1];
    tau_photon_ = (inputData["mc_photoncontrol"][0]+inputData["mc_photoncontrol"][1]) / (inputData["mc_Zinv"][0]+inputData["mc_Zinv"][1]);
    sigma_Zinv_ = inputData["sigma_Zinv"]
    
    n_control_1_ = inputData["n_htcontrol"][1]
    n_control_2_ = inputData["n_htcontrol"][0]
    n_bar_control_1_ = inputData["n_bar_htcontrol"][1]
    n_bar_control_2_ = inputData["n_bar_htcontrol"][0]
    sigma_x_ = inputData["sigma_x"]

    sigma_SigEff_ = inputData["sigma_SigEff"]

    wimport("n_signal", n_signal_, n_signal_/10, n_signal_*10)
    wimport("n_muoncontrol", n_muoncontrol_, 0.001, n_muoncontrol_*10)
    wimport("n_photoncontrol", n_photoncontrol_, 0.001, n_photoncontrol_*10)

    wimport("n_bar_signal", n_bar_signal_, n_bar_signal_/10, r.RooNumber.infinity())
    wimport("n_control_1", n_control_1_, 0.001, r.RooNumber.infinity())
    wimport("n_bar_control_1", n_bar_control_1_, n_bar_control_1_/10, r.RooNumber.infinity())
    wimport("n_control_2", n_control_2_, n_control_2_/10, r.RooNumber.infinity())
    wimport("n_bar_control_2", n_bar_control_2_, n_bar_control_2_/10,r.RooNumber.infinity())

    #Parameter of interest; the number of (SUSY) signal events above the Standard Model background
    wimport("s", 2.5, 0.0001, n_signal_*3) #expected numer of (SUSY) signal events above background 

    #Nuisance parameters
    wimport("TTplusW", n_signal_/2, 0.01, n_signal_*10)#expected tt+W background in signal-like region
    wimport("ZINV", n_signal_/2, 0.001, n_signal_*10)#expected Zinv background in signal-like region
    wimport("QCD", 0.001, 0, n_signal_*10)#expected QCD background in signal-like region

    #Nuisance parameter for low HT inclusive background estimation method
    wimport("bbar", n_bar_signal_, n_bar_signal_/10, n_bar_signal_*10)#expected total background in alphaT<0.55 and HT>350 GeV
    wimport("tau", 1.0, 0.001, 4.)#factor which relates expected background in alphaT > 0.55 for HT > 350 GeV and 300 < HT < 350 GeV
    wimport("tauprime", 2.515, 0, 5.)#factor which relates expected background in alphaT > 0.55 for HT > 350 GeV and 250 < HT < 300 GeV
    wimport("rho", 1.18, 0., 2.)#factor rho which takes into account differences between alphaT > 0.55 and alphaT < 0.55 in the signal yield development with HT    
    wimport("sigma_x", sigma_x_)#uncertainty on Monte Carlo estimation of X
    
    #Nuisance parameter for tt+W estimation
    wimport("tau_mu", tau_mu_)
    wimport("sigma_ttW", sigma_ttW_)

    #Nuisance parameter for Zinv estiamtion
    wimport("tau_photon", tau_photon_)
    wimport("sigma_Zinv", sigma_Zinv_)
    #Systematic uncertainty on singal*acceptance*efficiency*luminosity
    wimport("sigma_SigEff", sigma_SigEff_)

    setupLikelihoodOneBin(wspace, switches)

    #set values of observables
    lolArgSet = wspace.set("obs")
    newSet = r.RooArgSet(wspace.set("obs"))
    newSet.setRealValue("n_signal", n_signal_)
    newSet.setRealValue("n_muoncontrol", n_muoncontrol_) #set observables for muon control method
    newSet.setRealValue("n_photoncontrol", n_photoncontrol_) #set observable for photon control method
    if not switches["fixQcdToZero"] :
        #set observables for SixBin low HT method
        newSet.setRealValue("n_control_1",     n_control_1_    )
        newSet.setRealValue("n_bar_control_1", n_bar_control_1_)
        newSet.setRealValue("n_control_2",     n_control_2_    )
        newSet.setRealValue("n_bar_control_2", n_bar_control_2_)
        newSet.setRealValue("n_signal",        n_signal_       )
        newSet.setRealValue("n_bar_signal",    n_bar_signal_   )

    data = r.RooDataSet(dataName, "title", lolArgSet)
    data.Print()
    data.add(lolArgSet)
    getattr(wspace, "import")(data)
    return data

def modelConfiguration(wspace, pdfName)  :
    modelConfig = r.RooStats.ModelConfig("Combine")
    modelConfig.SetWorkspace(wspace)
    modelConfig.SetPdf(wspace.pdf(pdfName))
    modelConfig.SetPriorPdf(wspace.pdf("prior"))
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
    nuispar = RooArgList(wspace.set("nuis"))
    for i in range(nuispar.getSize()) :
        par = nuispar[i]
        par.setMin(max(par.getVal()-10*par.getError(), par.getMin() ) )
        par.setMax(min(par.getVal()+10*par.getError(), par.getMax() ) )

        poipar = RooArgList(wspace.set("poi"))
        for i in range(poipar.getSize()) :
            spar = poipar[i]
            spar.setMin(max(spar.getVal()-10*spar.getError(), spar.getMin() ) )
            spar.setMax(min(spar.getVal()+10*spar.getError(), spar.getMax() ) )

def profileLikelihood(modelConfig, wspace, dataName, signalVar, d_s = 0.0) :
    isInInterval = False

    plc = r.RooStats.ProfileLikelihoodCalculator(wspace.data(dataName), modelConfig)
    plc.SetConfidenceLevel(0.95)
    plInt = r.RooStats.LikelihoodInterval = plc.GetInterval()

    if d_s<=1.0 :
        lrplot = r.RooStats.LikelihoodIntervalPlot(plInt)
        lrplot.Draw();
        print "Profile Likelihood interval on s = [%g, %g]"%(plInt.LowerLimit(wspace.var(signalVar)), plInt.UpperLimit(wspace.var(signalVar)))
        plInt.UpperLimit(wspace.var(signalVar))
    else :
        tmp_s = r.RooRealVar(wspace.var(signalVar))
        print "upper limit",plInt.UpperLimit(wspace.var(signalVar))
        tmp_s.setVal(d_s)
        isInInterval = plInt.IsInInterval(r.RooArgSet(tmp_s))

    return isInInterval

#def feldmanCousins(data, modelConfig, wspace) :
#    #setup for Felman Cousins
#  RooStats::FeldmanCousins fc(*data, *modelConfig);
#  fc.SetConfidenceLevel(0.95);
#  //number counting: dataset always has 1 entry with N events observed
#  fc.FluctuateNumDataEntries(false); 
#  fc.UseAdaptiveSampling(true);
#  fc.SetNBins(50);
#  RooStats::PointSetInterval* fcInt = (RooStats::PointSetInterval*) fc.GetInterval();
#
#  cout << "Feldman Cousins interval on s = ["
#       << fcInt.LowerLimit( *wspace.var("s") ) << ", "
#       << fcInt.UpperLimit( *wspace.var("s") ) << "]" << endl;
#  //Feldman Cousins interval on s = [18.75 +/- 2.45, 83.75 +/- 2.45]
#  fcInt.UpperLimit( *wspace.var("s") );
#}
#
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

def setSignalVars(switches, specs, strings, wspace, m0, m12, mChi, lumi, sigma_SigEff_) :
    signal = None
    muon   = None
    sys05  = None
    sys2   = None

    if switches["nlo"] :
        signal = nloYieldHisto(specs["sig10"], specs["sig10"]["350Dirs"] + specs["sig10"]["450Dirs"],lumi)
        muon   = nloYieldHisto(specs["muon"],  specs["muon"]["350Dirs"]  + specs["muon"]["450Dirs"], lumi)
        sys05  = nloYieldHisto(specs["sig05"], specs["sig05"]["350Dirs"] + specs["sig05"]["450Dirs"],lumi)
        sys2   = nloYieldHisto(specs["sig20"], specs["sig20"]["350Dirs"] + specs["sig20"]["450Dirs"],lumi)
    else :
        signal =  loYieldHisto(specs["sig10"], specs["sig10"]["350Dirs"] + specs["sig10"]["450Dirs"],lumi)
        muon   =  loYieldHisto(specs["muon"],  specs["muon"]["350Dirs"]  + specs["muon"]["450Dirs"], lumi)

    tau_s_muon = 1
    d_s       = signal.GetBinContent(m0, m12, mChi)
    d_muon    = muon.GetBinContent(m0, m12, mChi)
    signal_sys = sigma_SigEff_
    
    if d_s>0.0 : tau_s_muon = d_muon / d_s

    if switches["nlo"] :
        assert sys05
        assert sys2
        d_s_sys05 = sys05.GetBinContent(m0, m12, mChi)#the event yield if the NLO factorizaiton and renormalizaiton are varied by a factor of 0.5
        d_s_sys2  = sys2.GetBinContent(m0, m12, mChi)#the event yield if the NLO factorizaiton and renormalizaiton are varied by a factor of 2
        masterPlus =  abs(max((max((d_s_sys2 - d_s),(d_s_sys05 - d_s))),0.))
        masterMinus = abs(max((max((d_s - d_s_sys2),(d_s - d_s_sys05))),0.))
        signal_sys = math.sqrt( math.pow( max(masterMinus,masterPlus)/d_s,2) + pow(sigma_SigEff_,2)  )

    #set background contamination
    wspace.var("tau_s_mu").setVal(tau_s_muon);
    wspace.var("sigma_SigEff").setVal(signal_sys);

    return d_s

def canvas(doBayesian, doMCMC) :
    c1 = r.TCanvas("c1")
  
    if doBayesian and doMCMC :
        c1.Divide(3)
        c1.cd(1)
    elif doBayesian or doMCMC :
        c1.Divide(2)
        c1.cd(1)
    return c1

def writeExclusionLimitPlot(exampleHisto, outputPlotFileName, m0, m12, mChi, isInInterval) :
    output = r.TFile(outputPlotFileName, "RECREATE")
    assert not output.IsZombie()
    assert exampleHisto

    exclusionLimit = exampleHisto.Clone("ExclusionLimit")
    exclusionLimit.SetTitle("ExclusionLimit;m_{0} (GeV);m_{1/2} (GeV);z-axis")
    exclusionLimit.Reset()
    exclusionLimit.SetBinContent(m0, m12, mChi, 2.0*isInInterval - 1.0)
    exclusionLimit.Write()
    output.Close()

def checkMap(nInitial, nFinal, name) :
    assert nInitial==nFinal, "ERROR in %s : nInitial = %d; nFinal = %s"%(name, nInitial, nFinal)

def Lepton(switches,
           specs,
           strings,
           inputData,
           m0,
           m12,
           mChi
           ) :

    t = r.TStopwatch()
    t.Start()

    #set RooFit random seed for reproducible results
    r.RooRandom.randomGenerator().SetSeed(inputData["seed"])
    #make a workspace
    wspace = workspace()
    
    #import variables and set up total likelihood function
    data = None
    modelConfig = None
    
    if not switches["twoHtBins"] :
        data = importVarsOneBin(wspace, inputData, switches, strings["dataName"])
        modelConfig = modelConfiguration(wspace, strings["pdfName"])
    else :
        pass
    ##RobsPdfFactory f;
    ##f.AddModel_Lin_Combi(s, signal_sys, muon_sys, phot_sys, 2, wspace, strings["pdfName"], strings["signalVar"]);
    ##f.AddDataSideband_Combi(bkgd_sideband, bkgd_bar_sideband, 4, muonMeas, photMeas, tau_muon, tau_phot, 2, wspace, strings["dataName"]);
    ##modelConfig = modelConfiguration(wspace, strings["pdfName"]);

    if switches["writeWorkspaceFile"] : wspace.writeToFile(strings["outputWorkspaceFileName"])
    if switches["printCovarianceMatrix"] : printCovMat(wspace, data)
    if switches["constrainParameters"] : constrainParams(wspace)
    
    canvas(switches["doBayesian"], switches["doMCMC"])#prepare a canvas
    
    #profileLikelihood(modelConfig, wspace, strings["dataName"], strings["signalVar"]) #run with no signal contamination

    if switches["doFeldmanCousins"] : feldmanCousins(data, modelConfig, wspace) #takes 7 minutes
    if switches["doBayesian"] : bayesian(data, modelConfig, wspace) #use BayesianCalculator (only 1-d parameter of interest, slow for this problem)
    if switches["doMCMC"] : mcmc(data, modelConfig, wspace) #use MCMCCalculator (takes about 1 min)
    
    d_s = setSignalVars(switches, specs, strings, wspace, m0, m12, mChi, inputData["lumi"], inputData["sigma_SigEff"])
    isInInterval = profileLikelihood(modelConfig, wspace, strings["dataName"], strings["signalVar"], d_s)
    
    exampleHisto = loYieldHisto(specs["muon"],  specs["muon"]["350Dirs"], inputData["lumi"])
    writeExclusionLimitPlot(exampleHisto, strings["plotFileName"], m0, m12, mChi, isInInterval)
    t.Print()
