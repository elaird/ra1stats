#!/usr/bin/env python

import os

import configuration.signal
import histogramProcessing as hp
import utils
from signalScan import scan

import ROOT as r


def drawStamp(canvas, lspMass=None, lumiStamp="", processStamp="",
              preliminary=None, dM=None):
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

    if dM:
        tl.DrawLatex(x, y-2*dy,
                     'm_{%s} - m_{%s} = %d GeV' % ("#tilde{t}",
                                                   configuration.signal.chi(),
                                                   dM)
                     )
    else:
        tl.DrawLatex(x, y-2*dy,
                     'm_{%s} = %d GeV' % (configuration.signal.chi(),
                                          int(lspMass))
                     )


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


def exclusionHistos(expectedLimitFile="", observedLimitFile = "", model=None, shift=(True, False)):
    limitHistoDict = {
        'T2cc_UpperLimit': {
            'label': 'Observed Limit (95% CL)',
            'LineWidth': 3,
            'LineColor': r.kBlue+2,
            },
        'T2cc_ExpectedUpperLimit': {
            'label': 'Median Expected Limit #pm #sigma exp.',
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'LineStyle': 9,
            # for legend
            'FillStyle': 1001,
            'FillColor': r.kBlue-10,
            },
        'T2cc_ExpectedUpperLimit_+1_Sigma': {
            'label': 'Expected Upper Limit (+1#sigma)',
            'FillStyle': 1001,
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'FillColor': r.kBlue-10,
            },
        'T2cc_ExpectedUpperLimit_-1_Sigma': {
            'label': 'Expected Upper Limit (-1#sigma)',
            'LineColor': r.kOrange+7,
            'LineWidth': 2,
            'FillStyle': 1001,
            'FillColor': 10,
            },
        'T2cc_ExpectedUpperLimit_+2_Sigma': {
            'label': 'Expected Upper Limit (+2#sigma)',
            'FillStyle': 1001,
            'LineWidth': 2,
            'LineColor': r.kOrange+7,
            'FillColor': r.kBlue-10,
            },
        'T2cc_ExpectedUpperLimit_-2_Sigma': {
            'label': 'Expected Upper Limit (-2#sigma)',
            'LineColor': r.kOrange+7,
            'LineWidth': 2,
            'FillStyle': 1001,
            'FillColor': 10,
            }
        }
    efile = r.TFile(expectedLimitFile, 'READ')
    ofile = r.TFile(observedLimitFile, 'READ')
    for limitHistoName, opts in limitHistoDict.iteritems():
        if limitHistoName == "T2cc_UpperLimit":
            opts['hist'] = hp.modifiedHisto(h3=ofile.Get(limitHistoName),
                                            model=model,
                                            shiftX=True,
                                            shiftY=True,
                                            shiftErrors=False,
                                            range=False,)
        else:
            opts['hist'] = hp.modifiedHisto(h3=efile.Get(limitHistoName),
                                            model=model,
                                            shiftX=True,
                                            shiftY=True,
                                            shiftErrors=False,
                                            range=False,
                                            info=False)

    efile.Close()
    ofile.Close()
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
    ratio.Print('all')
    if xMax is None:
        xMax = ratio.GetXaxis().GetXmax()
    if xMin is None:
        xMin = ratio.GetXaxis().GetXmin()
    line = r.TLine()
    line.DrawLine(xMin, 1., xMax, 1.)
    return ratio, line


def oneD(h=None, yValue=None, dM=None):
    yBin = h.GetYaxis().FindBin(yValue)
    proj = h.ProjectionX(h.GetName()+"_", yBin, yBin)
    if dM:
        cntr = 0
        dMhisto = r.TH1D(h.GetName()+"_%i" % dM,"", 11, 87.5, 362.5)
        #proj.Reset()
        xBin = h.GetXaxis().FindBin(yValue + dM)
        for ixBin in range(xBin, h.GetXaxis().GetNbins()):
            yVal = h.GetYaxis().GetBinCenter(h.GetYaxis().FindBin(h.GetBinCenter(ixBin)-dM))
            yBin = h.GetYaxis().FindBin(yVal)
            xVal = h.GetXaxis().GetBinCenter(ixBin)
            val = h.GetBinContent(ixBin,yBin)
            err = h.GetBinError(ixBin,yBin)
            if val > 0. : cntr += 1
            if val == 0.0 :
                #print "HACK! SO that curve doesnt connect empty bin, don't publish like this"
                yBin = h.GetYaxis().FindBin(yVal)
                yValHigh = h.GetYaxis().GetBinCenter(h.GetYaxis().FindBin(h.GetBinCenter(ixBin-1)-dM))
                yBinHigh = h.GetYaxis().FindBin(yValHigh)
                yValLow = h.GetYaxis().GetBinCenter(h.GetYaxis().FindBin(h.GetBinCenter(ixBin+1)-dM))
                yBinLow = h.GetYaxis().FindBin(yValLow)
                val = (h.GetBinContent(ixBin-1,yBinHigh)+h.GetBinContent(ixBin+1,yBinLow))/2.
            dMhisto.SetBinContent(dMhisto.FindBin(h.GetBinCenter(ixBin)),val)
            dMhisto.SetBinError(dMhisto.FindBin(h.GetBinCenter(ixBin)),err)
        return dMhisto if cntr > 0 else None
    return proj


def compareXs(histoSpecs={}, model=None, xLabel="", yLabel="", yValue=None,
              nSmooth=0, xMin=300, xMax=350, yMin=1e-3, yMax=1e+4,
              showRatio=False, dumpRatio=False, preliminary=None,
              lumiStamp="", processStamp="", dM=None):

    canvas = r.TCanvas('c1', 'c1', 700, 600)
    utils.divideCanvas(canvas)
    if showRatio:
        pad = canvas.cd(1)
    else:
        pad = canvas.cd(0)

    leg = r.TLegend(0.25, 0.65, 0.85, 0.85)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)

    histo_range = None
    processed_histos = {}
    histos = [#'T2cc_ExpectedUpperLimit_+2_Sigma',
              'T2cc_ExpectedUpperLimit_+1_Sigma',
              'T2cc_ExpectedUpperLimit',
              'T2cc_ExpectedUpperLimit_-1_Sigma',
              #'T2cc_ExpectedUpperLimit_-2_Sigma',
              'refHisto',
              'T2cc_UpperLimit']
    for iHisto, hname in enumerate(histos):
        props = histoSpecs[hname]
        if hname == 'T2cc_UpperLimit':
            his = props["hist"]
            histo_range = (his.GetXaxis().GetBinCenter(his.FindFirstBinAbove(0.,1)),\
                           his.GetXaxis().GetBinCenter(his.FindLastBinAbove(0.,1)),\
                           his.GetYaxis().GetBinCenter(his.FindFirstBinAbove(0.,2)),\
                           his.GetYaxis().GetBinCenter(his.FindLastBinAbove(0.,2)))
        if hname != 'refHisto':
            props["hist"] = oneD(props["hist"], yValue, dM)
            gopts = 'HIST C'
        else:
            gopts = 'e3'
        h = props['hist']
        if h is None :
            print "No histogram!"
            continue
        processed_histos[hname] = h
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
#            if "Expected" in hname:
#                props['label'] = props['label'].replace("#sig","%s#sig"%nSigma)
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
    tl = drawStamp(canvas, lspMass=yValue , lumiStamp=lumiStamp,
                   processStamp=processStamp, preliminary=preliminary, dM=dM)
    pad.RedrawAxis()
    pad.SetLogy()
    pad.SetTickx()
    pad.SetTicky()

    ref = histoSpecs['refHisto']
    obs = histoSpecs['T2cc_UpperLimit']

    if dumpRatio:
        #printRatio(obs, ref)
        printRatio(obs, ref, errSign='+')
        #printRatio(obs, ref, errSign='-')

    if showRatio:
        ratio, line = drawRatio(ref, obs, canvas, 2, xMin=xMin, xMax=xMax)

    strName = [model.name,
               "mlsp%d" % int(yValue),
               "xmin%d" % int(xMin),
               "smooth%d" % nSmooth,
               ]

    epsFile = "plots/" + "_".join((strName + ["dM%d" % int(dM)]) if dM else strName)+".eps"#+"_%ssigma"%nSigma+".eps"

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

    return histo_range,processed_histos

def setup():
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetHatchesSpacing(1.4*r.gStyle.GetHatchesSpacing())

def transitions(input):
    output = {}
    try : ref = input["refHisto"]
    except: return output
    for histo in input.keys():
        if "refHisto" in histo : continue
        fit = r.TF1("","expo(0)+expo(2)")
        his = input[histo]
        his.Fit(fit,"Q0")
        nbins = ref.GetXaxis().GetNbins()
        (fstart,fend) = (-1.,-1.)
        (hstart,hend) = (-1.,-1.)
        for bin in range(1000):#nbins) :
            msusy = bin*1.#ref.GetBinCenter(bin+1)
            if msusy < his.GetBinCenter(1) : continue
            #theory = ref.GetBinContent(bin+1)
            theory = ref.Interpolate(msusy)
            fresult = fit.Eval(msusy)
            hresult = his.Interpolate(msusy)
            #theory = ref.Interpolate(ref.GetBinCenter(msusy))
            #fresult = fit.Eval(ref.GetBinCenter(msusy))
            #hresult = his.Interpolate(ref.GetBinCenter(msusy))
            #print bin,msusy,theory,fresult,hresult
            if fresult < theory and fstart < 0. : fstart = msusy
            if fend < 0. and fresult > theory and fstart > 0. : fend = msusy
            if hresult < theory and hstart < 0. : hstart = msusy
            if hend < 0. and hresult > theory and hstart > 0. : hend = msusy
        output[histo] = (fstart,fend),(hstart,hend)
    return output

def points():
    out = []
    for mlsp, xMin in [(90, 100), (20,100), (50, 300), (100, 300), (150, 350)][0:2]:
        for nSmooth in [0, 1, 2, 5][:1]:
            out.append({"yValue": mlsp,
                        "nSmooth": nSmooth,
                        "xMin": xMin,
                        "dM" : xMin-mlsp})
    return out

def onePoint(model,
             expFileNameSuffix=None,
             obsFileNameSuffix=None,
             yValue=None, nSmooth=None, xMin=None, dM=None):

    (expFileName,obsFileName) = configuration.limit.mergedFiles(model=model,
                                                                expFileNameSuffix=expFileNameSuffix,
                                                                obsFileNameSuffix=obsFileNameSuffix)
    
    hSpec = configuration.signal.xsHistoSpec(model)

    refHisto = referenceXsHisto(refHistoName=hSpec['histo'],
                                refName='#tilde{t} #tilde{t}',
                                xsFileName=hSpec['file'],
                                )

    exclHistos = exclusionHistos(expectedLimitFile=expFileName,
                                 observedLimitFile=obsFileName,
                                 model=model)

    options = {
        'histoSpecs': dict(refHisto.items() + exclHistos.items()),
        'xLabel': 'm_{#tilde{t}} (GeV)',
        'yLabel': '#sigma (pb)',
        'showRatio': False,
        'lumiStamp': 'L = 18.7 fb^{-1}, #sqrt{s} = 8 TeV',
        'preliminary': False,
        'processStamp': configuration.signal.processStamp(model.name)['text'],
        'dM': dM,
        }

    histo_range,processed_histos = compareXs(model=model, yValue=yValue, nSmooth=nSmooth, xMin=xMin,
                                             **options)

    return transitions(processed_histos)

def main():
    setup()
    for model in configuration.signal.models():
        for dct in points():
            onePoint(model,
                     expFileNameSuffix="_exp",
                     obsFileNameSuffix="_exp",
                     **dct)


if __name__ == "__main__":
    main()
