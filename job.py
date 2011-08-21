#!/usr/bin/env python
import sys,cPickle,math
import fresh
import configuration as conf
import histogramProcessing as hp

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def writeNumbers(fileName = None, d = None) :
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()

def description(key, cl = None) :
    if key[:2]=="CL" : return key
    if key[-5:]=="Limit" and cl : return "%g%% C.L. %s limit on XS factor"%(cl, key[:-5])
    else : return ""

def signalEff(switches, data, point) :
    binsInput = data.htBinLowerEdgesInput()
    binsMerged =  data.htBinLowerEdges()
    
    out = {}
    for item in ["effHad"]+([] if switches["ignoreSignalContaminationInMuonSample"] else ["effMuon"]) :
        box = item.replace("eff","").lower()
        out[item] = [hp.effHisto(box = box, scale = "1", htLower = htLower, htUpper = htUpper).GetBinContent(*point)\
                     for htLower, htUpper in zip(binsInput, list(binsInput[1:])+[None])]
        out[item] = data.mergeEfficiency(out[item])
        if switches["nloToLoRatios"] :
            out[item+"_NLO_over_LO"] = [hp.loEffHisto(box = box, scale = "1", htLower = htLower, htUpper = htUpper).GetBinContent(*point)\
                                    for htLower, htUpper in zip(binsInput, list(binsInput[1:])+[None])]
            out[item+"_NLO_over_LO"] = data.mergeEfficiency(out[item+"_NLO_over_LO"])
            out[item+"_NLO_over_LO"] = [nlo/lo if lo else 0.0 for nlo,lo in zip(out[item], out[item+"_NLO_over_LO"])]
        
    if switches["ignoreSignalContaminationInMuonSample"] :
        out["effMuon"] = [0.0]*len(out["effHad"])
        if switches["nloToLoRatios"] :        
            out["effMuon_NLO_over_LO"] = [0.0]*len(out["effHad"])
    return out

def stuffVars(switches = None, binsMerged = None, signal = None) :
    titles = {"xs": "#sigma (pb)",
              "xs_NLO_over_LO": "#sigma (NLO) / #sigma (LO)",
              "nEventsIn": "N events in",
              "effHadSum": "eff. of hadronic selection (all bins summed)",
              "nEventsHad": "N events after selection (all bins summed)",
              "effHadSumUncRelMcStats": "rel. unc. on total had. eff. from MC stats",
              }
    
    out = {}
    for key,value in signal.iteritems() :
        if type(value) is list : continue
        out[key] = (value, titles[key] if key in titles else "")
        
    for i,bin in enumerate(binsMerged) :
        for sel in ["effHad", "effMuon"] :
            out["%s%d"%(sel, bin)] = (signal[sel][i], "#epsilon of %s %d selection"%(sel.replace("eff", ""), bin))
            if switches["nloToLoRatios"] :
                out["%s_NLO_over_LO%d"%(sel, bin)] = (signal[sel+"_NLO_over_LO"][i], "#epsilon (NLO) / #epsilon (LO)")
    return out

def printDict(d) :
    print "{"
    for key,value in d.iteritems() :
        out = '"%s":'%key
        if type(value)!=tuple and type(value)!=list :
            out+=str(value)
        else :
            out += "[%s]"%(", ".join(["%s"%str(item) for item in value]))
        print out+","
    print "}"

def effSum(signal = None, samples = []) :
    total = 0.0
    for key,value in signal.iteritems() :
        if not any([key=="eff"+sample for sample in samples]) : continue
        total += sum(value)
    return total

def signalDict(switches, data, point) :
    out = {}
    out.update(signalEff(switches, data, point))

    out["xs"] = hp.xsHisto().GetBinContent(*point)
    out["nEventsIn"] = hp.nEventsInHisto().GetBinContent(*point)
    for sample in ["Had", "Muon"] :
        out["eff%sSum"%sample] = effSum(out, samples = [sample])
        out["nEvents%s"%sample] = out["eff%sSum"%sample]*out["nEventsIn"]
        if out["nEvents%s"%sample] :
            out["eff%sSumUncRelMcStats"%sample] = 1.0/math.sqrt(out["nEvents%s"%sample])
        
    if switches["nloToLoRatios"] :    
        signal["xs_NLO_over_LO"] = signal["xs"]/hp.loXsHisto().GetBinContent(*point) if hp.loXsHisto().GetBinContent(*point) else 0.0
    return out

def onePoint(switches = None, data = None, point = None) :
    signal = signalDict(switches, data, point)
    printDict(signal)
    out = {}
    eventsInRange = True
    if switches["minEventsIn"]!=None : eventsInRange &= switches["minEventsIn"]<=signal["nEventsIn"]
    if switches["maxEventsIn"]!=None : eventsInRange &= signal["nEventsIn"]<=switches["maxEventsIn"]
    if eventsInRange :
        out.update(stuffVars(switches, binsMerged = data.htBinLowerEdges(), signal = signal))
        if bool(signal["effHadSum"]) : out.update(results(switches = switches, data = data, signal = signal))
    return out

def results(switches = None, data = None, signal = None) :
    out = {}
    for cl in switches["CL"] :
        cl2 = 100*cl
        f = fresh.foo(inputData = data, REwk = switches["REwk"], RQcd = switches["RQcd"], nFZinv = switches["nFZinv"], signal = signal,
                      simpleOneBin = switches["simpleOneBin"], hadTerms = switches["hadTerms"], hadControlSamples = switches["hadControlSamples"],
                      muonTerms = switches["muonTerms"], photTerms = switches["photTerms"], mumuTerms = switches["mumuTerms"],
                      rhoSignalMin = switches["rhoSignalMin"])

        if switches["method"]=="CLs" :
            results = f.cls(cl = cl, nToys = switches["nToys"], plusMinus = switches["expectedPlusMinus"], testStatType = switches["testStatistic"],
                            plSeed = switches["plSeedForCLs"], plNIterationsMax = switches["nIterationsMax"])
            for key,value in results.iteritems() :
                out[key] = (value, description(key))
                if switches["plSeedForCLs"] : continue
                if key=="CLs" or ("Median" in key) :
                    threshold = 1.0 - cl
                    out["excluded_%s_%g"%(key, cl2)] = (compare(results[key], threshold), "is %s<%g ?"%(key, threshold))
        elif switches["method"]=="CLsCustom" :
            results = f.clsCustom(nToys = switches["nToys"], testStatType = switches["testStatistic"])
            for key,value in results.iteritems() :
                out[key] = (value, description(key))
                if key=="CLs" or ("Median" in key) :
                    threshold = 1.0 - cl
                    out["excluded_%s_%g"%(key, cl2)] = (compare(results[key], threshold), "is %s<%g ?"%(key, threshold))
        elif not switches["computeExpectedLimit"] :
            results = f.interval(cl = cl, method = switches["method"], nIterationsMax = switches["nIterationsMax"])
            for key,value in results.iteritems() : out["%s%g"%(key, cl2)] = (value, description(key, cl2))
            out["excluded%g"%cl2] = (compare(results["upperLimit"], 1.0), "is (%g%% upper limit on XS factor)<1?"%cl2)
        else :
            d,nSuccesses = f.expectedLimit(cl = cl, nToys = switches["nToys"], plusMinus = switches["expectedPlusMinus"], makePlots = False)
            for key,value in d.iteritems() :
                out["%s%g"%(key, cl2)] = (value, description(key, cl2))
                out["excluded%s%g"%(key, cl2)] = (compare(value, 1.0), "is (%s %g%% upper limit on XS factor)<1?"%(key, cl2))
            out["nSuccesses%g"%cl2] = (nSuccesses, "# of successfully fit toys")
    return out

def compare(item, threshold) :
    return 2.0*(item<threshold)-1.0

def go() :
    s = conf.switches()
    data = conf.data()
    for point in points() :
        writeNumbers(conf.strings(*point)["pickledFileName"], onePoint(switches = s, data = data, point = point))

if False :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
