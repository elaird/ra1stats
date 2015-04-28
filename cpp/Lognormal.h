#ifndef LOGNORMAL
#define LOGNORMAL

#include "RooLognormal.h"
#include "RooRealProxy.h"

class Lognormal : public RooLognormal {
public:
  Lognormal() {} ;
  Lognormal(const RooLognormal& other, const char* name=0) ;
  inline virtual ~Lognormal() { }

  double xVal() {return x.arg().getVal();}
  double m0Val() {return m0.arg().getVal();}
  double kVal() {return k.arg().getVal();}

private:
  ClassDef(Lognormal,1)
};

#endif
