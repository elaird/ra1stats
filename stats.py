#!/usr/bin/env python
import os
from multiprocessing import Process,JoinableQueue
import ROOT as r
############################################
def opts() :
    from optparse import OptionParser
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch", dest = "batch", default = None,  metavar = "N",          help = "split into N jobs and submit to batch queue (N>0)")
    parser.add_option("--local", dest = "local", default = None,  metavar = "N",          help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge", dest = "merge", default = False, action  = "store_true", help = "merge job output")
    options,args = parser.parse_args()
    assert options.batch==None or options.local==None,"Choose only one of (batch, local)"
    for item in [options.batch, options.local] :
        assert item==None or int(item)>0,"N must be greater than 0"
    return options
#####################################
def operateOnListUsingQueue(nCores, workerFunc, inList) :
    q = JoinableQueue()
    listOfProcesses=[]
    for i in range(nCores):
        p = Process(target = workerFunc, args = (q,))
        p.daemon = True
        p.start()
        listOfProcesses.append(p)
    map(q.put,inList)
    q.join()# block until all tasks are done
    #clean up
    for process in listOfProcesses :
        process.terminate()
############################################
def jobCmds(nSlices = None) :
    pwd = os.environ["PWD"]
    if nSlices==None :
        return ["%s/job.sh %s %s/%s %g %g"%(pwd, pwd, pwd, sourceFile, point[0], point[1]) for point in points()]
    else :
        out = []
        for iSlice in range(nSlices) :
            args = [ "%g %g"%point for point in points()[iSlice::nSlices] ]
            out.append("%s/job.sh %s %s/%s %s"%(pwd, pwd, pwd, sourceFile, " ".join(args)))
        return out
############################################    
def batch(nSlices) :
    for jobCmd in jobCmds(nSlices) :
        subCmd = "bsub %s"%jobCmd
        print subCmd
        #os.system(subCmd)
############################################    
def local(nWorkers) :
    def worker(q) :
        while True:
            item = q.get()
            os.system(item)
            q.task_done()
    operateOnListUsingQueue(nWorkers, worker, jobCmds())
############################################
def compile(file) :
    r.gROOT.LoadMacro("%s+"%file)
############################################
def points() :
    return [(100.0, 50.0), (150.0, 50.0), (100.0, 75.0), (150.0, 75.0)]
############################################
options = opts()

sourceFile = "Lepton.C"
compile(sourceFile)

if options.batch :
    batch(int(options.batch))

if options.local :
    local(int(options.local))
    
if options.merge :
    pass
