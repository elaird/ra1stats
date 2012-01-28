import configuration as conf
import histogramProcessing as hp
import common,utils,likelihoodSpec
import cPickle,math,os
import ROOT as r

##I/O
def writeNumbers(fileName = None, d = None) :
    outFile = open(fileName, "w")
    cPickle.dump(d, outFile)
    outFile.close()

def readNumbers(fileName) :
    inFile = open(fileName)
    d = cPickle.load(inFile)
    inFile.close()
    return d

##number collection
def effHistos(nloToLoRatios = False) :
    out = {}
    for sel in likelihoodSpec.spec()["selections"] :
        assert sel.data.htBinLowerEdgesInput()==sel.data.htBinLowerEdges(), "merging bins is not yet supported"
        bins = sel.data.htBinLowerEdges()
        htThresholds = zip(bins, list(bins[1:])+[None])

        alphaT = {"alphaTLower": sel.alphaTMinMax[0], "alphaTUpper": sel.alphaTMinMax[1]}
        d = {}
        for box,considerSignal in sel.samplesAndSignalEff.iteritems() :
            item = "eff%s"%(box.capitalize())
            if not considerSignal :
                d[item] = [0.0]*len(bins)
                if nloToLoRatios : d["_LO"%item] = out[item]
                continue

    	    d[item] = [hp.effHisto(box = box, scale = "1", htLower = l, htUpper = u, **alphaT) for l,u in htThresholds]
    	    if not nloToLoRatios : continue
            d[item+"_LO"] = [hp.loEffHisto(box = box, scale = "1", htLower = l, htUpper = u, **alphaT) for l,u in htThresholds]
        out[sel.name] = d
    return out

def numberDict(histos = {}, data = None, point = None) :
    out = {}
    for key,value in histos.iteritems() :
        numList = []
        for item in value :
            if not hasattr(item, "GetBinContent") : break
            numList.append(item.GetBinContent(*point))
        if numList : out[key] = numList
        else : out[key] = value
        out[key] = data.mergeEfficiency(out[key])
        out[key+"Sum"] = sum(out[key])
    return out

def histoList(histos = {}) :
    out = []
    for key,value in histos.iteritems() :
        for item in value :
            if not hasattr(item, "GetBinContent") : continue
            out.append(item)
    return out

def effSums(d = {}) :
    out = {}
    for key,value in d.iteritems() :
        if key[-3:]=="Sum" :
            key2 = key.replace("eff","nEvents")
            out[key2] = value*d["nEventsIn"]
            if out[key2] :
                out[key+"UncRelMcStats"] = 1.0/math.sqrt(out[key2])
    return out

def eventsInRange(switches = None, nEventsIn = None) :
    out = True
    if switches["minEventsIn"]!=None : out &= switches["minEventsIn"]<=nEventsIn
    if switches["maxEventsIn"]!=None : out &= nEventsIn<=switches["maxEventsIn"]
    return out

def signalDict(point = None, eff = None, xs = None, xsLo = None, nEventsIn = None, data = None, switches = None) :
    out = {}
    out["x"] = xs.GetXaxis().GetBinLowEdge(point[0])
    out["y"] = xs.GetYaxis().GetBinLowEdge(point[1])
    out["nEventsIn"] = nEventsIn.GetBinContent(*point)
    out["eventsInRange"] = eventsInRange(switches, out["nEventsIn"])
    if not out["eventsInRange"] : return out
    
    out["xs"] = xs.GetBinContent(*point)
    out.update(numberDict(histos = eff, data = data, point = point))
    out.update(effSums(out))

    if switches["nloToLoRatios"] :
        remove = []
        for key,value in out.iteritems() :
            if key+"_LO" in out :
                out[item+"_NLO_over_LO"] = [nlo/lo if lo else 0.0 for nlo,lo in zip(out[item], out[item+"_LO"])]
                remove.append(key+"_LO")
        for item in remove : del out[item]
            
        #if xsLo : lo = xsLo.GetBinContent(*point)
        #signal["xs_NLO_over_LO"] = signal["xs"]/lo if lo else 0.0
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
        sels = []
        for item in conf.likelihood()["alphaT"].keys() : sels += ["effHad%s"%item, "effMuon%s"%item]
            
        for sel in sels :
            if sel not in signal : continue
            out["%s%d"%(sel, bin)] = (signal[sel][i], "#epsilon of %s %d selection"%(sel.replace("eff", ""), bin))
            if switches["nloToLoRatios"] :
                out["%s_NLO_over_LO%d"%(sel, bin)] = (signal[sel+"_NLO_over_LO"][i], "#epsilon (NLO) / #epsilon (LO)")
    return out

def writeSignalFiles(points = [], outFilesAlso = False) :
    switches = conf.switches()
    
    args = {"switches": switches,
            "eff": effHistos(nloToLoRatios = switches["nloToLoRatios"]),
            "xs": hp.xsHisto(),
            "nEventsIn": hp.nEventsInHisto(),
            }

    hp.checkHistoBinning([args["xs"]]+histoList(args["eff"]))

    def one(point) :
        signal = signalDict(point = point, **args)
        stem = conf.strings(*point)["pickledFileName"]
        writeNumbers(fileName = stem + ".in", d = signal)
        if not outFilesAlso : return
        writeNumbers(fileName = stem + ".out", d = stuffVars(switches, binsMerged = args["data"].htBinLowerEdges(), signal = signal))

    map(one, points)
        
##merge functions
def mergedFile() :
    note = common.note(likelihoodSpec = conf.likelihood())
    return "%s_%s%s"%(conf.stringsNoArgs()["mergedFileStem"], note, ".root")

def mergePickledFiles(printExample = False) :
    example = hp.xsHisto()
    if printExample :
    	print "Here are the example binnings:"
    	print "x:",example.GetNbinsX(), example.GetXaxis().GetXmin(), example.GetXaxis().GetXmax()
    	print "y:",example.GetNbinsY(), example.GetYaxis().GetXmin(), example.GetYaxis().GetXmax()
    	print "z:",example.GetNbinsZ(), example.GetZaxis().GetXmin(), example.GetZaxis().GetXmax()

    histos = {}
    zTitles = {}
    
    for point in hp.points() :
        fileName = conf.strings(*point)["pickledFileName"]+".out"
        if not os.path.exists(fileName) :
            print "skipping file",fileName            
        else :
            d = readNumbers(fileName)
            for key,value in d.iteritems() :
                if type(value) is tuple :
                    content,zTitle = value
                else :
                    content = value
                    zTitle = ""
                if key not in histos :
                    histos[key] = example.Clone(key)
                    histos[key].Reset()
                    zTitles[key] = zTitle

                histos[key].SetBinContent(point[0], point[1], point[2], content)
            os.remove(fileName)
            os.remove(fileName.replace(".out", ".in"))

    for key,histo in histos.iteritems() :
        histo.GetZaxis().SetTitle(zTitles[key])

    f = r.TFile(mergedFile(), "RECREATE")
    for histo in histos.values() :
        histo.Write()
    f.Close()

