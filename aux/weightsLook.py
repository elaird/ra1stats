import ROOT as r
import array


def rootSetup() :
    #r.gROOT.SetStyle("Plain")
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 3000
    r.gStyle.SetOptStat("oue")

def oneHisto(file, directory=None, histName=None):
    f = r.TFile(file)
    assert not f.IsZombie(), file
    hOld = f.Get("%s/%s" % (directory, histName))
    assert hOld, "%s/%s" % (directory, histName)
    h = hOld.Clone("%s/%s" % (directory, histName))
    h.SetDirectory(0)
    return h

def massPoints(h=None):
    mPoints = {}
    for ix in range(h.GetNbinsX()):
        for iy in range(h.GetNbinsY()):
            for iz in range(h.GetNbinsZ()):
                if h.GetBinContent(ix+1,iy+1,iz+1) != 0.0:
                    xLo = h.GetXaxis().GetBinLowEdge(ix+1)
                    yLo = h.GetYaxis().GetBinLowEdge(iy+1)
                    zLo = h.GetZaxis().GetBinLowEdge(iz+1)
                    mPoints[(xLo,yLo,zLo)] = (ix+1,iy+1,iz+1) 
    return mPoints
    
def multiHistoPerHT(file, directory=None, histNames=[], cat=[]):
    f = r.TFile(file)
    assert not f.IsZombie(), file
    histos={}
    for histName in histNames:
        hOld = f.Get("%s/%s" % (directory, histName))
        assert hOld, "%s/%s" % (directory, histName)
        h = hOld.Clone("%s/%s" % (directory, histName))
        h.SetDirectory(0)
        histos["%s/%s" % (directory, histName)] = h
    return histos
        
        
def averageWeight(directory=None, hists=[], cat=[]):
    h = hists["%s/%s" % (directory,"m0_m12_mChi_weight")].Clone(directory)
    h.Divide(hists["%s/%s" % (directory,"m0_m12_mChi_noweight")])
    h.SetName(", ".join(cat))
    return h

def draw(hist):
    hist.SetStats(False)
    hist.Draw()
    
    c1.Print(pdfFileName)

def parseCat(string = ""):
    return string.split("_")[1:3] 
    
def setup(file,directory=None,histName=[]):
    dummyHist = oneHisto(file,directory,histName)
    mP = massPoints(dummyHist)                    
    return mP

def fillAllWeights(h=None, points=None, point=None, hists=None, cat=[]):
    title = ""
    for hT,key in enumerate(hists):
        h.Fill(hists[key].GetBinContent(*points[point]))
    h.SetTitle("Average Weight: " + "%s_%s" % tuple(cat))
#    h.SetStats(False)
    h.SetXTitle("<w>_{after selection}")
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.08)
    h.GetYaxis().SetTitleOffset(0.35)
    h.GetXaxis().SetTitleSize(0.05)
    return h

def plotWeightVsHT(canvas=None, points=None, point=None, hists=None, cat=[], multiIndex=None):
    if multiIndex is None: canvas.cd(3)
    binEdges = [200,275,325,375]+[375 + 100*i for i in range(1,9)]
    binArray = array.array("d",binEdges)
    nBins = len(binArray)-1
    h = r.TH1D("average weight", "average test  weight", nBins, binArray)
    
    title = ""
    for hT,key in enumerate(hists):
        hTbin= h.FindBin(float(key.split("_")[4:5][0]))
        h.SetBinContent(hTbin,(hists[key].GetBinContent(*points[point])))
        h.SetBinError(hTbin, (hists[key].GetBinError(*points[point])))
    h.SetTitle("Average Weight: " + "%s_%s" % tuple(cat) + ", %d, %d" % (point[:2]))
    h.SetStats(False)
    h.SetMaximum(1.5)
    h.SetMinimum(0.0)
    h.SetYTitle("<w>_{after selection}")
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.08)
    h.GetYaxis().SetTitleOffset(0.35)
    h.GetXaxis().SetTitle("HT (GeV)")
    h.GetXaxis().SetTitleSize(0.05)

    h.Draw("e")
    canvas.Modified()
    canvas.Update()
    return h


def plotWeightVsHTBefore(canvas=None, points=None, point=None, hists=None, cat=[]):
    canvas.cd(4)
    binEdges = [200,275,325,375]+[375 + 100*i for i in range(1,9)]
    binArray = array.array("d",binEdges)
    nBins = len(binArray)-1
    h = r.TH1D("average weight", "average test  weight",  nBins, binArray)
    for key in hists:
        for ibin in range(1,h.GetNbinsX()+1):
            h.SetBinContent(ibin,(hists[key].GetBinContent(*points[point])))
            h.SetBinError(ibin, (hists[key].GetBinError(*points[point])))
    h.SetTitle("Average Weight Before: %d, %d" % (point[:2]))
    h.SetStats(False)
    h.SetMaximum(1.5)
    h.SetMinimum(0.0)
    h.SetYTitle("<w>_{before selection}")
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.08)
    h.GetYaxis().SetTitleOffset(0.35)
    h.GetXaxis().SetTitle("HT (GeV)")
    h.GetXaxis().SetTitleSize(0.05)
    h.Draw()
    return h

def plotWYieldsVsHT(canvas=None, points=None, point=None, hists=None, cat=[]):
    canvas.cd(2)
    binEdges = [200,275,325,375]+[375 + 100*i for i in range(1,9)]
    binArray = array.array("d",binEdges)
    nBins = len(binArray)-1
    h = r.TH1D("average weight", "average test  weight",   nBins, binArray)
    h.Rebin(nBins,"bins",binArray)
    for hT,key in enumerate(hists):
        hTbin= h.FindBin(float(key.split("_")[4:5][0]))
        h.SetBinContent(hTbin,(hists[key].GetBinContent(*points[point])))
        h.SetBinError(hTbin, (hists[key].GetBinError(*points[point])))
    h.SetTitle("Weighted Yield: " + "%s, %s" % tuple(cat) + ", %d, %d" % (point[:2]))
    r.gPad.SetLogy(True)
    h.SetStats(False)
    h.SetYTitle("Weighted Yield")
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.08)
    h.GetYaxis().SetTitleOffset(0.35)
    h.GetXaxis().SetTitle("HT (GeV)")
    h.GetXaxis().SetTitleSize(0.05)
    h.SetMaximum(3000.0)
    h.SetMinimum(.1)
    h.Draw()
    return h

def plotYieldsVsHT(canvas=None, points=None, point=None, hists=None, cat=[]):
    canvas.cd(1)
    binEdges = [200.0,275.0,325.0,375.0]+[375.0 + 100.0*i for i in range(1,9)]
    binArray = array.array("d",binEdges)
    nBins = len(binArray)-1
    h = r.TH1D("average weight", "average test  weight", nBins, binArray)
    for hT,key in enumerate(hists):
        hTbin= h.FindBin(float(key.split("_")[4:5][0])+1.0)
        h.SetBinContent(hTbin,(hists[key].GetBinContent(*points[point])))
        h.SetBinError(hTbin, (hists[key].GetBinError(*points[point])))
    h.SetTitle("Yield: " + "%s, %s" % tuple(cat) + ", %d, %d" % (point[:2]))
    h.SetStats(False)
    r.gPad.SetLogy(True)
    h.SetYTitle("Yield")
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.08)
    h.GetYaxis().SetTitleOffset(0.35)
    h.GetXaxis().SetTitle("HT (GeV)")
    h.GetXaxis().SetTitleSize(0.05)
    h.SetMaximum(3000.0)
    h.SetMinimum(.1)
    h.Draw()
    return h

def weightedYields(directory=None, hists=[], cat=[]):
    h = hists["%s/%s" % (directory,"m0_m12_mChi_weight")].Clone(directory)
    h.SetName("%s, %s" % (tuple(h.GetName().split("_"))[1:3]))
    return h

def unweightedYields(directory=None, hists=[], cat=[]):
    h = hists["%s/%s" % (directory,"m0_m12_mChi_noweight")].Clone(directory)
    h.SetName("%s, %s" % (tuple(h.GetName().split("_"))[1:3]))
    return h

def plotWeightRatio(canvas=None, num=None, den=None, cat=[]):
    canvas.cd(5)
    assert num.GetNbinsX() == den.GetNbinsX(), "Different Binning"
    h = num.Clone()
    h.Divide(den)
    h.SetYTitle("#frac{<w>_{after selection}}{<w>_{before selection}}")
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.08)
    h.GetYaxis().SetTitleOffset(0.35)
    h.GetXaxis().SetTitle("HT (GeV)")
    h.GetXaxis().SetTitleSize(0.05)
    h.SetTitle(h.GetTitle().replace("Average Weight:","Weight Ratios:"))
    h.Draw()
    return h
    
def openIndivPdf(points=None, point=None, cat=[]):
    canvas = r.TCanvas("canvas", "canvas", 600, 800)
    massString = ["%i_%i" % point[0:2]]
    catPlusMass = cat + massString
    fileName = "weightPlots/weights_" + ("_").join(catPlusMass) + ".pdf"
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    canvas.Divide(1, 5)
    canvas.Print(fileName+"[")
    return canvas,fileName

def openInclPdf(cat=[], suffix=None):
    canvas = r.TCanvas("canvas", "canvas", 600, 800)
    fileName = "weightPlots/weights_%s_%s" % tuple(cat)
    fileName += "_%s.pdf" % suffix if suffix else ".pdf"
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    canvas.Divide(1, 5)
    canvas.Print(fileName+"[")
    return canvas,fileName

def closeIndivPdf(canvas=None, fileName=""):
    canvas.Print(fileName)
    canvas.Print(fileName+"]")

def closeInclPdf(canvas=None, fileName=""):
    canvas.Print(fileName)
    canvas.Print(fileName+"]")

def go(category=[]):
    rootSetup()
    base = "../ra1e/sms_8/T2cc/had/v9/" 
    fileName = "had.root"
    file = base+fileName
    massPoints = setup(file, directory = "smsScan_before", 
                                histName = "m0_m12_mChi_weight")

    histNames = ["m0_m12_mChi_weight","m0_m12_mChi_noweight"]
    directories = ["smsScan_%s_%s_AlphaT0.6_200_275",
                   "smsScan_%s_%s_AlphaT0.55_275_325",
                   "smsScan_%s_%s_AlphaT0.55_325_375",
                   "smsScan_%s_%s_AlphaT0.55_375_475",
                   "smsScan_%s_%s_AlphaT0.55_475_575",
                   "smsScan_%s_%s_AlphaT0.55_575_675",
                   "smsScan_%s_%s_AlphaT0.55_675_775",
                   "smsScan_%s_%s_AlphaT0.55_775_875",
                   "smsScan_%s_%s_AlphaT0.55_875_975",
                   "smsScan_%s_%s_AlphaT0.55_975_1075",
                   "smsScan_%s_%s_AlphaT0.55_1075",]
    directories = [x % tuple(cat) for x in directories]
    avgWeight = {}
    wYields = {}
    yields = {}
    avgWeightBefore ={}

    histosPerHTBefore = multiHistoPerHT(file=file,directory="smsScan_before",
                                        histNames=histNames)
    avgWeightBefore["smsScan_before"] = averageWeight(directory="smsScan_before",
                                         hists=histosPerHTBefore)

    canvas,fileName = openInclPdf(cat)
    for directory in directories :
        histosPerHT = multiHistoPerHT(file=file,directory=directory,
                                      histNames=histNames, cat=cat)
        avgWeight[directory] = averageWeight(directory=directory, 
                                             hists=histosPerHT, cat=cat)

        wYields[directory] = weightedYields(directory=directory, 
                                            hists=histosPerHT, cat=cat)
        yields[directory] = unweightedYields(directory=directory, 
                                            hists=histosPerHT, cat=cat)

    for massPoint in sorted(massPoints):
        yVsHT = plotYieldsVsHT(canvas=canvas, points=massPoints, point=massPoint, hists=yields, cat=cat)
        wYsHT = plotWYieldsVsHT(canvas=canvas, points=massPoints, point=massPoint, hists=wYields, cat=cat)
        wVsHT = plotWeightVsHT(canvas=canvas, points=massPoints, point=massPoint, hists=avgWeight, cat=cat)
        wVsHTBefore = plotWeightVsHTBefore(canvas=canvas, points=massPoints, point=massPoint, hists=avgWeightBefore, cat=cat)
        wRatio = plotWeightRatio(canvas=canvas, num=wVsHT, den=wVsHTBefore, cat=cat)
        canvas.cd(0)
        canvas.Print(fileName)
    closeInclPdf(canvas=canvas, fileName=fileName)

def goSummary(category=[]):
    rootSetup()
    base = "../ra1e/sms_8/T2cc/had/v9/" 
    fileName = "had1.root"
    file = base+fileName
    massPoints = setup(file, directory = "smsScan_before", 
                                histName = "m0_m12_mChi_weight")

    histNames = ["m0_m12_mChi_weight","m0_m12_mChi_noweight"]
    directories = ["smsScan_%s_%s_AlphaT0.6_200_275",
                   "smsScan_%s_%s_AlphaT0.55_275_325",
                   "smsScan_%s_%s_AlphaT0.55_325_375",
                   "smsScan_%s_%s_AlphaT0.55_375_475",
                   "smsScan_%s_%s_AlphaT0.55_475_575",
                   "smsScan_%s_%s_AlphaT0.55_575_675",
                   "smsScan_%s_%s_AlphaT0.55_675_775",
                   "smsScan_%s_%s_AlphaT0.55_775_875",
                   "smsScan_%s_%s_AlphaT0.55_875_975",
                   "smsScan_%s_%s_AlphaT0.55_975_1075",
                   "smsScan_%s_%s_AlphaT0.55_1075",]
    directories = [x % tuple(cat) for x in directories]
    avgWeight = {}
    canvas,fileName = openInclPdf(cat, suffix="summary")
    allWeights = r.TH1D("allWeights","allWeights", 50,0,2)
    for directory in directories :
        histosPerHT = multiHistoPerHT(file=file,directory=directory,
                                      histNames=histNames, cat=cat)
        avgWeight[directory] = averageWeight(directory=directory, 
                                             hists=histosPerHT, cat=cat)

    for iMassPoint, massPoint in enumerate(sorted(massPoints)):
        canvas.cd((iMassPoint % 5) + 1)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        wVsHT = plotWeightVsHT(canvas=canvas, points=massPoints, point=massPoint, hists=avgWeight, cat=cat, multiIndex=iMassPoint)
        allWeights = fillAllWeights(h=allWeights, points=massPoints, point=massPoint, hists=avgWeight, cat=cat)
        wVsHT.DrawCopy("e")
        if iMassPoint % 5 == 4. or iMassPoint == len(massPoints)-1:
            canvas.cd(0)
            canvas.Print(fileName)
            canvas.Update()
            canvas.Clear()
            canvas.Divide(1,5)
    allWeights.Draw()
    canvas.Print(fileName)
    closeInclPdf(canvas=canvas, fileName=fileName)
        
for cat in [["eq0b","le3j"],["eq1b","le3j"],["eq0b","ge4j"]]:
    go(category=cat)
    goSummary(category=cat)
    
