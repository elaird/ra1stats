#ifndef GAUSSIAN
#define GAUSSIAN

#include "RooGaussian.h"
#include "RooRealProxy.h"

class Gaussian : public RooGaussian {
public:
  Gaussian() {} ;
  Gaussian(const RooGaussian& other, const char* name=0) ;
  inline virtual ~Gaussian() { }

  RooRealProxy x ;
  RooRealProxy mean ;
  RooRealProxy sigma ;

private:
  ClassDef(Gaussian,1)
};

#endif
