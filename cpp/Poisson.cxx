#include "Poisson.h" 
#include "RooPoisson.h" 

ClassImp(Poisson) 

Poisson::Poisson(const RooPoisson& other, const char* name) :  
   RooPoisson(other,name), 
   x("x",this,other.x),
   mean("mean",this,other.mean),
   _noRounding(other._noRounding),
   _protectNegative(other._protectNegative)
{ 
}
