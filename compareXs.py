#!/usr/bin/env python

import os

import configuration.signal
import histogramProcessing as hp
import utils
from signalScan import scan
from collections import OrderedDict as odict
import ROOT as r


def drawStamp(canvas, lspMass=None, lumiStamp="", processStamp="",
              preliminary=None, dM=None):
    canvas.cd()
    tl = r.TLatex()
    tl.SetNDC()
    tl.SetTextAlign(12)
    tl.SetTextSize(0.035)
    #tl.DrawLatex(0.16,0.84,'CMS')
    #x = 0.42
    x = 0.15
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
    label = 'Theory #pm 1#sigma'.format(rn=refName)
    histoD = {'refHisto': {'hist': refHisto,
                           'LineWidth': 1,
                           'LineStyle': 1,
                           'LineColor': r.kBlack,
                           'FillColor': r.kGray+1,
                           'FillStyle': 3144,
                           'label': label,
                           'nSmooth': 0,
                           }
              }
    return histoD


def exclusionHistos(expectedLimitFile="", observedLimitFile = "", model=None, shift=(False,False)):#(True, False)):
    offset = 7
    limitHistoDict = {
        model.name+'_UpperLimit': {
            'label': 'Observed',
            'LineWidth': 3,
            'LineColor': r.kBlack,
            },
        model.name+'_ExpectedUpperLimit': {
            'label': 'Expected',
            'LineWidth': 1,
            'LineColor': r.kBlack,
            'LineStyle': 2,
            # for legend
            'FillStyle': 0,
            'FillColor': 0,
            },
        model.name+'_ExpectedUpperLimit_+2_Sigma': {
            'label': 'Expected #pm 2#sigma',
            'LineWidth': 0,
            'LineColor': r.kYellow-offset,
            'FillStyle': 1001,
            'FillColor': r.kYellow-offset,
            },
        model.name+'_ExpectedUpperLimit_+1_Sigma': {
            'label': 'Expected #pm 1#sigma',
            'LineWidth': 0,
            'LineColor': r.kGreen-offset,
            'FillStyle': 1001,
            'FillColor': r.kGreen-offset,
            },
        model.name+'_ExpectedUpperLimit_-1_Sigma': {
            'label': 'None',
            'LineWidth': 0,
            'LineColor': r.kYellow-offset,
            'FillStyle': 1001,
            'FillColor': r.kYellow-offset,
            },
        model.name+'_ExpectedUpperLimit_-2_Sigma': {
            'label': 'None',
            'LineWidth': 0,
            'LineColor': 0,
            'FillStyle': 1001,
            'FillColor': 10,
            },
        }
    efile = r.TFile(expectedLimitFile, 'READ')
    ofile = r.TFile(observedLimitFile, 'READ')
    for limitHistoName, opts in limitHistoDict.iteritems():
        if "_UpperLimit" in limitHistoName :
            opts['hist'] = hp.modifiedHisto(h3=ofile.Get(limitHistoName),
                                            model=model,
                                            shiftX=False,#True,
                                            shiftY=False,#True,
                                            shiftErrors=False,
                                            range=False,)
        else:
            opts['hist'] = hp.modifiedHisto(h3=efile.Get(limitHistoName),
                                            model=model,
                                            shiftX=False,#True,
                                            shiftY=False,#True,
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
    #print h,yValue,dM,proj
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
            #print xBin,yBin,xVal,yVal,val,err
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
        #print "HERE",cntr
        return dMhisto if cntr > 0 else None
    return proj

def compareXs(histoSpecs={}, model=None, xLabel="", yLabel="", yValue=None,
              nSmooth=0, xMin=300, xMax=350, yMin=1e-1, yMax=1e+3,
              showRatio=False, dumpRatio=False, preliminary=None,
              lumiStamp="", processStamp="", dM=None):

    canvas = r.TCanvas('c1', 'c1', 700, 600)
    utils.divideCanvas(canvas)
    if showRatio:
        pad = canvas.cd(1)
    else:
        pad = canvas.cd(0)

    legs = odict.fromkeys(['refHisto',
                           model.name+'_UpperLimit',
                           model.name+'_ExpectedUpperLimit',
                           model.name+'_ExpectedUpperLimit_+1_Sigma',
                           model.name+'_ExpectedUpperLimit_+2_Sigma'])
    
    processed_histos = {}
    histos = [model.name+'_ExpectedUpperLimit_+2_Sigma',
              model.name+'_ExpectedUpperLimit_+1_Sigma',
              model.name+'_ExpectedUpperLimit',
              model.name+'_ExpectedUpperLimit_-1_Sigma',
              model.name+'_ExpectedUpperLimit_-2_Sigma',
              'refHisto',
              model.name+'_UpperLimit']
    for iHisto, hname in enumerate(histos):
        props = histoSpecs[hname]
        #print hname,props
        if hname == model.name+'_UpperLimit': 
            his = props["hist"]
#            if dM == 80 :
#                r.gROOT.SetBatch(False)
#                r.SetOwnership(his,False)
#                c1 = r.TCanvas()
#                his.Draw()
#                raw_input("")
        if hname != 'refHisto':
            #print "TEST1",props["hist"].Print()
            props["hist"] = oneD(props["hist"], yValue, dM)
            #print "TEST1",props["hist"].Print()
            gopts = 'hist'
        else:
            gopts = 'e3'
        h = props['hist']
        if h is None :
            #print "No histogram!"
            continue
        processed_histos[hname] = h
        h.SetStats(False)
        h.GetXaxis().SetRangeUser(xMin, xMax)
        h.SetMinimum(yMin)
        h.SetMaximum(yMax)
#        if nSmooth and (hname != 'refHisto'):
#            h.Smooth(nSmooth, 'R')
        h.Draw("%s%s" % (gopts, "same" if iHisto else ""))
        for attr in ['LineColor', 'LineStyle', 'LineWidth']:
            setAttr = getattr(h, 'Set{attr}'.format(attr=attr))
            setAttr(props.get(attr, 1))
        for attr in ['FillStyle', 'FillColor']:
            if attr in props:
                setAttr = getattr(h, 'Set{attr}'.format(attr=attr))
                setAttr(props.get(attr, 1))
        # if "UpperLimit_-" not in hname:
        if hname in legs.keys() : 
            legs[hname] = (h,props['label'],"lf")
#        else :
#            print "TEST",hname,legs.keys()
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

    #print len(legs.keys()),legs
    leg = r.TLegend(0.6, 0.6, 0.85, 0.85)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    for key,val in legs.items() : 
#        print "TEST",key,val
        if val is not None : leg.AddEntry(val[0],val[1],val[2])
    leg.Draw()

    tl = drawStamp(canvas, lspMass=yValue , lumiStamp=lumiStamp,
                   processStamp=processStamp, preliminary=preliminary, dM=dM)
    pad.RedrawAxis()
    pad.SetLogy()
    pad.SetTickx()
    pad.SetTicky()

    ref = histoSpecs['refHisto']
    obs = histoSpecs[model.name+'_UpperLimit']

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

    return processed_histos

def setup():
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetHatchesSpacing(1.4*r.gStyle.GetHatchesSpacing())

def transitions(input):
    output = {}
    try : ref = input["refHisto"]
    except: return output
    refu = ref.Clone("_up")
    refd = ref.Clone("_down")
    for bin in range(ref.GetNbinsX()) : refu.SetBinContent( bin+1, ref.GetBinContent(bin+1)+ref.GetBinError(bin+1) )
    for bin in range(ref.GetNbinsX()) : refd.SetBinContent( bin+1, ref.GetBinContent(bin+1)-ref.GetBinError(bin+1) )
    for histo in input.keys():# [x for x in input.keys() if "_ExpectedUpperLimit_+1" in x ]:
        for hist in [histo] if "_UpperLimit" not in histo else [histo+x for x in ["","_+1_Sigma","_-1_Sigma"]] : 
            if "refHisto" in histo : continue
            fit = r.TF1("","expo(0)+expo(2)")
            his = input[histo]
            his.Fit(fit,"Q0")
            nbins = ref.GetXaxis().GetNbins()
            (fstart,fend) = (-1.,-1.)
            (hstart,hend) = (-1.,-1.)
            for bin in range(350):#nbins) :
                msusy = bin*1.#ref.GetBinCenter(bin+1)
                if msusy < his.GetBinCenter(1) : continue
                #theory = ref.GetBinContent(bin+1)
                theory = ref.Interpolate(msusy) 
                if "_UpperLimit" in hist and "_+1_Sigma" in hist : theory = refu.Interpolate(msusy) 
                elif "_UpperLimit" in hist and "_-1_Sigma" in hist : theory = refd.Interpolate(msusy) 
                fxs = fit.Eval(msusy)
                hxs = his.Interpolate(msusy)
                #theory = ref.Interpolate(ref.GetBinCenter(msusy))
                #fxs = fit.Eval(ref.GetBinCenter(msusy))
                #hxs = his.Interpolate(ref.GetBinCenter(msusy))
                #print bin,msusy,theory,fxs,hxs
                if fxs < theory and fstart < 0. : fstart = msusy
                #if fend < 0. and fxs > theory and fstart > 0. : fend = msusy
                if fxs < theory and fstart > 0. : fend = msusy
                if hxs < theory and hstart < 0. : hstart = msusy
                #if hend < 0. and hxs > theory and hstart > 0. : hend = msusy
                if hxs < theory and hstart > 0. : hend = msusy
                #print msusy,theory,hxs,hxs<theory,hstart,hend
            output[hist] = (fstart,fend),(hstart,hend)
    return output

def points():
    #print "TEMP",[ (x,100) for x in range(100,0,-10) ]
    out = []
    #for mlsp, xMin in [(90, 100), (20,100), (50, 300), (100, 300), (150, 350)][0:2]:
    for mlsp, xMin in [ (x,100) for x in range(100,0,-10) ]:
    #for mlsp, xMin in [ (90,100), (80,100), (70,100), (60,100), (40,100), (20,100), ]:
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

    #print "TEST",expFileName,obsFileName
    
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
        'lumiStamp': 'L = 18.5 fb^{-1}, #sqrt{s} = 8 TeV',
        'preliminary': True,
        'processStamp': configuration.signal.processStamp(model.name)['text'],
        'dM': dM,
        }

    #for key,val in options.items() : print key,val
    
    processed_histos = compareXs(model=model, yValue=yValue, nSmooth=nSmooth, xMin=xMin, **options)

    # Calculate where UL crossed XS
    return transitions(processed_histos)

def main():
    setup()
    for model in configuration.signal.models():
        for dct in points():
            #print "MLSP",dct["yValue"]
            onePoint(model,
                     expFileNameSuffix="_exp",
                     obsFileNameSuffix="_obs",
                     **dct)


if __name__ == "__main__":
    main()
