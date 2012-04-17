import ROOT as r
import math
import utils,plotting
from common import pdf,pseudoData

def collect(wspace, results, extraStructure = False) :
    def lMax(results) :
        #return math.exp(-results.minNll())
        return -results.minNll()

    out = {}
    out["lMax"] = lMax(results)
    funcBestFit,funcLinPropError = utils.funcCollect(wspace)
    parBestFit,parError,parMin,parMax = utils.parCollect(wspace)

    if extraStructure :
        out["funcBestFit"] = funcBestFit
        out["parBestFit"] = parBestFit
        out["parError"] = parError
        return out
    
    assert set(funcBestFit.keys()).isdisjoint(set(parBestFit.keys()))
    for d in [funcBestFit, parBestFit] :
        for key,value in d.iteritems() :
            out[key] = value
    return out

def ntupleOfFitToys(wspace = None, data = None, nToys = None, cutVar = ("",""), cutFunc = None ) :
    results = utils.rooFitResults(pdf(wspace), data)
    wspace.saveSnapshot("snap", wspace.allVars())

    obs = collect(wspace, results, extraStructure = True)

    toys = []
    for i,dataSet in enumerate(pseudoData(wspace, nToys)) :
        wspace.loadSnapshot("snap")
        #dataSet.Print("v")
        results = utils.rooFitResults(pdf(wspace), dataSet)

        if all(cutVar) and cutFunc and cutFunc(getattr(wspace,cutVar[0])(cutVar[1]).getVal()) :
            wspace.allVars().assignValueOnly(dataSet.get())
            wspace.saveSnapshot("snapA", wspace.allVars())
            return obs,results,i
        
        toys.append( collect(wspace, results) )
        utils.delete(results)
    return obs,toys

def pValueGraphs(obs = None, toys = None) :
    lMaxData = obs["lMax"]
    lMaxs = []
    ps = []
    for toy in toys :
        lMaxs.append(toy["lMax"])
        ps.append(utils.indexFraction(lMaxData, lMaxs))
    
    return {"lMaxData": utils.TGraphFromList([lMaxData], name = "lMaxData"),
            "lMaxs": utils.TGraphFromList(lMaxs, name = "lMaxs"),
            "pValue": utils.TGraphFromList(ps, name = "pValue")}

def histos1D(obs = None, toys = None, vars = [], shift = True, style = "") :
    out = {}
    for var in vars :
        if style=="par" :
            mean  = obs["parBestFit"][var]
            error = obs["parError"][var]
            lo = mean - 2.0*error
            hi = mean + 2.0*error
        elif style=="func" :
            mean  = obs["funcBestFit"][func]
            error = math.sqrt(mean)
            lo = mean - 3.0*error
            hi = mean + 3.0*error
        else : #automatic range
            lo = 1.0
            hi = -1.0

        h = out[var] = r.TH1D(var, var, 100, lo, hi)
        h.Sumw2()
        for toy in toys : h.Fill(toy[var])
    if shift : utils.shiftUnderAndOverflows(1, out.values())
    return out

def parHistos2D(obs = None, toys = None, pairs = [], suffix = "") :
    histos = {}

    for pair in pairs :
        name = "_".join(pair)
        name += suffix
        title = ";".join([""]+list(pair))
        h = histos[name] = r.TH2D(name, title, 100, 1.0, -1.0, 100, 1.0, -1.0)
        h.Sumw2()
        h.SetStats(False)
        h.SetTitleOffset(1.3)
        for toy in toys :
            if (pair[0] not in toy) or (pair[1] not in toy) : continue
            h.Fill(toy[pair[0]], toy[pair[1]])
    return histos

def latex(histos = {}, bestDict = {}) :
    out = []
    for key,histo in histos.iteritems() :
        q = utils.quantiles(histo, sigmaList = [-1.0, 0.0, 1.0])
        best = bestDict[key]
        if best >= 100 :
            out.append( (histo.GetName(), "$%d^{+%d}_{-%d}$" % ( round(best), round(q[2]-best), round(best-q[0]) )) )
        else :
            out.append( (histo.GetName(), "$%.1f^{+%.1f}_{-%.1f}$" % ( best, q[2]-best, best-q[0] )) )
    return out

def fileName(note = "") :
    return "ensemble_%s.root"%note

def writeHistosAndGraphs(wspace, data, nToys = None, note = "") :
    obs,toys = ntupleOfFitToys(wspace, data, nToys)
    
    graphs = pValueGraphs(obs, toys)
    pHistos  = histos1D(obs = obs, toys = toys, vars = utils.parCollect(wspace)[0].keys())
    fHistos  = histos1D(obs = obs, toys = toys, vars = utils.funcCollect(wspace)[0].keys())
    oHistos  = histos1D(obs = obs, toys = toys, vars = ["lMax"])
    pHistos2 = parHistos2D(obs = obs, toys = toys, pairs = [("A_qcd","k_qcd"), ("A_ewk","A_qcd"), ("A_ewk","k_qcd"), ("A_ewk","fZinv0")])

    tfile = r.TFile(fileName(note), "RECREATE")
    for dir,dct in [("graphs", graphs),
                    ("pars",   pHistos),
                    ("funcs",  fHistos),
                    ("other",  oHistos),
                    ("pars2D", pHistos2), ] :
        tfile.mkdir(dir)
        tfile.cd("/%s"%dir)
        for key,obj in dct.iteritems() :
            obj.Write()
    tfile.Close()

def plotsAndTables(note = "", plotsDir = "") :
    tfile = r.TFile(fileName(note))

    #p-value plots
    kargs = {}
    for item in ["pValue", "lMaxData", "lMaxs"] :
        kargs[item] = tfile.Get("/graphs/%s"%item)
    for item in ["note", "plotsDir"] :
        kargs[item] = eval(item)
    
    print kargs
    plotting.pValuePlots(**kargs)

#    #latex yield tables
#    print latex(histos = fHistos, bestDict = obs["funcBestFit"])
#    
#    ##ensemble plots
#    #canvas = utils.numberedCanvas()
#    #fileName = "%s/ensemble_%s.pdf"%(plotsDir, note)
#    #canvas.Print(fileName+"[")
#    #
#    #utils.cyclePlot(d = pHistos, f = plotting.histoLines, canvas = canvas, fileName = fileName,
#    #                args = {"bestColor":r.kGreen, "quantileColor":r.kRed, "bestDict":obs["parBestFit"], "errorDict":obs["parError"], "errorColor":r.kGreen})
#    #utils.cyclePlot(d = fHistos, f = plotting.histoLines, canvas = canvas, fileName = fileName,
#    #                args = {"bestColor":r.kGreen, "quantileColor":r.kRed, "bestDict":obs["funcBestFit"], "errorColor":r.kGreen, "print":True})
#    #utils.cyclePlot(d = oHistos, canvas = canvas, fileName = fileName)
#    ##utils.cyclePlot(d = pHistos2, canvas = canvas, fileName = fileName)
#    #canvas.Print(fileName+"]")

    tfile.Close()
