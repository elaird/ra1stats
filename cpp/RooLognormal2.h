 /***************************************************************************** 
  * Project: RooFit                                                           * 
  * @(#)root/roofit:$Id: RooLognormal.h 34064 2010-06-22 15:05:19Z wouter $ *
  *                                                                           * 
  * RooFit Lognormal PDF                                                      *
  *                                                                           * 
  * Author: Gregory Schott and Stefan Schmitz                                 *
  *                                                                           * 
  *****************************************************************************/ 

#ifndef ROO_LOGNORMAL2
#define ROO_LOGNORMAL2

#include "RooAbsPdf.h"
#include "RooRealProxy.h"

class RooRealVar;

class RooLognormal2 : public RooAbsPdf {
public:
  RooLognormal2() {} ;
  RooLognormal2(const char *name, const char *title,
	      RooAbsReal& _x, RooAbsReal& _m0, RooAbsReal& _k);
  RooLognormal2(const RooLognormal2& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooLognormal2(*this,newname); }
  inline virtual ~RooLognormal2() { }

  Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const ;
  Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const ;

  Int_t getGenerator(const RooArgSet& directVars, RooArgSet &generateVars, Bool_t staticInitOK=kTRUE) const;
  void generateEvent(Int_t code);

protected:

  RooRealProxy x ;
  RooRealProxy m0 ;
  RooRealProxy k ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooLognormal2,1) // log-normal PDF
};

#endif
