#!/usr/bin/env python

import sys
import ROOT as r

def checkArgs() :
    if len(sys.argv)!=2 :
        print "Usage: %s file"%sys.argv[0]
        exit()

def points(fileName) :
    out = []
    f = open(fileName)
    lookNext = False
    for line in f :
        if "NeymanConstruction" in line :
            lookNext = True
            stat = float(line.split()[-1])
        else :
            if lookNext :
                fields = line.split()
                s = float(fields[0].replace("s=",""))
                isIn = int(fields[-1])
                out.append( (s,stat,isIn) )
            lookNext = False
    f.close()
    return out

def graphs(points) :
    inGraph = r.TGraph()
    inGraph.SetName("insideInterval")
    allGraph = r.TGraph()
    allGraph.SetName("allPoints")

    iIn = 0
    iAll = 0
    for s,stat,isIn in points :
        allGraph.SetPoint(iAll, s, stat)
        iAll += 1
        if isIn :
            inGraph.SetPoint(iIn, s, stat)
            iIn += 1
    return (inGraph, allGraph)

def plotFc(inGraph, allGraph, markerStyle = 25) :
    allGraph.SetMarkerStyle(markerStyle)
    allGraph.SetMarkerColor(r.kBlack)
    inGraph.SetMarkerStyle(markerStyle)
    inGraph.SetMarkerColor(r.kRed)

    allGraph.Draw("psame")
    inGraph.Draw("psame")

    bl = r.TLine(); bl.SetLineColor(r.kBlue)
    gr = r.TLine(); gr.SetLineColor(r.kGreen)
    fc = r.TLine(); fc.SetLineColor(r.kMagenta)
    
    legend = r.TLegend(0.15, 0.65, 0.45, 0.85, "L = Pois(1 | 4.0 + s)")
    x = 0.00; fc.DrawLine(x, 0.0, x, 3.0)
    x = 2.08; fc.DrawLine(x, 0.0, x, 3.0)

    #legend = r.TLegend(0.2, 0.65, 0.5, 0.85, "L = Pois(6 | 4.0 + s)")
    #x = 0.00; fc.DrawLine(x, 0.0, x, 3.0)
    #x = 8.75; fc.DrawLine(x, 0.0, x, 3.0)

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)

    legend.AddEntry(fc, "FC 1998 paper", "l")
    legend.AddEntry(bl, "PL ratio", "l")
    legend.AddEntry(gr, "PL upper limit", "l")
    legend.AddEntry(allGraph, "FC point tested", "p")
    legend.AddEntry(inGraph, "FC point accepted", "p")
    legend.Draw("same")
    return (inGraph, allGraph, legend, bl, gr, fc)

def plotPl(fileName) :
    f = r.TFile(fileName)
    canvas = f.Get("c1").Clone("c2")
    f.Close()
    return canvas

r.gROOT.SetStyle("Plain")
#r.gROOT.SetBatch(True)
checkArgs()
canvas = plotPl("intervalPlot__95.root")
canvas.Draw()
stuff = plotFc(*graphs(points(sys.argv[1])))
canvas.Print("foo.ps")
