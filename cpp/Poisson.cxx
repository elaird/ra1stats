#include "Poisson.h" 
#include "RooPoisson.h" 

ClassImp(Poisson) 

Poisson::Poisson(const RooPoisson& other, const char* name) :  
   RooPoisson(other,name)
{ 
}
