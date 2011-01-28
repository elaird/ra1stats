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

TH2F* yieldPlot(TString mSuGraFile,TString mSuGraDir, TString mSuGraHist){
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile);
  TDirectory* dir = (TDirectory*)f->Get(mSuGraDir);
  
  TH2F* hnev = (TH2F*)dir->Get(mSuGraHist);

  return hnev;
}

//a little plotting routine to calculate the NLO cross-section
TH2F* sysPlot(TString mSuGraFile){
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile);
  TDirectory* dir = (TDirectory*)f->Get("mSuGraScan_beforeAll");
  TDirectory* dir2 = (TDirectory*)f->Get("mSuGraScan_350");
  
  TH2F* gg = (TH2F*)dir2->Get("m0_m12_gg_0");
  TH2F* gg_noweight = (TH2F*)dir->Get("m0_m12_gg_5");
  TH2F* sb = (TH2F*)dir2->Get("m0_m12_sb_0");
  TH2F* sb_noweight = (TH2F*)dir->Get("m0_m12_sb_5");
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
  TH2F* ng = (TH2F*)dir2->Get("m0_mg12_ng_0");                                                               
  TH2F* ng_noweight = (TH2F*)dir->Get("m0_m12_ng_5");
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

using namespace RooFit;
using namespace RooStats;

void Lepton(TString& outputPlotFileName,
	    TString& outputWorkspaceFileName,

	    TString& mSuGraFile_signal,
	    TString& mSuGraFile_muoncontrol,
	    TString& mSuGraDir_muoncontrol,
	    TString& mSuGraHist_muoncontrol,
	    TString& mSuGraFile_sys05,
	    TString& mSuGraFile_sys2,

	    int m0, int m12, double lumi,
	    bool doBayesian=false, bool doFeldmanCousins=false, bool doMCMC=false
	    ) {

  // let's time this challenging example
  TStopwatch t;
  t.Start();

  //Define output file 
  TFile* output = new TFile(outputPlotFileName,"RECREATE");
  if( !output || output->IsZombie()){
    cout << " zombie alarm output is a zombie " << std::endl; 
    return;
  }
  
  // set RooFit random seed for reproducible results
  RooRandom::randomGenerator()->SetSeed(4357);

  //*************************************************************************************************************************************************************
  //set all necessary numbers as obtained from measurements or Monte Carlo studies
  //*******************************************************************************************************
  Double_t n_signal_ = 13; //number of events measured at HT > 350 GeV and alphaT > 0.55
  Double_t n_bar_signal_ = 336044; //number of events measured at HT > 350 GeV and alphaT < 0.55
  Double_t n_control_1_ = 11; //number of events measured at 300 < HT < 350 GeV and alphaT > 0.55
  Double_t n_bar_control_1_ = 332265; //number of events measured at 300 < HT < 350 GeV and alphaT < 0.55
  Double_t n_control_2_ = 33; //number of events measured at 250 < HT < 300 GeV and alphaT  > 0.55
  Double_t n_bar_control_2_ = 845157; //number of events measured at 250 < HT < 300 GeV and alphaT < 0.55

  Double_t sigma_x_ =0.11;//systematic uncertainty on inclusive background estimation (uncertainty on the assumpotion that rhoprime = rho*rho

  Double_t n_muoncontrol_ = 7;//number of events measured in muon control sample
  Double_t n_tau_mu_ = 5.9/5.1; //Monte Carlo estimation of the factor tau which relates expected events in muon control sample to expected tt+W background in signal-like region
  Double_t sigma_ttW_ = 0.3; //systematic uncertainty on tt+W background estimation

  //numbers for photon contorl sample
  Double_t n_photoncontrol_ = 7;//number of events measured in photon control sample
  Double_t n_tau_photon_ = 6.5/4.1;//Monte Carlo estimation of the factor tau which relates expected events in photon control sample to expected Zinv background in signal-like region
  Double_t sigma_Zinv_ = 0.4;//systematic uncertainty on Zinv background estimation

  Double_t sigma_SigEff_ = 0.12;//systematic uncertainty on signal acceptance*efficiency*luminosity //added single uncertainties quadratically

  //____________________________________________________________________________________________________
  //Put numbers into RooRealVars
  //____________________________________________________________________________________________________
  //number of events measured in signal-like region alphaT > 0.55 ; HT > 350 GeV; and no leptons or photons
  RooRealVar n_signal("n_signal","n_signal",n_signal_,n_signal_/10,n_signal_*10);

  //number of events measured in muon and photon conrol samples
  RooRealVar n_muoncontrol("n_muoncontrol","n_muoncontrol",n_muoncontrol_,0.001,n_muoncontrol_*10);//number of measured events in muon control sample
  RooRealVar n_photoncontrol("n_photoncontrol","n_photoncontrol",n_photoncontrol_,0.001,n_photoncontrol_*10);//number of measured events in photon control sample
  //Parameter of interest; the number of (SUSY) signal events above the Standard Model background
  RooRealVar s("s","s",2.5,0.0001,n_signal_*3);//expected numer of (SUSY) signal events above background 
  //Nuisance parameters
  RooRealVar TTplusW("TTplusW","TTplusW",n_signal_/2,0.01,n_signal_*10); //expected tt+W background in signal-like region
  RooRealVar ZINV("ZINV","ZINV",n_signal_/2,0.001,n_signal_*10);//expected Zinv background in signal-like region  

  //Nuisance parameter for tt+W estimation
  RooRealVar tau_mu("tau_mu","tau_mu",n_tau_mu_);
  RooRealVar sigma_ttW("sigma_ttW","sigma_ttW",sigma_ttW_);
  //Nuisance parameter for Zinv estiamtion
  RooRealVar tau_photon("tau_photon","tau_photon",n_tau_photon_); 
  RooRealVar sigma_Zinv("sigma_Zinv","sigma_Zinv",sigma_Zinv_);
  //Systematic uncertainty on singal*acceptance*efficiency*luminosity
  RooRealVar sigma_SigEff("sigma_SigEff","sigma_SigEff",sigma_SigEff_);
 
  // make model
  RooWorkspace* wspace = new RooWorkspace("Combine");



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
 
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  //set up Total likelihood function
  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

  
 
  RooRealVar* ratioSigEff = wspace->var("ratioSigEff");
  RooRealVar* ratioBkgdEff_1 = wspace->var("ratioBkgdEff_1");
  RooRealVar* ratioBkgdEff_2 = wspace->var("ratioBkgdEff_2");
 
  RooArgSet constrainedParams(*ratioBkgdEff_1,*ratioBkgdEff_2,*ratioSigEff);


  /////////////////////////////////////////////////////
  //set values of observables
   
  const RooArgSet* lolArgSet=wspace->set("obs");
  RooArgSet* newSet=new RooArgSet(*lolArgSet);
  newSet->setRealValue("n_signal",n_signal_);
  //set observables for muon control method
  newSet->setRealValue("n_muoncontrol"    ,n_muoncontrol_); 
  //set observable for photon control method
  newSet->setRealValue("n_photoncontrol"    ,n_photoncontrol_);
  

  RooDataSet *data=new RooDataSet("obsDataSet","title",*lolArgSet);
  data->Print();
  data->add(*lolArgSet);
  wspace->import(*data);


  /////////////////////////////////////////////////////
  // Now the statistical tests
  // model config
  ModelConfig* modelConfig = new ModelConfig("Combine");
  modelConfig->SetWorkspace(*wspace);
  modelConfig->SetPdf(*wspace->pdf("total_model"));
  modelConfig->SetPriorPdf(*wspace->pdf("prior"));
  modelConfig->SetParametersOfInterest(*wspace->set("poi"));
  modelConfig->SetNuisanceParameters(*wspace->set("nuis"));
  wspace->import(*modelConfig);

  wspace->writeToFile(outputWorkspaceFileName.Data());

  //////////////////////////////////////////////////
  // If you want to see the covariance matrix uncomment
  /* wspace->pdf("total_model")->fitTo(*data,RooFit::Constrain(constrainedParams));

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
  */  

  RooRealVar* mu = wspace->var("s");
  RooArgSet* nullParams = new RooArgSet("nullParams");
  nullParams->addClone(*mu);
  nullParams->setRealValue("s",0);

   //setup for ProfileLikelihood
  ProfileLikelihoodCalculator plc(*data, *modelConfig);
  plc.SetConfidenceLevel(0.95);
  
  LikelihoodInterval* plInt = plc.GetInterval();
  
  //setup for Felman Cousins
  FeldmanCousins fc(*data, *modelConfig);
  fc.SetConfidenceLevel(0.95);
  //number counting: dataset always has 1 entry with N events observed
  fc.FluctuateNumDataEntries(false); 
  fc.UseAdaptiveSampling(true);
  fc.SetNBins(50);
  PointSetInterval* fcInt = NULL;
  if(doFeldmanCousins){ // takes 7 minutes
    fcInt = (PointSetInterval*) fc.GetInterval(); // fix cast
  }
  
  // use BayesianCalculator (only 1-d parameter of interest, slow for this problem)  
  BayesianCalculator bc(*data, *modelConfig);
  bc.SetConfidenceLevel(0.95);
  SimpleInterval* bInt = NULL;
  if(doBayesian && wspace->set("poi")->getSize() == 1)   {
    bInt = bc.GetInterval();
  } else{
    cout << "Bayesian Calc. only supports on parameter of interest" << endl;
  }
  
  
  // use MCMCCalculator  (takes about 1 min)
  // Want an efficient proposal function, so derive it from covariance
  // matrix of fit
  RooFitResult* fit = wspace->pdf("total_model")->fitTo(*data,Save());
  ProposalHelper ph;
  ph.SetVariables((RooArgSet&)fit->floatParsFinal());
  ph.SetCovMatrix(fit->covarianceMatrix());
  ph.SetUpdateProposalParameters(kTRUE); // auto-create mean vars and add mappings
  ph.SetCacheSize(100);
  ProposalFunction* pf = ph.GetProposalFunction();
  
  MCMCCalculator mc(*data, *modelConfig);
  mc.SetConfidenceLevel(0.95);
  mc.SetProposalFunction(*pf);
  mc.SetNumBurnInSteps(200); // first N steps to be ignored as burn-in
  mc.SetNumIters(20000000);
  mc.SetLeftSideTailFraction(0.5); // make a central interval
  MCMCInterval* mcInt = NULL;
  if(doMCMC)
    mcInt = mc.GetInterval();
  

  //////////////////////////////////////
  // Make some  plots
  TCanvas* c1 = (TCanvas*) gROOT->Get("c1");  
  if(!c1)
    c1 = new TCanvas("c1");
  
  if(doBayesian && doMCMC){
    c1->Divide(3);
    c1->cd(1);
  }
  else if (doBayesian || doMCMC){
    c1->Divide(2);
    c1->cd(1);
  }
  
  LikelihoodIntervalPlot* lrplot = new LikelihoodIntervalPlot(plInt);
  lrplot->Draw();
  

  double upperlimit = 0;

  cout << " Limit " << endl;
  ////////////////////////////////////
  // querry intervals
  cout << "Profile Likelihood interval on s = [" << 
    plInt->LowerLimit( *wspace->var("s") ) << ", " <<
    plInt->UpperLimit( *wspace->var("s") ) << "]" << endl; 
  upperlimit = plInt->UpperLimit( *wspace->var("s") );
  //Profile Likelihood interval on s = [12.1902, 88.6871]
  
  if(doBayesian && wspace->set("poi")->getSize() == 1)   {
    cout << "Bayesian interval on s = [" << 
      bInt->LowerLimit( ) << ", " <<
      bInt->UpperLimit( ) << "]" << endl;
    upperlimit = bInt->UpperLimit( );
  }  
  
  if(doFeldmanCousins){    
    cout << "Feldman Cousins interval on s = [" << 
      fcInt->LowerLimit( *wspace->var("s") ) << ", " <<
      fcInt->UpperLimit( *wspace->var("s") ) << "]" << endl;
    //Feldman Cousins interval on s = [18.75 +/- 2.45, 83.75 +/- 2.45]
    upperlimit = 	fcInt->UpperLimit( *wspace->var("s") );
  }
  
  if(doMCMC){
    cout << "MCMC interval on s = [" << 
      mcInt->LowerLimit(*wspace->var("s") ) << ", " <<
      mcInt->UpperLimit(*wspace->var("s") ) << "]" << endl;
    upperlimit = 	mcInt->UpperLimit(*wspace->var("s") );
    //MCMC interval on s = [15.7628, 84.7266]
    
  }
  
 
    //output root file
  TH2F* exclusionLimits = new TH2F("ExclusionLimit","ExclusionLimit",100,0,1000,40,100,500);

  TH2F* yield_signal = sysPlot(mSuGraFile_signal);//event yields in signal like region
  TH2F* yield_muoncontrol =  yieldPlot(mSuGraFile_muoncontrol, mSuGraDir_muoncontrol, mSuGraHist_muoncontrol);
  TH2F* yield_sys05 = sysPlot(mSuGraFile_sys05);//NLO modified 0.5
  TH2F* yield_sys2 = sysPlot(mSuGraFile_sys2); //NLO modified 2

  
  
  bool mytry = false;

 
  double tau_s_muon = 1;

  output->cd();
  
  mytry = false;
  
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
  
  
  
  if(d_s > 1 && mytry == false){
    bool isInInterval = true;
    
    plInt = (LikelihoodInterval*)plc.GetInterval();
    
    RooRealVar* tmp_s = wspace->var("s");
    
    cout << " upper limit " << plInt->UpperLimit(*tmp_s) << endl;
    tmp_s->setVal(d_s);
    isInInterval = plInt->IsInInterval(*tmp_s);
    
    if(isInInterval == false){
      mytry = true;//if one point is excluded assume that the points in m12 below this point are also excluded, have been tested to be true and makes the code faster
      exclusionLimits->SetBinContent(m0+1,m12,1);//if one point which is excluded is found set the output point to 1	 
    }
    else{
      exclusionLimits->SetBinContent(m0+1,m12,0);//if not set it to 0	 
    }
    
    delete plInt;
  }
  if(mytry == true){
    exclusionLimits->SetBinContent(m0+1,m12,1);
  }
  
  t.Print();

  exclusionLimits->Write();

  output->cd();
  output->Write();
  output->Close();
  
   

}
