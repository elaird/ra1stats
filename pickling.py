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

        kargs = {"alphaTLower": sel.alphaTMinMax[0], "alphaTUpper": sel.alphaTMinMax[1], "nbTag": sel.nbTag, "bTagLower": sel.bTagLower }
        d = {}
        for box,considerSignal in sel.samplesAndSignalEff.iteritems() :
            item = "eff%s"%(box.capitalize())
            if not considerSignal :
                d[item] = [0.0]*len(bins)
                if nloToLoRatios : d["_LO"%item] = out[item]
                continue

    	    d[item] = [hp.effHisto(box = box, scale = "1", htLower = l, htUpper = u, **kargs) for l,u in htThresholds]
    	    if not nloToLoRatios : continue
            d[item+"_LO"] = [hp.loEffHisto(box = box, scale = "1", htLower = l, htUpper = u, **kargs) for l,u in htThresholds]
        out[sel.name] = d
    return out

def histoList(histos = {}) :
    out = []
    for key,value in histos.iteritems() :
        for item in value :
            if not hasattr(item, "GetBinContent") : continue
            out.append(item)
    return out

def eventsInRange(switches = None, nEventsIn = None) :
    out = True
    if switches["minEventsIn"]!=None : out &= switches["minEventsIn"]<=nEventsIn
    if switches["maxEventsIn"]!=None : out &= nEventsIn<=switches["maxEventsIn"]
    return out

def signalModel(point = None, eff = None, xs = None, xsLo = None, nEventsIn = None, switches = None) :
    out = common.signal(xs = xs.GetBinContent(*point), label = "%d_%d_%d"%point)
    if xsLo : out["xs_LO"] = xsLo.GetBinContent(*point)
    out["xs"] = out.xs
    out["x"] = xs.GetXaxis().GetBinLowEdge(point[0])
    out["y"] = xs.GetYaxis().GetBinLowEdge(point[1])
    out["nEventsIn"] = nEventsIn.GetBinContent(*point)
    out["eventsInRange"] = eventsInRange(switches, out["nEventsIn"])
    if not out["eventsInRange"] : return out

    for selName,dct in eff.iteritems() :
        d = {}
        for box,effHistos in dct.iteritems() :
            if not all([hasattr(item, "GetBinContent") for item in effHistos]) : continue
            d[box] = map(lambda x:x.GetBinContent(*point), effHistos)

            d[box+"Sum"] = sum(d[box])
            key = box.replace("eff","nEvents")
            d[key] = d[box+"Sum"]*out["nEventsIn"]
            if d[key] : d[box+"SumUncRelMcStats"] = 1.0/math.sqrt(d[key])
        out[selName] = d
    return out

def broken() :
    if switches["nloToLoRatios"] :
        for selName,dct in out.iteritems() :
            for box,effs in dct.iteritems() :
                if box+"_LO" in dct :
                    pass
        remove = []
        for key,value in out.iteritems() :
            if key+"_LO" in out :
                out[item+"_NLO_over_LO"] = [nlo/lo if lo else 0.0 for nlo,lo in zip(out[item], out[item+"_LO"])]
                remove.append(key+"_LO")
        for item in remove : del out[item]
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
        signal = signalModel(point = point, **args)
        stem = conf.strings(*point)["pickledFileName"]
        writeNumbers(fileName = stem + ".in", d = signal)
        if not outFilesAlso : return
        writeNumbers(fileName = stem + ".out", d = signal)
        #stuffVars(switches, binsMerged = args["data"].htBinLowerEdges(), signal = signal))

    print "FIX: stuff vars"
    map(one, points)
        
##merge functions
def mergedFile() :
    note = common.note(likelihoodSpec.spec())
    return "%s_%s%s"%(conf.stringsNoArgs()["mergedFileStem"], note, ".root")

#note: improve this data format
def flatten(target = {}, key = None, obj = None) :
    if type(obj)==dict :
        for k,v in obj.iteritems() :
            flatten(target, "%s_%s"%(key, k), v)
    elif type(obj)==list :
        for i,x in enumerate(obj) :
            flatten(target, "%s_%d"%(key, i), x)
    elif type(obj) in [float, int, bool] :
        flatten(target, key, (obj, ''))
    elif type(obj)==tuple and len(obj)==2 and type(obj[1])==str :
        assert key not in target,key
        target[key] = obj
    else :
        assert False,type(obj)
    return

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
            continue

        d = readNumbers(fileName)
        contents = {}
        for key,value in d.iteritems() :
            flatten(contents, key, value)

        for key,value in contents.iteritems() :
            if key not in histos :
                histos[key] = example.Clone(key)
                histos[key].Reset()
            histos[key].SetBinContent(point[0], point[1], point[2], value[0])
            zTitles[key] = value[1]

        os.remove(fileName)
        os.remove(fileName.replace(".out", ".in"))

    for key,histo in histos.iteritems() :
        histo.GetZaxis().SetTitle(zTitles[key])

    f = r.TFile(mergedFile(), "RECREATE")
    for histo in histos.values() :
        histo.Write()
    f.Close()

