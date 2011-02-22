#include <sstream>
#include "TTree.h"
#include "TMath.h"

#include "RooWorkspace.h"
#include "RooDataSet.h"
#include "RooRealVar.h"
#include "RooAddition.h"
#include "RooProdPdf.h"
#include "RooArgSet.h"
#include "RooProduct.h"
#include "RooPoisson.h"
#include "RooGaussian.h"
#include "RooMsgService.h"
#include "RooLognormal.h"
#include "RooFormulaVar.h"


RooPoisson* makePoisson(RooRealVar& meas,RooRealVar& masterSignal,RooRealVar& A,RooRealVar& B,RooRealVar& C,RooRealVar& K,RooRealVar& HT1,RooRealVar& HT2,RooRealVar& signal_cont,TString bin){

  RooFormulaVar* bkgd_HTbin = new RooFormulaVar("bkgd_"+bin+"HTbin","","@0*@2/(@1+@3)*(exp(-@4*(@1+@3)) - exp(-@5*(@1+@3)))",RooArgList(A,B,C,K,HT1,HT2));
 
  RooProduct* signal_HTbin = new RooProduct("signal_"+bin+"HTbin","masterSignal*signal_cont_"+bin,RooArgList(masterSignal,signal_cont));

  RooAddition* exp_HTbin = new RooAddition("exp_"+bin+"HTbin","bkgd_"+bin+"HTbin+signal_"+bin+"HTbin",RooArgList(*bkgd_HTbin,*signal_HTbin));

  RooPoisson* pois_HTbin = new RooPoisson("pois_"+bin+"HTbin","pois_"+bin+"HTbin",meas,*exp_HTbin);

  return pois_HTbin;

}


void DevModel(RooWorkspace *ws,
	      Double_t* _meas,
	      Double_t* _B,
	      Double_t* _C,
	      Double_t* _HT,
	      Double_t* _signal_cont,
	      Double_t _A,
	      Double_t _K,
	      Int_t nbins){

  
  RooRealVar* masterSignal = new RooRealVar("masterSignal","masterSignal",0.5,0,50);

 
  //background stuff
  RooRealVar* A = new RooRealVar("A","A",_A,0,_A*10);
  RooRealVar* K = new RooRealVar("K","K",_K,0,_K*10);

  TList likelihoodFactors;

  for(int i = 0; i < nbins;++i){

    std::stringstream str;
    str<<"_"<<i+1;

    double _HT_up = 100000;
    if(i < nbins-1) _HT_up = _HT[i+1];


    RooRealVar* meas = new RooRealVar(("meas"+str.str()).c_str(),("meas"+str.str()).c_str(),_meas[i]);
    RooRealVar* HT_low = new RooRealVar(("HT_low"+str.str()).c_str(),("HT_low"+str.str()).c_str(),_HT[i]);
    RooRealVar* HT_up = new RooRealVar(("HT_up"+str.str()).c_str(),("HT_up"+str.str()).c_str(),_HT_up);
    RooRealVar* C = new RooRealVar(("C"+str.str()).c_str(),("C"+str.str()).c_str(),_C[i]);
    RooRealVar* B = new RooRealVar(("B"+str.str()).c_str(),("B"+str.str()).c_str(),_B[i]);
    RooRealVar* signal_cont = new RooRealVar(("K"+str.str()).c_str(),("K"+str.str()).c_str(),_signal_cont[i]);

    RooPoisson* P_HTbin = makePoisson(*meas,*masterSignal,*A,*B,*C,*K,*HT_low,*HT_up,*signal_cont,(str.str()).c_str());
    
    likelihoodFactors.Add(P_HTbin);
  }



  RooArgSet likelihoodFactorSet(likelihoodFactors);
  RooProdPdf joint("pdfName","joint",likelihoodFactorSet);

  RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
  ws->import(joint);
  RooMsgService::instance().setGlobalKillBelow(RooFit::DEBUG);
  
}


