#!/usr/bin/env python
#####################################
from multiprocessing import Process,JoinableQueue
import os,subprocess,math
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
class numberedCanvas(r.TCanvas) :
    page = 0
    text = r.TText()
    text.SetNDC()
    text.SetTextFont(102)
    text.SetTextSize(0.45*text.GetTextSize())
    text.SetTextAlign(33)
    
    def Print(self, *args) :
        if self.page : self.text.DrawText(0.95, 0.02, "page %2d"%self.page)
        self.page += 1
        super(numberedCanvas, self).Print(*args)
#####################################
def ps2pdf(psFileName, removePs = True) :
    os.system("ps2pdf %s"%psFileName)
    if removePs : os.remove(psFileName)
#####################################
def rooFitResults(pdf, data, options = (r.RooFit.Verbose(False), r.RooFit.PrintLevel(-1), r.RooFit.Save(True))) :
    return pdf.fitTo(data, *options)
#####################################
def compile(sourceFile) :
    r.gSystem.SetAclicMode(r.TSystem.kDebug)
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
def quadSum(l) :
    return math.sqrt(sum([x**2 for x in l]))
#####################################
