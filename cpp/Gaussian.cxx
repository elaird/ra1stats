#include "Gaussian.h"

ClassImp(Gaussian)

Gaussian::Gaussian(const RooGaussian& other, const char* name) : 
  RooGaussian(other,name), x("x",this,other.x), mean("mean",this,other.mean),
  sigma("sigma",this,other.sigma)
{
}
