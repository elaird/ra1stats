#!/usr/bin/env python

import ROOT as r
import refXsProcessing as rxs
import os,copy,array

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gROOT.SetStyle("Plain")
    r.gStyle.SetPalette(1)

def mother(model) :
    return {"T1": "gluino", "T2": "squark"}[model]

def ranges() :
    d = {}

    #2-tuples have the form (min, max)
    #3-tuples have the form (zMin, zMax[, nContours][, zTitleOffset])
    
    #common ranges    
    d["smsXRange"] = (400.0, 999.9)
    d["smsYRange"] = (100.0, 975.0)
    d["smsLimZRange"] = (0.0, 40.0, 40)
    d["smsLimLogZRange"] = (0.1, 40.0)
    d["smsLim_NoThUncLogZRange"] = (0.1, 40.0)
    d["smsEffUncExpZRange"] = (0.0, 0.20, 20)
    d["smsEffUncThZRange"] = (0.0, 0.40, 40)
    d["smsLim_NoThUncLogZRangeCombined"] = (0.1, 20.0) #combined
    d["smsLimLogZRangeCombined"]         = (0.1, 20.0) #combined
    
    #specific ranges
    if specs()["ra1Specific"] :
        d["smsEffZRange"] = (0.0, 0.40, 40)
        d["smsLimLogZRange"] = (1.0, 40.0)
        d["smsLim_NoThUncLogZRange"] = (1.0, 40.0)
        
    else : d["smsEffZRange"] = (0.0, 0.60, 30) #trio

    #special ranges
    d["smsExclZRange"] = (-1.0, 1.0)
    d["smsWhichAnaZRange"] = (0.0, 3.0, 3)

    return d

def specs() :
    d = {}

    d["ra1Specific"] = False
    d["noOneThird"] = d["ra1Specific"]
    d["printC"] = False
    d["printTxt"] = False
    d["printPng"] = False
    d["writeTGraphs"] = False
    d["writeRootFiles"] = False
    d["pruneAndExtrapolateGraphs"] = True
    d["yValueToPrune"] = 100.0
    
    dir = "/home/hep/elaird1/60_ra_comparison"
    d["razor"] = {"T1_Eff": ("%s/razor/v2/t1_eff.root"%dir,"hist"),
                  "T2_Eff": ("%s/razor/v2/t2_eff.root"%dir,"hist"),
                  #"T1_Lim": ("%s/razor/v2/t1_limit.root"%dir,"hist"),
                  #"T2_Lim": ("%s/razor/v2/t2_limit.root"%dir,"hist"),
                  "T1_Lim": ("%s/razor/v4/t1_limit.root"%dir,"LimitT1s"),
                  "T2_Lim": ("%s/razor/v4/t2_limit.root"%dir,"LimitT2s"),
                  "T1_Lim_NoSys": ("%s/razor/v4/t1_limit_noSys.root"%dir,"LimitT1"),
                  "T2_Lim_NoSys": ("%s/razor/v4/t2_limit_noSys.root"%dir,"LimitT2"),
                  "T1_Lim_NoThUnc": ("%s/razor/v3_noThUnc/t1_limit.root"%dir,"LimitT1"),
                  "T2_Lim_NoThUnc": ("%s/razor/v3_noThUnc/t2_limit.root"%dir,"LimitT2"),
                  "name": "Razor",
                  "shiftX": False,
                  "shiftY": False,
                  }

    d["ra2"] = {"T1_Eff": ("%s/ra2/v2/t1_eff.root"%dir,"DefaultAcceptance"),
                "T2_Eff": ("%s/ra2/v2/t2_eff.root"%dir,"DefaultAcceptance"),
                "T1_Lim": ("%s/ra2/v4/t1_limit.root"%dir,"hlimit_gluino_T1_MHT"),
                "T2_Lim": ("%s/ra2/v4/t2_limit.root"%dir,"hlimit_squark_T2_MHT"),
                "T1_Lim_NoThUnc": ("%s/ra2/v4_NoThUnc/t1_limit.root"%dir,"hlimit_gluino_T1_MHT"),
                "T2_Lim_NoThUnc": ("%s/ra2/v4_NoThUnc/t2_limit.root"%dir,"hlimit_squark_T2_MHT"),
                "T1_EffUncExp": ("%s/ra2/v2/t1_effUncExp.root"%dir,"ExpRelUnc_gluino_T1_MHT"),
                "T2_EffUncExp": ("%s/ra2/v2/t2_effUncExp.root"%dir,"ExpRelUnc_squark_T2_MHT"),
                "T1_EffUncTh":  ("%s/ra2/v2/t1_effUncTh.root"%dir,"theoryUnc_gluino_T1_MHT"),
                "T2_EffUncTh":  ("%s/ra2/v2/t2_effUncTh.root"%dir,"theoryUnc_squark_T2_MHT"),
                "name": "Jets +",
                "name2": "Missing HT",
                "shiftX": False,
                "shiftY": True,
                }

    d["ra1"] = {"T1_Eff": ("%s/ra1/v1/T1_eff.root"%dir,"m0_m12_0"),
                "T2_Eff": ("%s/ra1/v1/T2_eff.root"%dir,"m0_m12_0"),
                "T1_Lim": ("%s/ra1/v1/profileLikelihood_T1_lo_1HtBin_expR_xsLimit.root"%dir,"UpperLimit_2D"),
                "T2_Lim": ("%s/ra1/v1/profileLikelihood_T2_lo_1HtBin_expR_xsLimit.root"%dir,"UpperLimit_2D"),
                "T1_Lim_NoThUnc": ("%s/ra1/v1_noThUnc/profileLikelihood_T1_lo_1HtBin_expR_xsLimit.root"%dir,"UpperLimit_2D"),
                "T2_Lim_NoThUnc": ("%s/ra1/v1_noThUnc/profileLikelihood_T2_lo_1HtBin_expR_xsLimit.root"%dir,"UpperLimit_2D"),
                "T1_EffUncExp": ("%s/ra1/v1/T1_effUncRelExp.root"%dir,"effUncRelExperimental_2D"),
                "T2_EffUncExp": ("%s/ra1/v1/T2_effUncRelExp.root"%dir,"effUncRelExperimental_2D"),
                "T1_EffUncTh":  ("%s/ra1/v1/T1_effUncRelTh.root"%dir,"effUncRelTheoretical_2D"),
                "T2_EffUncTh":  ("%s/ra1/v1/T2_effUncRelTh_patched.root"%dir,"effUncRelTheoretical_2D"),
                "name": "#alpha_{T}",
                "shiftX": True,
                "shiftY": True,
                }

    d["combined"] = {"name":  "Hadronic",
                     "name2": "Searches",
                     }
    d["whichAna"] = {"name":  "Hadronic",
                     "name2": "Searches",
                     }
    return d

def binByBinMin(histos) :
    def minContent(histos, x, y) :
        l = map(lambda h:h.GetBinContent(h.FindBin(x, y)), histos)
        m = min(l)
        return m, l.index(m)

    def newHisto(h, name) :
        out = h.Clone(name)
        out.Reset()
        return out
    
    h = histos[0]
    combMin = newHisto(h, "combined_min")
    combInd = newHisto(h, "combined_index")
    combInd.GetZaxis().SetTitle("")#analysis with best XS limit")
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinCenter(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = h.GetYaxis().GetBinCenter(iBinY)
            m,i = minContent(histos, x, y)
            if not m : continue
            combMin.Fill(x, y, m)
            combInd.Fill(x, y, i+0.5)
    return combMin,combInd
    
def shifted(h, shiftX, shiftY) :
    binWidthX = (h.GetXaxis().GetXmax() - h.GetXaxis().GetXmin())/h.GetNbinsX() if shiftX else 0.0
    binWidthY = (h.GetYaxis().GetXmax() - h.GetYaxis().GetXmin())/h.GetNbinsY() if shiftY else 0.0

    if binWidthX or binWidthY : print "INFO: shifting %s by (%g, %g)"%(h.GetName(), binWidthX, binWidthY)
    out = r.TH2D(h.GetName()+"_shifted","",
                 h.GetNbinsX(), h.GetXaxis().GetXmin() - binWidthX/2.0, h.GetXaxis().GetXmax() - binWidthX/2.0,
                 h.GetNbinsY(), h.GetYaxis().GetXmin() - binWidthY/2.0, h.GetYaxis().GetXmax() - binWidthY/2.0,
                 )

    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            out.SetBinContent(iBinX, iBinY, h.GetBinContent(iBinX, iBinY))
    return out

def freshHisto(h) :
    out = r.TH2D(h.GetName()+"_fresh","",
                 h.GetNbinsX(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax(),
                 h.GetNbinsY(), h.GetYaxis().GetXmin(), h.GetYaxis().GetXmax(),
                 )
    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            out.SetBinContent(iBinX, iBinY, h.GetBinContent(iBinX, iBinY))
    return out

def fetchHisto(file, dir, histo, name) :
    f = r.TFile(file)
    hOld = f.Get("%s/%s"%(dir, histo))
    assert hOld, "%s %s %s"%(file, dir, histo)
    h = hOld.Clone(name)
    h.SetDirectory(0)
    f.Close()
    return freshHisto(h)

def setRange(var, ranges, histo, axisString) :
    if var not in ranges : return
    nums = ranges[var]
    getattr(histo,"Get%saxis"%axisString)().SetRangeUser(*nums[:2])
    if len(nums)>2 : r.gStyle.SetNumberContours(nums[2])
    if len(nums)>3 : histo.GetZaxis().SetTitleOffset(nums[3])
    if axisString=="Z" :
        maxContent = histo.GetBinContent(histo.GetMaximumBin())
        if maxContent>nums[1] :
            print "ERROR: histo truncated in Z (maxContent = %g, maxSpecified = %g) %s"%(maxContent, nums[1], histo.GetName())

def adjust(h, singleAnalysisTweaks) :
    h.UseCurrentStyle()
    h.SetStats(False)
    for a,size,offset in zip([h.GetXaxis(), h.GetYaxis(), h.GetZaxis()],
                             [1.5, 1.5, 1.0 if singleAnalysisTweaks else 1.3],
                             [1.0, 1.05, 1.5 if singleAnalysisTweaks else 1.0],
                             ) :
        a.CenterTitle(False)
        a.SetTitleSize(size*a.GetTitleSize())
        a.SetTitleOffset(offset)
    
def printText(h, tag, ana) :
    out = open("%s_%s.txt"%(tag, ana), "w")
    for iBinX in range(1, 1+h.GetNbinsX()) :
        x = h.GetXaxis().GetBinCenter(iBinX)
        for iBinY in range(1, 1+h.GetNbinsY()) :
            y = h.GetYaxis().GetBinCenter(iBinY)
            c = h.GetBinContent(iBinX, iBinY)
            out.write("%g %g %g\n"%(x,y,c))
    out.close()

def writeGraphs(graphs, tag, ana) :
    f = r.TFile("%s_%s_graphs.root"%(tag.replace("_logZ",""), ana), "RECREATE")
    for d in graphs :
        d["graph"].Write("refXs_%4.2f"%d["factor"])
    f.Close()

def writeRootFile(h, tag, ana) :
    f = r.TFile("%s_%s.root"%(tag.replace("_logZ",""), ana), "RECREATE")
    name = h.GetName().replace("_logZ", "").replace("_fresh", "").replace("_shifted", "")
    h.Write(name)
    f.Close()

def preparedHistograms(model, analyses, key, tag, zAxisLabel, singleAnalysisTweaks) :
    out = []
    for ana in analyses :
        d = specs()[ana]
        if key not in d :
            h = None
        else :
            h = fetchHisto(d[key][0], "/", d[key][1], name = "%s_%s"%(tag, ana))
            h = shifted(h, d["shiftX"], d["shiftY"])
            adjust(h, singleAnalysisTweaks)
            h.SetTitle(";m_{%s} (GeV); m_{LSP} (GeV);%s"%(mother(model), zAxisLabel))
        out.append(h)
    return out

def plotMulti(model = "", suffix = "", zAxisLabel = "", analyses = [], logZ = False,
              exclPlotIndex = None, combined = False, minLimit = False, mcOnly = False, singleAnalysisTweaks = False) :
    if exclPlotIndex!=None or minLimit :
        logZ = False
    
    key = "%s_%s"%(model, suffix)
    tag = "%s%s"%(key, "_logZ" if logZ else "")
    fileName = "%s%s.eps"%(tag, "_combined" if combined else "")
    zKey = "sms%s%sZRange%s"%(suffix, "Log" if logZ else "", "Combined" if combined else "")
    if exclPlotIndex!=None : zKey = "smsExclZRange"
    histos = preparedHistograms(model, analyses, key, tag, zAxisLabel, singleAnalysisTweaks)

    if not combined :
        makePlot(histosToDraw = histos, histosForRefXsGraphs = histos, analysesToCompare = analyses, analysesForLabels = analyses,
                 logZ = logZ, zKey = zKey, exclPlotIndex = exclPlotIndex, minLimit = minLimit, mcOnly = mcOnly, singleAnalysisTweaks = singleAnalysisTweaks,
                 model = model, suffix = suffix, tag = tag, fileName = fileName)
    else :
        minHisto,whichAnaHisto = binByBinMin(histos)
        if minLimit :
            makePlot(histosToDraw = [whichAnaHisto], histosForRefXsGraphs = [minHisto], analysesToCompare = ["whichAna"], analysesForLabels = analyses,
                     logZ = logZ, zKey = "smsWhichAnaZRange", exclPlotIndex = exclPlotIndex, minLimit = minLimit, mcOnly = mcOnly, singleAnalysisTweaks = singleAnalysisTweaks,
                     model = model, suffix = suffix, tag = tag, fileName = fileName)
        else :
            makePlot(histosToDraw = [minHisto], histosForRefXsGraphs = [minHisto], analysesToCompare = ["combined"], analysesForLabels = analyses,
                     logZ = logZ, zKey = zKey, exclPlotIndex = exclPlotIndex, minLimit = minLimit, mcOnly = mcOnly, singleAnalysisTweaks = singleAnalysisTweaks,
                     model = model, suffix = suffix, tag = tag, fileName = fileName)

def makePlot(histosToDraw = None, histosForRefXsGraphs = None, analysesToCompare = None, analysesForLabels = None,
             logZ = None, zKey = None, exclPlotIndex = None, minLimit = None, mcOnly = None, singleAnalysisTweaks = None,
             model = None, suffix = None, tag = None, fileName = None) :
    
    rangeDict = ranges()

    c = r.TCanvas("canvas_%s"%tag,"canvas", 500*len(analysesToCompare), 500)
    c.Divide(len(analysesToCompare), 1)

    out = []
    for i,ana in enumerate(analysesToCompare) :
        c.cd(i+1)
        value = 0.17 if singleAnalysisTweaks else 0.15
        r.gPad.SetTopMargin(value)
        r.gPad.SetBottomMargin(value)
        r.gPad.SetLeftMargin(value)
        r.gPad.SetRightMargin(value)
        if logZ : r.gPad.SetLogz(True)

        histo = histosToDraw[i]
        if not histo : continue
        histo.Draw("colz")
        
        if exclPlotIndex!=None :
            histo = rxs.graphs(histosForRefXsGraphs[i], model, "Center",
                               specs()["pruneAndExtrapolateGraphs"],
                               specs()["yValueToPrune"],
                               specs()["noOneThird"])[exclPlotIndex]["histo"]
            histo.Draw("colz")
        
        setRange("smsXRange", rangeDict, histo, "X")
        setRange("smsYRange", rangeDict, histo, "Y")
        setRange(zKey,        rangeDict, histo, "Z")

        if minLimit :
            def stampLoop(xs, ys, sizeFactor, analyses) :
                out = []
                for x,y,a in zip(xs, ys, analyses) :
                    d = specs()[a]
                    out.append(stampName(d["name"],
                                         d["name2"].replace("Missing HT","H_{T} miss.") if "name2" in d else "",
                                         singleAnalysisTweaks, x, y, sizeFactor = sizeFactor, align = 12))
                return out
                
            colors = array.array('i', [r.kOrange, r.kBlue+1, r.kRed+1])
            r.gStyle.SetPalette(len(colors), colors)
            r.gPad.Update()
            axis = histo.GetListOfFunctions().FindObject("palette").GetAxis()
            axis.SetTickSize(0.0)
            axis.SetLabelSize(0.0)
            axis.SetLineColor(r.kWhite)
            sizeFactor = 0.6
            step = 0.7/3
            stuff = stampLoop(xs = [0.9, 0.9, 0.9], ys = [0.5 - step, 0.5 + 0.03*sizeFactor, 0.5 + step], sizeFactor = sizeFactor, analyses = analysesForLabels)
            out.append(stuff)
            
        if suffix[:3]=="Lim" :
            stuff = rxs.drawGraphs(rxs.graphs(histosForRefXsGraphs[i], model, "Center",
                                              specs()["pruneAndExtrapolateGraphs"],
                                              specs()["yValueToPrune"],
                                              specs()["noOneThird"])
                                   )
            if specs()["writeTGraphs"] : writeGraphs(stuff[1], tag, ana.upper())
            out.append(stuff)

        if specs()["printTxt"] : printText(histo, tag, ana.upper())
        if specs()["writeRootFiles"] : writeRootFile(histo, tag, ana.upper())
        out.append(stampCmsPrel(mcOnly))
        d = specs()[ana]
        out.append(stampName(d["name"], d["name2"] if "name2" in d else "", singleAnalysisTweaks))
        out.append(histo)
    printOnce(c, fileName)

def epsToPdf(fileName, tight = True) :
    if not tight : #make pdf
        os.system("epstopdf "+fileName)
        os.system("rm       "+fileName)
    else : #make pdf with tight bounding box
        epsiFile = fileName.replace(".eps",".epsi")
        os.system("ps2epsi "+fileName+" "+epsiFile)
        os.system("epstopdf "+epsiFile)
        os.system("rm       "+epsiFile)
        os.system("rm       "+fileName)

    if specs()["printPng"] :
        os.system("convert %s %s"%(fileName.replace(".eps", ".pdf"), fileName.replace(".eps", ".png")))

def stampCmsPrel(mcOnly) :
    y = 0.87
    text = r.TLatex()
    text.SetTextSize(0.9*text.GetTextSize())
    text.SetNDC()
    text.SetTextAlign(11)
    text.DrawLatex(0.1, y, "CMS Preliminary")
    text.SetTextAlign(31)
    text.DrawLatex(0.9, y, "#sqrt{s} = 7 TeV")
    if mcOnly : return text
    text.SetTextAlign(21)
    text.DrawLatex(0.55, y, "L_{int} = 35 pb^{-1}")
    return text

def stampName(name, name2, singleAnalysisTweaks, x = None, y = None, sizeFactor = 1.0, align = 11) :
    if x is None : x = 0.18 if not singleAnalysisTweaks else 0.2
    if y is None : y = 0.66 if name2 else 0.63
    
    text = r.TLatex()
    text.SetNDC()
    text.SetTextAlign(align)
    text.SetTextSize(sizeFactor * text.GetTextSize())
    if name2 :
        text.DrawLatex(x, y,                 name)
        text.DrawLatex(x, y-0.06*sizeFactor, name2)
    else :
        text.DrawLatex(x, y, name)
    return text

def printOnce(canvas, fileName, tight = True) :
    canvas.Print(fileName)
    if specs()["printC"] : canvas.Print(fileName.replace(".eps",".C"))
    epsToPdf(fileName, tight)
    
def plotRefXs(models) :
    def graph(h, color) :
        out = r.TGraph()
        out.SetMarkerColor(color)
        out.SetLineColor(color)
        out.SetName("%s_graph"%h.GetName())
        index = 0
        for iBinX in range(1, 1+h.GetNbinsX()) :
            x = h.GetBinLowEdge(iBinX)
            y = h.GetBinContent(iBinX)
            if not y : continue
            out.SetPoint(index, x, y)
            index += 1
        return out

    def graphs(models) :
        colors = {}
        colors["T1"] = r.kBlue
        colors["T2"] = r.kRed

        out = []
        for model in models :
            out.append(graph(rxs.refXsHisto(model), color = colors[model]))
        return out

    def gMax(inGraphs, axis) :
        return max([getattr(g,"Get%s"%axis)()[0] for g in inGraphs])

    def gMin(inGraphs, axis) :
        return min([getattr(g,"Get%s"%axis)()[g.GetN()-1] for g in inGraphs])

    g = graphs(models)
    h = r.TH2D("null", ";particle mass (GeV); reference production #sigma (pb)", 1, 0.0, 1.0e3, 1, 0.5*gMin(g, "Y"), 2.0*gMax(g, "Y"))
    h.SetStats(False)
    h.Draw()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    r.gPad.SetLogy()
    leg = r.TLegend(0.7, 0.7, 0.9, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    
    for graph in g :
        graph.SetMarkerStyle(20)
        graph.Draw("psame")
        label = "%s pair"%graph.GetName().replace("_graph","").replace("_clone","")
        leg.AddEntry(graph, label, "p")
    leg.Draw()
    printOnce(r.gPad, "referenceXs.eps", tight = False)

def go(models, analyses, combined, minLimit) :
    for model in models :
        #plotMulti(model = model, suffix = "Eff", zAxisLabel = "analysis efficiency", analyses = analyses, mcOnly = True, singleAnalysisTweaks = specs()["ra1Specific"])
        #plotMulti(model = model, suffix = "EffUncExp", zAxisLabel = "#sigma^{exp} / #epsilon", analyses = analyses, mcOnly = True, singleAnalysisTweaks = specs()["ra1Specific"])
        #plotMulti(model = model, suffix = "EffUncTh", zAxisLabel = "#sigma^{theo} / #epsilon", analyses = analyses, mcOnly = True, singleAnalysisTweaks = specs()["ra1Specific"])
        plotMulti(model = model, suffix = "Lim",         zAxisLabel = "95% C.L. limit on #sigma (pb)", analyses = analyses, logZ = True, combined = combined, minLimit = minLimit)
        #plotMulti(model = model, suffix = "Lim_NoThUnc", zAxisLabel = "95% C.L. limit on #sigma (pb)", analyses = analyses, logZ = True, combined = combined, minLimit = minLimit)
        #plotMulti(model = model, suffix = "Lim_NoSys", zAxisLabel = "95% C.L. limit on #sigma (pb)", analyses = analyses, logZ = True, combined = combined, minLimit = minLimit)
    return

setup()
#plotRefXs(models = ["T1", "T2"])
go(models = ["T1", "T2"],
   analyses = ["ra1", "ra2", "razor"] if not specs()["ra1Specific"] else ["ra1"],
   combined = False,
   minLimit = False,
   )
