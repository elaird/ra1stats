#!/usr/bin/env python
#####################################
from multiprocessing import Process,JoinableQueue
import os,subprocess,math,traceback,sys,array
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
class thstack(object) :
    """work-around for bugging THStacks in ROOT 5.30.00"""
    def __init__(self, name = "") :
        self.name = name
        self.histos = []
    def Add(self, inHisto, options = "") :
        histo = inHisto.Clone("%s_%s"%(inHisto.GetName(), self.name))
        self.histos.append( (histo, options) )
        if len(self.histos)>1 :
            self.histos[-1][0].Add(self.histos[-2][0])
    def Draw(self, goptions, reverse = False) :
        histos = self.histos if not reverse else reversed(self.histos)
        for histo,options in histos :
            histo.Draw(goptions+options)
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
def epsToPdf(epsFileName, removeEps = True) :
    os.system("epstopdf %s"%epsFileName)
    if removeEps : os.remove(epsFileName)
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
class qWorker(object) :
    def __init__(self, func = None, star = True) :
        self.func = func
        self.star = star
    def __call__(self,q) :
        while True:
            item = q.get()
            try:
                if self.func :
                    if self.star : self.func(*item)
                    else : self.func(item)
                else: item()
            except Exception as e:
                traceback.print_tb(sys.exc_info()[2], limit=20, file=sys.stdout)
                print e.__class__.__name__,":", e
            q.task_done()
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
def quantiles(histo = None, sigmaList = []) :
    areaFractions = [ ( 1.0+r.TMath.Erf(nSigma/math.sqrt(2.0)) )/2.0 for nSigma in sigmaList]
    probSum = array.array('d', areaFractions)
    q = array.array('d', [0.0]*len(probSum))
    histo.GetQuantiles(len(probSum), q, probSum)
    return q
#####################################
