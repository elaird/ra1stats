#!/usr/bin/env python

import os

from configuration import signal
import histogramProcessing as hp
import utils

import ROOT as r

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
                 'm_{%s} = %d GeV' % (signal.chi(), int(lspMass)))

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


def referenceXsHisto(refHistoName="", refName="", xsFileName=""):
    refFile = r.TFile(xsFileName, 'READ')
    refHisto = refFile.Get(refHistoName).Clone()
    refHisto.SetDirectory(0)
    refFile.Close()
    label = '#sigma^{{NLO+NLL}}({rn}) #pm th. unc.'.format(rn=refName)
    histoD = {'refHisto': {'hist': refHisto,
                           'LineWidth': 2,
                           'LineStyle': 1,
                           'LineColor': r.kBlack,
                           'FillColor': r.kGray+1,
                           'FillStyle': 3144,
                           'label': label,
                           'nSmooth': 0,
                           }
              }
    return histoD


def exclusionHistos(limitFile="", model="", shift = (True, False)):
    limitHistoDict = {
        'UpperLimit': {
            'label': 'Observed Limit (95% CL)',
            'LineWidth': 3,
            'LineColor': r.kBlue+2,
            },
        'ExpectedUpperLimit': {
            'label': 'Median Expected Limit #pm 1#sigma exp.',
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'LineStyle': 9,
            # for legend
            'FillStyle': 1001,
            'FillColor': r.kBlue-10,
            },
        'ExpectedUpperLimit_+1_Sigma': {
            'label': 'Expected Upper Limit (+1#sigma)',
            'FillStyle': 1001,
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'FillColor': r.kBlue-10,
            },
        'ExpectedUpperLimit_-1_Sigma': {
            'label': 'Expected Upper Limit (-1#sigma)',
            'LineColor': r.kOrange+7,
            'LineWidth': 2,
            'FillStyle': 1001,
            'FillColor': 10,
            },
        }

    rfile = r.TFile(limitFile, 'READ')
    for limitHistoName, opts in limitHistoDict.iteritems():
        h = utils.shifted(utils.threeToTwo(rfile.Get(limitHistoName)),
                          shift = shift, shiftErrors = False)
        hp.modifyHisto(h, model)
        opts['hist'] = h
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


def oneD(h=None, yValue=None):
    yBin = h.GetYaxis().FindBin(yValue)
    return h.ProjectionX(h.GetName()+"_", yBin, yBin)


def compareXs(histoSpecs={}, model="", xLabel="", yLabel="", yValue=None,
              nSmooth=0, xMin=300, xMax=800, yMin=1e-3, yMax=1e+1,
              showRatio=False, dumpRatio=False, preliminary=None,
              lumiStamp="", processStamp=""):

    canvas = r.TCanvas('c1', 'c1', 700, 600)
    utils.divideCanvas(canvas)
    if showRatio:
        pad = canvas.cd(1)
    else:
        pad = canvas.cd(0)

    leg = r.TLegend(0.25, 0.65, 0.85, 0.85)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    for iHisto, hname in enumerate(['ExpectedUpperLimit_+1_Sigma',
                                    'ExpectedUpperLimit',
                                    'ExpectedUpperLimit_-1_Sigma',
                                    'refHisto',
                                    'UpperLimit',
                                    ]):
        props = histoSpecs[hname]
        if hname != 'refHisto':
            props["hist"] = oneD(props["hist"], yValue)
            gopts = 'c'
        else:
            gopts = 'e3'

        h = props['hist']
        h.SetStats(False)
        h.GetXaxis().SetRangeUser(xMin, xMax)
        h.SetMinimum(yMin)
        h.SetMaximum(yMax)
        if nSmooth and (hname != 'refHisto'):
            h.Smooth(nSmooth, 'R')
        h.Draw("%s%s" % (gopts, "same" if iHisto else ""))
        for attr in ['LineColor', 'LineStyle', 'LineWidth']:
            setAttr = getattr(h, 'Set{attr}'.format(attr=attr))
            setAttr(props.get(attr, 1))
        for attr in ['FillStyle', 'FillColor']:
            if attr in props:
                setAttr = getattr(h, 'Set{attr}'.format(attr=attr))
                setAttr(props.get(attr, 1))
        if "Sigma" not in hname:
            leg.AddEntry(h, props['label'], "lf")
        h.GetXaxis().SetTitle(xLabel)
        h.GetYaxis().SetTitle(yLabel)
        if hname == 'refHisto':
            hCentral = h.Clone("central")
            hUpper = h.Clone("upper")
            hLower = h.Clone("lower")
            for h2 in [hCentral, hUpper, hLower]:
                h2.Reset()
                h2.SetFillStyle(0)
                h2.SetLineWidth(1)
            for iBin in range(1, 1+h.GetXaxis().GetNbins()):
                hCentral.SetBinContent(iBin, h.GetBinContent(iBin))
                hUpper.SetBinContent(iBin, h.GetBinContent(iBin) + h.GetBinError(iBin))
                hLower.SetBinContent(iBin, h.GetBinContent(iBin) - h.GetBinError(iBin))

            hLower.SetLineColor(h.GetFillColor())
            hUpper.SetLineColor(h.GetFillColor())
            for h2 in [hCentral, hUpper, hLower][:1]:
                h2.Draw('lsame')
    leg.Draw()
    tl = drawStamp(canvas, lspMass=yValue, lumiStamp=lumiStamp,
                   processStamp=processStamp, preliminary=preliminary)
    pad.RedrawAxis()
    pad.SetLogy()
    pad.SetTickx()
    pad.SetTicky()

    ref = histoSpecs['refHisto']
    obs = histoSpecs['UpperLimit']

    if dumpRatio:
        #printRatio(obs, ref)
        printRatio(obs, ref, errSign='+')
        #printRatio(obs, ref, errSign='-')

    if showRatio:
        ratio, line = drawRatio(ref, obs, canvas, 2, xMin=xMin, xMax=xMax)

    epsFile = "_".join([model,
                        "mlsp%d" % int(yValue),
                        "xmin%d" % int(xMin),
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
    r.gStyle.SetHatchesSpacing(1.4*r.gStyle.GetHatchesSpacing())


def points():
    out = []
    for mlsp, xMin in [(0, 300), (50, 300), (100, 300), (150, 350)]:
        for nSmooth in [0, 1, 2, 5][-1:]:
            out.append({"yValue": mlsp,
                        "nSmooth": nSmooth,
                        "xMin": xMin})
    return out

def onePoint(yValue=None, nSmooth=None, xMin=None):
    model = 'T2tt'
    hSpec = signal.xsHistoSpec(model=model, xsVariation="default")

    refHisto = referenceXsHisto(refHistoName=hSpec['histo'],
                                refName='#tilde{t} #tilde{t}',
                                xsFileName=hSpec['file'],
                                )

    exclFileName = 'CLs_frequentist_TS3_T2tt_2012hcp_RQcdFallingExpExt_fZinvTwo_1b_ge4j-1hx2p_2b_ge4j-1h.root'
    exclHistos = exclusionHistos(limitFile='ra1r/scan/%s' % exclFileName, model=model)

    options = {
        'histoSpecs': dict(refHisto.items() + exclHistos.items()),
        'xLabel': 'm_{#tilde{t}} (GeV)',
        'yLabel': '#sigma (pb)',
        'showRatio': False,
        'lumiStamp': 'L = 11.7 fb^{-1}, #sqrt{s} = 8 TeV',
        'preliminary': False,
        'processStamp': signal.processStamp(model)['text'],
        }

    compareXs(model=model, yValue=yValue, nSmooth=nSmooth, xMin=xMin,
              **options)


def main():
    setup()
    for dct in points():
        onePoint(**dct)


if __name__ == "__main__":
    main()
