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
    f.AddModel_EWK(s,signal_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_EWK(mainMeas,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
  if(method == 2) {//incl linear
    f.AddModel_Lin(s,signal_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband(  bkgd_sideband,bkgd_bar_sideband,4,wspace,"ObservedNumberCountingDataWithSideband"); 
  }
  if(method == 3) {//incl exponential
    f.AddModel_Exp(s,signal_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband(  bkgd_sideband,bkgd_bar_sideband,4,wspace,"ObservedNumberCountingDataWithSideband"); 
  }
  if(method == 4) {//incl + EWK linear
    f.AddModel_Lin_Combi(s,signal_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
  if(method == 5) {//incl. + EWK combi
    f.AddModel_Exp_Combi(s,signal_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
  if(method == 6) {
    f.AddModel_Lin_Combi_one(s,signal_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi_one(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
    


  //Constrain some parameters (only necessary for combination of incl. and EWK)
  wspace->pdf("TopLevelPdf")->fitTo(*wspace->data("ObservedNumberCountingDataWithSideband"));

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



  
  wspace->Print("v");
  
  RooRealVar* mu = wspace->var("masterSignal");
  RooArgSet* poi = new RooArgSet(*mu);
  RooArgSet* nullParams = new RooArgSet("nullParams");
  nullParams->addClone(*mu);
  nullParams->setRealValue("masterSignal",0);

  RooStats::ProfileLikelihoodCalculator plc(*wspace->data("ObservedNumberCountingDataWithSideband"), *wspace->pdf("TopLevelPdf"),*poi,0.05,nullParams);

				   // ProfileLikelihoodCalculator plc(*data,				  *wspace->pdf("TopLevelPdf"),*poi,0.05,nullParams);

  //wspace->pdf("TopLevelPdf")->fitTo(*wspace->data("ObservedNumberCountingDataWithSideband"));

  //Step 6, Use the calculator to get a HypoTestResult
  RooStats::HypoTestResult* htr = plc.GetHypoTest();
  assert(htr!=0);
  cout << "++++++++++++++++++++++++++++++++++++++++++++"<< endl;
  cout << " the p-value for the null is " << htr->NullPValue() << endl;
  cout << " corresponding to a significance of " << htr->Significance() << endl;
  cout << "++++++++++++++++++++++++++++++++++++++++++++" << endl;
  
  ///////////////////////////////////////////////////////////////////////////
  //Step 8 here we reuse the ProfileLikelihoodCalculator to return a confidence interval
  //we need to specify what our parameters of interest are
  RooArgSet* paramsOfInterest = nullParams;//they are the same as before
  plc.SetParameters(*paramsOfInterest);
  RooStats::LikelihoodInterval* lrint = (RooStats::LikelihoodInterval*)plc.GetInterval();
  lrint->SetConfidenceLevel(0.95);
  
  //Step 9 make a plot of the likelihood ratio and the interval obtained 
  double lower = lrint->LowerLimit(*mu);
  double upper = lrint->UpperLimit(*mu);
  
  RooStats::LikelihoodIntervalPlot lrPlot(lrint);
  lrPlot.SetMaximum(3.);
  lrPlot.Draw();
  
  //Step 10 print upper and lower limits
  cout << " lower limit on master signal " << lower << endl;
  cout << " upper limit on master signal " << upper << endl;
    

  

  


  delete wspace;
  







}
