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

#include "TStyle.h"

#include "PlottingStuff.cxx"

#include "RobsPdfFactory.cxx"


RooStats::ModelConfig* modelConfiguration(RooWorkspace* wspace) {
  /////////////////////////////////////////////////////
  // model config
  ModelConfig* modelConfig = new ModelConfig("Combine");
  modelConfig->SetWorkspace(*wspace);
  modelConfig->SetPdf( *wspace->pdf("TopLevelPdf"));
  modelConfig->SetObservables (*wspace->set("obs"));
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
  cout << " try " << endl;
  //some limitations good for fitting
  RooArgList nuispar(*wspace->set("nuis"));
  cout << " heer e" << endl;
  for(int i = 0; i < nuispar.getSize();++i){
    cout << " i " << endl;
    RooRealVar &par = (RooRealVar&) nuispar[i];
    par.setMin(std::max(par.getVal()-5*par.getError(),par.getMin() ) );
    par.setMax(std::min(par.getVal()+5*par.getError(),par.getMax() ) );
  }
  RooArgList poipar(*wspace->set("poi"));
  for(int i = 0; i < poipar.getSize();++i){
    RooRealVar &spar = (RooRealVar&) poipar[i];
    spar.setMin(std::max(spar.getVal()-10*spar.getError(),spar.getMin() ) );
    spar.setMax(std::min(spar.getVal()+10*spar.getError(),spar.getMax() ) );
  }
}


bool updateLikelihood(RooStats::ProfileLikelihoodCalculator* plc,RooWorkspace* wspace,double d_s = 0.0){

  cout << " d_s " << d_s << endl;

  bool isInInterval = false;

  RooStats::LikelihoodInterval *plInt = (LikelihoodInterval*)plc->GetInterval();
  RooRealVar* tmp_s = wspace->var("masterSignal");

  Double_t lowerLimit = plInt->LowerLimit( *tmp_s );
  cout << " lower LImit " << lowerLimit <<  endl;
  
  Double_t upperLimit = plInt->UpperLimit( *tmp_s );
  cout << " upper limit " << upperLimit << endl;

  
 
  tmp_s->setVal(d_s);
  isInInterval = plInt->IsInInterval(*tmp_s);
  
  delete plInt;

  cout << " is in " << isInInterval << endl;

  return isInInterval;


}

ProfileLikelihoodCalculator* profileLikelihood(RooStats::ModelConfig* modelConfig, RooWorkspace* wspace, double d_s = 0.0) {

bool isInInterval = false;
  
  RooStats::ProfileLikelihoodCalculator* plc = new ProfileLikelihoodCalculator(*wspace->data("ObservedNumberCountingDataWithSideband"), *modelConfig);
  plc->SetConfidenceLevel(0.95);
  RooStats::LikelihoodInterval* plInt = plc->GetInterval();

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

  return plc;
}




bool feldmanCousins(RooStats::ModelConfig* modelConfig, RooWorkspace* wspace, double d_s = 0.0) {
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

  if(d_s < upperLimit) return true;

  return false;
 
}


void CLs(RooDataSet* data,RooStats::ModelConfig* modelConfig,RooWorkspace *wspace){

  RooWorkspace* myW = new RooWorkspace("myW");
  myW->factory("Uniform::f(m[0.,1])");
  myW->factory("ExtendPdf::px(f,sum::splusb([s[0,0,100],ttW[100,0,300],Zinv[100,0,300]))");
  myW->factory("Poisson::muon(mu_meas[100,0,500],prod::taub(tau[1.],ttW))");
  myW->factory("Poisson::photon(phot_meas[100,0,500],prod::tau1b(tau1[1.],Zinv))");
  myW->factory("PROD::model(px,muon,photon)");
  myW->factory("Uniform::prior_Zinv(Zinv)");
  myW->factory("Uniform::prior_ttW(ttW)");

  
  /*  ModelConfig b_model("B_model",*ws);
  b_model.SetPdf( *wspace->pdf("TopLevelPdf"));
  b_model.SetParametersOfInterest(*wspace->set("poi"));
  b_model.SetObservables(*wspace->set("obs"));
  b_model.var("masterSignal")->setVal(0.0);
  b_model.SetSnapshot(*ws->set("poi"));

  ModelConfig sb_model("B_model",*ws);
  sb_model.SetPdf( *wspace->pdf("TopLevelPdf"));
  sb_model.SetParametersOfInterest(*wspace->set("poi"));
  sb_model.SetObservables(*wspace->set("obs"));
  sb_model.var("masterSignal")->setVal(20.0);
  sb_model.SetSnapshot(*ws->set("poi")); 


  NumEventsTestStata eventCount(*myW->pdf("px"));
  */
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


void SplitSignal(Int_t method
	     ) {


  //void SplitSignal(Int_t method = 5,bool useProfile=1,bool useFeldmanCousin=1){
  //if method == 1 EWK only
  //if method == 2 incl only (linear)
  //if method == 3 incl only (exp)
  //if method == 4 incl + EWK (linear)
  //if method == 5 incl + EWK (exp)
  //if method == 6 incl + EWK (linear) 1bin inclusive
  //if method == 7 incl + EWK (exp) 1 bin inclusive


   // set RooFit random seed for reproducible results
  RooRandom::randomGenerator()->SetSeed(4357);

  //mSUGRA
  Double_t s[2] = {0.25,0.75};//how signal is split

  Double_t signal_sys = 0.12;
  Double_t muon_sys = 0.3;
  Double_t phot_sys = 0.4;

  Double_t bkgd_sideband[4] = {33,11,8,5};
  Double_t bkgd_bar_sideband[4] = {844459,331948,225649,110034};

  Double_t bkgd_sideband_3[3] = {33,11,13};
  Double_t bkgd_bar_sideband_3[3] = {844459,331948,335683};


  Double_t mainMeas[2] = {8,5};
  Double_t muonMeas[2] = {5,2};
  Double_t photMeas[2] = {6,1};
  Double_t tau_muon[2] = {1.2,1.1};
  Double_t tau_phot[2] = {1.7,1.4};

  Double_t mainMeas_1[1] = {13};
  Double_t muonMeas_1[1] = {7};
  Double_t photMeas_1[1] = {7};
  Double_t tau_muon_1[1] = {1.15};
  Double_t tau_phot_1[1] = {1.58};

  Double_t lumi = 1;
  Double_t lumi_sys = 0.11;
  
  Double_t accXeff = 1.;
  Double_t accXeff_sys = sqrt(pow(0.12,2) - pow(0.11,2) );
  

  //MyPdfFactory f;

  
  RobsPdfFactory f;
  RooWorkspace* wspace = new RooWorkspace("myWorkspace");
 
  if(method == 1) {//EWK only
    f.AddModel_EWK(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
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
    Double_t _lumi = 1;
    Double_t _lumi_sys = 0.18;
    Double_t _accXeff = 1.;
    Double_t _accXeff_sys = 0.01;
    Double_t _muon_sys = 0.3;
    Double_t _phot_sys = 0.4;
    Double_t _muon_cont_1 = 0.2;
    Double_t _muon_cont_2 = 0.2;
    Double_t _lowHT_cont_1 = 0.2;
    Double_t _lowHT_cont_2 = 0.2;

    f.AddModel_Lin_Combi(s,_lumi, _lumi_sys,
			 _accXeff,_accXeff_sys,
			 _muon_sys,_phot_sys,
			 _muon_cont_1,_muon_cont_2,
			 _lowHT_cont_1,_lowHT_cont_2,
			 wspace,"TopLevelPdf","masterSignal");

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
   if(method == 7) {//incl.(one bin) + EWK (two bins) linear
    f.AddModel_Exp_Combi_one(s,signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
    f.AddDataSideband_Combi_one(  bkgd_sideband,bkgd_bar_sideband,4,muonMeas,photMeas,tau_muon,tau_phot,2,wspace,"ObservedNumberCountingDataWithSideband");
  }
   if(method == 8){//incl. (one bin) 
     f.AddModel_Exp_one(signal_sys,2,wspace,"TopLevelPdf","masterSignal");
     f.AddDataSideband(  bkgd_sideband_3,bkgd_bar_sideband_3,3,wspace,"ObservedNumberCountingDataWithSideband"); 
   }
   if(method == 9){//incl. (one bin) + EWK (one bin) exp
     f.AddModel_Exp_Combi_both_one(signal_sys,muon_sys,phot_sys,2,wspace,"TopLevelPdf","masterSignal");
     f.AddDataSideband_Combi(  bkgd_sideband_3,bkgd_bar_sideband_3,3,muonMeas_1,photMeas_1,tau_muon_1,tau_phot_1,1,wspace,"ObservedNumberCountingDataWithSideband");
   }

  

   constrainParameters(wspace);

  

   RooStats::ModelConfig* modelConfig = modelConfiguration(wspace);

   profileLikelihood(modelConfig,wspace);

   // feldmanCousins(modelConfig,wspace);

   TString outputPlotName = "Significance_LO_observed_tanBeta10.root";
  

  //Define output file 
  TFile* output = new TFile(outputPlotName,"RECREATE");
  if( !output || output->IsZombie()){
    cout << " zombie alarm output is a zombie " << std::endl; 
    return;
  }


   TString dir = "./rootFiles/MsugraTanBeta10/";
   TString signal_file = dir+ "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta10.root";
   
   

   TString signal_dir_1 = "mSuGraScan_350_10";
   TString signal_dir_2 = "mSuGraScan_450_10";
   TString beforeAll_dir = "mSuGraScan_beforeAll_10";
   TString signal_hist = "m0_m12_mChi_0";

   TString muon_dir = "./rootFiles/MuonFinal/";
   TString muon_dir_1 = "mSuGraScan_350";
   TString muon_dir_2 = "mSuGraScan_450";
   TString muon_file = muon_dir + "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta10.root";
      
   TH2F* yield_signal_1 =  sysPlot(signal_file,signal_dir_1,beforeAll_dir);

   TH2F* yield_signal_2 = sysPlot(signal_file,signal_dir_2,beforeAll_dir);

   TH3F* yield_muon_1 = yieldPlot_3d(muon_file,muon_dir_1,signal_hist);
   TH3F* yield_muon_2 = yieldPlot_3d(muon_file,muon_dir_2,signal_hist);

   //output root file
   TH2F* exclusionLimits = new TH2F("ExclusionLimit","ExclusionLimit",yield_signal_1->GetXaxis()->GetNbins(),yield_signal_1->GetXaxis()->GetXmin(),yield_signal_1->GetXaxis()->GetXmax(),yield_signal_1->GetYaxis()->GetNbins(),yield_signal_1->GetYaxis()->GetXmin(),yield_signal_1->GetYaxis()->GetXmax());
 
 


   bool mytry = false;
   
   lumi = 35.;
   
  
   ProfileLikelihoodCalculator* plc = profileLikelihood(modelConfig,wspace);

   cout << " bin width x " << yield_signal_1->GetXaxis()->GetBinWidth(1) << " bin min " << yield_signal_1->GetXaxis()->GetXmin() << " bin max " << yield_signal_1->GetXaxis()->GetXmax() << endl;

   cout << " bin width y " << yield_signal_1->GetYaxis()->GetBinWidth(1) << " bin min " << yield_signal_1->GetYaxis()->GetXmin() << " bin max " << yield_signal_1->GetYaxis()->GetXmax() << endl;

   for(int m0 = 0; m0 < yield_signal_1->GetXaxis()->GetNbins();m0++){
     mytry = false;
      
     for(int m12 = yield_signal_1->GetYaxis()->GetNbins();m12 > 0; m12--){
       
       // for(int mz = 0; mz < yield_signal_1->GetZaxis()->GetNbins();mz++){

       //cout << "m12 " << endl;

       if(!yield_signal_1) cout << "no file " << endl;

       Double_t d_s_1 = yield_signal_1->GetBinContent(m0+1,m12)/100*lumi;
       Double_t d_s_2 = yield_signal_2->GetBinContent(m0+1,m12)/100*lumi;

       Double_t muon_1 = yield_muon_1->GetBinContent(m0+1,m12,1)/100*lumi;
       Double_t muon_2 = yield_muon_2->GetBinContent(m0+1,m12,1)/100*lumi;

       //cout << " here " << endl;
       
       if(d_s_1 > 0 || d_s_2 > 0){


	 Double_t BR1 = d_s_1/(d_s_1+d_s_2);
	 Double_t BR2 = d_s_2/(d_s_1+d_s_2);

	 Double_t muon_cont_1 = muon_1/(d_s_1+d_s_2);
	 Double_t muon_cont_2 = muon_2/(d_s_1+d_s_2);
	 
	 f.AddParameters( BR1,BR2,muon_cont_1,muon_cont_2,wspace);
	 
	 cout << " m0 " << m0*50 << " m12 " << m12*25 << " d_s_1 "<< d_s_1 << " d_s_2 " << d_s_2 << " BR1 " << BR1 << " BR2 " << BR2 << " muon_cont_1 " << muon_cont_1 << " muon_cont_2 " << muon_cont_2 << endl;
	 //bool isIn = profileLikelihood(modelConfig,wspace,(d_s_1 + d_s_2));
	 bool isIn = updateLikelihood(plc,wspace,(d_s_1+d_s_2));
	 //  }

	 exclusionLimits->SetBinContent(m0,m12,isIn);

       }

     }

     
   }
   gStyle->SetPalette(1);
   
   output->cd();
   exclusionLimits->Draw("colz");
   exclusionLimits->Write();

   output->Write();
  output->Close();
  

  delete wspace;
  







}
