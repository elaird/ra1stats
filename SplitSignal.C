#include "RooStats/ProfileLikelihoodCalculator.h"
#include "RooStats/LikelihoodInterval.h"
#include "RooStats/LikelihoodIntervalPlot.h"
#include "RooStats/BayesianCalculator.h"
#include "RooStats/MCMCCalculator.h"
#include "RooStats/MCMCInterval.h"
#include "RooStats/MCMCIntervalPlot.h"
#include "RooStats/ProposalHelper.h"
#include "RooStats/SimpleInterval.h"
#include "RooStats/FeldmanCousins.h"
#include "RooStats/PointSetInterval.h"
#include "RooStats/HypoTestResult.h"
#include "RooRealVar.h"
#include "RooGlobalFunc.h"
#include "RooRandom.h"

#include "RobsPdfFactory.cxx"



RooStats::ModelConfig* modelConfiguration(RooWorkspace* wspace) {
  /////////////////////////////////////////////////////
  // model config
  ModelConfig* modelConfig = new ModelConfig("Combine");
  modelConfig->SetWorkspace(*wspace);
  modelConfig->SetPdf( *wspace->pdf("TopLevelPdf"));
  // modelConfig->SetPriorPdf(*wspace->pdf("prior"));
  modelConfig->SetParametersOfInterest(*wspace->set("poi"));
  modelConfig->SetNuisanceParameters(*wspace->set("nuis"));
  wspace->import(*modelConfig);
  wspace->writeToFile("Combine.root");
  ///////////////////////////////////////////////////////

  return modelConfig;
}

void constrainParameters(RooWorkspace* wspace) {
  wspace->pdf("TopLevelPdf")->fitTo(*wspace->data("ObservedNumberCountingDataWithSideband"));

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


bool profileLikelihood(RooStats::ModelConfig* modelConfig, RooWorkspace* wspace, double d_s = 0.0) {

bool isInInterval = false;
  
  RooStats::ProfileLikelihoodCalculator plc(*wspace->data("ObservedNumberCountingDataWithSideband"), *modelConfig);
  plc.SetConfidenceLevel(0.95);
  RooStats::LikelihoodInterval* plInt = plc.GetInterval();

  Double_t lowerLimit = plInt->LowerLimit( *wspace->var("masterSignal") );
  Double_t upperLimit = plInt->UpperLimit( *wspace->var("masterSignal") );

  if (d_s<=1.0) {
    RooStats::LikelihoodIntervalPlot* lrplot = new RooStats::LikelihoodIntervalPlot(plInt);
    lrplot->Draw();
    
    cout << "Profile Likelihood interval on s = ["
	 << lowerLimit << ", "
	 << upperLimit << "]" << endl;
    
    //Profile Likelihood interval on s = [12.1902, 88.6871]
  }
  else {
    RooRealVar* tmp_s = wspace->var("poi");
    cout << " upper limit " << plInt->UpperLimit(*tmp_s) << endl;
    tmp_s->setVal(d_s);
    isInInterval = plInt->IsInInterval(*tmp_s);
  }

  return isInInterval;
}




void feldmanCousins(RooStats::ModelConfig* modelConfig, RooWorkspace* wspace) {
  //setup for Felman Cousins
  RooStats::FeldmanCousins fc(*wspace->data("ObservedNumberCountingDataWithSideband"), *modelConfig);
  fc.SetConfidenceLevel(0.95);
  //number counting: dataset always has 1 entry with N events observed
  fc.FluctuateNumDataEntries(false); 
  fc.UseAdaptiveSampling(true);
  fc.AdditionalNToysFactor(4);

  fc.SetNBins(40);
  RooStats::PointSetInterval* fcInt = (RooStats::PointSetInterval*) fc.GetInterval();

  Double_t lowerLimit = fcInt->LowerLimit( *wspace->var("masterSignal") );
  Double_t upperLimit = fcInt->UpperLimit( *wspace->var("masterSignal") );

  cout << "Feldman Cousins interval on s = ["
       << lowerLimit << ", "
       << upperLimit << "]" << endl;
  //Feldman Cousins interval on s = [18.75 +/- 2.45, 83.75 +/- 2.45]
 
}


void SplitSignal(Int_t method = 5){
  //if method == 1 EWK only
  //if method == 2 incl only (linear)
  //if method == 3 incl only (exp)
  //if method == 4 incl + EWK (linear)
  //if method == 5 incl + EWK (exp)

   // set RooFit random seed for reproducible results
  RooRandom::randomGenerator()->SetSeed(4357);

  //mSUGRA
  Double_t s[2] = {0.25,0.75};//how signal is split

  Double_t signal_sys = 0.12;
  Double_t muon_sys = 0.3;
  Double_t phot_sys = 0.4;

  Double_t bkgd_sideband[4] = {33,11,8,5};
  Double_t bkgd_bar_sideband[4] = {844459,331948,225649,110034};

  Double_t mainMeas[2] = {8,5};
  Double_t muonMeas[2] = {5,2};
  Double_t photMeas[2] = {6,1};
  Double_t tau_muon[2] = {1.2,1.1};
  Double_t tau_phot[2] = {1.7,1.4};

  /*Double_t mainMeas[1] = {13};
  Double_t muonMeas[1] = {7};
  Double_t photMeas[1] = {7};
  Double_t tau_muon[1] = {1.2};
  Double_t tau_phot[1] = {1.6};
  */

  //MyPdfFactory f;

  
  RobsPdfFactory f;
  RooWorkspace* wspace = new RooWorkspace();
 
  if(method == 1) {//EWK only
    f.AddModel_EWK(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_EWK(mainMeas,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
  if(method == 2) {//incl linear
    f.AddModel_Lin(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband(  bkgd_sideband,bkgd_bar_sideband,4,wspace,"ObservedNumberCountingDataWithSideband"); 
  }
  if(method == 3) {//incl exponential
    f.AddModel_Exp(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband(  bkgd_sideband,bkgd_bar_sideband,4,wspace,"ObservedNumberCountingDataWithSideband"); 
  }
  if(method == 4) {//incl + EWK linear
    f.AddModel_Lin_Combi(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
  if(method == 5) {//incl. + EWK exponential
    f.AddModel_Exp_Combi(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
  if(method == 6) {//incl.(one bin) + EWK (two bins) linear
    f.AddModel_Lin_Combi_one(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi_one(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
    

   constrainParameters(wspace);

   RooStats::ModelConfig* modelConfig = modelConfiguration(wspace);

   profileLikelihood(modelConfig,wspace);

   feldmanCousins(modelConfig,wspace);


   //wspace->Print("v");
  
 
    

  

  


  delete wspace;
  







}
