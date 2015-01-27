#ifndef GAUSSIAN
#define GAUSSIAN

#include "RooGaussian.h"
#include "RooRealProxy.h"

class Gaussian : public RooGaussian {
public:
  Gaussian() {} ;
  Gaussian(const RooGaussian& other, const char* name=0) ;
  inline virtual ~Gaussian() { }

  double xVal() {return x.arg().getVal();}
  double meanVal() {return mean.arg().getVal();}
  double sigmaVal() {return sigma.arg().getVal();}

private:
  ClassDef(Gaussian,1)
};

#endif
