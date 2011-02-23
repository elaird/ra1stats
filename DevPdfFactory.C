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
#include "DevPdfFactory.hh"


DevPdfFactory::DevPdfFactory(Double_t* _meas,
			     Double_t* _meas_low,
			     Double_t* _B,
			     Double_t* _C,
			     Double_t* _HT,
			     Double_t* _HT_mean,
			     Double_t* _signal_cont,
			     Double_t _A,
			     Double_t _K,
			     Int_t nbins):nuisList("nuis"),observableList("obs"),poiList("poi"),MeasLowList("meas_low"),HTLowList("HT_low"),HTUpList("HT_up"),HTMeanList("HT_mean"),CList("C"),BList("B"),SignalContList("signal_cont"){

 
  TList nuisCollection;
  TList poiCollection;


  masterSignal = new RooRealVar("masterSignal","masterSignal",0.5,0,50);
   
  //background stuff
  A = new RooRealVar("A","A",_A,0,_A*100);
  K = new RooRealVar("K","K",_K,0,_K*10);
  
  nuisList.add(*A);
  nuisList.add(*K);

  poiList.add(*masterSignal);
  
  for(int i = 0; i < nbins;++i){
    
    std::stringstream str;
    str<<"_"<<i+1;
    
    double _HT_up = 1000000;
    if(i < nbins-1) _HT_up = _HT[i+1];


    RooRealVar* meas = new RooRealVar(("meas"+str.str()).c_str(),("meas"+str.str()).c_str(),_meas[i]);
    RooRealVar* meas_low = new RooRealVar(("meas_low"+str.str()).c_str(),("meas_low"+str.str()).c_str(),_meas_low[i]);
    RooRealVar* HT_low = new RooRealVar(("HT_low"+str.str()).c_str(),("HT_low"+str.str()).c_str(),_HT[i]);
    RooRealVar* HT_up = new RooRealVar(("HT_up"+str.str()).c_str(),("HT_up"+str.str()).c_str(),_HT_up);
    RooRealVar* HT_mean = new RooRealVar(("HT_mean"+str.str()).c_str(),("HT_mean"+str.str()).c_str(),_HT_mean[i]);
    RooRealVar* C = new RooRealVar(("C"+str.str()).c_str(),("C"+str.str()).c_str(),_C[i]);
    RooRealVar* B = new RooRealVar(("B"+str.str()).c_str(),("B"+str.str()).c_str(),_B[i]);
    RooRealVar* signal_cont = new RooRealVar(("signal_cont"+str.str()).c_str(),("signal_cont"+str.str()).c_str(),_signal_cont[i]);

    observableList.add(*meas);
    // observableCollection.push_back(meas);

    MeasLowList.add(*meas_low);
    HTLowList.add(*HT_low);
    HTUpList.add(*HT_up);
    HTMeanList.add(*HT_mean);
    CList.add(*C);
    BList.add(*B);
    SignalContList.add(*signal_cont);
  }

 
}


RooPoisson* DevPdfFactory::makePoisson(int bin,bool exp){

  std::stringstream str;
  str<<"_"<<bin;

  RooFormulaVar* bkgd_HTbin;

 RooRealVar meas("meas","meas",300);

  if(exp == true)bkgd_HTbin = new RooFormulaVar(("bkgd_"+str.str()+"HTbin").c_str(),"","@0*@2/(@1+@3)*(exp(-@4*(@1+@3)) - exp(-@5*(@1+@3)))",RooArgList(*A,*BList.at(bin),*CList.at(bin),*K,*HTLowList.at(bin),*HTUpList.at(bin)));

  else bkgd_HTbin = new RooFormulaVar(("bkgd_"+str.str()+"HTbin").c_str(),"","@0*@1*exp(-@2*@3)",RooArgList(*MeasLowList.at(bin),*A,*K,*HTMeanList.at(bin)));
  

  RooProduct* signal_HTbin = new RooProduct(("signal_"+str.str()+"HTbin").c_str(),("masterSignal*signal_cont_"+str.str()).c_str(),RooArgList(*masterSignal,*SignalContList.at(bin)));

  RooAddition* exp_HTbin = new RooAddition(("exp_"+str.str()+"HTbin").c_str(),("bkgd_"+str.str()+"HTbin+signal_"+str.str()+"HTbin").c_str(),RooArgList(*bkgd_HTbin,*signal_HTbin));

  //  RooPoisson* pois_HTbin = new RooPoisson(("pois_"+str.str()+"HTbin").c_str(),("pois_"+str.str()+"HTbin").c_str(),*observableCollection.at(bin),*exp_HTbin);

   RooPoisson* pois_HTbin = new RooPoisson(("pois_"+str.str()+"HTbin").c_str(),("pois_"+str.str()+"HTbin").c_str(),meas,*exp_HTbin);

  return pois_HTbin;

}


RooProdPdf* DevPdfFactory::DevPdf(TString pdfName,bool exp){
 
  TList likelihoodFactors;
 
  for(int i = 0; i < observableList.getSize();++i){

    RooPoisson* P_HTbin = makePoisson(i,exp);
    
    likelihoodFactors.Add(P_HTbin);    
  }

 
  RooArgSet likelihoodFactorSet(likelihoodFactors);

  RooProdPdf* joint = new RooProdPdf(pdfName,pdfName,likelihoodFactorSet);

  return joint;
}

void DevPdfFactory::SetWorkspace(RooWorkspace* ws,RooProdPdf *joint){

  RooMsgService::instance().setGlobalKillBelow(RooFit::ERROR);
  ws->import(*joint);
  ws->defineSet("obs",observableList);
  ws->defineSet("poi",poiList);
  ws->defineSet("nuis",nuisList);
  RooMsgService::instance().setGlobalKillBelow(RooFit::DEBUG);
  
}

void DevPdfFactory::makeModel(RooWorkspace* ws,TString pdfName,bool exp){
  RooProdPdf* joint = DevPdf(pdfName,exp);
  SetWorkspace(ws,joint);
}


