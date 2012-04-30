#ifndef POISSON
#define POISSON

#include "RooPoisson.h"
#include "RooRealProxy.h"

class Poisson : public RooPoisson {
public:
  Poisson() { };
  Poisson(const RooPoisson& other, const char* name=0) ;
  inline virtual ~Poisson() { }

  RooRealProxy x ;
  RooRealProxy mean ;

protected:
  Bool_t  _noRounding ;
  Bool_t  _protectNegative ;

private:
  ClassDef(Poisson,3)
};
 
#endif
