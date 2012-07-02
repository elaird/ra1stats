#!/usr/bin/env python

import ROOT as r
from utils import threeToTwo
from plottingGrid import shifted

options = {
    'refProcess': 'stop_or_sbottom',
    'refName': '#tilde{t} #tilde{t}',
    'refXsFile': 'sms_xs/sms_xs.root',
    'limitFile': '~/Projects/ra1ToyResults/2011/1000_toys/T2tt/'
                 'CLs_frequentist_TS3_T2tt_lo_RQcdFallingExpExt_fZinvTwo_55_'
                 '0b-1hx2p_55_1b-1hx2p_55_2b-1hx2p_55_gt2b-1h.root',
    'plotTitle': 'pp#rightarrow#tilde{t} #tilde{t}#; #tilde{t}#rightarrow t+'
                 '#tilde{#chi}    m_{#tilde{#chi}} = 50 GeV/c^{2}',
    'refYRange': (50.,50.),
    'shiftX': True,
    }

plotOptOverrides = { 'xLabel': 'm_{#tilde{t}} [GeV/c^{2}]' }


def drawStamp(canvas):
    canvas.cd()
    tl = r.TLatex()
    tl.SetNDC()
    tl.SetTextAlign(12)
    tl.SetTextSize(0.04)
    tl.DrawLatex(0.25,0.8,'CMS Preliminary')
    tl.DrawLatex(0.50,0.793,'#sqrt{s} = 7 TeV, #int L dt = 4.98 fb^{-1}')
    tl.SetTextSize(0.1)
    tl.DrawLatex(0.50,0.72,'#alpha_{T}')
    return tl

def getReferenceXsHisto(refHistoName, refName, filename):
    refFile = r.TFile(filename,'READ')
    refHisto = refFile.Get(refHistoName).Clone()
    refHisto.SetDirectory(0)
    refFile.Close()
    histoD = {
        'refHisto': {
            'hist': refHisto,
            'LineWidth': 3,
            'LineStyle': 7,
            'LineColor': r.kBlack,
            'FillColor': r.kGray+2,
            'FillStyle': 3002,
            'hasErrors': True,
            'opts': 'e3c',
            'label': '#sigma_{{NLO+NLL}}({rn}) #pm 1#sigma (th)'.format(rn=refName),
            }
        }
    return histoD


def getExclusionHistos(limitFile, yMinMax=(50,50)):
    limitHistoDict = {
        'UpperLimit': {
            'label': 'Observed Limit',
            'LineWidth': 3,
            'LineColor': r.kBlue+2,
            'opts': 'c',
            'Smooth': False,
            },
        'ExpectedUpperLimit': {
            'label': 'Median Expected Limit #pm 1 #sigma (exp)',
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
            'label': 'Expected Upper Limit (+1 #sigma)',
            'FillStyle': 3001,
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'FillColor': r.kBlue-10,
            'opts': 'c',
            'Smooth': True,
            },
        'ExpectedUpperLimit_-1_Sigma': {
            'label': 'Expected Upper Limit (-1 #sigma)',
            'LineColor': r.kOrange+7,
            'LineWidth': 2,
            'FillColor': 10,
            'opts': 'c',
            'Smooth': True,
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


def compareXs(refProcess, refName=None, refXsFile="sms_xs/sms_xs.root",
              limitFile="xsLimit.root", pdfFile="sms_xs/compareXs.pdf",
              refYRange=(50,50), plotTitle="", plotOptOverrides=None,
              shiftX=False) :
    plotOpts = {
        'yMax': 2e+1,
        'yMin': 2e-4,
        'xMin': 300,
        'xMax': 1200,
        'xLabel': "{p} mass [GeV/c^{{2}}]".format(
            p=refProcess.capitalize().replace('_',' ')),
        'yLabel': '#sigma [pb]',
        'legendPosition': [0.12, 0.12, 0.47, 0.30],
        }
    if plotOptOverrides is not None:
        plotOpts.update(plotOptOverrides)

    refHisto = getReferenceXsHisto(refProcess, refName, refXsFile)
    exclusionHistos = getExclusionHistos(limitFile)

    canvas = r.TCanvas('c1','c1',700,600)
    hs = dict(refHisto.items() + exclusionHistos.items())

    leg = r.TLegend(*plotOpts['legendPosition'])
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    histosToDraw = ['ExpectedUpperLimit_+1_Sigma', 'ExpectedUpperLimit',
                    'ExpectedUpperLimit_-1_Sigma', 'refHisto', 'UpperLimit']
    for hname in histosToDraw:
        print "shifting", hname
        hs[hname]['hist'] = shifted(hs[hname]['hist'],shiftX=shiftX, shiftErrors=hs[hname].get('hasErrors',False))
    for iHisto, hname in enumerate(histosToDraw):
        props = hs[hname]
        h = props['hist']
        #h = shifted(props['hist'],shiftX=shiftX)
        h.SetStats(False)
        h.SetTitle(plotTitle)
        h.GetXaxis().SetRangeUser(plotOpts['xMin'],plotOpts['xMax'])
        h.SetMinimum(plotOpts['yMin'])
        h.SetMaximum(plotOpts['yMax'])
        if props.get('Smooth', False):
            h.Smooth(1,'R')
        h.Draw("%s%s"%(props.get('opts','c'), "same" if iHisto else ""))
        for attr in ['LineColor', 'LineStyle', 'LineWidth']:
            eval('h.Set{attr}(props.get("{attr}",1))'.format(attr=attr))
        for attr in ['FillStyle', 'FillColor']:
            if attr in props:
                eval('h.Set{attr}(props.get("{attr}",1))'.format(attr=attr))
        if "Sigma" not in hname:
            leg.AddEntry(h, props['label'], "lf")
        h.GetXaxis().SetTitle(plotOpts['xLabel'])
        h.GetYaxis().SetTitle(plotOpts['yLabel'])
    leg.Draw()
    tl = drawStamp(canvas)
    r.gPad.RedrawAxis()
    canvas.SetLogy()
    canvas.SetTickx()
    canvas.SetTicky()
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
