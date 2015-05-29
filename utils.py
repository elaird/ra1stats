import array
import cPickle
import math
import os
import subprocess
import sys
import traceback
import re
from multiprocessing import Process, JoinableQueue
import ROOT as r


def writeNumbers(fileName=None, d=None):
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()


def readNumbers(fileName):
    inFile = open(fileName)
    d = cPickle.load(inFile)
    inFile.close()
    return d


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
def threeToTwo(h3) :
    name = h3.GetName()
    h2 = r.TH2D(name+"_2D",h3.GetTitle(),
                h3.GetNbinsX(), h3.GetXaxis().GetXmin(), h3.GetXaxis().GetXmax(),
                h3.GetNbinsY(), h3.GetYaxis().GetXmin(), h3.GetYaxis().GetXmax(),
                )

    for iX in range(1, 1+h3.GetNbinsX()) :
        for iY in range(1, 1+h3.GetNbinsY()) :
            content = h3.GetBinContent(iX, iY, 1)
            h2.SetBinContent(iX, iY, content)
    h2.GetZaxis().SetTitle(h3.GetZaxis().GetTitle())
    h2.SetDirectory(0)
    return h2
#####################################
def bins(h, interBin=""):
    assert interBin in ["LowEdge", "Center"], interBin
    out = []
    funcs = {"X":getattr(h.GetXaxis(),"GetBin%s"%interBin),
             "Y":getattr(h.GetYaxis(),"GetBin%s"%interBin),
             "Z":getattr(h.GetZaxis(),"GetBin%s"%interBin),
             }
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = funcs["X"](iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = funcs["Y"](iBinY)
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                z = funcs["Z"](iBinZ)
                out.append((iBinX, x, iBinY, y, iBinZ, z))
    return out
#####################################
def histoMax(h) :
    i = h.GetMaximumBin()
    return (h.GetBinContent(i)+h.GetBinError(i))
#####################################
def shifted(h=None, shift=(False, False), shiftErrors=True, info=True):
    assert len(shift) in range(1,4),shift

    axes = [ 'X', 'Y', 'Z' ]
    try:
        dim = int(h.ClassName()[2])
    except ValueError as e:
        print "Tried shifting h w/ dim>3 or non-histo:", h.ClassName(), "=>", e
        print "Object will remain unshifted"
        return h

    htype = h.ClassName()[-1]

    args = []
    shiftWidths = []
    for i in range(dim) :
        axis = getattr(h, "Get%saxis"%axes[i])()
        nBins = getattr(h, "GetNbins%s"%axes[i])()
        max = axis.GetXmax()
        min = axis.GetXmin()
        shiftWidths.append((max - min)/(2.0*nBins) if shift[i] else 0.0)
        args += [nBins, min - shiftWidths[-1], max - shiftWidths[-1]]

    hname = h.GetName()
    if any(shiftWidths) and info:
        print "INFO: shifting {0} by {1}".format(hname,shiftWidths)

    histoConstructor= getattr(r,'TH%d%s'%(dim,htype))
    out = histoConstructor( hname+"_shifted", h.GetTitle(), *args)
    out.SetDirectory(0)

    for iBinX,x,iBinY,y,iBinZ,z in bins(h, interBin="Center"):#"LowEdge"):
        out.SetBinContent(iBinX, iBinY, iBinZ, h.GetBinContent(iBinX, iBinY, iBinZ))
        if shiftErrors:
            out.SetBinError(iBinX, iBinY, iBinZ, h.GetBinError(iBinX, iBinY, iBinZ))
    return out
#####################################
class thstack(object) :
    """work-around for buggy THStacks in ROOT 5.30.00"""
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
    def Maximum(self) :
        if not len(self.histos) : return None
        return max([histoMax(h[0]) for h in self.histos])
#####################################
class thstackMulti(object) :
    def __init__(self, name = "", drawErrors = False) :
        self.name = name
        self.drawErrors = drawErrors
        self.histos = []

    def Add(self, histos = {}, spec = {}) :
        self.histos.append( (histos, spec) )
        if len(self.histos)>1 :
            self.histos[-1][0]["value"].Add(self.histos[-2][0]["value"])
            #propagate error too?

    def Draw(self, goptions, reverse = False) :
        repeat = []
        for histos,spec in self.histos if not reverse else reversed(self.histos) :
            histos2 = {}
            for key,value in histos.iteritems() :
                if key in spec.get("suppress", []) : continue
                histos2[key] = value

            if spec.get("repeatNoBand", False) :
                repeat.append( (histos2, spec) )
            self.DrawOne(histos2,
                         goptions = goptions + ("" if "goptions" not in spec else spec["goptions"]),
                         noErrors = ("type" in spec) and spec["type"]=="function" and not self.drawErrors,
                         errorBand = spec.get("errorBand", False),
                         bandFillStyle = spec.get("bandStyle", [1001,3004][0]))

        for histos,spec in repeat :
            self.DrawOne(histos,
                         goptions = goptions + ("" if "goptions" not in spec else spec["goptions"]),
                         noErrors = True,
                         )

    def Maximum(self) :
        if not len(self.histos) : return None
        return max([histoMax(h[0]["value"]) for h in self.histos])

    def DrawOne(self, histos = None, goptions = "", noErrors = None, errorBand = False, bandFillStyle = 1001) :
        if (not errorBand) or noErrors :
            histos["value"].Draw(goptions)
            for key in ["min", "max"] :
                if key in histos :
                    histos[key].Draw(goptions)
        else :
            histos["errors"].SetFillColor(errorBand)
            histos["errors"].SetMarkerColor(errorBand)
            histos["errors"].SetMarkerStyle(1)
            histos["errors"].SetFillStyle(bandFillStyle)
            histos["errors"].Draw("e2same")
            histos["noErrors"].Draw("he2"+goptions)
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
def divideCanvas( canvas, ratioCanvas = True, dimension = 1, nhistos = 0 ) :
    canvas.Clear()
    if dimension==1 :
        if ratioCanvas :
            split = 0.2
            canvas.Divide(1,2)
            canvas.cd(1).SetPad(0.01,split+0.01,0.99,0.99)
            canvas.cd(2).SetPad(0.01,0.01,0.99,split)
            #canvas.cd(2).SetTopMargin(0.07)#default=0.05
            #canvas.cd(2).SetBottomMargin(0.45)
            canvas.cd(1)
        else :
            canvas.Divide(1,1)
            #if self.anMode : canvas.UseCurrentStyle()
    else :
        mx=1
        my=1
        while mx*my<nhistos :
            if mx==my : mx+=1
            else :      my+=1
        canvas.Divide(mx,my)
#####################################
def ps2pdf(psFileName, removePs = True, sameDir = False) :
    cmd = ("ps2pdf %s"%psFileName) if not sameDir else ("ps2pdf %s %s"%(psFileName, psFileName.replace(".ps", ".pdf")))
    os.system(cmd)
    if removePs : os.remove(psFileName)
#####################################
def epsToPdf(fileName, tight = True, alsoPng = False) :
    pdfFileName = fileName.replace(".eps", ".pdf")
    if not tight : #make pdf
        os.system("epstopdf "+fileName)
        os.system("rm       "+fileName)
    else : #make pdf with tight bounding box
        epsiFile = fileName.replace(".eps",".epsi")
        os.system("ps2epsi "+fileName+" "+epsiFile)
        os.system("epstopdf "+epsiFile)
        os.system("rm       "+epsiFile)
        os.system("rm       "+fileName)

    if alsoPng :
        os.system("convert %s %s"%(pdfFileName, pdfFileName.replace(".pdf",".png")))
    print "INFO: %s has been written."%pdfFileName
#####################################
def rooFitResults(pdf, data, options=(r.RooFit.Verbose(False),
                                      r.RooFit.PrintLevel(-1),
                                      r.RooFit.Save(True),
                                      #r.RooFit.Strategy(r.RooMinuit.Robustness),
                                      ),
                  ):
    return pdf.fitTo(data, *options)
#####################################
def checkResults(results) :
    status = results.status()
    covQual = results.covQual()
    numIN = results.numInvalidNLL()
    if status : print "WARNING: status = %d"%status
    if numIN : print "WARNING: num invalid NLL = %d"%numIN
    #if covQual : print "WARNING: covQual = %d"%covQual
    return numIN
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
    def __init__(self, func = None, star = True, dstar =  False) :
        self.func = func
        self.star = star
        self.dstar = dstar
    def __call__(self,q) :
        while True:
            item = q.get()
            try:
                if self.func :
                    if self.star : self.func(*item)
                    if self.dstar: self.func(**item)
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
def indexFraction(item, l) :
    totalList = sorted(l+[item])
    i1 = totalList.index(item)
    totalList.reverse()
    i2 = len(totalList)-totalList.index(item)-1
    return (i1+i2)/2.0/len(l)
#####################################
def ListFromTGraph(graph = None) :
    ys = []
    x = r.Double()
    y = r.Double()
    for i in range(graph.GetN()) :
        graph.GetPoint(i, x, y)
        ys.append(float(y))
    return ys
#####################################
def TGraphFromList(lst = [], name = "") :
    out = r.TGraph()
    if name : out.SetName(name)
    for i,item in enumerate(lst) :
        out.SetPoint(i, i, item)
    return out
#####################################
def funcCollect(wspace, results = None) :
    funcs = wspace.allFunctions()
    func = funcs.createIterator()

    funcBestFit = {}
    funcLinPropError = {}
    while func.Next() :
        key = func.GetName()
        funcBestFit[key] = func.getVal()
        if results : funcLinPropError[key] = func.getPropagatedError(results)
    return funcBestFit,funcLinPropError
#####################################
def parCollect(wspace) :
    vars = wspace.allVars()
    it = vars.createIterator()

    parBestFit = {}
    parError = {}
    parMin = {}
    parMax = {}
    while it.Next() :
        if it.getMax()==r.RooNumber.infinity() : continue
        if it.getMin()==-r.RooNumber.infinity() : continue
        if not it.hasError() : continue
        key = it.GetName()
        parBestFit[key] = it.getVal()
        parError[key] = it.getError()
        parMin[key] = it.getMin()
        parMax[key] = it.getMax()
    return parBestFit,parError,parMin,parMax
##############################
def combineBinContentAndError(histo, binToContainCombo, binToBeKilled) :
    xflows     = histo.GetBinContent(binToBeKilled)
    xflowError = histo.GetBinError(binToBeKilled)

    if xflows==0.0 : return #ugly

    currentContent = histo.GetBinContent(binToContainCombo)
    currentError   = histo.GetBinError(binToContainCombo)

    histo.SetBinContent(binToBeKilled, 0.0)
    histo.SetBinContent(binToContainCombo, currentContent+xflows)

    histo.SetBinError(binToBeKilled, 0.0)
    histo.SetBinError(binToContainCombo, math.sqrt(xflowError**2+currentError**2))
##############################
def shiftUnderAndOverflows(dimension, histos, dontShiftList = []) :
    if dimension!=1 : return
    for histo in histos:
        if not histo : continue
        if histo.GetName() in dontShiftList : continue
        bins = histo.GetNbinsX()
        entries = histo.GetEntries()
        combineBinContentAndError(histo, binToContainCombo = 1   , binToBeKilled = 0     )
        combineBinContentAndError(histo, binToContainCombo = bins, binToBeKilled = bins+1)
        histo.SetEntries(entries)
##############################
def cyclePlot(d = {}, f = None, args = {}, optStat = 1110, canvas = None, fileName = None, divide = (2,2), goptions = "", ticks = True) :
    if optStat!=None :
        oldOptStat = r.gStyle.GetOptStat()
        r.gStyle.SetOptStat(optStat)

    needPrint = False
    stuff = []
    n = divide[0]*divide[1]
    for i,key in enumerate(sorted(d.keys())) :
        j = i%n
        if not j :
            canvas.cd(0)
            canvas.Clear()
            canvas.Divide(*divide)

        canvas.cd(1+j)
        if ticks :
            r.gPad.SetTickx()
            r.gPad.SetTicky()

        l = d[key] if (type(d[key]) is list) else [d[key]]
        for iItem,item in enumerate(l) :
            item.Draw("%s%s"%(goptions, "same" if iItem else ""))

        if f!=None : stuff.append( f(args = args, key = key, histo = d[key]) )
        needPrint = True

        #move stat box
        r.gPad.Update()
        tps = d[key].FindObject("stats") if len(l)==1 else None
        if tps :
            tps.SetX1NDC(0.78)
            tps.SetX2NDC(0.98)
            tps.SetY1NDC(0.90)
            tps.SetY2NDC(1.00)

        if j==(n-1) :
            canvas.cd(0)
            canvas.Print(fileName)
            needPrint = False

    if needPrint :
        canvas.cd(0)
        canvas.Print(fileName)
    if optStat!=None : r.gStyle.SetOptStat(oldOptStat)
    return
##############################
def naturalSortKey(s):
        return tuple(int(part) if re.match(r'[0-9]+$', part) else part
                     for part in re.split(r'([0-9]+)', s))
