#include "Lognormal.h"

ClassImp(Lognormal)

Lognormal::Lognormal(const RooLognormal& other, const char* name) : 
  RooLognormal(other,name), x("x",this,other.x), m0("m0",this,other.m0),
  k("k",this,other.k)
{
}
