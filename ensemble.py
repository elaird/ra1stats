import ROOT as r
import math
import utils,pickling
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

def latex(quantiles = {}, bestDict = {}, stdout = False) :
    src = {}
    lst = []
    for key,q in quantiles.iteritems() :
        best = bestDict[key]
        if best >= 100 :
            src[key] = "$%d^{+%d}_{-%d}$" % ( round(best), round(q[2]-best), round(best-q[0]) )
        else :
            src[key] = "$%.1f^{+%.1f}_{-%.1f}$" % ( best, q[2]-best, best-q[0] )

        lst.append("%20s: %g + %g - %g"%(key, best, q[2]-best, best-q[0]))

    if stdout :
        for item in sorted(lst) :
            print item

    from makeTables import ensembleResultsFromDict as ltxResults
    from makeTables import ensembleHadSummaryTable as ltxSummary
    import likelihoodSpec
    ltxResults( src, [ x.data for x in likelihoodSpec.spec().selections() ] )
    ltxSummary( src, [ x.data for x in likelihoodSpec.spec().selections() ] )

def rootFileName(note = "") :
    return "ensemble_%s.root"%note

def pickledFileName(note = "") :
    return rootFileName(note).replace(".root", ".obs")

def writeHistosAndGraphs(wspace, data, nToys = None, note = "") :
    obs,toys = ntupleOfFitToys(wspace, data, nToys)
    pickling.writeNumbers(pickledFileName(note), d = obs)

    graphs = pValueGraphs(obs, toys)
    pHistos  = histos1D(obs = obs, toys = toys, vars = utils.parCollect(wspace)[0].keys())
    fHistos  = histos1D(obs = obs, toys = toys, vars = utils.funcCollect(wspace)[0].keys())
    oHistos  = histos1D(obs = obs, toys = toys, vars = ["lMax"])
    pHistos2 = parHistos2D(obs = obs, toys = toys, pairs = [("A_qcd","k_qcd"), ("A_ewk","A_qcd"), ("A_ewk","k_qcd"), ("A_ewk","fZinv0")])

    tfile = r.TFile(rootFileName(note), "RECREATE")
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

def histosAndQuantiles(tfile = None, dir = "") :
    histos = {}
    quantiles = {}
    for tkey in tfile.Get(dir).GetListOfKeys() :
        key = tkey.GetName()
        histos[key] = tfile.Get("/%s/%s"%(dir, key))
        quantiles[key] = utils.quantiles(histos[key], sigmaList = [-1.0, 0.0, 1.0])
    return histos,quantiles

def functionQuantiles(note = "") :
    tfile = r.TFile(rootFileName(note))
    fHistos,fQuantiles = histosAndQuantiles(tfile, "funcs")
    tfile.Close()
    return fQuantiles

def results(note = "") :
    obs = pickling.readNumbers(pickledFileName(note))
    tfile = r.TFile(rootFileName(note))
    return obs,tfile
