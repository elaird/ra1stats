#!/usr/bin/env python
import sys
import histogramProcessing as hp

if len(sys.argv)<3 :
    print "usage: %s obsFile expFile"%sys.argv[0]
    exit()
    
hp.expectedLimit(sys.argv[1], sys.argv[2])
