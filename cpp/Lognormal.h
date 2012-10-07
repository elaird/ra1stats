#ifndef LOGNORMAL
#define LOGNORMAL

#include "RooLognormal.h"
#include "RooRealProxy.h"

class Lognormal : public RooLognormal {
public:
  Lognormal() {} ;
  Lognormal(const RooLognormal& other, const char* name=0) ;
  inline virtual ~Lognormal() { }

  RooRealProxy x;
  RooRealProxy m0;
  RooRealProxy k;

private:
  ClassDef(Lognormal,1)
};

#endif
