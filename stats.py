#!/usr/bin/env python
from optparse import OptionParser
import os
############################################
def opts() :
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch",      dest = "batch",      default = None,  metavar = "N",          help = "split into N jobs and submit to batch queue (N=0 means max splitting)")
    parser.add_option("--pbatch",     dest = "pbatch",     default = False, metavar = "N",          help = "split into maximum number of jobs and submit parametrically to the queue", action="store_true")
    parser.add_option("--offset",     dest = "offset",     default = 0,     metavar = "N",          help = "offset by N*nJobsMax")
    parser.add_option("--local",      dest = "local",      default = None,  metavar = "N",          help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge",      dest = "merge",      default = False, action  = "store_true", help = "merge job output")
    parser.add_option("--skip",       dest = "skip",       default = False, action  = "store_true", help = "skip jobs; merge input rather than output files")
    parser.add_option("--validation", dest = "validation", default = False, action  = "store_true", help = "make validation plots")
    parser.add_option("--output",     dest = "output",     default = False, action  = "store_true", help = "write stdout&stderr to disk rather than to /dev/null")
    options,args = parser.parse_args()
    assert options.local==None or int(options.local)>0,"N must be greater than 0"
    for pair in [("local", "batch"), ("merge", "batch"), ("pbatch", "batch"), ("local","pbatch"), ("merge","pbatch")] :
        assert (not getattr(options, pair[0])) or (not getattr(options, pair[1])),"Choose only one of (%s, %s)"%pair
    return options
############################################
def jobCmds(nSlices = None, offset = 0, skip = False) :
    pwd = os.environ["PWD"]
    points = histogramProcessing.points()
    if not offset : pickling.writeSignalFiles(points, outFilesAlso = skip)
    if not nSlices : nSlices = len(points)
    out = []
    if skip : return out,""
    
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
                   3:"%s/%s_%d.log"%(pwd, logStem, iSlice) if options.output else "/dev/null"}
        args = [argDict[key] for key in sorted(argDict.keys())]
        slices = [ "%d %d %d"%point for point in points[iSlice::nSlices] ]
        out.append(" ".join(args+slices))

    return out,warning

def pjobCmds( filename ) :
    pwd = os.environ["PWD"]
    points = histogramProcessing.points()
    npoints = len(points)
    njm = conf.switches()["nJobsMax"]
    pickling.writeSignalFiles(points, outFilesAlso = False)
    pointsToFile( filename, points )

    logStem = conf.stringsNoArgs()["logStem"]
    switches = conf.switches()

    njobs = (npoints/njm) + 1
    out = []
    iStart = 0
    iFinish = ( npoints /  njm ) + 1
    if npoints % njm == 0 :
        iFinish-=1
    for i in range(iStart, iFinish) :
        argDict = {0:"%s/pjob.sh"%pwd, 1:pwd, 2:switches["envScript"],
                   3:"/dev/null" }
        args = [argDict[key] for key in sorted(argDict.keys())]
        out.append("%s %s" %(" ".join(args),filename))
    return out, npoints

def pointsToFile( filename, points ) :
    file = open( filename, 'w')
    for point in points:
        # bit of a hack to get a clean list out
        out = " ".join( [ str(p) for p in point ] )
        print>>file, out
    file.close()

############################################
def pbatch() :
    from socket import gethostname
    utils.mkdir("points")
    filename = "points/%s_%d.points" % ( gethostname(), os.getpid() )
    jcs, npoints = pjobCmds(filename)
    njm = conf.switches()["nJobsMax"]
    njobs = (npoints/njm) + 1

    subCmds = []
    for i,j in enumerate(jcs) :
        start = i*njm + 1
        end   = i*njm + njm
        if end > npoints : 
            end = npoints
        subCmds.append( "%s -t %d-%d:1 %s"%(conf.switches()["subCmd"], start, end, j ) )
    utils.operateOnListUsingQueue(4, utils.qWorker(os.system, star = False), subCmds)

############################################
def batch(nSlices = None, offset = None, skip = False) :
    jcs,warning = jobCmds(nSlices = nSlices, offset = offset, skip = skip)
    subCmds = ["%s %s"%(conf.switches()["subCmd"], jobCmd) for jobCmd in jcs]
    utils.operateOnListUsingQueue(4, utils.qWorker(os.system, star = False), subCmds)
    if warning : print warning
############################################
def local(nWorkers = None, skip = False) :
    jcs,warning = jobCmds(skip = skip)
    if skip : return
    utils.operateOnListUsingQueue(nWorkers, utils.qWorker(os.system, star = False), jcs)
############################################
def mkdirs() :
    s = conf.stringsNoArgs()
    utils.mkdir(s["logDir"])
    utils.mkdir(s["outputDir"])
############################################
def compile() :
    import ROOT as r
    r.gROOT.LoadMacro("cpp/StandardHypoTestInvDemo.cxx+")
############################################
options = opts()

import configuration as conf
import plottingGrid,pickling,histogramProcessing,utils

mkdirs()
compile()

if options.batch  : batch(nSlices = int(options.batch), offset = int(options.offset), skip = options.skip)
if options.local  : local(nWorkers = int(options.local), skip = options.skip)
if options.merge  : pickling.mergePickledFiles()
if options.pbatch : pbatch()

if options.merge or options.validation :
    plottingGrid.makePlots()

if not any([getattr(options,item) for item in ["batch", "local", "merge", "validation"]]) :
    print "nPoints = %s"%len(histogramProcessing.points())
