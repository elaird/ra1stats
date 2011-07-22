#!/usr/bin/env python

import os,math
import ROOT as r

def like(n, mu) : return r.TMath.Poisson(n, mu)
#def like(x, mu) : return r.TMath.Gaus(x, mu, 1.0)

def hist(values, name, title, nBins = 1000, min = 1, max = -1) :
    out = r.TH1D(name, title, nBins, min, max)
    map(out.Fill, values)
    return out

def draw(items) :
    for i,item in enumerate(items) :
        item.Draw("" if not i else "same")

class foo(object) :
    def __init__(self, b = 3.0, s = 2.0, obs = 1, tsMin = None, tsMax = None, tsIndex = 0) :
        self.rand = r.TRandom3()
        self.rand.SetSeed(1)

        self.nToys = 80000
        tsPair = [(self.tsN, "num events"),
                  (self.tsLLR, "log( L(n | s+b) / L(n | b) )"),
                  (self.tsLLRm, "log( L(n | b) / L(n | s+b) )"),
                  (self.tsLH, "log( L(n | b) )")][tsIndex]
        self.ts = tsPair[0]
        self.tsDesc = tsPair[1]

        for item in ["b", "s", "obs", "tsMin", "tsMax"] :
            setattr(self, item, eval(item))

        self.stuff = []

    def keep(self, x) :
        self.stuff.append(x)
        
    def tsN(self, n) :
        return n

    def tsLH(self, n) :
        return math.log(like(n, self.b))
        
    def tsLLR(self, n) :
        return math.log(like(n, self.b + self.s)/like(n, self.b))
        
    def tsLLRm(self, n) :
        return -self.tsLLR(n)
        
    def tsValues(self, mu) :
        return [self.ts(self.rand.Poisson(mu)) for i in range(self.nToys)]
        #return [self.ts(self.rand.Gaus(mu, 1.0)) for i in range(self.nToys)]
        
    def tsPlot(self, canvas, psFile) :
        bValues = self.tsValues(self.b)
        sbValues = self.tsValues(self.b + self.s)

        minimum = min(bValues + sbValues) if not self.tsMin else self.tsMin
        maximum = max(bValues + sbValues) if not self.tsMax else self.tsMax
        bHist  = hist(bValues,  name = "b",  title = ";%s;toys / bin"%self.tsDesc, min = minimum, max = maximum)
        sbHist = hist(sbValues, name = "sb", title = ";%s;toys / bin"%self.tsDesc, min = minimum, max = maximum)

        yMax = max(bHist.GetMaximum(), sbHist.GetMaximum())
        x = self.ts(self.obs)
        obsLine = r.TLine(x, 0.0, x, yMax)
        obsLine.SetLineWidth(1)
        obsLine.SetLineStyle(3)

        center = bHist.Integral(0, bHist.FindBin(x))
        plus   = bHist.Integral(0, bHist.FindBin(x)+1)
        minus  = bHist.Integral(0, bHist.FindBin(x)-1)
        total  = bHist.Integral(0, bHist.GetNbinsX()+1)
        text = r.TText(bHist.GetXaxis().GetXmin(), bHist.GetMaximum(),
                       "CLb = %6.4f +- %6.4f"%(center/total, (plus-minus)/total))
            
        leg = r.TLegend(0.5, 0.7, 0.9, 0.9)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.AddEntry(bHist, "b hypothesis; b = %g"%self.b, "l")
        leg.AddEntry(sbHist, "s + b hypothesis; s = %g"%self.s, "l")
        leg.AddEntry(obsLine, "observed value", "l")

        bHist.SetLineColor(r.kBlue)
        sbHist.SetLineColor(r.kRed)

        bHist.SetStats(False)
        bHist.SetFillStyle(3001)

        draw([bHist, sbHist, obsLine, leg, text])
        canvas.Print(psFile)

psFile = "out.ps"
canvas = r.TCanvas()
canvas.Print(psFile+"[")

#s1 = 29.0
#s2 = 3.08

#items  = []
#items += [foo(s = s1, tsIndex = 0, tsMin = 0.0, tsMax = 50.0)]
#items += [foo(s = s2, tsIndex = 0, tsMin = 0.0, tsMax = 50.0)]
#items += [foo(s = s1, tsIndex = 1)]
#items += [foo(s = s2, tsIndex = 1)]
#items += [foo(s = s1, tsIndex = 2, tsMin = -50.0, tsMax =  0.0)]
#items += [foo(s = s2, tsIndex = 2, tsMin = -50.0, tsMax =  0.0)]

s1 = 30.0
s2 =  3.0

items  = []
items += [foo(s = s1, tsIndex = 2)]
items += [foo(s = s2, tsIndex = 2)]

for item in items :
    item.tsPlot(canvas, psFile)

canvas.Print(psFile+"]")
os.system("ps2pdf %s"%psFile)
os.remove(psFile)
