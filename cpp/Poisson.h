#ifndef POISSON
#define POISSON

#include "RooPoisson.h"
#include "RooRealProxy.h"

class Poisson : public RooPoisson {
public:
  Poisson() { };
  Poisson(const RooPoisson& other, const char* name=0) ;
  inline virtual ~Poisson() { }

  double xVal() {return x.arg().getVal();}
  double meanVal() {return mean.arg().getVal();}

private:
  ClassDef(Poisson,3)
};
 
#endif
