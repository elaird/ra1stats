#!/usr/bin/env python

from collections import defaultdict
from optparse import OptionParser
import os

from configuration import batch as batchConf
############################################
def opts() :
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch",      dest = "batch",      default = None,  metavar = "N",          help = "split into N jobs and submit to batch queue (N=0 means max splitting)")
    parser.add_option("--pbatch",     dest = "pbatch",     default = False, metavar = "N",          help = "split into maximum number of jobs and submit parametrically to the queue", action="store_true")
    parser.add_option("--queue",      dest = "queue",      default = None,  metavar = "QUEUE_NAME", help = "choose specific queue for pbatch submission", action="store")
    parser.add_option("--offset",     dest = "offset",     default = 0,     metavar = "N",          help = "offset by N*nJobsMax")
    parser.add_option("--local",      dest = "local",      default = None,  metavar = "N",          help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge",      dest = "merge",      default = False, action  = "store_true", help = "merge job output")
    parser.add_option("--skip",       dest = "skip",       default = False, action  = "store_true", help = "skip jobs; merge input rather than output files")
    parser.add_option("--validation", dest = "validation", default = False, action  = "store_true", help = "make validation plots")
    parser.add_option("--output",     dest = "output",     default = False, action  = "store_true", help = "write stdout&stderr to disk rather than to /dev/null")
    options,args = parser.parse_args()
    assert options.local==None or int(options.local)>0,"N must be greater than 0"
    if options.queue is not None :
        assert options.pbatch, "Cannot choose queue for non parametric batch submission"
    for pair in [("local", "batch"), ("merge", "batch"), ("pbatch", "batch"), ("local","pbatch"), ("merge","pbatch")] :
        assert (not getattr(options, pair[0])) or (not getattr(options, pair[1])),"Choose only one of (%s, %s)"%pair
    return options
############################################
def jobCmds(nSlices = None, offset = 0, skip = False, ignoreScript=False) :
    pwd = os.environ["PWD"]
    points = histogramProcessing.points()
    if not offset : pickling.writeSignalFiles(points, outFilesAlso = skip)
    if not nSlices : nSlices = len(points)
    out = []
    if skip : return out,""

    logDir = conf.directories.log()

    nJobsMax = batchConf.nJobsMax()
    iStart = offset*nJobsMax
    iFinish = min(iStart+nJobsMax, nSlices) if nJobsMax > 0 else nSlices
    if (iFinish!=nSlices) or offset :
        warning = "Only jobs [%d - %d] / [%d - %d] jobs have been submitted."%(iStart, iFinish-1, 0, nSlices-1)
    else :
        warning = ""
    if (iFinish!=nSlices) and iFinish!=0 :
        warning += "  Re-run with --offset=%d when your jobs have completed."%(1+offset)
    #assert iStart<iFinish,warning
    for iSlice in range(iStart, iFinish) :
        argDict = {0:"%s/job.sh"%pwd, 1:pwd, 2:batchConf.envScript(),
                   3:"%s/%s/job_%d.log"%(pwd, logDir, iSlice) if options.output else "/dev/null"}
        keyslice = 1 if ignoreScript else 0
        args = [argDict[key] for key in sorted(argDict.keys())[keyslice:]]
        slices = [ "%d %d %d"%point for point in points[iSlice::nSlices] ]
        out.append(" ".join(args+slices))

    return out,warning

def pjobCmds(queue=None) :
    from socket import gethostname

    pwd = os.environ["PWD"]

    points = histogramProcessing.points()
    n_points = len(points)

    njm = batchConf.nJobsMax()
    pickling.writeSignalFiles(points, outFilesAlso = False)

    pos = 0
    host=gethostname()
    pid=os.getpid()
    out = defaultdict(dict)
    for q_name, num_points in getQueueRanges(n_points,queue).iteritems():
        out[q_name]["args"] = []
        out[q_name]["n_points"] = num_points
        filename = "{dir}/{host}_{queue}_{pid}.points".format(dir=conf.directories.points(),
                                                              host=host,
                                                              queue=q_name,
                                                              pid=pid)
        pointsToFile( filename, points[pos:pos+num_points] )
        pos += num_points
        n_para_jobs = (num_points/njm) + 1
        iStart = 0
        iFinish = ( num_points /  njm ) + 1
        if num_points % njm == 0 :
            # if they exactly divide we don't need the final job
            iFinish-=1

        for i in range(iStart, iFinish) :
            argDict = {0:"%s/pjob.sh"%pwd, 1:pwd, 2:batchConf.envScript(),
                       3:"/dev/null" }
            args = [argDict[key] for key in sorted(argDict.keys())]
            out[q_name]["args"].append("%s %s" %(" ".join(args),filename))
    return out, n_points

def pointsToFile( filename, points ) :
    file = open( filename, 'w')
    for point in points:
        # bit of a hack to get a clean list out
        out = " ".join( [ str(p) for p in point ] )
        print>>file, out
    file.close()

def getQueueRanges( npoints, queue=None ) :
    qData = batchConf.qData()
    from math import ceil
    if queue is not None and queue in qData.keys():
        # allow override for running on a single queue
        qData = { queue : qData[queue] }
    total_cores = sum( [ q["ncores"] for q in qData.values() ] )
    jobs_per_core = npoints / float(total_cores)
    jobsPerQueue = {}
    total_covered = 0
    for qname, info in qData.iteritems() :
        n_jobs = int(ceil(info["ncores"]*jobs_per_core))
        jobsPerQueue[qname] = n_jobs if (total_covered + n_jobs) <= npoints \
                                     else (npoints - total_covered)
        total_covered += n_jobs

    return jobsPerQueue

############################################
def pbatch(queue=None, debug=False) :
    queue_job_details, n_points = pjobCmds(queue)
    n_jobs_max = batchConf.nJobsMax()

    subCmds = []
    for q_name, details in queue_job_details.iteritems():
        for i, args in enumerate(details["args"]):
            #print "{q} => {a}".format( q=q_name, a=args )
            #continue
            start = i*n_jobs_max + 1
            end   = min(i*n_jobs_max + n_jobs_max, details["n_points"])
            base_cmd = batchConf.subCmdFormat() % q_name
            cmd = "{subcmd} -t {start}-{end}:1 {args}".format(subcmd=base_cmd,
                                                              start=start, end=end,
                                                              args=args)
            subCmds.append(cmd)
    if debug:
        for cmd in subCmds:
            print cmd
    utils.operateOnListUsingQueue(4, utils.qWorker(os.system, star = False), subCmds)

############################################
def batch(nSlices = None, offset = None, skip = False) :
    jcs,warning = jobCmds(nSlices = nSlices, offset = offset, skip = skip,
            ignoreScript = (conf.batchHost=="FNAL"))
    subCmds = []
    star = False
    dstar = False
    if conf.batchHost == "IC" :
        subCmds = ["%s %s"%(batchConf.subCmd(), jobCmd) for jobCmd in jcs]
        qFunc = os.system
    elif conf.batchHost == "FNAL" :
        dstar = True
        # replaces os.system in the below example
        from condor import submitBatchJob
        qFunc = submitBatchJob
        subCmds = [ {
                        "jobCmd": "./job.sh %s" % (jc),
                        "indexDict": { "dir": "condor_batch", "ind": i },
                        "subScript": conf.getSubCmds(),
                        "jobScript": "job.sh",
                        "condorTemplate": "condor/fnal_cmsTemplate.condor",
                        "jobScriptFileName_format": "%(dir)s/job_%(ind)d.sh",
                    } for i,jc in enumerate(jcs) ]
    utils.operateOnListUsingQueue(4, utils.qWorker(qFunc, star = star, dstar = dstar), subCmds)
    if warning : print warning
############################################
def local(nWorkers = None, skip = False) :
    jcs,warning = jobCmds(skip = skip)
    if skip : return
    utils.operateOnListUsingQueue(nWorkers, utils.qWorker(os.system, star = False), jcs)
############################################
def mkdirs():
    module = conf.directories
    for name in ["job", "log", "plot", "points"]:
        dirName = getattr(module, name)()
        utils.mkdir(dirName)
############################################
options = opts()

import configuration as conf
import plottingGrid,pickling,histogramProcessing,utils,cpp

mkdirs()
cpp.compile()

if options.batch  : batch(nSlices = int(options.batch), offset = int(options.offset), skip = options.skip)
if options.local  : local(nWorkers = int(options.local), skip = options.skip)
if options.merge  : pickling.mergePickledFiles()
if options.pbatch : pbatch(options.queue)

if options.merge or options.validation :
    plottingGrid.makePlots()

if not any([getattr(options,item) for item in ["batch", "local", "merge", "validation"]]) :
    print "nPoints = %s"%len(histogramProcessing.points())
