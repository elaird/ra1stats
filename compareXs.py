#!/usr/bin/env python

import os
import ROOT as r
import utils
import histogramProcessing
import signalAux


def drawStamp(canvas, lspMass=None, lumiStamp="", processStamp="",
              preliminary=None):
    canvas.cd()
    tl = r.TLatex()
    tl.SetNDC()
    tl.SetTextAlign(12)
    tl.SetTextSize(0.04)
    #tl.DrawLatex(0.16,0.84,'CMS')
    #x = 0.42
    x = 0.16
    y = 0.3
    dy = 0.06

    tl.DrawLatex(x, y-2*dy,
                 'm_{%s} = %d GeV' % (signalAux.chi(), int(lspMass)))

    if preliminary:
        tl.DrawLatex(x, y+dy, "CMS Preliminary")
        tl.DrawLatex(x, y, lumiStamp)
    else:
        tl.DrawLatex(x, y, "CMS, "+lumiStamp)

    #tl.SetTextSize(0.07)
    #tl.DrawLatex(0.20,0.75,'#alpha_{T}')

    tl.SetTextSize(0.04)
    tl.DrawLatex(x, y-dy, processStamp)
    return tl


def getReferenceXsHisto(refHistoName, refName, filename):
    refFile = r.TFile(filename, 'READ')
    refHisto = refFile.Get(refHistoName).Clone()
    refHisto.SetDirectory(0)
    refFile.Close()
    label = '#sigma^{{NLO+NLL}}({rn}) #pm th. unc.'.format(rn=refName)
    histoD = {'refHisto': {'hist': refHisto,
                           'LineWidth': 2,
                           'LineStyle': 1,
                           'LineColor': r.kBlack,
                           'FillColor': r.kGray+2,
                           'FillStyle': 3002,
                           'hasErrors': True,
                           'opts': 'e3l',
                           'label': label,
                           'nSmooth': 0,
                           }
              }
    return histoD


def getExclusionHistos(limitFile, yValue=None, gopts="c", nSmooth=0, model=""):
    limitHistoDict = {
        'UpperLimit': {
            'label': 'Observed Limit (95% CL)',
            'LineWidth': 3,
            'LineColor': r.kBlue+2,
            'opts': gopts,
            'nSmooth': nSmooth},
        'ExpectedUpperLimit': {
            'label': 'Median Expected Limit #pm 1#sigma exp.',
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'LineStyle': 9,
            'opts': gopts,
            'nSmooth': nSmooth,
            # for legend
            'FillStyle': 3001,
            'FillColor': r.kBlue-10},
        'ExpectedUpperLimit_+1_Sigma': {
            'label': 'Expected Upper Limit (+1#sigma)',
            'FillStyle': 3001,
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'FillColor': r.kBlue-10,
            'opts': gopts,
            'nSmooth': nSmooth},
        'ExpectedUpperLimit_-1_Sigma': {
            'label': 'Expected Upper Limit (-1#sigma)',
            'LineColor': r.kOrange+7,
            'LineWidth': 2,
            'FillColor': 10,
            'opts': gopts,
            'nSmooth': nSmooth}}

    rfile = r.TFile(limitFile, 'READ')
    for limitHistoName, opts in limitHistoDict.iteritems():
        limitHisto = utils.threeToTwo(rfile.Get(limitHistoName))
        histogramProcessing.modifyHisto(limitHisto, model)

        yBin = limitHisto.GetYaxis().FindBin(yValue)

        opts['hist'] = limitHisto.ProjectionX(limitHistoName+"_",
                                              yBin,
                                              yBin).Clone()
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
    ratio = h2.Clone()
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
        ratio.SetBinContent(h2Bin, binRatio)
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
    if xMax is None:
        xMax = ratio.GetXaxis().GetXmax()
    if xMin is None:
        xMin = ratio.GetXaxis().GetXmin()
    line = r.TLine()
    line.DrawLine(xMin, 1., xMax, 1.)
    return ratio, line


def compareXs(refProcess, refName, refXsFile, limitFile="xsLimit.root",
              yValue=None, plotOptOverrides=None, shiftX=False,
              showRatio=False, nSmooth=0, dumpRatio=False, lumiStamp="",
              processStamp="", model="", xMin=300, preliminary=None):
    plotOpts = {'yMax': 1e+1,
                'yMin': 1e-3,
                'xMin': xMin,
                'xMax': 800,
                'xLabel': "{p} mass (GeV)".format(
                    p=refProcess.capitalize().replace('_', ' ')),
                'yLabel': '#sigma (pb)',
                'legendPosition': [0.40, 0.65, 0.85, 0.88],
                }
    if plotOptOverrides is not None:
        plotOpts.update(plotOptOverrides)

    refHisto = getReferenceXsHisto(refProcess, refName, refXsFile)
    exclusionHistos = getExclusionHistos(limitFile, yValue=yValue,
                                         nSmooth=nSmooth, model=model)

    canvas = r.TCanvas('c1', 'c1', 700, 600)
    utils.divideCanvas(canvas)
    if showRatio:
        pad = canvas.cd(1)
    else:
        pad = canvas.cd(0)
    hs = dict(refHisto.items() + exclusionHistos.items())

    leg = r.TLegend(*plotOpts['legendPosition'])
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    for iHisto, hname in enumerate(['ExpectedUpperLimit_+1_Sigma',
                                    'ExpectedUpperLimit',
                                    'ExpectedUpperLimit_-1_Sigma',
                                    'refHisto',
                                    'UpperLimit']):
        hs[hname]['hist'] = utils.shifted(hs[hname]['hist'], shift=(shiftX,),
                                          shiftErrors=hs[hname].get(
                                              'hasErrors', False)
                                          )
        props = hs[hname]
        h = props['hist']
        h.SetStats(False)
        h.GetXaxis().SetRangeUser(plotOpts['xMin'], plotOpts['xMax'])
        h.SetMinimum(plotOpts['yMin'])
        h.SetMaximum(plotOpts['yMax'])
        if props['nSmooth']:
            h.Smooth(props.get('nSmooth', 1), 'R')
        h.Draw("%s%s" % (props.get('opts', 'c'), "same" if iHisto else ""))
        for attr in ['LineColor', 'LineStyle', 'LineWidth']:
            setAttr = getattr(h, 'Set{attr}'.format(attr=attr))
            setAttr(props.get(attr, 1))
        for attr in ['FillStyle', 'FillColor']:
            if attr in props:
                setAttr = getattr(h, 'Set{attr}'.format(attr=attr))
                setAttr(props.get(attr, 1))
        if "Sigma" not in hname:
            leg.AddEntry(h, props['label'], "lf")
        h.GetXaxis().SetTitle(plotOpts['xLabel'])
        h.GetYaxis().SetTitle(plotOpts['yLabel'])
        if hname == 'refHisto':
            h2 = h.Clone()
            brange = range(h2.GetXaxis().GetNbins())
            h2.Reset()
            for iBin in brange:
                h2.SetBinContent(iBin, h.GetBinContent(iBin))
            h2.SetFillStyle(0)
            h2.SetLineWidth(1)
            h2.Draw('lsame')
    leg.Draw()
    tl = drawStamp(canvas, lspMass=yValue, lumiStamp=lumiStamp,
                   processStamp=processStamp, preliminary=preliminary)
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

    epsFile = "_".join([model,
                        "mlsp%d" % int(yValue),
                        "xmin%d" % int(plotOpts['xMin']),
                        "smooth%d" % nSmooth,
                        ]
                       )+".eps"

    if preliminary:
        epsFile = epsFile.replace(".eps", "_prelim.eps")
    print "Saving to {file}".format(file=epsFile)
    canvas.Print(epsFile)
    canvas.Print(epsFile.replace(".eps", ".C"))

    epsiFile = epsFile.replace(".eps", ".epsi")
    os.system("ps2epsi "+epsFile+" "+epsiFile)
    os.system("epstopdf "+epsiFile)
    os.system("rm       "+epsiFile)
    os.system("rm       "+epsFile)


def setup():
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000


def main():
    setup()

    model = 'T2tt'
    hSpec = signalAux.xsHistoSpec(model=model, xsVariation="default")

    options = {
        'refProcess': hSpec['histo'],
        'refXsFile': hSpec['file'],
        'refName': '#tilde{t} #tilde{t}',
        'limitFile': 'ra1r/scan/CLs_frequentist_TS3_T2tt_2012hcp_RQcdFallingExpExt_fZinvTwo_1b_ge4j-1hx2p_2b_ge4j-1h.root',
        #'/vols/cms04/samr/ra1DataFiles/ToyResults/2011/1000_toys/T2tt/'
        #'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_'
        #'0b-1hx2p_55_1b-1hx2p_55_2b-1hx2p_55_gt2b-1h.root',
        'yValue': 0.,
        'shiftX': True,
        'showRatio': False,
        'plotOptOverrides': {'xLabel': 'm_{#tilde{t}} (GeV)'},
        'lumiStamp': 'L = 11.7 fb^{-1}, #sqrt{s} = 8 TeV',
        'preliminary': False,
        'processStamp': signalAux.processStamp(model)['text'],
        'model': model}

    lst = []
    for mlsp, xMin in [(0, 300), (50, 300), (100, 300), (150, 350)][:1]:
        for nSmooth in [0, 1, 2, 5][-1:]:
            lst.append({"yValue": mlsp, "nSmooth": nSmooth, "xMin": xMin})

    for dct in lst:
        options.update(dct)
        compareXs(**options)

if __name__ == "__main__":
    main()
