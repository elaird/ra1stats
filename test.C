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
#include "DevPdfFactory.C"

void test(){


  RooWorkspace* wspace = new RooWorkspace("myWorkspace");

  Double_t meas[4] = {33,11,8,5};
  Double_t B[4] = {0.0169,0.0211,0.0112,0.0122};
  Double_t C[4] = {1720095,5984762,185677,185677};
  Double_t HT[4] = {250,300,350,450};
  Double_t signal_cont[4] = {0.1,0.2,0.4,0.6};
  Double_t A = 5;
  Double_t K = 10;
  Int_t nbins = 4;
  
  DevModel(wspace,
	   meas,
	   B,
	   C,
	   HT,
	   signal_cont,
	   A,
	   K,
	   nbins,
	   "myPdf");


  wspace->Print("v");

  wspace->set("obs")->Print("v");

  RooDataSet* data = wspace->pdf("myPdf")->generate(*wspace->set("obs"),10);
  wspace->import(*data);
  data->Print("v");

  wspace->pdf("myPdf")->fitTo(*data);


}
