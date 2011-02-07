#!/usr/bin/env python
import data
from simplePL import *

pl = simplePL( data.numbers() )
CL = 0.95
bound = pl.upperLimit(CL)

print "\n"
print "The %0.2f CL upper bound on the parameter of interest is %0.4f" % (CL, bound)
print

