#!/usr/bin/env python

import ROOT as r
import math,array,os

htLower    = (250,       300,    350,    450)
countsBulk = (844459, 331948, 225649, 110034)
#countsTail = (33,         11,      8,      5)

def deltaHt(index) :
    return htLower[index+1]-htLower[index]

def l(index, bOfIndexPlusOne, cOfIndexPlusOne) :
    return cOfIndexPlusOne*math.exp(-bOfIndexPlusOne*htLower[index+1])

def f(x, index, bOfIndexPlusOne, cOfIndexPlusOne) :
    return l(index, bOfIndexPlusOne, cOfIndexPlusOne)*(math.exp(x*deltaHt(index))-1.0) - countsBulk[index]*x

def fPrime(x, index, bOfIndexPlusOne, cOfIndexPlusOne) :
    return l(index, bOfIndexPlusOne, cOfIndexPlusOne)*deltaHt(index)*math.exp(x*deltaHt(index)) - countsBulk[index]

def newton(index, bOfIndexPlusOne, cOfIndexPlusOne, nMax = 20) :
    debug = False
    if debug : print "newton",index,bOfIndexPlusOne,cOfIndexPlusOne
    x = 10.0*bOfIndexPlusOne #initial guess
    for i in range(nMax) :
        x -= f(x, index, bOfIndexPlusOne, cOfIndexPlusOne)/fPrime(x, index, bOfIndexPlusOne, cOfIndexPlusOne)
        if debug : print x
    if debug : print
    return x

def B(index, bOfIndexPlusOne, cOfIndexPlusOne) :
    if index>=len(htLower)-2 :
        return math.log(1.0 + float(countsBulk[-2])/countsBulk[-1]) / deltaHt(-2)
    else :
        return newton(index, bOfIndexPlusOne, cOfIndexPlusOne)

def C(index, bThisIndex) :
    d = math.exp(-bThisIndex*htLower[index])
    if index!=len(htLower)-1 :
        d-= math.exp(-bThisIndex*htLower[index+1])
    return countsBulk[index]*bThisIndex/d

def expectedBackground(A, k, index) :
    b = B(index = index)
    return A*C(index)/(b+k)*(math.exp(-htLower[index]*(b+k)) - math.exp(-htLower[index+1]*(b+k)))

def go() :
    def tup(a) :
        return tuple([a[i] for i in range(len(a))])
    b = {}
    c = {}
    for i in range(len(htLower)-1, -1, -1) :
        bOfIndexPlusOne = b[i+1] if i!=len(htLower)-1 else None
        cOfIndexPlusOne = c[i+1] if i!=len(htLower)-1 else None
        b[i] = B(i, bOfIndexPlusOne, cOfIndexPlusOne)
        c[i] = C(i, b[i])
    print "b=",tup(b)
    print "c=",tup(c)
    return b,c
    
def plot(b, c, timeStamp) :
    def countGraph() :
        out = r.TGraph()
        out.SetMarkerStyle(20)
        for i,ht in enumerate(htLower) :
            out.SetPoint(i, ht, countsBulk[i])
        return out

    def integralGraph(integrals) :
        out = r.TGraph()
        out.SetMarkerStyle(20)
        for i,integral in enumerate(integrals) :
            out.SetPoint(i, htLower[i], integral)
        return out

    bogusHtEndPoint = 3000.0
    
    r.gROOT.SetStyle("Plain")

    canvas = r.TCanvas()
    canvas.Divide(3, 1)
    canvas.cd(1)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    cg = countGraph()
    cg.Draw("ap")
    cg.SetTitle("input data;HT bin lower edge (GeV);events / bin")
    cg.GetYaxis().SetTitleOffset(1.3)
    print "input:"
    cg.Print()
    h = cg.GetHistogram()
    print
    
    canvas.cd(2)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    h1 = r.TH1D("h1", "differential distribution determined from input data;HT (GeV);dN/dHT (/GeV)", 1, htLower[0], htLower[-1]+100.0)
    h1.SetStats(False)
    h1.GetYaxis().SetRangeUser(0.0, h.GetMaximum()/30.0)
    h1.GetYaxis().SetTitleOffset(1.4)
    h1.Draw()
    funcs = []
    integrals = []
    points = list(htLower)+[bogusHtEndPoint]
    for i in sorted(b.keys()) :
        func = r.TF1("func%d"%i, "[0]*exp(-[1]*x)", htLower[i], htLower[i+1] if i!=len(b)-1 else bogusHtEndPoint)
        func.SetParameter(0, c[i])
        func.SetParameter(1, b[i])
        func.Draw("same")
        funcs.append(func)
        integrals.append(func.Integral(points[i], points[i+1]))

    canvas.cd(3)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    h2 = h.Clone("clone")
    h2.Draw()
    h2.SetTitle("diff. dist. integrated in bins;HT bin lower edge (GeV);events / bin")
    h2.GetYaxis().SetTitleOffset(1.3)
    ig = integralGraph(integrals)
    ig.Draw("p")
    print "integrals:"
    ig.Print()

    canvas.cd(0)

    if timeStamp :
        text = r.TText()
        text.SetTextSize(0.6*text.GetTextSize())
        text.DrawText(0.1, 0.92, r.TDatime().AsString())
    
    fileName = "foo.eps"
    canvas.Print(fileName)
    os.system("epstopdf %s"%fileName)
    os.remove(fileName)
    return [canvas, cg, funcs, ig]

l = plot(*go(), timeStamp = False)
