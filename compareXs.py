#!/usr/bin/env python

import ROOT as r
from utils import threeToTwo

def getReferenceXsHisto(refHistoName, filename):
    refFile = r.TFile(filename,'READ')
    refHisto = refFile.Get(refHistoName).Clone()
    refHisto.SetDirectory(0)
    refFile.Close()
    histoD = {
        'refHisto': {
            'hist': refHisto,
            'LineColor': r.kBlue,
            'label': '{0} pair production'.format(refHistoName.capitalize())
            }
        }
    return histoD


def getExclusionHistos(limitFile, yMinMax=(50,50)):
    limitHistoDict = {
        'UpperLimit': {
            'label': 'Upper Limit',
            'LineWidth': 2,
            'LineColor': r.kPink,
            'opts': '][',
            },
        'ExpectedUpperLimit': {
            'label': 'Expected Upper Limit (#pm 1 #sigma)',
            'LineColor': 46,
            'FillColor': 48,
            'FillStyle': 3002,
            'opts': '][',
            },
        'ExpectedUpperLimit_+1_Sigma': {
            'label': 'Expected Upper Limit (+1 #sigma)',
            'LineStyle': 2,
            'LineColor': 0,
            'FillStyle': 3002,
            'FillColor': 48,
            'opts': '][',
            },
        'ExpectedUpperLimit_-1_Sigma': {
            'label': 'Expected Upper Limit (-1 #sigma)',
            'LineStyle': 2,
            'LineColor': 0,
            'FillColor': 10,
            'opts': '][',
            },
        }

    rfile = r.TFile(limitFile,'READ')
    for limitHistoName, opts in limitHistoDict.iteritems():
        limitHisto = threeToTwo(rfile.Get(limitHistoName))
        minYBin = limitHisto.GetYaxis().FindBin(yMinMax[0])
        maxYBin = limitHisto.GetYaxis().FindBin(yMinMax[1])

        opts['hist'] = limitHisto.ProjectionX('T2tt',minYBin,maxYBin).Clone()
        opts['hist'].SetDirectory(0)

    rfile.Close()
    return limitHistoDict


def compareXs(refProcess, refXsFile="sms_xs/sms_xs.root",
              limitFile="xsLimit.root", pdfFile="sms_xs/compareXs.pdf",
              plotOptOverrides=None) :
    plotOpts = {
        'yMax': 2e+1,
        'yMin': 2e-4,
        'xMin': 300,
        'xMax': 1200,
        'xLabel': "{p} mass [GeV/c^{{2}}]".format(
            p=refProcess.capitalize().replace('_',' ')),
        'yLabel': '#sigma [pb]',
        }
    if plotOptOverrides is not None:
        plotOpts.update(plotOptOverrides)

    refHisto = getReferenceXsHisto(refProcess, refXsFile)
    exclusionHistos = getExclusionHistos(limitFile)

    canvas = r.TCanvas()
    hs = dict(refHisto.items() + exclusionHistos.items())

    leg = r.TLegend(0.5, 0.7, 0.88, 0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    histosToDraw = [ 'ExpectedUpperLimit_+1_Sigma',
                     'ExpectedUpperLimit',
                     'ExpectedUpperLimit_-1_Sigma',
                     'UpperLimit',
                     'refHisto' ]
    for iHisto, hname in enumerate(histosToDraw):
        props = hs[hname]
        h = props['hist']
        h.SetStats(False)
        h.SetTitle("")
        h.GetXaxis().SetRangeUser(plotOpts['xMin'],plotOpts['xMax'])
        h.SetMinimum(plotOpts['yMin'])
        h.SetMaximum(plotOpts['yMax'])
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
    r.gPad.RedrawAxis()
    canvas.SetLogy()
    canvas.SetTickx()
    canvas.SetTicky()
    canvas.Print(pdfFile)

def setup() :
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

def main():
    setup()
    limitFile = ('~/Projects/ra1ToyResults/2011/1000_toys/T2tt/'
                 'CLs_frequentist_TS3_T2tt_lo_RQcdFallingExpExt_fZinvTwo_55_'
                 '0b-1hx2p_55_1b-1hx2p_55_2b-1hx2p_55_gt2b-1h.root')
    xLabel = 'm_{#tilde{q}} [GeV/c^{2}]'
    compareXs(refProcess='squark', refXsFile="sms_xs/sms_xs.root",
              limitFile=limitFile, plotOptOverrides={'xLabel': xLabel})

if __name__=="__main__":
    main()
