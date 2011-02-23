#ifndef DEVPDFFACTORY
#define DEVPDFFACTORY

#include "RooWorkspace.h"
#include "RooProdPdf.h"
#include "RooPoisson.h"
#include "TString.h"
#include "RooArgList.h"
//#include <vector>

//Tanja Rommerskirchen 23.02.2011
//class for constructing the likelihood function for the inclusive background estimation method
//input different measured values, HT ranges, precalculated constants, best guess for fit parameters, number of HT bins,workspace
//output workspace filled with everything necessary

//background in each HT bin: bi = Int_HTi^HTi+1(dN/dHT(HT)*A*exp(-k*HT)) A and k are fit parameters

//two different assumptions about the distribution of alphaT<0.55 events in the HT bins can be chosen
//exp for exponential, dN/dHT(HT) = Ci*exp(-Bi*HT)
//delta function all events can be found in mean of HT bin dN/dHT(HT) = mi*Delta(HT - <HT>i)
//for exp need to provide Ci and Bi for delta function need to provide <HT> and mi, constructor takes both

class DevPdfFactory {
public:

  //constructor takes as input (measured values in HT alphaT > 0.55(meas),measured values in HT alphaT < 0.55 (meas_low),calculated B,calculated C, HT borders, mean of HT bins, frac of total signal in each bin, starting guess for A and K, number of HT bins
  DevPdfFactory(Double_t* _meas,
		Double_t* _meas_low,
		Double_t* _B,
		Double_t* _C,
		Double_t* _HT,
		Double_t* _HT_mean,
		Double_t* _signal_cont,
		Double_t _A,
		Double_t _K,
		Int_t nbins);

  //destructor
  virtual ~DevPdfFactory();
 
  //calls DevPdf and setWorkspace to be called from outside
  void makeModel(RooWorkspace* ws,TString pdfName,bool exp);

private:
  //make the Poissons function for each HT bin expected mean is bi + si*signal_cont
  RooPoisson* makePoisson(int bin,bool exp);
  
  //make the full likelihood function for the observation in different HT bins
  RooProdPdf* DevPdf(TString pdfName,bool exp);

  //put everything necessary into workspace
  void SetWorkspace(RooWorkspace* ws,RooProdPdf* pdf);


  //nuisance parameters
  RooRealVar* A;//fit parameter
  RooRealVar* K;//fit parameter

  //parameter of interest
  RooRealVar* masterSignal;


  RooArgList nuisList;
  RooArgList observableList;
  RooArgList poiList;


  RooArgList MeasLowList; //measured number of events in alphaT > 0.55

  //provided variables 
  RooArgList HTLowList;//lower HT value for each bin
  RooArgList HTUpList; //higher HT value for each bin
  RooArgList HTMeanList; //mean HT value for each bin

  
  RooArgList CList;
  RooArgList BList;
  RooArgList SignalContList;


  //  std::vector<RooRealVar*> observableCollection;
  


};

#endif


