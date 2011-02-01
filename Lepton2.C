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

TH2F* yieldPlot(std::string& mSuGraFile,std::string& mSuGraDir, std::string& mSuGraHist) {
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile.c_str());
  TDirectory* dir = (TDirectory*)f->Get(mSuGraDir.c_str());
  
  TH2F* hnev = (TH2F*)dir->Get(mSuGraHist.c_str());

  return hnev;
}

//a little plotting routine to calculate the NLO cross-section
TH2F* sysPlot(std::string& mSuGraFile, std::string& mSuGraDir1, std::string& mSuGraDir2) {
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile.c_str());
  TDirectory* dir = (TDirectory*)f->Get(mSuGraDir1.c_str());
  TDirectory* dir2 = (TDirectory*)f->Get(mSuGraDir2.c_str());
  
  TH2F* gg = (TH2F*)dir2->Get("m0_m12_gg_0");
  TH2F* gg_noweight = (TH2F*)dir->Get("m0_m12_gg_5");
  TH2F* sb = (TH2F*)dir2->Get("m0_m12_sb_0");
  //TH2F* sb_noweight = (TH2F*)dir->Get("m0_m12_sb_5");
  TH2F* ss = (TH2F*)dir2->Get("m0_m12_ss_0");
  TH2F* ss_noweight = (TH2F*)dir->Get("m0_m12_ss_5");
  TH2F* sg = (TH2F*)dir2->Get("m0_m12_sg_0");
  TH2F* sg_noweight = (TH2F*)dir->Get("m0_m12_sg_5");
  TH2F* ll = (TH2F*)dir2->Get("m0_m12_ll_0");
  TH2F* ll_noweight = (TH2F*)dir->Get("m0_m12_ll_5");
  TH2F* nn = (TH2F*)dir2->Get("m0_m12_nn_0");
  TH2F* nn_noweight = (TH2F*)dir->Get("m0_m12_nn_5");
  TH2F* ns = (TH2F*)dir2->Get("m0_m12_ns_0");
  TH2F* ns_noweight = (TH2F*)dir->Get("m0_m12_ns_5");
  //TH2F* ng = (TH2F*)dir2->Get("m0_mg12_ng_0");                                                               
  //TH2F* ng_noweight = (TH2F*)dir->Get("m0_m12_ng_5");
  TH2F* bb = (TH2F*)dir->Get("m0_m12_bb_0");
  TH2F* bb_noweight = (TH2F*)dir->Get("m0_m12_bb_5");
  TH2F* tb = (TH2F*)dir->Get("m0_m12_tb_0");
  TH2F* tb_noweight = (TH2F*)dir->Get("m0_m12_tb_5");
  
  gg->Divide(gg_noweight);
  sb->Divide(sg_noweight);
  ss->Divide(ss_noweight);
  sg->Divide(sg_noweight);
  ll->Divide(ll_noweight);
  nn->Divide(nn_noweight);
  //ng->Divide(ng_noweight);
  bb->Divide(bb_noweight);
  tb->Divide(tb_noweight);
  ns->Divide(ns_noweight);

  TH2F* all = (TH2F*)gg->Clone();
  all->Add(sb);
  all->Add(ss);
  all->Add(sg);
  all->Add(ll);
  all->Add(nn);
  //all->Add(ng);
  all->Add(bb);
  all->Add(tb);
  all->Add(ns);

  all->Scale(100);
  
  
 

  return all;
}


//A word of explanation before starting
//The RA1 analysis uses three kinds of background estimation 
//one estimates the combined tt+W background from a muon control auxiliary measurement
// assumption the expected background in the muon control sample is tau_mu*TTplusW (expected tt+W background in signal-like region)
//one estimates the Zinv background from a photon control auxiliary measurement
// assumption the expected background in the photon control sample is tau_photon*ZINV (expected Zinv background in signal-like region)
//one estimates the total background (tt+W+Zinv+QCD) using low HT and low alphaT control measurement

RooWorkspace* workspace() {
  return new RooWorkspace("Combine");
}

void setupLikelihood(RooWorkspace* wspace) {
  //likelihood for the signal region
  //a poisson to include the statistic uncertainty
  wspace->factory("Poisson::signal(n_signal,sum::splusb(sum::b(prod::ttW(ratioBkgdEff_1[1.0,0.,5.],TTplusW),prod::Zinv(ratioBkgdEff_2[1.0,0.,5.],ZINV)),prod::SigUnc(s,ratioSigEff[1,0.3,1.9])))");
  //gaussians to include the systematic uncertainties on the background estimations and the signal acceptance*efficiency*luminosity
  wspace->factory("Gaussian::sigConstraint(1.,ratioSigEff,sigma_SigEff)");
  wspace->factory("Gaussian::mcCons_ttW(1.,ratioBkgdEff_1,sigma_ttW)"); 
  wspace->factory("Gaussian::mcCons_Zinv(1.,ratioBkgdEff_2,sigma_Zinv)");
  wspace->factory("PROD::signal_model(signal,sigConstraint,mcCons_ttW,mcCons_Zinv)");
  //set pdf for muon control 
  wspace->factory("Poisson::muoncontrol(n_muoncontrol,sum::MuSPlusB(prod::TTWside(tau_mu,TTplusW),prod::smu(tau_s_mu[0.001],s)))");
  //set pdf for photon control
  wspace->factory("Poisson::photoncontrol(n_photoncontrol,prod::sideband_photon(tau_photon,ZINV))");
  //combine the three
  wspace->factory("PROD::total_model(signal_model,muoncontrol,photoncontrol)");
  // to use for bayesian methods
  wspace->factory("Uniform::prior_poi({s})");
  wspace->factory("Uniform::prior_nuis({TTplusW,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff})"); 
  wspace->factory("PROD::prior(prior_poi,prior_nuis)");
  //define some sets to use later (plots)
  wspace->defineSet("obs","n_signal,n_muoncontrol,n_photoncontrol"); 
  wspace->defineSet("poi","s");
  wspace->defineSet("nuis","TTplusW,ZINV,ratioBkgdEff_1,ratioBkgdEff_2,ratioSigEff");
}

RooDataSet* importVars(RooWorkspace* wspace, std::map<std::string,double>& inputData) {
  RooRealVar n_signal("n_signal", "n_signal", inputData["n_signal"], inputData["n_signal"]/10, inputData["n_signal"]*10);
  RooRealVar n_muoncontrol("n_muoncontrol", "n_muoncontrol", inputData["n_muoncontrol"], 0.001, inputData["n_muoncontrol"]*10);
  RooRealVar n_photoncontrol("n_photoncontrol", "n_photoncontrol", inputData["n_photoncontrol"], 0.001, inputData["n_photoncontrol"]*10);

  //Parameter of interest; the number of (SUSY) signal events above the Standard Model background
  RooRealVar s("s", "s", 2.5, 0.0001, inputData["n_signal"]*3);//expected numer of (SUSY) signal events above background 
  //Nuisance parameters
  RooRealVar TTplusW("TTplusW", "TTplusW", inputData["n_signal"]/2, 0.01, inputData["n_signal"]*10); //expected tt+W background in signal-like region
  RooRealVar ZINV("ZINV", "ZINV", inputData["n_signal"]/2,0.001, inputData["n_signal"]*10);//expected Zinv background in signal-like region  

  //Nuisance parameter for tt+W estimation
  RooRealVar tau_mu("tau_mu", "tau_mu", inputData["tau_mu"]);
  RooRealVar sigma_ttW("sigma_ttW", "sigma_ttW", inputData["sigma_ttW"]);
  //Nuisance parameter for Zinv estiamtion
  RooRealVar tau_photon("tau_photon", "tau_photon", inputData["tau_photon"]); 
  RooRealVar sigma_Zinv("sigma_Zinv", "sigma_Zinv", inputData["sigma_Zinv"]);
  //Systematic uncertainty on singal*acceptance*efficiency*luminosity
  RooRealVar sigma_SigEff("sigma_SigEff", "sigma_SigEff", inputData["sigma_SigEff"]);
 
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

  setupLikelihood(wspace);

  //set values of observables
  const RooArgSet* lolArgSet=wspace->set("obs");
  RooArgSet* newSet = new RooArgSet(*lolArgSet);
  newSet->setRealValue("n_signal", inputData["n_signal"]);
  //set observables for muon control method
  newSet->setRealValue("n_muoncontrol", inputData["n_muoncontrol"]); 
  //set observable for photon control method
  newSet->setRealValue("n_photoncontrol", inputData["n_photoncontrol"]);
  
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

double setSignalVars(std::string& mSuGraFile_signal, std::string& mSuGraDir1_signal, std::string& mSuGraDir2_signal,
		     std::string& mSuGraFile_muoncontrol, std::string& mSuGraDir_muoncontrol, std::string& mSuGraHist_muoncontrol,
		     std::string& mSuGraFile_sys05,
		     std::string& mSuGraFile_sys2,
		     RooWorkspace* wspace,
		     int m0,
		     int m12,
		     double lumi,
		     double sigma_SigEff_
		     ) {
  
  TH2F* yield_signal = sysPlot(mSuGraFile_signal, mSuGraDir1_signal, mSuGraDir2_signal);//event yields in signal like region
  TH2F* yield_muoncontrol = yieldPlot(mSuGraFile_muoncontrol, mSuGraDir_muoncontrol, mSuGraHist_muoncontrol);
  TH2F* yield_sys05 = sysPlot(mSuGraFile_sys05, mSuGraDir1_signal, mSuGraDir2_signal);//NLO modified 0.5
  TH2F* yield_sys2 = sysPlot(mSuGraFile_sys2, mSuGraDir1_signal, mSuGraDir2_signal); //NLO modified 2

  double tau_s_muon = 1;

  Double_t d_s = yield_signal->GetBinContent(m0,m12)/100*lumi;
  Double_t d_s_sys05 = yield_sys05->GetBinContent(m0,m12)/100*lumi;//the event yield if the NLO factorizaiton and renormalizaiton are varied by a factor of 0.5
  Double_t d_s_sys2 = yield_sys2->GetBinContent(m0,m12)/100*lumi;//the event yield if the NLO factorizaiton and renormalizaiton are varied by a factor of 2
  Double_t masterPlus = 0;
  Double_t masterMinus = 0;
  Double_t signal_sys = sigma_SigEff_;
  
  if(d_s > 0){
    tau_s_muon = yield_muoncontrol->GetBinContent(m0,m12)/yield_signal->GetBinContent(m0,m12); 
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

TH2F *histoWithBinning(std::string& mSuGraFile_muoncontrol,
		       std::string& mSuGraDir_muoncontrol,
		       std::string& mSuGraHist_muoncontrol
		       ) {
  TFile f(mSuGraFile_muoncontrol.c_str());
  TH2F *h = (TH2F*)f.Get((mSuGraDir_muoncontrol+"/"+mSuGraHist_muoncontrol).c_str());
  TString name = h->GetName();
  name += "_clone";
  TH2F *g = (TH2F*)h->Clone(name);
  g->SetDirectory(0);
  f.Close();
  return g;
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

  output.cd();
  output.Close();
}

void checkMap(int nInitial, int nFinal) {
  if (nInitial!=nFinal) std::cerr << "ERROR: nInitial = " << nInitial << "; nFinal = " << nFinal << std::endl;  
}

void Lepton2(std::map<std::string,int>& switches,
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

  RooDataSet* data = importVars(wspace, inputData);

  RooRealVar* ratioSigEff = wspace->var("ratioSigEff");
  RooRealVar* ratioBkgdEff_1 = wspace->var("ratioBkgdEff_1");
  RooRealVar* ratioBkgdEff_2 = wspace->var("ratioBkgdEff_2");
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

  double d_s = setSignalVars(strings["signalFile"], strings["signalDir1"], strings["signalDir2"],
			     strings["muonControlFile"], strings["muonControlDir"], strings["muonControlHist"],
			     strings["sys05File"], strings["sys2File"],
			     wspace, m0, m12, inputData["lumi"], inputData["sigma_SigEff"]
			     );
  
  bool isInInterval = profileLikelihood(data, modelConfig, wspace, d_s);
  
  TH2F *exampleHisto = histoWithBinning(strings["muonControlFile"], strings["muonControlDir"], strings["muonControlHist"]);
  writeExclusionLimitPlot(exampleHisto, strings["plotFileName"], m0, m12, isInInterval);
  t.Print();

  checkMap(nSwitches, switches.size());
  checkMap(nStrings, strings.size());
  checkMap(nData, inputData.size());
}
