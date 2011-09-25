#!/usr/bin/env python

import os,math
import ROOT as r

def like(nList, muList) :
    out = 1.0
    for n,mu in zip(nList, muList) :
        out *= r.TMath.Poisson(n, mu)
    return out

def hist(values, name, title, nBins = 1000, min = 1, max = -1) :
    out = r.TH1D(name, title, nBins, min, max)
    map(out.Fill, values)
    return out

def indexFraction(item, l) :
    totalList = sorted(l+[item])
    i1 = totalList.index(item)
    totalList.reverse()
    i2 = len(totalList)-totalList.index(item)-1
    return (i1+i2)/2.0/len(l), (i2-i1)/2.0/len(l)

def draw(items) :
    for i,item in enumerate(items) :
        item.Draw("" if not i else "same")

class foo(object) :
    def __init__(self, bList = [3.0, 3.0], sList = [2.0, 6.0], obsList = [3, 1], tsMin = None, tsMax = None, tsIndex = 0, nToys = 8000) :
        self.rand = r.TRandom3()
        self.rand.SetSeed(1)

        tsPair = [(self.tsN, "num events"),
                  (self.tsLLR, "log( L(n | s+b) / L(n | b) )"),
                  (self.tsLLRm, "log( L(n | b) / L(n | s+b) )"),
                  (self.tsLH, "log( L(n | b) )")][tsIndex]

        self.ts,self.tsDesc = tsPair

        for item in ["nToys", "bList", "sList", "obsList", "tsMin", "tsMax"] :
            setattr(self, item, eval(item))
        self.sbList = [b+s for b,s in zip(self.bList, self.sList)]

    def tsN(self, nList) :
        return sum(nList)

    def tsLH(self, nList) :
        return math.log(like(nList, self.bList))
        
    def tsLLR(self, nList) :
        return math.log(like(nList, self.sbList)/like(nList, self.bList))
        
    def tsLLRm(self, nList) :
        return -self.tsLLR(nList)
        
    def tsValues(self, muList) :
        out = []
        for i in range(self.nToys) :
            out.append( self.ts([self.rand.Poisson(mu) for mu in muList]) )
        return out
        
    def tsPlot(self, canvas, psFile) :
        bValues = self.tsValues(self.bList)
        sbValues = self.tsValues(self.sbList)

        factor = 1.1
        minimum = min(bValues + sbValues) if not self.tsMin else self.tsMin
        maximum = max(bValues + sbValues) if not self.tsMax else self.tsMax
        maximum = factor*maximum if maximum>0 else maximum/factor
        minimum = factor*minimum if maximum<0 else minimum/factor
        
        bHist  = hist(bValues,  name = "b",  title = ";%s;toys / bin"%self.tsDesc, min = minimum, max = maximum)
        sbHist = hist(sbValues, name = "sb", title = ";%s;toys / bin"%self.tsDesc, min = minimum, max = maximum)

        yMax = max(bHist.GetMaximum(), sbHist.GetMaximum())
        x = self.ts(self.obsList)
        obsLine = r.TLine(x, 0.0, x, yMax)
        obsLine.SetLineWidth(1)
        obsLine.SetLineStyle(3)

        leg = r.TLegend(0.5, 0.7, 0.9, 0.9)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.AddEntry(bHist, "b hypothesis; b = %s"%str(self.bList), "l")
        leg.AddEntry(sbHist, "s + b hypothesis; s = %s"%str(self.sList), "l")
        leg.AddEntry(obsLine, "observed value; n = %s"%str(self.obsList), "l")

        bHist.SetLineColor(r.kBlue)
        sbHist.SetLineColor(r.kRed)

        bHist.SetStats(False)
        bHist.SetFillStyle(3001)

        draw([bHist, sbHist, obsLine, leg])

        text = r.TText()
        text.SetNDC()

        xBin = bHist.FindBin(x)
        value = bHist.Integral(0, xBin)
        error = bHist.Integral(xBin, xBin)/2.0
        value -= error
        total  = bHist.Integral(0, bHist.GetNbinsX()+1)
        t2 = text.DrawText(0.13, 0.85, "CLb = %6.3f +- %6.3f"%(1.0-value/total, error/total))

        #pValueFromLeft,pValueFromLeftError = indexFraction(x, bValues)
        #t1 = text.DrawText(0.1, 0.85, "CLb (v2) = %6.3f +- %6.3f"%(1.0 - pValueFromLeft, pValueFromLeftError))

        canvas.Print(psFile)

def go(name = "out", items = []) :
    psFile = "%s.ps"%name
    canvas = r.TCanvas()
    canvas.Print(psFile+"[")

    for item in items :
        item.tsPlot(canvas, psFile)

    canvas.Print(psFile+"]")
    os.system("ps2pdf %s"%psFile)
    os.remove(psFile)

nToys = 8000
go("oneBin_varying_s_obs1",
   [foo(sList = [60.0], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys), 
    foo(sList = [30.0], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys),
    foo(sList = [12.0], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys),
    foo(sList = [ 6.0], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys),
    foo(sList = [ 3.0], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys),
    foo(sList = [ 1.0], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys),
    foo(sList = [0.25], bList = [3.0], obsList = [1], tsIndex = 2, nToys = nToys),
    ])

go("oneBin_varying_s_obs6",
   [foo(sList = [60.0], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys), 
    foo(sList = [30.0], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys),
    foo(sList = [12.0], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys),
    foo(sList = [ 6.0], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys),
    foo(sList = [ 3.0], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys),
    foo(sList = [ 1.0], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys),
    foo(sList = [0.25], bList = [3.0], obsList = [6], tsIndex = 2, nToys = nToys),
    ])

go("multiBin_different_sOverb",
   [foo(sList = [60.0,  6.0], tsIndex = 2, nToys = nToys), 
    foo(sList = [30.0,  6.0], tsIndex = 2, nToys = nToys),
    foo(sList = [12.0,  6.0], tsIndex = 2, nToys = nToys),
    foo(sList = [ 6.0,  6.0], tsIndex = 2, nToys = nToys),
    foo(sList = [ 3.0,  6.0], tsIndex = 2, nToys = nToys),
    foo(sList = [ 1.0,  6.0], tsIndex = 2, nToys = nToys),
    foo(sList = [0.25,  6.0], tsIndex = 2, nToys = nToys),
    ])

go("multiBin_same_sOverb",
   [foo(sList = [60.0, 60.0], tsIndex = 2, nToys = nToys), 
    foo(sList = [30.0, 30.0], tsIndex = 2, nToys = nToys),
    foo(sList = [12.0, 12.0], tsIndex = 2, nToys = nToys),
    foo(sList = [ 6.0,  6.0], tsIndex = 2, nToys = nToys),
    foo(sList = [ 3.0,  3.0], tsIndex = 2, nToys = nToys),
    foo(sList = [ 1.0,  1.0], tsIndex = 2, nToys = nToys),
    foo(sList = [0.25, 0.25], tsIndex = 2, nToys = nToys),
    ])
