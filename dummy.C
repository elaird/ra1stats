#include <TH2F.h>

TH2F* dummy(double m0, double m12) {
  
  TH2F *h = new TH2F("h", "h", 1, 0.0, 1.0, 1, 0.0, 1.0);
  return h;
}
