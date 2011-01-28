#!/usr/bin/env python
import os
import ROOT as r
############################################
def opts() :
    from optparse import OptionParser
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--submit",  dest = "submit", default = False, action  = "store_true", help = "submit to batch queue")
    parser.add_option("--merge",   dest = "merge",  default = False, action  = "store_true", help = "merge job output")
    options,args = parser.parse_args()

    return options
############################################
def points() :
    return [(100.0, 50.0), (150.0, 50.0), (100.0, 75.0), (150.0, 75.0)]
############################################
def submitJob(point) :
    jobCmd = "%s/job.sh %s %g %g"%(os.environ["PWD"], os.environ["PWD"], point[0], point[1])
    subCmd = "bsub %s"%jobCmd
    print subCmd
    os.system(subCmd)
############################################
options = opts()

if options.submit :
    for point in points() :
        submitJob(point)

if options.merge :
    pass
