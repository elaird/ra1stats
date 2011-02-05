#ifndef ROBSPDFFACTORY
#define ROBSPDFFACTORY

#include "RooWorkspace.h"

class RobsPdfFactory {
public:
  RobsPdfFactory();
  virtual ~RobsPdfFactory();

  void AddModel_EWK(Double_t* BR,Double_t signal_sys,Double_t muon_sys,Double_t phot_sys,Int_t nbins,RooWorkspace* ws,const char* pdfName,const char* muName);


  //up to date
void AddModel_Lin_Combi(Double_t* BR,
			Double_t _lumi, Double_t _lumi_sys,
			Double_t _accXeff,Double_t _accXeff_sys,
			Double_t _muon_sys,Double_t _phot_sys,Double_t _lowHT_sys_1,Double_t _lowHT_sys_2,
			Double_t _muon_cont_1,Double_t _muon_cont_2,
			Double_t _lowHT_cont_1,Double_t _lowHT_cont_2,
			RooWorkspace* ws,const char* pdfName,const char* muName);
  // void AddModel_Lin_Combi(Double_t* sigExp,Double_t _lumi, Double_t _lumi_sys,Double_t _accXeff,Double_t _accXeff_sys,Double_t muon_sys,Double_t phot_sys, Int_t nchan, RooWorkspace* ws, const char* pdfName ="CombinedPdf",const char* masterSignalName ="masterSignal");



  void AddModel_Exp_Combi_both_one(Double_t _lumi, Double_t _lumi_sys,
				   Double_t _accXeff,Double_t _accXeff_sys,
				   Double_t _muon_sys,Double_t _phot_sys,Double_t _lowHT_sys,
				   Double_t _muon_cont_1,
				   Double_t _lowHT_cont_1,Double_t _lowHT_cont_2,
				   RooWorkspace* ws,const char* pdfName,const char* muName);

  void AddModel_Exp_Combi(Double_t* sigExp,Double_t signal_sys,Double_t muon_sys,Double_t phot_sys, Int_t nchan, RooWorkspace* ws, const char* pdfName ="CombinedPdf",const char* masterSignalName ="masterSignal");

  void AddModel_Exp_Combi_one(Double_t* sigExp,Double_t signal_sys,Double_t muon_sys,Double_t phot_sys, Int_t nchan, RooWorkspace* ws, const char* pdfName ="CombinedPdf",const char* masterSignalName ="masterSignal");
  
  void AddModel_Lin(Double_t* sigExp,Double_t signal_sys, Int_t nchan, RooWorkspace* ws, const char* pdfName ="CombinedPdf",const char* masterSignalName ="masterSignal");
  void AddModel_Exp(Double_t* sigExp,Double_t signal_sys, Int_t nchan, RooWorkspace* ws, const char* pdfName ="CombinedPdf",const char* masterSignalName ="masterSignal");

  void AddModel_Exp_one(Double_t d_signal_sys,Int_t nbins,RooWorkspace* ws,const char* pdfName,const char* muName);

  
 
  void AddDataSideband(  Double_t* bkgd_sideband,
			 Double_t* bkgdbar_sideband,
			 Int_t nbins,
			 RooWorkspace* ws, 
			 const char* dsName);


  void AddDataSideband_Combi(  Double_t* bkgd_sideband,
			       Double_t* bkgdbar_sideband,
			       Int_t nbins_incl,
			        Double_t* muon_sideband,
			       Double_t* photon_sideband,
			       Double_t* tau_ttWForTree,
			       Double_t* tau_ZinvForTree,
			       Int_t nbins_EWK,
			       RooWorkspace* ws, 
			       const char* dsName);

  void AddDataSideband_Combi_one(  Double_t* bkgd_sideband,
				   Double_t* bkgdbar_sideband,
				   Int_t nbins_incl,
				   Double_t* muon_sideband,
				   Double_t* photon_sideband,
				   Double_t* tau_ttWForTree,
				   Double_t* tau_ZinvForTree,
				   Int_t nbins_EWK,
				   RooWorkspace* ws, 
				   const char* dsName);
  

  void AddDataSideband_EWK(Double_t* mainMeas, 
			       Double_t* muon_sideband,
			       Double_t* photon_sideband,
			       Double_t* tau_ttWForTree,
			       Double_t* tau_ZinvForTree,
			       Int_t nbins,
			       RooWorkspace* ws, 
			       const char* dsName);


  void AddParameters(Double_t _BR1,Double_t _BR2,Double_t signal_sys,Double_t _muon_cont_1,Double_t _muon_cont_2,Double_t lowHT_cont_1,Double_t lowHT_cont_2,RooWorkspace* ws);

  void AddParameters_1d(Double_t signal_sys,Double_t _muon_cont_1,Double_t _lowHT_cont_1,Double_t _lowHT_cont_2,RooWorkspace* ws);

private:
  
  RooRealVar* SafeObservableCreation(RooWorkspace* ws,const char* varName,Double_t value);

  RooRealVar* SafeObservableCreation(RooWorkspace* ws, const char* varName,Double_t value, Double_t maximum);


};

#endif









