#!/usr/bin/env python

import ROOT as r

def parsed(fileName = "") :
    dct = {}
    headers = []
    f = open(fileName)
    for iLine,line in enumerate(f) :
        key = "Interactions"
        if key in line :
            fields = " ".join(line.split("|")).split()
            assert fields[0]==key,"%s!=%s"%(fields[0], key)
            headers = fields[1:]
            continue
        elif "tanbeta" not in line :
            assert line=="\n",line
            continue

        try:
            fields = line.split("|")
            _,_,tanBeta,_,_,m0,_,_,m12 = fields[1].split()
            coords = (float(tanBeta.replace(",","")), float(m0), float(m12))

            xsList = fields[2:-1]
            assert len(xsList)==len(headers),"%s\n%s"%(str(headers), str(xsList))

            dct[coords] = {}
            for header,xsAndUnc in zip(headers,xsList) :
                xs,_,xsUnc = xsAndUnc.split()
                dct[coords][header] = (float(xs), float(xsUnc))
        except:
            print "Bad format on line %d of file %s:"%(1+iLine, fileName)
            print line
            exit()
    f.close()
    return dct

def extracted(lst = [], i = None, minLength = None, maxLength = None) :
    out = map(lambda x:x[i],lst)
    out = sorted(list(set(out)))
    n = len(out)
    if minLength!=None : assert minLength<=n,out
    if maxLength!=None : assert n<=maxLength,out
    return out

def binning(lst = []) :
    n = len(lst)
    assert n>1,n
    xMin = min(lst)
    xMax = max(lst)
    binWidth = (xMax - xMin + 0.0) / (n-1)
    return [n, xMin - binWidth/2.0, xMax + binWidth/2.0]

def histos(fileName = "combined_cross_section_Errmsugra_m0_m12_10_0_1.txt") :
    dct = parsed(fileName)
    coords = sorted(dct.keys())
    tbs  = extracted(coords, i = 0, minLength = 1, maxLength = 1)
    m0s  = extracted(coords, i = 1, minLength = 2)
    m12s = extracted(coords, i = 2, minLength = 2)
    bins = tuple(binning(m0s)+binning(m12s))

    out = {}
    for (tb,m0,m12),procs in dct.iteritems() :
        for proc,(xs,xsUnc) in procs.iteritems() :
            if proc not in out :
                out[proc] = r.TH2D(proc, "%s; m_{0} (GeV);m_{1/2} (GeV); #sigma (pb)"%proc, *bins)
            h = out[proc]
            iBin = h.FindBin(m0, m12)
            h.SetBinContent(iBin, xs)
            h.SetBinError(iBin, xsUnc)
    
    title = "total";          total      = out.values()[0].Clone(title); total.SetTitle(title)
    title = "total_+1_Sigma"; totalPlus  = out.values()[0].Clone(title); totalPlus.SetTitle(title)
    title = "total_-1_Sigma"; totalMinus = out.values()[0].Clone(title); totalMinus.SetTitle(title)
    for h in [total, totalPlus, totalMinus] :
        h.Reset()

    for iBinX in range(1, 1+total.GetNbinsX()) :
        for iBinY in range(1, 1+total.GetNbinsY()) :
            content = 0.0
            contentPlus = 0.0
            contentMinus = 0.0
            for proc,h in out.iteritems() :
                c = h.GetBinContent(iBinX, iBinY)
                e = h.GetBinError(iBinX, iBinY)
                content += c
                contentPlus  += c+e
                contentMinus += c-e
            total.SetBinContent(iBinX, iBinY, content)
            totalPlus.SetBinContent(iBinX, iBinY, contentPlus)
            totalMinus.SetBinContent(iBinX, iBinY, contentMinus)
    out["total"] = total
    out["totalMinus"] = totalMinus
    out["totalPlus"] = totalPlus
    return out

def makeRootFile(fileName = "") :
    outFile = r.TFile(fileName, "RECREATE")
    
    canvas = r.TCanvas()
    canvas.cd(0)
    canvas.Clear()
    canvas.Divide(4,4)
    pdfFile = "cmssm_xs.pdf"
    hs = histos()
    for i,key in enumerate(sorted(hs.keys())) :
        h = hs[key]
        canvas.cd(1+i)
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        r.gPad.SetLogz()
        r.gPad.SetRightMargin(0.15)
        h.Write()
        h.SetStats(False)
        h.Draw("colz")
        h.GetZaxis().SetRangeUser(1.0e-6, 1.0e2)
    canvas.SetLogy()
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(pdfFile)
    outFile.Close()

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetPalette(1)

setup()
makeRootFile(fileName = "cmssm_xs.root")
