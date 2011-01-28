#!/usr/bin/env python
import os,subprocess
from multiprocessing import Process,JoinableQueue
import ROOT as r
import configuration as conf
import histogramProcessing as hp
############################################
def opts() :
    from optparse import OptionParser
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch", dest = "batch", default = None,  metavar = "N",          help = "split into N jobs and submit to batch queue (N<=0 means max splitting)")
    parser.add_option("--local", dest = "local", default = None,  metavar = "N",          help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge", dest = "merge", default = None,  metavar = "N",          help = "merge job output using N temporary slices (N>0)")
    options,args = parser.parse_args()
    assert options.batch==None or options.local==None,"Choose only one of (batch, local)"
    assert options.local==None or int(options.local)>0,"N must be greater than 0"
    assert options.merge==None or int(options.merge)>0,"N must be greater than 0"
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
#####################################
def mkdir(path) :
    try:
        os.makedirs(path)
    except OSError as e :
        if e.errno!=17 :
            raise e
############################################
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}
############################################
def jobCmds(nSlices = None, useCompiled = True) :
    pwd = os.environ["PWD"]

    if nSlices<=0 : nSlices = len(hp.points())
    out = []
    for iSlice in range(nSlices) :
        args = [ "%g %g"%point for point in hp.points()[iSlice::nSlices] ]
        s  = "%s/job.sh"%pwd                             #0
        s += " %s"%pwd                                   #1
        s += " %s/%s%s"%(pwd,                            #2
                         conf.sourceFile(),
                         "+" if useCompiled else " "
                         )
        s += " %s"%(" ".join(args))                      #3
        s += " >& %s/%s"%(pwd, conf.logFileName(iSlice))
        out.append(s)
    return out
############################################
def batch(nSlices) :
    for jobCmd in jobCmds(nSlices, useCompiled = False) :
        subCmd = "bsub %s"%jobCmd
        os.system(subCmd)
############################################
def local(nWorkers) :
    def worker(q) :
        while True:
            item = q.get()
            os.system(item)
            q.task_done()
    operateOnListUsingQueue(nWorkers, worker, jobCmds())
############################################
def compile() :
    r.gROOT.LoadMacro("%s+"%conf.sourceFile())
############################################
def mkdirs() :
    for item in ["logDir", "outputDir"] :
        mkdir(getattr(conf, item)())
############################################
def merge(nSlices) :
    def cleanUp(stderr, files) :
        assert not stderr, "hadd had this stderr: %s"%stderr
        for fileName in files :
            os.remove(fileName)

    def mergeOneType(attr) :
        inList = [getattr(conf, "%sFileName"%attr)(*point) for point in hp.points()]
        outFile = "%s%s"%(getattr(conf, "%sStem"%attr)(), ".root")

        outFiles = []
        for iSlice in range(nSlices) :
            tmpList = inList[iSlice::nSlices]
            tmpFile = "%s%d"outFile.replace(".root","_%d.root"%iSlice)
            hAdd = getCommandOutput("hadd -f %s %s"%(tmpFile, " ".join(tmpList)))
            #cleanUp(hAdd["stderr"], tmpList)
            outFiles.append(tmpFile)

        hAdd = getCommandOutput("hadd -f %s %s"%(outFile, " ".join(outFiles)))
        #cleanUp(hAdd["stderr"], outFiles)

    mergeOneType("plot")
    if conf.writeWorkspaceFile() :
        mergeOneType("workspace")
############################################    
options = opts()
compile()
mkdirs()
if options.batch : batch(int(options.batch))
if options.local : local(int(options.local))
if options.merge : merge(int(options.merge))
