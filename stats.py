#!/usr/bin/env python
import os,cPickle,utils
import configuration as conf
import histogramProcessing as hp
############################################
def opts() :
    from optparse import OptionParser
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch", dest = "batch", default = None,  metavar = "N", help = "split into N jobs and submit to batch queue (N<=0 means max splitting)")
    parser.add_option("--local", dest = "local", default = None,  metavar = "N", help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge", dest = "merge", default = None,  metavar = "N", help = "merge job output using N temporary slices (N>0)")
    options,args = parser.parse_args()
    assert options.batch==None or options.local==None,"Choose only one of (batch, local)"
    assert options.local==None or int(options.local)>0,"N must be greater than 0"
    assert options.merge==None or int(options.merge)>0,"N must be greater than 0"
    return options
############################################
def jobCmds(nSlices = None, useCompiled = True) :
    def logFileName(iSlice) :
        return "%s_%d.log"%(conf.stringsNoArgs()["logStem"], iSlice)

    def writeYields() :
        for point,yields in hp.points().iteritems() :
            outFile = open(conf.strings(*point)["configFileName"], "w")
            cPickle.dump(yields, outFile)
            outFile.close()
    pwd = os.environ["PWD"]

    if nSlices<=0 : nSlices = len(hp.points())
    out = []

    writeYields()
    strings = conf.stringsNoArgs()
    for iSlice in range(nSlices) :
        args = [ "%d %d %d"%point for point in hp.points().keys()[iSlice::nSlices] ]
        s  = "%s/job.sh"%pwd                             #0
        s += " %s"%pwd                                   #1
        s += " %s/%s%s"%(pwd,                            #2
                         strings["sourceFile"],
                         "+" if useCompiled else "+"
                         )
        s += " %s"%(" ".join(args))                      #3
        s += " >& %s/%s"%(pwd, logFileName(iSlice))
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
    utils.operateOnListUsingQueue(nWorkers, worker, jobCmds())
############################################
def mkdirs() :
    s = conf.stringsNoArgs()
    utils.mkdir(s["configDir"])
    utils.mkdir(s["logDir"])
    utils.mkdir(s["outputDir"])
############################################
def merge(nSlices) :
    def cleanUp(stderr, files) :
        if stderr :
            print "hadd had this stderr: %s"%stderr
            return
        else :
            for fileName in files :
                os.remove(fileName)

    def prunedList(l) :
        out = []
        for fileName in l :
            if os.path.exists(fileName) :
                out.append(fileName)
            else :
                print "Skipping %s"%fileName
        return out

    def go(outFile, inList) :
        inList2 = prunedList(inList)
        hAdd = utils.getCommandOutput("hadd -f %s %s"%(outFile, " ".join(prunedList(inList2))))
        cleanUp(hAdd["stderr"], inList2)
        return outFile if inList2 else None
        
    def mergeOneType(attr) :
        inList = [conf.strings(*point)["%sFileName"%attr] for point in hp.points()]
        outFile = "%s.root"%conf.stringsNoArgs()["%sStem"%attr]

        outFiles = []
        for iSlice in range(nSlices) :
            tmpFile = outFile.replace(".root","_%d.root"%iSlice)
            addedFile = go(tmpFile, inList[iSlice::nSlices])
            if addedFile : outFiles.append(addedFile)
        go(outFile, outFiles)

    mergeOneType("plot")
    if conf.switches()["writeWorkspaceFile"] :
        mergeOneType("workspace")
############################################    
options = opts()
hp.checkHistoBinning()
utils.generateDictionaries()
utils.compile(conf.stringsNoArgs()["sourceFile"])
mkdirs()
if options.batch : batch(int(options.batch))
if options.local : local(int(options.local))
if options.merge : merge(int(options.merge))
