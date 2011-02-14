#!/usr/bin/env python
#####################################
from multiprocessing import Process,JoinableQueue
import os,subprocess
import ROOT as r
#####################################
def delete(thing) :
    #free up memory (http://wlav.web.cern.ch/wlav/pyroot/memory.html)
    thing.IsA().Destructor( thing )
#####################################
def generateDictionaries() :
    r.gInterpreter.GenerateDictionary("std::pair<std::string,std::string>","string")
    r.gInterpreter.GenerateDictionary("std::map<std::string,std::string>","string;map")
    r.gInterpreter.GenerateDictionary("std::pair<std::string,std::vector<double> >","string;vector")
    r.gInterpreter.GenerateDictionary("std::map<string,vector<double> >","string;map;vector")
#####################################
def compile(sourceFile) :
    r.gROOT.LoadMacro("%s+"%sourceFile)
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
#####################################
def getCommandOutput(command):
    p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return {"stdout":stdout, "stderr":stderr, "returncode":p.returncode}
#####################################
def stdMap(d, t1, t2) :
    out = r.std.map(t1, t2)()
    for key,value in d.iteritems() :
        out[key] = value
    return out
#####################################
def stdMap_String_VectorDoubles(d) :
    out = r.std.map("std::string", "std::vector<double>")()
    for key,value in d.iteritems() :
        v = r.std.vector('double')()
        if type(value) is tuple :
            for item in value :
                v.push_back(item)
        else :
            v.push_back(value)
        out[key] = v
    return out
#####################################
