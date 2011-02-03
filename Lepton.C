#include <sstream>
#include <algorithm>
#include "TROOT.h"
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TLine.h"
#include "TStopwatch.h"
#include "RooRandom.h"
#include "RooProfileLL.h"
#include "RooAbsPdf.h"
#include "RooStats/HypoTestResult.h"
#include "RooRealVar.h"
#include "RooPlot.h"
#include "RooDataSet.h"
#include "RooTreeDataStore.h"
#include "RooWorkspace.h"
#include "RooAddition.h"
#include "RooPoisson.h"
#include "RooFitResult.h"
#include "RooStats/ProfileLikelihoodCalculator.h"
#include "RooStats/MCMCCalculator.h"
#include "RooStats/UniformProposal.h"
#include "RooStats/FeldmanCousins.h"
#include "RooStats/NumberCountingPdfFactory.h"
#include "RooStats/ConfInterval.h"
#include "RooStats/PointSetInterval.h"
#include "RooStats/LikelihoodInterval.h"
#include "RooStats/LikelihoodIntervalPlot.h"
#include "RooStats/RooStatsUtils.h"
#include "RooStats/ModelConfig.h"
#include "RooStats/MCMCInterval.h"
#include "RooStats/MCMCIntervalPlot.h"
#include "RooStats/ProposalFunction.h"
#include "RooStats/ProposalHelper.h"
#include "RooStats/BayesianCalculator.h"
#include "RooStats/PointSetInterval.h"

//Comments from Tanja:
//A word of explanation before starting
//The RA1 analysis uses three kinds of background estimation 
//one estimates the combined tt+W background from a muon control auxiliary measurement
// assumption the expected background in the muon control sample is tau_mu*TTplusW (expected tt+W background in signal-like region)
//one estimates the Zinv background from a photon control auxiliary measurement
// assumption the expected background in the photon control sample is tau_photon*ZINV (expected Zinv background in signal-like region)
//one estimates the total background (tt+W+Zinv+QCD) using low HT and low alphaT control measurement
//Here a little (hopefully helpful) drawing (yaxis is alphaT, xaxis is HT)
//
// ^ (alphaT)
// |                                 |                                  |
// | observe: n_control_2 events     | observe:n_control_1 events       | observe: n_signal events
// | tauprime*b*rhoprime             | expect: tau*b*rho                | expect: s+ b
// |                                 |                                  |
//_|HT=250GeV________________________|HT=300 GeV________________________|HT=350 GeV_____________> (HT)
// |alphaT = 0.55                    |                                  |
// |                                 |                                  |
// | observe: n_bar_control_2 events | observe: n_bar_control_1 events  | observe: n_bar_signal events               
// | expect: tauprime*bbar           | expect: tau*bbar                 | expect: bbar
// |                                 |                                  |
// 
// The asumption made in the method is that R_alphaT (#events with alphaT>0.55/#events with alphaT < 0.55) for a given HT bin behave the following in the bkgd only scenario
// R_alphaT (HT>350 GeV) / R_alphaT (300 < HT < 350 GeV) = R_alphaT (300 < HT < 350 GeV) / R_alphaT (250 < HT < 300 GeV)
// this corresponds to the assumption that rhoprime = rho*rho
// using this assumption the b can be obtained
// ! the influence of signal contamination is not included in this macro for simplicity reasons (it would modify e.g. tau*b*rho to tau*b*rho+s*tau_s
// ! where tau_s would be taken from the signal monte carlo for each of the different test m0-m12 points

TString histoName(std::string& s1, std::string& s2, std::string& s3) {
  return s1+"_"+s2+"_"+s3;
}

TString histoName(std::string& s1, std::string& s2, std::string& s3, std::string& s4) {
  return s1+"_"+s2+"_"+s3+"_"+s4;
}

TH2F* loYieldHisto(std::string& fileName, std::string& dirName, std::string& histName, double lumi) {
  TFile f(fileName.c_str());
  TDirectory* dir = (TDirectory*)f.Get(dirName.c_str());

  if (!dir) {
    std::cerr << "ERROR: dir " << dirName << " does not exist in file " << fileName << std::endl;
    return 0;
  }
  TH2F* hOld = (TH2F*)dir->Get(histName.c_str());
  if (!hOld) {
    std::cerr << "ERROR: histo " << histoName(fileName, dirName, histName) << " does not exist." << std::endl;
    return 0;
  }
  TH2F* h = (TH2F*)hOld->Clone(histoName(fileName, dirName, histName));
  h->SetDirectory(0);
  h->Scale(lumi/100.0);//100/pb is the default normalization
  f.Close();
  return h;
}

TH2F* nloYieldHisto(std::string& fileName, std::string& dirName1, std::string& dirName2, double lumi) {
  TFile f(fileName.c_str());
  TDirectory* dir = (TDirectory*)f.Get(dirName1.c_str());
  TDirectory* dir2 = (TDirectory*)f.Get(dirName2.c_str());

  TH2F* gg = (TH2F*)dir2->Get("m0_m12_gg_0");
  std::string ggName = gg->GetName();
  TH2F* all = (TH2F*)gg->Clone(histoName(fileName, dirName1, dirName2, ggName));
  all->SetDirectory(0);
  all->Reset();

  std::vector<std::string> names;
  names.push_back("gg");
  names.push_back("sb");
  names.push_back("ss");
  names.push_back("sg");
  names.push_back("ll");
  names.push_back("nn");
  //names.push_back("ng");
  names.push_back("bb");
  names.push_back("tb");
  names.push_back("ns");

  for(unsigned int i=0;i<names.size();++i) {
    std::string numName = "m0_m12_"+names.at(i)+"_0";
    std::string denName = "m0_m12_"+names.at(i)+"_5";
    TH2F* num = (TH2F*)dir2->Get(numName.c_str());
    TH2F* den = (TH2F*)dir->Get(denName.c_str());

    if (!num) {
      std::cerr << "ERROR: histo " << numName << " does not exist." << std::endl;
      continue;
    }
    if (!den) {
      std::cerr << "ERROR: histo " << denName << " does not exist." << std::endl;
      continue;
    }

    num->Divide(den);
    all->Add(num);
  }

  all->Scale(lumi);
  f.Close();
  return all;
}

RooWorkspace* workspace() {
  return new RooWorkspace("Combine");
}

void setupLikelihood(RooWorkspace* wspace, std::map<std::string,int>& switches) {
  bool fixQcdToZero = switches["fixQcdToZero"];
  
  //likelihood for the signal region (Poisson to include the statistical uncertainty)
  if (!fixQcdToZero) {
    wspace->factory("Poisson::signal(n_signal,sum::splusb(sum::b(prod::ttW(ratioBkgdEff_1[1.0,0.,5.],TTplusW),QCD,prod::Zinv(ratioBkgdEff_2[1.0,0.,5.],ZINV)),prod::SigUnc(s,ratioSigEff[1,0.3,1.9])))");
  }
  else {
    wspace->factory("Poisson::signal(n_signal,sum::splusb(sum::b(prod::ttW(ratioBkgdEff_1[1.0,0.,5.],TTplusW),prod::Zinv(ratioBkgdEff_2[1.0,0.,5.],ZINV)),prod::SigUnc(s,ratioSigEff[1,0.3,1.9])))");
  }

  if (!fixQcdToZero) {
    //likelihood for the low HT and/or low alphaT auxiliary measurements
    wspace->factory("Poisson::bar_signal(n_bar_signal,bbar)");//alphaT < 0.55 && HT > 350 GeV
    wspace->factory("Poisson::control_1(n_control_1,prod::taub(tau,b,rho))"); //alphaT > 0.55 && 300 < HT < 350 GeV
    wspace->factory("Poisson::bar_control_1(n_bar_control_1,prod::taubar(tau,bbar))");  //alphaT < 0.55 && 300 < HT << 350 GeV
    wspace->factory("Poisson::control_2(n_control_2,prod::taub_2(tauprime,b,prod::rhoprime(f[1.,0.,2.],rho,rho)))");//alphaT > 0.55 && 250 < HT < 300 GeV
    wspace->factory("Poisson::bar_control_2(n_bar_control_2,prod::taubar_2(tauprime,bbar))");//alphaT < 0.55 && 250 < HT < 300 GeV
    //pdf for the systeamtic uncertainty on the assumption that rhoprime = rho*rho
    wspace->factory("Gaussian::xConstraint(1.,f,sigma_x)");
    wspace->factory("PROD::QCD_model(bar_signal,control_1,bar_control_1,control_2,bar_control_2,xConstraint)");
  }

  //gaussians to include the systematic uncertainties on the background estimations and the signal acceptance*efficiency*luminosity
  wspace->factory("Gaussian::sigConstraint(1.,ratioSigEff,sigma_SigEff)");
  wspace->factory("Gaussian::mcCons_ttW(1.,ratioBkgdEff_1,sigma_ttW)"); 
  wspace->factory("Gaussian::mcCons_Zinv(1.,ratioBkgdEff_2,sigma_Zinv)");
  wspace->factory("PROD::signal_model(signal,sigConstraint,mcCons_ttW,mcCons_Zinv)");

  //set pdf for muon control 
  if (!fixQcdToZero) {
    wspace->factory("Poisson::muoncontrol(n_muoncontrol,prod::sideband_muon(tau_mu,TTplusW))");
  }
  else {
    wspace->factory("Poisson::muoncontrol(n_muoncontrol,sum::MuSPlusB(prod::TTWside(tau_mu,TTplusW),prod::smu(tau_s_mu[0.001],s)))");
  }

  //set pdf for photon control
  wspace->factory("Poisson::photoncontrol(n_photoncontrol,prod::sideband_photon(tau_photon,ZINV))");

  //combine the three
  if (!fixQcdToZero) {
    wspace->factory("PROD::total_model(signal_model,QCD_model,muoncontrol,photoncontrol)");
  }
  else {
    wspace->factory("PROD::total_model(signal_model,muoncontrol,photoncontrol)");
  }

  //to use for bayesian methods
  wspace->factory("Uniform::prior_poi({s})");
  if (!fixQcdToZero) {
    wspace->factory("Uniform::prior_nuis({TTplusW,QCD,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff})");
  }
  else {
    wspace->factory("Uniform::prior_nuis({TTplusW,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff})");
  }
  wspace->factory("PROD::prior(prior_poi,prior_nuis)");

  //define some sets to use later (plots)
  wspace->defineSet("poi","s");
  if (!fixQcdToZero) {
    wspace->defineSet("obs","n_signal,n_muoncontrol,n_photoncontrol,n_bar_signal,n_control_1,n_bar_control_1,n_control_2,n_bar_control_2"); 
    wspace->defineSet("nuis","TTplusW,QCD,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff");
  }
  else {
    wspace->defineSet("obs","n_signal,n_muoncontrol,n_photoncontrol");
    wspace->defineSet("nuis","TTplusW,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff");
  }

}

void printByHandValues(std::map<std::string,double>& inputData) {
  //compute by hand the values of tau,tauprime and rho (good starting values)
  Double_t tauprime = inputData["n_bar_control_2"]/inputData["n_bar_signal"];
  Double_t tau = inputData["n_bar_control_1"]/inputData["n_bar_signal"];  
  Double_t rho = tau/tauprime*inputData["n_control_2"]/inputData["n_control_1"];
  cout << " tauprime " << tauprime << " tau " << tau << " rho " << rho << endl;
}

RooDataSet* importVars(RooWorkspace* wspace, std::map<std::string,double>& inputData, std::map<std::string,int>& switches) {
  RooRealVar n_signal("n_signal", "n_signal", inputData["n_signal"], inputData["n_signal"]/10, inputData["n_signal"]*10);
  RooRealVar n_muoncontrol("n_muoncontrol", "n_muoncontrol", inputData["n_muoncontrol"], 0.001, inputData["n_muoncontrol"]*10);
  RooRealVar n_photoncontrol("n_photoncontrol", "n_photoncontrol", inputData["n_photoncontrol"], 0.001, inputData["n_photoncontrol"]*10);

  RooRealVar n_bar_signal("n_bar_signal", "n_bar_signal", inputData["n_bar_signal"], inputData["n_bar_signal"]/10, RooNumber::infinity());
  RooRealVar n_control_1("n_control_1", "n_control_1", inputData["n_control_1"], 0.001, RooNumber::infinity());
  RooRealVar n_bar_control_1("n_bar_control_1", "n_bar_control_1", inputData["n_bar_control_1"], inputData["n_bar_control_1"]/10, RooNumber::infinity());
  RooRealVar n_control_2("n_control_2", "n_control_2", inputData["n_control_2"], inputData["n_control_2"]/10, RooNumber::infinity());
  RooRealVar n_bar_control_2("n_bar_control_2", "n_bar_control_2", inputData["n_bar_control_2"], inputData["n_bar_control_2"]/10,RooNumber::infinity());

  //Parameter of interest; the number of (SUSY) signal events above the Standard Model background
  RooRealVar s("s", "s", 2.5, 0.0001, inputData["n_signal"]*3);//expected numer of (SUSY) signal events above background 
  //Nuisance parameters
  RooRealVar TTplusW("TTplusW", "TTplusW", inputData["n_signal"]/2, 0.01, inputData["n_signal"]*10); //expected tt+W background in signal-like region
  RooRealVar ZINV("ZINV", "ZINV", inputData["n_signal"]/2, 0.001, inputData["n_signal"]*10);//expected Zinv background in signal-like region  
  RooRealVar QCD("QCD", "QCD", 0.001, 0, inputData["n_signal"]*10);//expected QCD background in signal-like region

  //Nuisance parameter for low HT inclusive background estimation method
  RooRealVar bbar("bbar", "bbar", inputData["n_bar_signal"], inputData["n_bar_signal"]/10, inputData["n_bar_signal"]*10);//expected total background in alphaT<0.55 and HT>350 GeV
  RooRealVar tau("tau", "tau", 1.0, 0.001, 4.);//factor which relates expected background in alphaT > 0.55 for HT > 350 GeV and 300 < HT < 350 GeV
  RooRealVar tauprime("tauprime", "tauprime", 2.515, 0, 5.);//factor which relates expected background in alphaT > 0.55 for HT > 350 GeV and 250 < HT < 300 GeV
  RooRealVar rho("rho", "rho", 1.18, 0., 2.);//factor rho which takes into account differences between alphaT > 0.55 and alphaT < 0.55 in the signal yield development with HT    
  RooRealVar sigma_x("sigma_x","sigma_x", inputData["sigma_x"]);//uncertainty on Monte Carlo estimation of X

  //Nuisance parameter for tt+W estimation
  RooRealVar tau_mu("tau_mu", "tau_mu", inputData["tau_mu"]);
  RooRealVar sigma_ttW("sigma_ttW", "sigma_ttW", inputData["sigma_ttW"]);
  //Nuisance parameter for Zinv estiamtion
  RooRealVar tau_photon("tau_photon", "tau_photon", inputData["tau_photon"]); 
  RooRealVar sigma_Zinv("sigma_Zinv", "sigma_Zinv", inputData["sigma_Zinv"]);
  //Systematic uncertainty on singal*acceptance*efficiency*luminosity
  RooRealVar sigma_SigEff("sigma_SigEff", "sigma_SigEff", inputData["sigma_SigEff"]);

  if (switches["printByHandValues"]) printByHandValues(inputData);
 
  //import RooRealVars
  wspace->import(TTplusW);
  wspace->import(ZINV);
  wspace->import(s);
  wspace->import(n_signal);
  //import variables for muon control
  wspace->import(n_muoncontrol);
  wspace->import(tau_mu); 
  wspace->import(sigma_ttW);
  //import variables for muon control
  wspace->import(n_photoncontrol);
  wspace->import(tau_photon);
  wspace->import(sigma_Zinv);
  wspace->import(sigma_SigEff);
  //import variables for QCD control
  if (!switches["fixQcdToZero"]) {
    wspace->import(bbar);
    wspace->import(QCD);
    wspace->import(tau);
    wspace->import(tauprime);
    wspace->import(rho);
    wspace->import(n_bar_signal);
    wspace->import(n_control_1);
    wspace->import(n_bar_control_1);
    wspace->import(n_control_2);
    wspace->import(n_bar_control_2);
    wspace->import(sigma_x);
  } 

  setupLikelihood(wspace, switches);

  //set values of observables
  const RooArgSet* lolArgSet=wspace->set("obs");
  RooArgSet* newSet = new RooArgSet(*lolArgSet);
  newSet->setRealValue("n_signal", inputData["n_signal"]);
  //set observables for muon control method
  newSet->setRealValue("n_muoncontrol", inputData["n_muoncontrol"]); 
  //set observable for photon control method
  newSet->setRealValue("n_photoncontrol", inputData["n_photoncontrol"]);
  if (!switches["fixQcdToZero"]) {
    //set observables for SixBin low HT method
    newSet->setRealValue("n_control_1",     inputData["n_control_1"]    );
    newSet->setRealValue("n_bar_control_1", inputData["n_bar_control_1"]);
    newSet->setRealValue("n_control_2",     inputData["n_control_2"]    );
    newSet->setRealValue("n_bar_control_2", inputData["n_bar_control_2"]);
    newSet->setRealValue("n_signal",        inputData["n_signal"]       );
    newSet->setRealValue("n_bar_signal",    inputData["n_bar_signal"]   );
  }

  RooDataSet *data = new RooDataSet("obsDataSet","title",*lolArgSet);
  data->Print();
  data->add(*lolArgSet);
  wspace->import(*data);

  return data;
} 

RooStats::ModelConfig* modelConfiguration(RooWorkspace* wspace) {
  RooStats::ModelConfig* modelConfig = new RooStats::ModelConfig("Combine");
  modelConfig->SetWorkspace(*wspace);
  modelConfig->SetPdf(*wspace->pdf("total_model"));
  modelConfig->SetPriorPdf(*wspace->pdf("prior"));
  modelConfig->SetParametersOfInterest(*wspace->set("poi"));
  modelConfig->SetNuisanceParameters(*wspace->set("nuis"));
  wspace->import(*modelConfig);
  return modelConfig;
}

void printCovMat(RooWorkspace* wspace, RooDataSet* data, RooArgSet& constrainedParams) {
  wspace->pdf("total_model")->fitTo(*data,RooFit::Constrain(constrainedParams));

  //some limitations good for fitting
  RooArgList nuispar(*wspace->set("nuis"));
  for(int i = 0; i < nuispar.getSize();++i){
    RooRealVar &par = (RooRealVar&) nuispar[i];
    par.setMin(std::max(par.getVal()-10*par.getError(),par.getMin() ) );
    par.setMax(std::min(par.getVal()+10*par.getError(),par.getMax() ) );
  }
  RooArgList poipar(*wspace->set("poi"));
  for(int i = 0; i < poipar.getSize();++i){
    RooRealVar &spar = (RooRealVar&) poipar[i];
    spar.setMin(std::max(spar.getVal()-10*spar.getError(),spar.getMin() ) );
    spar.setMax(std::min(spar.getVal()+10*spar.getError(),spar.getMax() ) );
  }
}

bool profileLikelihood(RooDataSet* data, RooStats::ModelConfig* modelConfig, RooWorkspace* wspace, double d_s = 0.0) {
  bool isInInterval = false;

  RooStats::ProfileLikelihoodCalculator plc(*data, *modelConfig);
  plc.SetConfidenceLevel(0.95);
  RooStats::LikelihoodInterval* plInt = plc.GetInterval();

  if (d_s<=1.0) {
    RooStats::LikelihoodIntervalPlot* lrplot = new RooStats::LikelihoodIntervalPlot(plInt);
    lrplot->Draw();
    
    cout << "Profile Likelihood interval on s = ["
	 << plInt->LowerLimit( *wspace->var("s") ) << ", "
	 << plInt->UpperLimit( *wspace->var("s") ) << "]" << endl;
    plInt->UpperLimit( *wspace->var("s") );
    //Profile Likelihood interval on s = [12.1902, 88.6871]
  }
  else {
    RooRealVar* tmp_s = wspace->var("s");
    cout << " upper limit " << plInt->UpperLimit(*tmp_s) << endl;
    tmp_s->setVal(d_s);
    isInInterval = plInt->IsInInterval(*tmp_s);
  }

  return isInInterval;
}

void feldmanCousins(RooDataSet* data, RooStats::ModelConfig* modelConfig, RooWorkspace* wspace) {
  //setup for Felman Cousins
  RooStats::FeldmanCousins fc(*data, *modelConfig);
  fc.SetConfidenceLevel(0.95);
  //number counting: dataset always has 1 entry with N events observed
  fc.FluctuateNumDataEntries(false); 
  fc.UseAdaptiveSampling(true);
  fc.SetNBins(50);
  RooStats::PointSetInterval* fcInt = (RooStats::PointSetInterval*) fc.GetInterval();

  cout << "Feldman Cousins interval on s = ["
       << fcInt->LowerLimit( *wspace->var("s") ) << ", "
       << fcInt->UpperLimit( *wspace->var("s") ) << "]" << endl;
  //Feldman Cousins interval on s = [18.75 +/- 2.45, 83.75 +/- 2.45]
  fcInt->UpperLimit( *wspace->var("s") );
}

void bayesian(RooDataSet* data, RooStats::ModelConfig* modelConfig, RooWorkspace* wspace) {
  RooStats::BayesianCalculator bc(*data, *modelConfig);
  bc.SetConfidenceLevel(0.95);
  RooStats::SimpleInterval* bInt = NULL;
  if(wspace->set("poi")->getSize() == 1)   {
    bInt = bc.GetInterval();
  } else{
    cout << "Bayesian Calc. only supports on parameter of interest" << endl;
    return;
  }

  cout << "Bayesian interval on s = ["
       << bInt->LowerLimit( ) << ", "
       << bInt->UpperLimit( ) << "]" << endl;
  bInt->UpperLimit( );
}

void mcmc(RooDataSet* data, RooStats::ModelConfig* modelConfig, RooWorkspace* wspace) {
  // Want an efficient proposal function, so derive it from covariance
  // matrix of fit
  RooFitResult* fit = wspace->pdf("total_model")->fitTo(*data, RooFit::Save());
  RooStats::ProposalHelper ph;
  ph.SetVariables((RooArgSet&)fit->floatParsFinal());
  ph.SetCovMatrix(fit->covarianceMatrix());
  ph.SetUpdateProposalParameters(kTRUE); // auto-create mean vars and add mappings
  ph.SetCacheSize(100);
  RooStats::ProposalFunction* pf = ph.GetProposalFunction();
  
  RooStats::MCMCCalculator mc(*data, *modelConfig);
  mc.SetConfidenceLevel(0.95);
  mc.SetProposalFunction(*pf);
  mc.SetNumBurnInSteps(200); // first N steps to be ignored as burn-in
  mc.SetNumIters(20000000);
  mc.SetLeftSideTailFraction(0.5); // make a central interval
  RooStats::MCMCInterval* mcInt = mc.GetInterval();

  cout << "MCMC interval on s = ["
       << mcInt->LowerLimit(*wspace->var("s") ) << ", "
       << mcInt->UpperLimit(*wspace->var("s") ) << "]" << endl;
  mcInt->UpperLimit(*wspace->var("s") );
  //MCMC interval on s = [15.7628, 84.7266]
}

double setSignalVars(std::map<std::string,std::string>& strings,
		     std::map<std::string,int>& switches,
		     RooWorkspace* wspace,
		     int m0,
		     int m12,
		     double lumi,
		     double sigma_SigEff_
		     ) {
  TH2F *signal = 0;
  TH2F *muon   = 0;
  TH2F *sys05  = 0;
  TH2F *sys2   = 0;

  if (switches["nlo"]) {
    signal = nloYieldHisto(strings["signalFile"],      strings["signalDir1"],      strings["signalDir2"],         lumi);
    muon   = nloYieldHisto(strings["muonControlFile"], strings["muonControlDir1"], strings["muonControlDir2"],    lumi);
    sys05  = nloYieldHisto(strings["sys05File"],       strings["sys05Dir1"],       strings["sys05Dir2"],          lumi);
    sys2   = nloYieldHisto(strings["sys2File"],        strings["sys2Dir1"],        strings["sys2Dir2"],           lumi);
  }
  else {
    signal =  loYieldHisto(strings["signalFile"],      strings["signalDir2"],      strings["signalLoYield"],      lumi);
    muon   =  loYieldHisto(strings["muonControlFile"], strings["muonControlDir2"], strings["muonControlLoYield"], lumi);
    sys05  =  loYieldHisto(strings["sys05File"],       strings["sys05Dir2"],       strings["sys05LoYield"],       lumi);
    sys2   =  loYieldHisto(strings["sys2File"],        strings["sys2Dir2"],        strings["sys2LoYield"],        lumi);
  }

  assert(signal);
  assert(muon);
  assert(sys05);
  assert(sys2);

  double tau_s_muon = 1;

  double d_s       = signal->GetBinContent(m0,m12);
  double d_s_sys05 = sys05->GetBinContent(m0,m12);//the event yield if the NLO factorizaiton and renormalizaiton are varied by a factor of 0.5
  double d_s_sys2  = sys2->GetBinContent(m0,m12);//the event yield if the NLO factorizaiton and renormalizaiton are varied by a factor of 2
  double d_muon    = muon->GetBinContent(m0,m12);
  double masterPlus = 0;
  double masterMinus = 0;
  double signal_sys = sigma_SigEff_;

  if(d_s > 0){
    tau_s_muon = d_muon / d_s;
    masterPlus =  fabs(TMath::Max((TMath::Max((d_s_sys2 - d_s),(d_s_sys05 - d_s))),0.));
    masterMinus = fabs(TMath::Max((TMath::Max((d_s - d_s_sys2),(d_s - d_s_sys05))),0.));
    signal_sys = sqrt( pow( TMath::Max(masterMinus,masterPlus)/d_s,2) + pow(sigma_SigEff_,2)  );
  }

  //set background contamination
  wspace->var("tau_s_mu")->setVal(tau_s_muon);
  wspace->var("sigma_SigEff")->setVal(signal_sys);

  return d_s;
}

TCanvas* canvas(bool doBayesian, bool doMCMC) {
  TCanvas* c1 = new TCanvas("c1");
  
  if(doBayesian && doMCMC){
    c1->Divide(3);
    c1->cd(1);
  }
  else if (doBayesian || doMCMC){
    c1->Divide(2);
    c1->cd(1);
  }
  return c1;
}

void writeExclusionLimitPlot(TH2F *exampleHisto, std::string& outputPlotFileName, int m0, int m12, bool isInInterval) {
  TFile output(outputPlotFileName.c_str(), "RECREATE");
  if (output.IsZombie()) std::cout << " zombie alarm output is a zombie " << std::endl;

  if (!exampleHisto) {
    std::cout << "exampleHisto is NULL" << std::endl;
    return;
  }

  TH2F *exclusionLimit = (TH2F*)exampleHisto->Clone("ExclusionLimit");
  exclusionLimit->SetTitle("ExclusionLimit;m_{0} (GeV);m_{1/2} (GeV)");
  exclusionLimit->Reset();
  exclusionLimit->SetBinContent(m0, m12, 2.0*isInInterval - 1.0);
  exclusionLimit->Write();

  output.Close();
}

void checkMap(int nInitial, int nFinal, std::string name) {
  if (nInitial!=nFinal) std::cerr << "ERROR in " << name << ": nInitial = " << nInitial << "; nFinal = " << nFinal << std::endl;
}

void Lepton(std::map<std::string,int>& switches,
	    std::map<std::string,std::string>& strings,
	    std::map<std::string,double>& inputData,
	    int m0,
	    int m12
	    ) {

  const int nSwitches = switches.size();
  const int nStrings = strings.size();
  const int nData = inputData.size();

  TStopwatch t;
  t.Start();

  //set RooFit random seed for reproducible results
  RooRandom::randomGenerator()->SetSeed(4357);
  //make a workspace
  RooWorkspace* wspace = workspace();
  //import variables and set up total likelihood function

  RooDataSet* data = importVars(wspace, inputData, switches);

  RooRealVar* ratioSigEff = wspace->var("ratioSigEff");
  RooRealVar* ratioBkgdEff_1 = wspace->var("ratioBkgdEff_1");
  RooRealVar* ratioBkgdEff_2 = wspace->var("ratioBkgdEff_2");
  //RooRealVar* f = wspace->var("f");
  RooArgSet constrainedParams(*ratioBkgdEff_1,*ratioBkgdEff_2,*ratioSigEff);

  RooStats::ModelConfig* modelConfig = modelConfiguration(wspace);
  if (switches["writeWorkspaceFile"]) wspace->writeToFile(strings["outputWorkspaceFileName"].c_str());
  if (switches["printCovarianceMatrix"]) printCovMat(wspace, data, constrainedParams);

  //RooRealVar* mu = wspace->var("s");
  //RooArgSet* nullParams = new RooArgSet("nullParams");
  //nullParams->addClone(*mu);
  //nullParams->setRealValue("s",0);
  
  canvas(switches["doBayesian"], switches["doMCMC"]); //prepare a canvas
  std::cout << " Limit " << std::endl;

  //profileLikelihood(data, modelConfig, wspace); //run with no signal contamination

  if (switches["doFeldmanCousins"]) feldmanCousins(data, modelConfig, wspace); //takes 7 minutes
  if (switches["doBayesian"]) bayesian(data, modelConfig, wspace); //use BayesianCalculator (only 1-d parameter of interest, slow for this problem)
  if (switches["doMCMC"]) mcmc(data, modelConfig, wspace); //use MCMCCalculator (takes about 1 min)

  if (switches["fixQcdToZero"]) {
    double d_s = setSignalVars(strings, switches, wspace, m0, m12, inputData["lumi"], inputData["sigma_SigEff"]);
    bool isInInterval = profileLikelihood(data, modelConfig, wspace, d_s);
    
    TH2F *exampleHisto = loYieldHisto(strings["muonControlFile"], strings["muonControlDir1"], strings["muonControlLoYield"], inputData["lumi"]);
    writeExclusionLimitPlot(exampleHisto, strings["plotFileName"], m0, m12, isInInterval);
  }
  else {
    std::cerr << "ERROR: Signal contamination is not yet handled when QCD is not fixed to zero." << std::endl;
  }

  t.Print();

  checkMap(nSwitches, switches.size(),"switches");
  checkMap(nStrings, strings.size(), "strings");
  checkMap(nData, inputData.size(), "inputData");
}
