import ROOT as r
import math,utils
import pickling,common,calc

def collect(wspace, results, extraStructure = False) :
    out = {}
    out["lMax"] = -results.minNll()
    out["chi2Prob"] = calc.pullStats(pulls = calc.pulls(pdf = common.pdf(wspace), poisKey = "simple", lognKey = "kMinusOne"),
                                     nParams = len(common.floatingVars(wspace))
                                     )["prob"]

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

def ntupleOfFitToys(wspace = None, data = None, nToys = None, cutVar = ("",""), cutFunc = None, toyNumberMod = 5) :
    results = utils.rooFitResults(common.pdf(wspace), data)
    wspace.saveSnapshot("snap", wspace.allVars())

    obs = collect(wspace, results, extraStructure = True)

    toys = []
    for i,dataSet in enumerate(common.pseudoData(wspace, nToys)) :
        if not (i%toyNumberMod) : print "iToy = %d"%i
        wspace.loadSnapshot("snap")
        #dataSet.Print("v")
        results = utils.rooFitResults(common.pdf(wspace), dataSet)

        wspace.allVars().assignValueOnly(dataSet.get()) #store this toy's observations, needed for (a) computing chi2 in collect(); (b) making "snapA"
        if all(cutVar) and cutFunc and cutFunc(getattr(wspace,cutVar[0])(cutVar[1]).getVal()) :
            wspace.saveSnapshot("snapA", wspace.allVars())
            return obs,results,i
        
        toys.append( collect(wspace, results) )
        utils.delete(results)
    return obs,toys

def pValueGraphs(obs = None, toys = None, key = "") :
    observed = obs[key]
    pseudo = []
    pvalues = []
    for toy in toys :
        pseudo.append(toy[key])
        pvalues.append(utils.indexFraction(observed, pseudo))
    
    return {"observed": utils.TGraphFromList([observed], name = "%s_observed"%key),
            "pseudo": utils.TGraphFromList(pseudo, name = "%s_pseudo"%key),
            "pValue": utils.TGraphFromList(pvalues, name = "%s_pValue"%key)}

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

def latex(quantiles = {}, bestDict = {}, stdout = False, selections = [], note = "", nToys = None) :
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

    from makeTables import ensembleResultsBySelection,ensembleResultsBySample
    rootFile = rootFileName(note = note, nToys = nToys)
    ensembleResultsBySelection(src, [ x.data for x in selections ],
                               fileName = rootFile.replace(".root","_bySelection.tex"))
    ensembleResultsBySample(src, [ x.data for x in selections ],
                            fileName = rootFile.replace(".root","_bySample.tex"))

def rootFileName(note = "", nToys = None) :
    return "ra1r/ensemble/ensemble_%s_%dtoys.root"%(note, nToys)

def pickledFileName(note = "", nToys = None) :
    return rootFileName(note, nToys).replace(".root", ".obs")

def writeHistosAndGraphs(wspace, data, nToys = None, note = "") :
    obs,toys = ntupleOfFitToys(wspace, data, nToys)
    pickling.writeNumbers(pickledFileName(note, nToys), d = obs)

    graphs_lMax = pValueGraphs(obs, toys, key = "lMax")
    graphs_chi2Prob = pValueGraphs(obs, toys, key = "chi2Prob")
    pHistos  = histos1D(obs = obs, toys = toys, vars = utils.parCollect(wspace)[0].keys())
    fHistos  = histos1D(obs = obs, toys = toys, vars = utils.funcCollect(wspace)[0].keys())
    oHistos  = histos1D(obs = obs, toys = toys, vars = ["lMax", "chi2Prob"])
    pHistos2 = parHistos2D(obs = obs, toys = toys, pairs = [("A_qcd","k_qcd"), ("A_ewk","A_qcd"), ("A_ewk","k_qcd"), ("A_ewk","fZinv0")])

    tfile = r.TFile(rootFileName(note, nToys), "RECREATE")

    for dir,lst in {"graphs": [graphs_lMax, graphs_chi2Prob],
                    "pars"  : [pHistos],
                    "funcs" : [fHistos],
                    "other" : [oHistos],
                    "pars2D": [pHistos2],
                    }.iteritems() :
        tfile.mkdir(dir)
        tfile.cd("/%s"%dir)
        for dct in lst :
            for obj in dct.values() :
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

def functionQuantiles(note = "", nToys = None) :
    tfile = r.TFile(rootFileName(note, nToys))
    fHistos,fQuantiles = histosAndQuantiles(tfile, "funcs")
    tfile.Close()
    return fQuantiles

def results(note = "", nToys = None) :
    obs = pickling.readNumbers(pickledFileName(note, nToys))
    tfile = r.TFile(rootFileName(note, nToys))
    return obs,tfile
