#!/usr/bin/env python
from optparse import OptionParser
import os
############################################
def opts() :
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch",      dest = "batch",      default = None,  metavar = "N", help = "split into N jobs and submit to batch queue (N=0 means max splitting)")
    parser.add_option("--offset",     dest = "offset",     default = 0,  metavar = "N", help = "offset by N*nJobsMax")
    parser.add_option("--local",      dest = "local",      default = None,  metavar = "N", help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge",      dest = "merge",      default = False, action  = "store_true", help = "merge job output")
    parser.add_option("--efficiency", dest = "efficiency", default = False, action  = "store_true", help = "make efficiency plots")
    parser.add_option("--validation", dest = "validation", default = False, action  = "store_true", help = "make validation plots")
    parser.add_option("--output",     dest = "output",     default = False, action  = "store_true", help = "write stdout&stderr to disk rather than to /dev/null")
    options,args = parser.parse_args()
    assert options.local==None or int(options.local)>0,"N must be greater than 0"
    for pair in [("local", "batch"), ("merge", "batch"), ("local", "efficiency"), ("batch", "efficiency")] :
        assert (not getattr(options, pair[0])) or (not getattr(options, pair[1])),"Choose only one of (%s, %s)"%pair
    return options
############################################
def jobCmds(nSlices = None, offset = 0) :
    pwd = os.environ["PWD"]
    points = hp.points()
    if not nSlices : nSlices = len(points)
    out = []

    logStem = conf.stringsNoArgs()["logStem"]
    switches = conf.switches()

    iStart = offset*switches["nJobsMax"]
    iFinish = min(iStart+switches["nJobsMax"], nSlices)
    if (iFinish!=nSlices) or offset :
        warning = "Only jobs [%d - %d] / [%d - %d] jobs have been submitted."%(iStart, iFinish-1, 0, nSlices-1)
    else :
        warning = ""
    if (iFinish!=nSlices) :
        warning += "  Re-run with --offset=%d when your jobs have completed."%(1+offset)
    assert iStart<iFinish,warning
    for iSlice in range(iStart, iFinish) :
        argDict = {0:"%s/job.sh"%pwd, 1:pwd, 2:switches["envScript"],
                   3:"/dev/null" if options.output else "%s/%s_%d.log"%(pwd, logStem, iSlice)}
        args = [argDict[key] for key in sorted(argDict.keys())]
        slices = [ "%d %d %d"%point for point in points[iSlice::nSlices] ]
        out.append(" ".join(args+slices))

    return out,warning
############################################
def batch(nSlices = None, offset = None) :
    jcs,warning = jobCmds(nSlices, offset)
    subCmds = ["%s %s"%(conf.switches()["subCmd"], jobCmd) for jobCmd in jcs]
    utils.operateOnListUsingQueue(4, utils.qWorker(os.system, star = False), subCmds)
    if warning : print warning
############################################
def local(nWorkers) :
    utils.operateOnListUsingQueue(nWorkers, utils.qWorker(os.system, star = False), jobCmds()[0])
############################################
def mkdirs() :
    s = conf.stringsNoArgs()
    utils.mkdir(s["logDir"])
    utils.mkdir(s["outputDir"])
############################################
options = opts()

import utils
import configuration as conf
import histogramProcessing as hp

hp.checkHistoBinning()
mkdirs()

if options.batch : batch(nSlices = int(options.batch), offset = int(options.offset))
if options.local : local(int(options.local))
if options.merge : hp.mergePickledFiles()

if options.merge or options.validation :
    hp.makeValidationPlots()
if options.efficiency :
    hp.makeEfficiencyPlots()
    hp.makeEfficiencyUncertaintyPlots()
    hp.makeTopologyXsLimitPlots()

if not any([getattr(options,item) for item in ["batch", "local", "merge", "validation", "efficiency"]]) :
    print "nPoints = %s"%len(hp.points())
