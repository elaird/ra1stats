#!/usr/bin/env python

import ROOT as r
import math,array,os

htLower       = (250,       300,    350,    450)
#countsTail    = (33,         11,      8,      5)
countsBulkRaw = (844459, 331948, 225649, 110034)
countsBulkInc = tuple([sum(countsBulkRaw[i:]) for i in range(len(countsBulkRaw))])

def deltaHt(index) :
    return htLower[index]-htLower[index+1]

def f(x = None, index = None, bOfIndexPlusOne = None) :
    return x*math.exp(x*deltaHt(index)) - countsBulkInc[index+1]*bOfIndexPlusOne/countsBulkInc[index]

def fPrime(x = None, index = None) :
    return ( 1.0 + (x*(deltaHt(index))) )*math.exp(x*(deltaHt(index)))

def newton(index = None, bOfIndexPlusOne = None, initialGuess = None, nMax = 20) :
    debug = False
    if debug : print "newton",index,bOfIndexPlusOne
    x = bOfIndexPlusOne #initial guess
    for i in range(nMax) :
        x = x - f(x = x, index = index, bOfIndexPlusOne = bOfIndexPlusOne)/fPrime(x = x, index = index)
        if debug : print x
    if debug : print
    return x

def B(index = None, bOfIndexPlusOne = None) :
    if index==len(htLower)-1 :
        return math.log((countsBulkInc[index-1]/countsBulkInc[index])) / (htLower[-1]-htLower[-2])
    else :
        return newton(index = index, bOfIndexPlusOne = bOfIndexPlusOne)

def C(index = None, bThisIndex = None) :
    return countsBulkInc[index]*bThisIndex/math.exp(-bThisIndex*htLower[index])

def expectedBackground(A, k, index) :
    b = B(index = index)
    return A*C(index)/(b+k)*(math.exp(-htLower[index]*(b+k)) - math.exp(-htLower[index+1]*(b+k)))

def go() :
    b = {}
    c = {}
    for i in range(len(htLower)-1, -1, -1) :
        b[i] = B(index = i, bOfIndexPlusOne = b[i+1] if i!=len(htLower)-1 else None)
        c[i] = C(index = i, bThisIndex = b[i])
    print b
    print c
    return b,c
    
def plot(b, c) :
    def countGraph() :
        out = r.TGraph()
        out.SetMarkerStyle(20)
        for i,ht in enumerate(htLower) :
            out.SetPoint(i, ht, countsBulkRaw[i])
        return out

    def integralGraph(f) :
        out = r.TGraph()
        out.SetMarkerStyle(20)
        points = list(htLower)+[1000.0]
        for i in range(len(points)-1) :
            out.SetPoint(i, points[i], f.Integral(points[i], points[i+1]))
        return out
    
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
    cg.Print()
    h = cg.GetHistogram()
    print
    
    canvas.cd(2)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    h1 = r.TH1D("h1", "differential distribution determined from input data;HT (GeV);dN/dHT (/GeV)", 1, htLower[0], htLower[-1]+100.0)
    h1.SetStats(False)
    h1.GetYaxis().SetRangeUser(0.0, h.GetMaximum()/100.0)
    h1.GetYaxis().SetTitleOffset(1.4)
    h1.Draw()
    stuff = []
    for i in b.keys() :
        func = r.TF1("func%d"%i, "[0]*exp(-[1]*x)", htLower[i], htLower[i+1] if i!=len(b)-1 else 1000.0)
        func.SetParameter(0, c[i])
        func.SetParameter(1, b[i])
        func.Draw("same")
        stuff.append(func)

    canvas.cd(3)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    h2 = h.Clone("clone")
    h2.Draw()
    h2.SetTitle("diff. dist. integrated in bins;HT bin lower edge (GeV);events / bin")
    h2.GetYaxis().SetTitleOffset(1.3)
    ig = integralGraph(func)
    ig.Draw("p")
    ig.Print()

    fileName = "foo.eps"
    canvas.Print(fileName)
    os.system("epstopdf %s"%fileName)
    os.remove(fileName)
    return [canvas, cg, stuff, ig]

l = plot(*go())
