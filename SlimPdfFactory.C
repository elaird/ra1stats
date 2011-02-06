//#include <sstream>
//#include <algorithm>
//
#include "TROOT.h"
#include "TTree.h"
#include "TMath.h"

#include "RooPlot.h"
#include "RooAbsPdf.h"
#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooGlobalFunc.h"
#include "RooFitResult.h"
#include "RooRealVar.h"
#include "RooAddition.h"
#include "RooDataSet.h"
#include "RooProdPdf.h"
#include "RooPoisson.h"
#include "RooGaussian.h"
#include "RooCmdArg.h"
#include "RooMsgService.h"
#include "RooLognormal.h"
#include "RobsPdfFactory.hh"
#include "RooAddPdf.h"

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

RooRealVar* SafeObservableCreation(RooWorkspace* ws, const char* varName,Double_t value, Double_t maximum){
 //need to be careful here that the range of the observable in the dataset is consistent with the one in the workspace. Don't rescale unless necessary. If it is necessary, then rescale by x10 or a defined maximum
  RooRealVar* x = ws->var( varName);
  if(!x) x = new RooRealVar(varName,varName,value,0,maximum);
  if(x->getMax() < value) x->setMax(max(x->getMax(),60*value));
  x->setVal(value);
  return x;
}

RooRealVar* SafeObservableCreation(RooWorkspace* ws,const char* varName,Double_t value){
  //need to be careful here that the range of the observable in the dataset is consistent with the one in the workspace. Don't rescale unless necessary. If it is necessary, then rescale by x10 or a defined maximum
  return SafeObservableCreation(ws,varName,value,60.*value);
}

void AddModel_Lin_Combi(Double_t* BR,
			Double_t _lumi, Double_t _lumi_sys,
			Double_t _accXeff, Double_t _accXeff_sys,
			Double_t _muon_sys,Double_t _phot_sys,Double_t _lowHT_sys1,Double_t _lowHT_sys2,
			Double_t _muon_cont_1,Double_t _muon_cont_2,
			Double_t _lowHT_cont_1,Double_t _lowHT_cont_2,
			RooWorkspace* ws,const char* pdfName,const char* muName){

  using namespace RooStats;
  using namespace RooFit;
  
  TList likelihoodFactors;

  TList nosignal_likelihoodFactors;

  //Measurements//////////////////////////
  //EWK
  RooRealVar* muonMeas_1 = new RooRealVar("muonMeas_1","muonMeas_1",0.5,0.,100.);
  RooRealVar* photMeas_1 = new RooRealVar("photMeas_1","photMeas_1",0.5,0.,100.);
  
  RooRealVar* muonMeas_2 = new RooRealVar("muonMeas_2","muonMeas_2",0.5,0.,100.);
  RooRealVar* photMeas_2 = new RooRealVar("photMeas_2","photMeas_2",0.5,0.,100.);
  
  //Different HT bins
  RooRealVar* meas_1 = new RooRealVar("meas_1","meas_1",33.,0.,100.);
  RooRealVar* meas_2 = new RooRealVar("meas_2","meas_2",11.,0.,100.);
  RooRealVar* meas_3 = new RooRealVar("meas_3","meas_3",8.,0.,100);
  RooRealVar* meas_4 = new RooRealVar("meas_4","meas_4",5.,0.,100);
 
  RooRealVar* meas_bar_1 = new RooRealVar("meas_bar_1","meas_bar_1",844459.,20000.,9000000.);
  RooRealVar* meas_bar_2 = new RooRealVar("meas_bar_2","meas_bar_2",331948.,10000.,9000000.);
  RooRealVar* meas_bar_3 = new RooRealVar("meas_bar_3","meas_bar_3",225652.,10000.,9000000.);
  RooRealVar* meas_bar_4 = new RooRealVar("meas_bar_4","meas_bar_4",110034.,50000., 9000000.);

  //define common variables
  RooRealVar* masterSignal = new RooRealVar(muName,"masterSignal",10.,0.,20.);//POI
  RooRealVar* lumi = new RooRealVar("lumi","lumi",_lumi);
  RooRealVar* accXeff = new RooRealVar("accXeff","accXeff",_accXeff);
  
  Double_t d_signal_sys = sqrt( pow(_lumi_sys,2) + pow(_accXeff_sys,2));

  RooRealVar* signal_sys = new RooRealVar("signal_sys","signal_sys",1.,0.,10.);
  RooRealVar* signal_sys_nom = new RooRealVar("signal_sys_nom","signal_sys_nom",1.);
  RooRealVar* signal_sys_sigma = new RooRealVar("signal_sys_sigma","signal_sys_sigma",d_signal_sys);
 
 
  RooRealVar* BR1 = new RooRealVar("BR1","BR1",BR[0]);
  RooRealVar* BR2 = new RooRealVar("BR2","BR2",BR[1]);

  RooProduct* sig_exp1 = new RooProduct("sig_exp1","sig_exp1",RooArgSet(*lumi,*accXeff,*masterSignal,*BR1,*signal_sys));
  RooProduct* sig_exp2 = new RooProduct("sig_exp2","sig_exp2",RooArgSet(*lumi,*accXeff,*masterSignal,*BR2,*signal_sys));
   

  //Easy variables for low HT inclusive method
  RooRealVar* bbar = new RooRealVar("bbar","bbar",110034.,0.,10000000.);
  //RooRealVar* rho = new RooRealVar("rho","rho",1.0,0.,10.);

  RooRealVar* tau_1 = new RooRealVar("tau_1","tau_1",7.7,0.,100);
  RooRealVar* tau_2 = new RooRealVar("tau_2","tau_2",3.2,0.,100);
  RooRealVar* tau_3 = new RooRealVar("tau_3","tau_3",2.1,0.,100);

 
  RooProduct* bkgd_bar_1 = new RooProduct("bkgd_bar_1","bkgd_bar_1",RooArgSet(*bbar,*tau_1));
  RooProduct* bkgd_bar_2 = new RooProduct("bkgd_bar_2","bkgd_bar_2",RooArgSet(*bbar,*tau_2));
  RooProduct* bkgd_bar_3 = new RooProduct("bkgd_bar_3","bkgd_bar_3",RooArgSet(*bbar,*tau_3));
  RooProduct* bkgd_bar_4 = new RooProduct("bkgd_bar_4","bkgd_bar_4",RooArgSet(*bbar));

 
  //The factors Tau_ which related lepton and photon control region to signal region
  RooRealVar* tau_ttW_1 = new RooRealVar("tau_ttW_1","tau_ttW_1",.5);
  RooRealVar* tau_Zinv_1 = new RooRealVar("tau_Zinv_1","tau_Zinv_1",.5);
 
  RooRealVar* tau_ttW_2 = new RooRealVar("tau_ttW_2","tau_ttW_2",.5);
  RooRealVar* tau_Zinv_2 = new RooRealVar("tau_Zinv_2","tau_Zinv_2",.5);

  //Everything for syst. uncertainties on TTW and Zinv background estimation
  RooRealVar* sys_ttW = new RooRealVar("sys_ttW","sys_ttW",1.,0.,2.);
  RooRealVar* sys_Zinv = new RooRealVar("sys_Zinv","sys_Zinv",1.,0.,2.);

  RooRealVar* sys_ttW_nom = new RooRealVar("sys_ttW_nom","sys_ttW_nom",1.);
  RooRealVar* sys_Zinv_nom = new RooRealVar("sys_Zinv_nom","sys_Zinv_nom",1.);

  RooRealVar* sys_ttW_sigma = new RooRealVar("sys_ttW_sigma","sys_ttW_sigma",TMath::Exp(_muon_sys));
  RooRealVar* sys_Zinv_sigma = new RooRealVar("sys_Zinv_sigma","sys_Zinv_sigma",TMath::Exp(_phot_sys));
  
 
 
  //The expected background
  //ttW_tot_1 = ttW_1 * sys_ttW
  //Zinv_tot_1 = Zinv_1 * sys_Zinv
  //ttW_tot_2 = ttW_2 * sys_ttW
  //Zinv_tot_2 = Zinv_2 * sys_Zinv
  

  // tau_3*b = ttW_tot_1 + Zinv_tot_1 + QCD_1 //1. signal bin
  // b       = ttW_tot_2 + Zinv_tot_2 + QCD_2 //2. signal bin
  // --> tau_3 * (ttW_tot_2 + Zinv_tot_2 + QCD_2) = ttW_tot_1 + Zinv_tot_1 + QCD_1
  // QCD_1 = tau_3 * (ttW_tot_2 + Zinv_tot_2 + QCD_2) - ttW_tot_1 - Zinv_tot_1 

  //tt_W_1 = ( tau_3 * (ttW_tot_2 + Zinv_tot_2 + QCD_2) - Zinv_tot_1 - QCD_1 ) / sys_ttW

  RooRealVar* ttW_1 = new RooRealVar("ttW_1","ttW_1",.5,0.,100.);
  RooRealVar* Zinv_1 = new RooRealVar("Zinv_1","Zinv_1",.5,0.,100.);
  //RooRealVar* QCD_1 = new RooRealVar("QCD_1","QCD_1",.5,0.,100.);
  
  RooRealVar* Zinv_2 = new RooRealVar("Zinv_2","Zinv_2",.5,0.,100.);
  RooRealVar* QCD_2 = new RooRealVar("QCD_2","QCD_2",.5,0.,100.);
  RooRealVar* ttW_2 = new RooRealVar("ttW_2","ttW_2",.5,0.,100.);

  //RooProduct* Zinv_tot_1 = new RooProduct("Zinv_tot_1","Zinv_1*sys_Zinv",RooArgSet(*Zinv_1,*sys_Zinv)); 
  //RooProduct* ttW_tot_1 = new RooProduct("ttW_tot_1","ttW_1*sys_ttW",RooArgSet(*ttW_1,*sys_ttW)); 

  RooProduct* Zinv_tot_2 = new RooProduct("Zinv_tot_2","Zinv_2*sys_Zinv",RooArgSet(*Zinv_2,*sys_Zinv));
  RooProduct* ttW_tot_2 = new RooProduct("ttW_tot_2","ttW_2*sys_ttW",RooArgSet(*ttW_2,*sys_ttW));
  


  RooRealVar* lowHT_sys1 = new RooRealVar("lowHT_sys1","lowHT_sys1",1.0,0.1,5.);
  RooRealVar* lowHT_sys1_nom = new RooRealVar("lowHT_sys1_nom","lowHT_sys1_nom",1.0);
  RooRealVar* lowHT_sys1_sigma = new RooRealVar("lowHT_sys1_sigma","lowHT_sys1_sigma",_lowHT_sys1);

  RooRealVar* lowHT_sys2 = new RooRealVar("lowHT_sys2","lowHT_sys2",1.0,0.1,5.);
  RooRealVar* lowHT_sys2_nom = new RooRealVar("lowHT_sys2_nom","lowHT_sys2_nom",1.0);
  RooRealVar* lowHT_sys2_sigma = new RooRealVar("lowHT_sys2_sigma","lowHT_sys2_sigma",_lowHT_sys2);

  //Now the awful combination part
  RooAddition* b = new RooAddition("b","b",RooArgSet(*ttW_tot_2,*Zinv_tot_2,*QCD_2));

 
  RooProduct* bkgd_1 = new RooProduct("bkgd_1","bkgd_1",RooArgSet(*b,*tau_1));
  RooProduct* bkgd_2 = new RooProduct("bkgd_2","bkgd_2",RooArgSet(*b,*tau_2));
  RooProduct *bkgd_3 = new RooProduct("bkgd_3","bkgd_3",RooArgSet(*lowHT_sys1,*b,*tau_3));

  RooProduct *bkgd_4 = new RooProduct("bkgd_4","bkgd_4",RooArgSet(*b,*lowHT_sys2));



  ////Do some weird things to allow substractions
  //RooRealVar* MOne = new RooRealVar("MOne","MOne",-1);  
  //RooProduct *MttW = new RooProduct("MttW","MTTW",RooArgSet(*MOne,*ttW_1));
  //RooProduct *MZinv = new RooProduct("MZinv","MZinv",RooArgSet(*MOne,*Zinv_1));

  //RooAddition *QCD_1 = new RooAddition("QCD_1","QCD_1",RooArgSet(*bkgd_3,*MttW,*MZinv));

  

  RooProduct* ttWTau_1 = new RooProduct("ttWTau_1","ttW_1*tau_ttW",RooArgSet(*ttW_1,*tau_ttW_1));
  RooProduct* ZinvTau_1 = new RooProduct("ZinvTau_1","Zinv_1*tau_Zinv",RooArgSet(*Zinv_1,*tau_Zinv_1));

  RooProduct* ttWTau_2 = new RooProduct("ttWTau_2","ttW_2*tau_ttW",RooArgSet(*ttW_2,*tau_ttW_2));
  RooProduct* ZinvTau_2 = new RooProduct("ZinvTau_2","Zinv_2*tau_Zinv",RooArgSet(*Zinv_2,*tau_Zinv_2));

  RooAddition* splusb_1 = new RooAddition("splusb_1","splusb_1",RooArgSet(*sig_exp1,*bkgd_3));
  RooAddition* splusb_2 = new RooAddition("splusb_2","splusb_2",RooArgSet(*sig_exp2,*bkgd_4));

  RooRealVar* muon_cont_1 = new RooRealVar("muon_cont_1","muon_cont_1",_muon_cont_1); 
  RooRealVar* muon_cont_2 = new RooRealVar("muon_cont_2","muon_cont_2",_muon_cont_2); 

  RooRealVar* lowHT_cont_1 = new RooRealVar("lowHT_cont_1","lowHT_cont_1",_lowHT_cont_1); 
  RooRealVar* lowHT_cont_2 = new RooRealVar("lowHT_cont_2","lowHT_cont_2",_lowHT_cont_2); 

  RooProduct* signal_in_muon_1 = new RooProduct("signal_in_muon_1","signal_in_muon_1",RooArgSet(*masterSignal,*muon_cont_1));
  RooProduct* signal_in_muon_2 = new RooProduct("signal_in_muon_2","signal_in_muon_2",RooArgSet(*masterSignal,*muon_cont_2));

  RooProduct* signal_in_lowHT_1 = new RooProduct("signal_in_lowHT_1","signal_in_lowHT_1",RooArgSet(*masterSignal,*lowHT_cont_1));
  RooProduct* signal_in_lowHT_2 = new RooProduct("signal_in_lowHT_2","signal_in_lowHT_2",RooArgSet(*masterSignal,*lowHT_cont_2));


  RooAddition* sPlusb_muon_1 = new RooAddition("sPlusb_muon_1","sPlusb_muon_1",RooArgSet(*signal_in_muon_1,*ttWTau_1));
  RooAddition* sPlusb_muon_2 = new RooAddition("sPlusb_muon_2","sPlusb_muon_2",RooArgSet(*signal_in_muon_2,*ttWTau_2));

  RooAddition* sPlusb_lowHT_1 = new RooAddition("sPlusb_lowHT_1","sPlusb_lowHT_1",RooArgSet(*signal_in_lowHT_1,*bkgd_1));
  RooAddition* sPlusb_lowHT_2 = new RooAddition("sPlusb_lowHT_2","sPlusb_lowHT_2",RooArgSet(*signal_in_lowHT_2,*bkgd_2));

  //Define all the necessary pdf
  //Gaussian
  RooLognormal *sys_ttW_Cons = new RooLognormal("sys_ttW_Cons","sys_ttW_Cons",*sys_ttW_nom,*sys_ttW,*sys_ttW_sigma);
  RooLognormal *sys_Zinv_Cons = new RooLognormal("sys_Zinv_Cons","sys_Zinv_Cons",*sys_Zinv_nom,*sys_Zinv,*sys_Zinv_sigma);
 
  RooGaussian *sys_signal_Cons = new RooGaussian("sys_signal_Cons","sys_signal_Cons",*signal_sys_nom,*signal_sys,*signal_sys_sigma);
  RooGaussian *sys_lowHT_Cons_1 = new RooGaussian("sys_lowHT_Cons_1","sys_lowHT_Cons_1",*lowHT_sys1_nom,*lowHT_sys1,*lowHT_sys1_sigma);
  RooGaussian *sys_lowHT_Cons_2 = new RooGaussian("sys_lowHT_Cons_2","sys_lowHT_Cons_2",*lowHT_sys2_nom,*lowHT_sys2,*lowHT_sys2_sigma);


  //Poisson
  RooPoisson* muonRegion_1 = new RooPoisson("muonRegion_1","muonRegion_1",*muonMeas_1,*sPlusb_muon_1);
  RooPoisson* photRegion_1 = new RooPoisson("photRegion_1","photRegion_1",*photMeas_1,*ZinvTau_1);

  RooPoisson* muonRegion_2 = new RooPoisson("muonRegion_2","muonRegion_2",*muonMeas_2,*sPlusb_muon_2);
  RooPoisson* photRegion_2 = new RooPoisson("photRegion_2","photRegion_2",*photMeas_2,*ZinvTau_2);

  RooPoisson* bkgd_poisson_1 = new RooPoisson("bkgd_poisson_1","bkgd_poisson_1",*meas_1,*sPlusb_lowHT_1);
  RooPoisson* bkgd_poisson_2 = new RooPoisson("bkgd_poisson_2","bkgd_poisson_2",*meas_2,*sPlusb_lowHT_2);

  RooPoisson* sig_poisson_1 = new RooPoisson("sig_poisson_1","sig_poisson_1",*meas_3,*splusb_1);
  RooPoisson* sig_poisson_2 = new RooPoisson("sig_poisson_2","sig_poisson_2",*meas_4,*splusb_2);

  RooPoisson* sig_poisson_1_bar = new RooPoisson("sig_poisson_1_bar","sig_poisson_1_bar",*meas_bar_3,*bkgd_bar_3);
  RooPoisson* sig_poisson_2_bar = new RooPoisson("sig_poisson_2_bar","sig_poisson_2_bar",*meas_bar_4,*bkgd_bar_4);

  RooPoisson* bkgd_poisson_1_bar = new RooPoisson("bkgd_poisson_1_bar","bkgd_poisson_1_bar",*meas_bar_1,*bkgd_bar_1);
  RooPoisson* bkgd_poisson_2_bar = new RooPoisson("bkgd_poisson_2_bar","bkgd_poisson_2_bar",*meas_bar_2,*bkgd_bar_2);

  //nosignal cont
  RooPoisson* sig_poisson_1_nosig = new RooPoisson("sig_poisson_1_nosig","sig_poisson_1_nosig",*meas_3,*bkgd_3);
  RooPoisson* sig_poisson_2_nosig = new RooPoisson("sig_poisson_2_nosig","sig_poisson_2_nosig",*meas_4,*bkgd_4);

  RooPoisson* bkgd_poisson_1_nosig = new RooPoisson("bkgd_poisson_1_nosig","bkgd_poisson_1_nosig",*meas_1,*bkgd_1);
  RooPoisson* bkgd_poisson_2_nosig = new RooPoisson("bkgd_poisson_2_nosig","bkgd_poisson_2_nosig",*meas_2,*bkgd_2);

  RooPoisson* muonRegion_1_nosig = new RooPoisson("muonRegion_1_nosig","muonRegion_1_nosig",*muonMeas_1,*ttWTau_1);
  RooPoisson* muonRegion_2_nosig = new RooPoisson("muonRegion_2_nosig","muonRegion_2_nosig",*muonMeas_2,*ttWTau_2);

  
  nosignal_likelihoodFactors.Add(sys_lowHT_Cons_1);
  nosignal_likelihoodFactors.Add(sys_lowHT_Cons_2);
 
  nosignal_likelihoodFactors.Add(sys_ttW_Cons);
  nosignal_likelihoodFactors.Add(sys_Zinv_Cons);
  nosignal_likelihoodFactors.Add(sys_signal_Cons);

  nosignal_likelihoodFactors.Add(muonRegion_1_nosig);
  nosignal_likelihoodFactors.Add(photRegion_1);
  
  nosignal_likelihoodFactors.Add(muonRegion_2_nosig);
  nosignal_likelihoodFactors.Add(photRegion_2);

  nosignal_likelihoodFactors.Add(sig_poisson_1_nosig);
  nosignal_likelihoodFactors.Add(sig_poisson_2_nosig);
  nosignal_likelihoodFactors.Add(bkgd_poisson_1_nosig);
  nosignal_likelihoodFactors.Add(bkgd_poisson_2_nosig);

  nosignal_likelihoodFactors.Add(sig_poisson_1_bar);
  nosignal_likelihoodFactors.Add(sig_poisson_2_bar);
  nosignal_likelihoodFactors.Add(bkgd_poisson_1_bar);
  nosignal_likelihoodFactors.Add(bkgd_poisson_2_bar);
 
  //add likelihood factors
  likelihoodFactors.Add(sys_lowHT_Cons_1);
  likelihoodFactors.Add(sys_lowHT_Cons_2);

  likelihoodFactors.Add(sys_ttW_Cons);
  likelihoodFactors.Add(sys_Zinv_Cons);
  likelihoodFactors.Add(sys_signal_Cons);

  likelihoodFactors.Add(muonRegion_1);
  likelihoodFactors.Add(photRegion_1);
  
  likelihoodFactors.Add(muonRegion_2);
  likelihoodFactors.Add(photRegion_2);

  likelihoodFactors.Add(sig_poisson_1);
  likelihoodFactors.Add(sig_poisson_2);
  likelihoodFactors.Add(bkgd_poisson_1);
  likelihoodFactors.Add(bkgd_poisson_2);

  likelihoodFactors.Add(sig_poisson_1_bar);
  likelihoodFactors.Add(sig_poisson_2_bar);
  likelihoodFactors.Add(bkgd_poisson_1_bar);
  likelihoodFactors.Add(bkgd_poisson_2_bar);

  RooArgSet likelihoodFactorSet(likelihoodFactors);
  RooProdPdf joint(pdfName,"joint",likelihoodFactorSet);

  RooArgSet nosignal_likelihoodFactorSet(nosignal_likelihoodFactors);
  RooProdPdf nosignal_joint("modelBkg","nosignal_joint",nosignal_likelihoodFactorSet);

 

  RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);

  ws->import(*muonMeas_1);
  ws->import(*photMeas_1);
  ws->import(*muonMeas_2);
  ws->import(*photMeas_2);
  ws->import(*meas_1);
  ws->import(*meas_2);
  ws->import(*meas_3);
  ws->import(*meas_4);
  ws->import(*meas_bar_1);
  ws->import(*meas_bar_2);
  ws->import(*meas_bar_3);
  ws->import(*meas_bar_4);
  ws->import(joint);

  // ws->import(nosignal_joint);
  
  // ws->import(poi);
  // ws->import(nuis);

  RooMsgService::instance().setGlobalKillBelow(RooFit::DEBUG);

  ws->defineSet("nuis","signal_sys,sys_ttW,lowHT_sys1,lowHT_sys2,sys_Zinv,ttW_1,ttW_2,Zinv_1,Zinv_2,QCD_2");  

   ws->defineSet("obs","meas_1,meas_2,meas_3,meas_4,meas_bar_1,meas_bar_2,meas_bar_3,meas_bar_4,muonMeas_1,muonMeas_2,photMeas_1,photMeas_2");
   ws->defineSet("poi",muName);


 

  cout << " here of modelmaking " << endl;


}


void AddDataSideband_Combi(  Double_t* meas,
			     Double_t* meas_bar,
			     Int_t nbins_incl,
			     Double_t* muon_sideband,
			     Double_t* photon_sideband,
			     Double_t* tau_ttWForTree,
			     Double_t* tau_ZinvForTree,
			     Int_t nbins_EWK,
			     RooWorkspace* ws, 
			     const char* dsName){


  //arguments are an array of measured events in signal region, measured events in control regions, factors that relate signal to background region and the number of channels

  using namespace RooFit;
  using std::vector;

  Double_t MaxSigma = 8;



  TList observablesCollection;


  TTree* tree = new TTree();
  Double_t* bkgdForTree = new Double_t[nbins_incl];
  Double_t* bkgdbarForTree = new Double_t[nbins_incl];

  Double_t* muonForTree = new Double_t[nbins_EWK];
  Double_t* photForTree = new Double_t[nbins_EWK];
 

  cout << " nbinx_incl " << nbins_incl << endl;
  //loop over channels
  for(Int_t i = 0; i < nbins_incl; ++i){
    std::stringstream str;
    str<<"_"<<i+1;

    cout << " i " << i << endl;
   
    //need to be careful
    RooRealVar* bkgdMeas = SafeObservableCreation(ws,("meas"+str.str()).c_str(),meas[i]);
    //need to be careful
    RooRealVar* bkgdBarMeas = SafeObservableCreation(ws, ("meas_bar"+str.str()).c_str(),meas_bar[i]);
    //need to be careful
   

    observablesCollection.Add(bkgdMeas);   
    observablesCollection.Add(bkgdBarMeas);

    bkgdForTree[i] = meas[i];
    bkgdbarForTree[i] = meas_bar[i];
 

    tree->Branch(("meas"+str.str()).c_str(),bkgdForTree+i,("meas"+str.str()+"/D").c_str());
    tree->Branch(("meas_bar"+str.str()).c_str(),bkgdbarForTree+i,("meas_bar"+str.str()+"/D").c_str());


    if( i < nbins_incl - 1){
      Double_t _tau = (meas_bar[i]/meas_bar[nbins_incl-1]);

      cout << " _tau " << _tau << endl;

      RooRealVar* tau = SafeObservableCreation(ws, ("tau"+str.str()).c_str(),_tau);
      RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
      ws->import(*((RooRealVar*)tau->clone(( string(tau->GetName())+string(dsName)).c_str() ) ));     
      RooMsgService::instance().setGlobalKillBelow(RooFit::DEBUG);

      
    }

  }

  cout << " nbins_EWK " << nbins_EWK << endl;
   //loop over channels
  for(Int_t i = 0; i < nbins_EWK; ++i){
    std::stringstream str;
    str<<"_"<<i+1;

    cout << " i " << i << endl;
    
    Double_t _tauTTW = tau_ttWForTree[i];
    RooRealVar* tauTTW = SafeObservableCreation(ws, ("tau_ttW"+str.str()).c_str(),_tauTTW);

    Double_t _tauZinv = tau_ZinvForTree[i];
    RooRealVar* tauZinv = SafeObservableCreation(ws, ("tau_Zinv"+str.str()).c_str(),_tauZinv);

    Double_t ttW_sys = 1./sqrt(muon_sideband[i]);
    Double_t Zinv_sys = 1./sqrt(photon_sideband[i]);

    Double_t ttW = (muon_sideband[i]/_tauTTW);
    Double_t Zinv = (photon_sideband[i]/_tauZinv);

    cout << " calc zinv " << Zinv << " photon sid " << photon_sideband[i] << endl;

    RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
    ws->import(*((RooRealVar*)tauTTW->clone(( string(tauTTW->GetName())+string(dsName)).c_str() ) ));
    ws->import(*((RooRealVar*)tauZinv->clone(( string(tauZinv->GetName())+string(dsName)).c_str() ) ));
    RooMsgService::instance().setGlobalKillBelow(RooFit::DEBUG);

   
   
    //need to be careful
    RooRealVar* muonMeas = SafeObservableCreation(ws, ("muonMeas"+str.str()).c_str(),muon_sideband[i]);
    //need to be careful
    RooRealVar* photMeas = SafeObservableCreation(ws, ("photMeas"+str.str()).c_str(),photon_sideband[i]);

   
    observablesCollection.Add(muonMeas);
    observablesCollection.Add(photMeas);

   
    muonForTree[i] = muon_sideband[i];
    photForTree[i] = photon_sideband[i];

   
    tree->Branch(("muonMeas"+str.str()).c_str(),muonForTree+i,("muonMeas"+str.str()+"/D").c_str());
    tree->Branch(("photMeas"+str.str()).c_str(),photForTree+i,("photMeas"+str.str()+"/D").c_str());

    ws->var(("ttW"+str.str()).c_str())->setMax(1.2*ttW+MaxSigma*(sqrt(ttW)+ttW*ttW_sys) );
    ws->var(("Zinv"+str.str()).c_str())->setMax(1.2*Zinv+MaxSigma*(sqrt(Zinv)+Zinv*Zinv_sys) );

    ws->var(("ttW"+str.str()).c_str())->setVal(ttW);
    ws->var(("Zinv"+str.str()).c_str())->setVal(Zinv);

  }

  tree->Fill();

  RooArgList* observableList = new RooArgList(observablesCollection);
  observableList->Print();

  RooDataSet* data = new RooDataSet(dsName,"Number Counting Data",tree,*observableList);
  //data->Scan();

 
  RooMsgService::instance().setGlobalKillBelow(RooFit::FATAL);
  ws->import(*data);
  RooMsgService::instance().setGlobalKillBelow(RooFit::DEBUG);



}
