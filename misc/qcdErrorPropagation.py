#!/usr/bin/env python

import math

def sigmaf(x0 = None, A = None, k = None, sigmaA = None, sigmak = None, rhoAk = None, verbose = False) :
    out = 0.0
    termA = sigmaA**2
    termk = sigmak**2*A**2*x0**2
    termAk = -2.0*A*x0*sigmak*sigmaA*rhoAk
    factor = math.exp(-2.0*k*x0)
    out += termA
    out += termk
    out += termAk
    out *= factor
    out = math.sqrt(out)

    if verbose :
        print
        print "termA  = %10.3e"%termA
        print "termk  = %10.3e"%termk
        print "termAk = %10.3e"%termAk
        print "sum    = %10.3e"%(termA+termk+termAk)
        print
        print "factor = %10.3e"%factor
        print "sf     = %10.3e"%out
    return out

def f(x0 = None, A = None, k = None, verbose = False) :
    out = A*math.exp(-k*x0)
    if verbose :
        print "f      = %10.3e"%out
    return out

def sfOverf(rhoAk = None, verbose = False) :
    if verbose :
        print "-"*19
        print "rhoAk  = %10.3e"%rhoAk
    den =  f(x0      = 296.0,
             A       = 1.402e-05,
             k       = 5.172e-03,
             verbose = verbose,
             )

    num = sigmaf(x0      = 296.0,
                 A       = 1.402e-05, 
                 sigmaA  = 1.883e-05, 
                 k       = 5.172e-03, 
                 sigmak  = 5.611e-03, 
                 rhoAk   = rhoAk,
                 verbose = verbose,
                 )
    if verbose :
        print "-"*19
        print

    return num/den

print "rhoAk     sigmaQcd0/Qcd0"
print "------------------------"
for i,rhoAk in enumerate([-1.0, -0.8, -0.4, 0.0, 0.4, 0.8, 1.0]) :
    ans = sfOverf(rhoAk = rhoAk, verbose = False)
    print "%5.2f    %10.3e"%(rhoAk,ans)
