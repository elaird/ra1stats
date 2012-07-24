#!/usr/bin/env python

import ROOT as r
from utils import threeToTwo, shifted
from refXsProcessing import histoSpec
import utils

model = 'T2tt'
hSpec = histoSpec(model)

options = {
    'refProcess': hSpec['histo'],
    'refXsFile': hSpec['file'],
    'refName': '#tilde{t} #tilde{t}',
    'limitFile': '~/Projects/ra1DataFiles/ToyResults/2011/1000_toys/T2tt/'
                 'CLs_frequentist_TS3_T2tt_lo_2011_RQcdFallingExpExt_fZinvTwo_55_'
                 '0b-1hx2p_55_1b-1hx2p_55_2b-1hx2p_55_gt2b-1h.root',
    'plotTitle': 'pp#rightarrow#tilde{t} #tilde{t}#; #tilde{t}#rightarrow t+'
                 '#tilde{#chi}    m_{#tilde{#chi}} = 50 GeV',
    'refYRange': (50.,50.),
    'shiftX': True,
    'showRatio': False,
    }

plotOptOverrides = { 'xLabel': 'm_{#tilde{t}} (GeV)' }


def drawStamp(canvas):
    canvas.cd()
    tl = r.TLatex()
    tl.SetNDC()
    tl.SetTextAlign(12)
    tl.SetTextSize(0.04)
    tl.DrawLatex(0.14,0.84,'CMS Preliminary')
    tl.DrawLatex(0.51,0.603,'#sqrt{s} = 7 TeV, L = 4.98 fb^{-1}')
    tl.SetTextSize(0.07)
    tl.DrawLatex(0.23,0.78,'#alpha_{T}')
    return tl

def getReferenceXsHisto(refHistoName, refName, filename):
    refFile = r.TFile(filename,'READ')
    refHisto = refFile.Get(refHistoName).Clone()
    refHisto.SetDirectory(0)
    refFile.Close()
    histoD = {
        'refHisto': {
            'hist': refHisto,
            'LineWidth': 2,
            'LineStyle': 1,
            'LineColor': r.kBlack,
            'FillColor': r.kGray+2,
            'FillStyle': 3002,
            'hasErrors': True,
            'opts': 'e3l',
            'label': '#sigma^{{NLO+NLL}}({rn}) #pm th. unc.'.format(rn=refName),
            }
        }
    return histoD


def getExclusionHistos(limitFile, yMinMax=(50,50)):
    limitHistoDict = {
        'UpperLimit': {
            'label': 'Observed Limit (95% C.L.)',
            'LineWidth': 3,
            'LineColor': r.kBlue+2,
            'opts': 'c',
            'Smooth': True,
            },
        'ExpectedUpperLimit': {
            'label': 'Median Expected Limit #pm 1#sigma exp.',
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'LineStyle': 9,
            'opts': 'c',
            'Smooth': True,
            # for legend
            'FillStyle': 3001,
            'FillColor': r.kBlue-10,
            },
        'ExpectedUpperLimit_+1_Sigma': {
            'label': 'Expected Upper Limit (+1#sigma)',
            'FillStyle': 3001,
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'FillColor': r.kBlue-10,
            'opts': 'c',
            'Smooth': True,
            },
        'ExpectedUpperLimit_-1_Sigma': {
            'label': 'Expected Upper Limit (-1#sigma)',
            'LineColor': r.kOrange+7,
            'LineWidth': 2,
            'FillColor': 10,
            'opts': 'c',
            'Smooth': True,
            'nSmooth': 5,
            },
        }

    rfile = r.TFile(limitFile,'READ')
    for limitHistoName, opts in limitHistoDict.iteritems():
        limitHisto = threeToTwo(rfile.Get(limitHistoName))
        minYBin = limitHisto.GetYaxis().FindBin(yMinMax[0])
        maxYBin = limitHisto.GetYaxis().FindBin(yMinMax[1])

        opts['hist'] = limitHisto.ProjectionX(limitHistoName+"_",minYBin,maxYBin).Clone()
        opts['hist'].SetDirectory(0)

    rfile.Close()
    return limitHistoDict


def printRatio(hd1, hd2, errSign=None):
    h1 = hd1['hist']
    h2 = hd2['hist']

    ratio = h2.Clone()
    for h2Bin in range(1, h2.GetNbinsX()+1):
        val = h2.GetBinLowEdge(h2Bin)
        h1Bin = h1.FindBin(val)

        ratio = h2.Clone()
        num = h1.GetBinContent(h1Bin)
        if errSign is None:
            denom = h2.GetBinContent(h2Bin)
        elif errSign == '+':
            denom = h2.GetBinContent(h2Bin) + h2.GetBinError(h2Bin)
        elif errSign == '-':
            denom = h2.GetBinContent(h2Bin) - h2.GetBinError(h2Bin)

        if denom > 0.:
            binRatio = num / denom
        else:
            binRatio = 0.
        binLo = ratio.GetBinLowEdge(h2Bin)
        binHi = ratio.GetBinLowEdge(h2Bin+1)
        print('{low},{high},{val}'.format(low=binLo, high=binHi,
                                          val=binRatio))

def drawRatio(hd1, hd2, canvas, padNum=2, title='observed / reference xs',
              xMin=None, xMax=None):
    h1 = hd1['hist']
    h2 = hd2['hist']
    pad = canvas.cd(padNum)
    pad.SetTickx()
    pad.SetTicky()
    ratio  = h2.Clone()
    ratio.SetTitle('')
    ratio.GetXaxis().SetTitle('')
    ratio.GetYaxis().SetTitle(title)
    ratio.GetXaxis().SetLabelSize(10.)
    ratio.GetYaxis().SetNdivisions(203)
    for h2Bin in range(1, h2.GetNbinsX()+1):
        val = h2.GetBinLowEdge(h2Bin)
        h1Bin = h1.FindBin(val)

        ratio = h2.Clone()
        num = h1.GetBinContent(h1Bin)
        denom = h2.GetBinContent(h2Bin)

        if denom > 0.:
            binRatio = num / denom
        else:
            binRatio = 0.
        ratio.SetBinContent(h2Bin,binRatio)
    ratio.SetLineWidth(1)
    ratio.SetLineColor(r.kBlack)
    ratio.SetMaximum(2.)
    ratio.DrawCopy('h')
    for iBin in range(1, ratio.GetNbinsX()+1):
        if ratio.GetBinContent(iBin) > 1:
            ratio.SetLineColor(r.kRed)
            ratio.SetLineWidth(2)
            ratio.GetXaxis().SetRange(iBin, iBin)
            ratio.DrawCopy('][same')
    #ratio.Print('all')
    if xMax == None:
        xMax = ratio.GetXaxis().GetXmax()
    if xMin == None:
        xMin = ratio.GetXaxis().GetXmin()
    line = r.TLine()
    line.DrawLine(xMin, 1., xMax, 1.)
    return ratio, line



def compareXs(refProcess, refName, refXsFile, limitFile="xsLimit.root",
              pdfFile="xs/compareXs.pdf", refYRange=(50,50), plotTitle="",
              plotOptOverrides=None, shiftX=False, showRatio=False,
              dumpRatio=True) :
    plotOpts = {
        'yMax': 1e+1,
        'yMin': 1e-3,
        'xMin': 300,
        'xMax': 1200,
        'xLabel': "{p} mass (GeV)".format(
            p=refProcess.capitalize().replace('_',' ')),
        'yLabel': '#sigma (pb)',
        'legendPosition': [0.40, 0.65, 0.85, 0.88],
        }
    if plotOptOverrides is not None:
        plotOpts.update(plotOptOverrides)

    refHisto = getReferenceXsHisto(refProcess, refName, refXsFile)
    exclusionHistos = getExclusionHistos(limitFile)

    canvas = r.TCanvas('c1','c1',700,600)
    utils.divideCanvas(canvas)
    if showRatio:
        pad = canvas.cd(1)
    else:
        pad = canvas.cd(0)
    hs = dict(refHisto.items() + exclusionHistos.items())

    leg = r.TLegend(*plotOpts['legendPosition'])
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    histosToDraw = ['ExpectedUpperLimit_+1_Sigma', 'ExpectedUpperLimit',
                    'ExpectedUpperLimit_-1_Sigma', 'refHisto', 'UpperLimit']
    for hname in histosToDraw:
        hs[hname]['hist'] = shifted(hs[hname]['hist'],shift=(shiftX,), shiftErrors=hs[hname].get('hasErrors',False))
    for iHisto, hname in enumerate(histosToDraw):
        props = hs[hname]
        h = props['hist']
        h.SetStats(False)
        h.SetTitle(plotTitle)
        h.GetXaxis().SetRangeUser(plotOpts['xMin'],plotOpts['xMax'])
        h.SetMinimum(plotOpts['yMin'])
        h.SetMaximum(plotOpts['yMax'])
        if props.get('Smooth', False):
            h.Smooth(props.get('nSmooth',1),'R')
        h.Draw("%s%s"%(props.get('opts','c'), "same" if iHisto else ""))
        for attr in ['LineColor', 'LineStyle', 'LineWidth']:
            setAttr = getattr(h,'Set{attr}'.format(attr=attr))
            setAttr(props.get(attr,1))
        for attr in ['FillStyle', 'FillColor']:
            if attr in props:
                setAttr = getattr(h,'Set{attr}'.format(attr=attr))
                setAttr(props.get(attr,1))
        if "Sigma" not in hname:
            leg.AddEntry(h, props['label'], "lf")
        h.GetXaxis().SetTitle(plotOpts['xLabel'])
        h.GetYaxis().SetTitle(plotOpts['yLabel'])
    leg.Draw()
    tl = drawStamp(canvas)
    pad.RedrawAxis()
    pad.SetLogy()
    pad.SetTickx()
    pad.SetTicky()

    ref = hs['refHisto']
    obs = hs['UpperLimit']

    if dumpRatio:
        #printRatio(obs, ref)
        printRatio(obs, ref, errSign='+')
        #printRatio(obs, ref, errSign='-')

    if showRatio:
        ratio, line = drawRatio(ref, obs, canvas, 2, xMin=plotOpts['xMin'],)
                                #xMax=plotOpts['xMax'])

    print "Saving to {file}".format(file=pdfFile)
    canvas.Print(pdfFile)

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

def main():
    setup()
    compareXs(plotOptOverrides=plotOptOverrides, **options )

if __name__=="__main__":
    main()
