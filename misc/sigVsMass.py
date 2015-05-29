#!/usr/bin/env python

from collections import OrderedDict as odict
import os
import sys
sys.path.append(os.path.dirname(__file__)+"/..")

import ROOT as r
import utils

from operator import itemgetter

model = "T2cc"

dir = ["sigVsMass/"+model+"/data",
       "sigVsMass/"+model+"/semiblind",
       "sigVsMass/"+model+"/blind",
       "sigVsMass/"+model+"/semiblind-sig-inj",
       "sigVsMass/"+model+"/blind-sig-inj",
       "."][-1]

def nice(tuple) :
    print "point={0:.0f} m_stop={1:.0f} label={2:s} xs/th={3:.2f}+/-{4:.2f} nll(0)={5:.2f} nll(1)={6:.2f} th={7:.2f}".format(*tuple)

def oneHisto(hName="", label=""):
    if mode.startswith("bestFit"):
        stem = "nlls" + mode.replace("bestFit", "")
    if mode == "CL":
        stem = "CLs_asymptotic_binaryExcl"

    print "input file:","ra1r/scan/%s/%s/%s_%s_2012dev_%s.root" % (dir, subDir, stem, model, label)

    f = r.TFile("ra1r/scan/%s/%s/%s_%s_2012dev_%s.root" % (dir, subDir, stem, model, label))
    if f.IsZombie():
        sys.exit()
    h = f.Get(hName)
    if h:
        h = h.Clone()
        h.SetDirectory(0)
        f.Close()
        return h
    else:
        print "ERROR: histogram %s:%s not found." % (f.GetName(), hName)


def bestFitContents(label=""):
    hVal = oneHisto(label=label,   hName=""+model+"_poiVal")
    hErr = oneHisto(label=label,   hName=""+model+"_poiErr")
    hSigma0 = oneHisto(label=label, hName=""+model+"_nSigma_s0_sHat")
    if mode == "bestFit_binaryExcl":
        hSigma1 = oneHisto(label=label, hName=""+model+"_nSigma_sNom_sHat")
    else:
        hSigma1 = None

    out = []
    if not all([hVal, hErr, hSigma0]):
        return out

    for (iBinX, x, iBinY, y, iBinZ, z) in utils.bins(hVal, interBin="Center"):
        if iBinZ != 1:
            continue

        t = (iBinX, iBinY, iBinZ)
        val = hVal.GetBinContent(*t)
        err = hErr.GetBinContent(*t)
        n0 = hSigma0.GetBinContent(*t)
        n1 = hSigma1.GetBinContent(*t) if hSigma1 else None
        if val == 0.0 and err == 0.0:
            continue
        label = "%3d %3d" % (x, y)
        out.append((x, label, val, err, n0, n1))
    return out


def bestFitPlots(label=""):
    cont = bestFitContents(label)
    nBins = len(cont)
    if mode == "bestFit":
        words = "value #pm unc (pb)"
    if mode == "bestFit_binaryExcl":
        words = "factor #pm unc"

    poi = r.TH1D("poi", "%s;;best-fit xs %s" % (label, words), nBins, 0, nBins)
    poiX = poi.GetXaxis()

    poiR = r.TH1D("poiR", "%s;;best-fit xs / model xs" % label, nBins, 0, nBins)
    poiRX = poiR.GetXaxis()

    rel = r.TH1D("rel", "%s;;best-fit xs value / unc" % label, nBins, 0, nBins)
    relX = rel.GetXaxis()

    nllSigma0 = r.TH1D("nllSigma0", "%s;;#pm #sqrt{2 (nll_{xs = 0}  -  nll_{xs = best-fit})}" % label, nBins, 0, nBins)
    nllSigma0X = nllSigma0.GetXaxis()

    nllSigma1 = r.TH1D("nllSigma1", "%s;;#pm #sqrt{2 (nll_{xs = nom}  -  nll_{xs = best-fit})}" % label, nBins, 0, nBins)
    nllSigma1X = nllSigma1.GetXaxis()

    xs = r.TH1D("xs", "%s;;model xs (pb)" % label, nBins, 0, nBins)
    xsX = xs.GetXaxis()

    #tfile = r.TFile("xs/sms_xs.root")
    tfile = r.TFile("xs/v5/8TeV.root")
    
    xsSB = tfile.Get("stop_or_sbottom").Clone()
    xsSB.SetDirectory(0)
    tfile.Close()

    ranked = []
    for i, (x, label, val, err, n0, n1) in enumerate(cont):
        iBin = 1 + i
        poi.SetBinContent(iBin, val)
        poi.SetBinError(iBin, err)
        poiX.SetBinLabel(iBin, label)

        #print x,xsSB.FindBin(x),xsSB.GetBinContent(xsSB.FindBin(x))
        xsVal = xsSB.GetBinContent(xsSB.FindBin(x))
        if xsVal == 0. : continue
        poiR.SetBinContent(iBin, val / xsVal)
        poiR.SetBinError(iBin, err / xsVal)
        poiRX.SetBinLabel(iBin, label)

        rel.SetBinContent(iBin, val/err)
        relX.SetBinLabel(iBin, label)
        
        nllSigma0.SetBinContent(iBin, n0)
        nllSigma0X.SetBinLabel(iBin, label)
        
#        if label not in dict.keys() : dict[label] = odict
#        if mode == "bestFit_binaryExcl": 
#            odict["bin"] = i
#            odict["mu"] = val
#            odict["err"] = err
#            odict["nll0"] = n0
#            odict["nll1"] = n1
#            odict["th"] = xsVal
#            odict["abs(nll1)"] = abs(n1)
#        if mode == "CL" :
#            print "CL",i, x, label, val, err, n0, n1, xsVal, val/xsVal, err/xsVal, abs(n1)

        if n1 is not None and x >= 200. :
            ranked.append((i, x, label, val, err, n0, n1, xsVal, val/xsVal, err/xsVal, abs(n1)))

        #print "i, x, label, val, err, n0, n1, xsVal, val/xsVal, err/xsVal, n0(xs=0), n1(xs=1)"
        #print i, x, label, val, err, n0, n1, xsVal, val/xsVal, err/xsVal, n0, n1

        if mode == "bestFit_binaryExcl":
            nllSigma1.SetBinContent(iBin, n1)
            nllSigma1X.SetBinLabel(iBin, label)

        xs.SetBinContent(iBin, xsVal)
        xsX.SetBinLabel(iBin, label)

    ranked_sorted = sorted(ranked, key=itemgetter(-1), reverse=False)

    #ranked.append((i, x, label, val, err, n0, n1, xsVal, val/xsVal, err/xsVal, abs(n1)))
    #print "point={0:.0f} m_stop={1:.0f} label={2:s} xs/th={3:.2f}+/-{4:.2f} nll(0)={5:.2f} nll(1)={6:.2f} th={7:.2f}".format(*tuple)
#    for entry in ranked :
#        print nice(entry)
#        if entry[2] == "250 240" :
#            print nice(entry)

    if len(ranked_sorted) > 0 :
        #print ranked_sorted[0]
        #print ranked_sorted[1]
        print nice(ranked_sorted[0])
        print nice(ranked_sorted[1])


    if mode == "bestFit":
        return poi, poiR, rel, nllSigma0, xs
    elif mode == "bestFit_binaryExcl":
        return nllSigma1, poi, rel, nllSigma0, xs

def clbContents(label=""):
    hClb = oneHisto(label=label,   hName=""+model+"_CLb")
    hCls = oneHisto(label=label,   hName=""+model+"_CLs")
    hClsb = oneHisto(label=label,  hName=""+model+"_CLs+b")

    out = []
    if not all([hClb, hCls]):
        return out

    for (iBinX, x, iBinY, y, iBinZ, z) in utils.bins(hClb, interBin="Center"):
        if iBinZ != 1:
            continue

        t = (iBinX, iBinY, iBinZ)
        clb = hClb.GetBinContent(*t)
        cls = hCls.GetBinContent(*t)
        clsb = hClsb.GetBinContent(*t)
        if clb == 0.0:
            continue
        label = "%3d %3d" % (x, y)
        out.append((x, label, clb, cls, clsb))
    return out


def clPlots(label=""):
    cont = clbContents(label)
    nBins = len(cont)

    oneMinusCLb = r.TH1D("1-CLb", "%s;;1 - CL_{b}" % label, nBins, 0, nBins)
    oneMinusCLbX = oneMinusCLb.GetXaxis()

    hCls = r.TH1D("CLs", "%s;;CL_{s} = CL_{s+b} / CL_{b}" % label, nBins, 0, nBins)
    hClsX = hCls.GetXaxis()

    hClsb = r.TH1D("CLsb", "%s;;CL_{s+b}" % label, nBins, 0, nBins)
    hClsbX = hClsb.GetXaxis()

    oneMinusCLb_over_oneMinusCLsb = r.TH1D("1-CLb_over_1-CLsb", "%s;;(1 - CL_{b})  /  (1 - CL_{s+b})" % label, nBins, 0, nBins)
    oneMinusCLb_over_oneMInusCLsbX = oneMinusCLb_over_oneMinusCLsb.GetXaxis()

    for i, (x, label, clb, cls, clsb) in enumerate(cont):
        iBin = 1 + i
        oneMinusCLb.SetBinContent(iBin, 1.0 - clb)
        oneMinusCLbX.SetBinLabel(iBin, label)

        hCls.SetBinContent(iBin, cls)
        hClsX.SetBinLabel(iBin, label)

        hClsb.SetBinContent(iBin, clsb)
        hClsbX.SetBinLabel(iBin, label)

        oneMinusCLb_over_oneMinusCLsb.SetBinContent(iBin, (1.0 - clb) / (1.0 - clsb))
        oneMinusCLb_over_oneMInusCLsbX.SetBinLabel(iBin, label)

    return [hClsb, hCls, oneMinusCLb, oneMinusCLb_over_oneMinusCLsb]


def onePage(c, name="", label=""):
    if mode.startswith("bestFit"):
        hs = bestFitPlots(label)
    elif mode == "CL":
        hs = clPlots(label)
    else:
        assert False

    k = []
    line = r.TLine()

    for i, h in enumerate(hs):
        if i < 4:
            c.cd(1+i)
            h.Draw("p")
        elif mode == "bestFit":
            c.cd(1)
            h.SetLineColor(r.kRed)
            h.Draw("histsame")

        h.GetXaxis().SetLabelSize(2.0*h.GetXaxis().GetLabelSize())
        h.GetYaxis().SetLabelSize(1.5*h.GetYaxis().GetLabelSize())
        h.GetYaxis().SetTitleSize(2.0*h.GetYaxis().GetTitleSize())
        h.GetYaxis().SetTitleOffset(0.4)
        h.GetYaxis().CenterTitle()
        h.SetStats(False)
        h.SetMarkerColor(h.GetLineColor())
        h.SetMarkerStyle(20)
        h.SetMarkerSize(0.4 * h.GetMarkerSize())

        xMin = h.GetXaxis().GetXmin()
        xMax = h.GetXaxis().GetXmax()
        if mode.startswith("bestFit"):
            if i == 0 and mode == "bestFit_binaryExcl":
                h.SetMinimum(-4.0)
                yLine = 0.0
                k.append(line.DrawLine(xMin, yLine, xMax, yLine))
            if i:
                h.SetMinimum(0.0)
            if i == 1:
                h.SetMaximum(3.0)
                yLine = 1.0
                k.append(line.DrawLine(xMin, 1.0, xMax, 1.0))
        else:
            h.SetMinimum(0.0)
            h.SetMaximum(1.1)
            if i == 1:
                yLine = 0.05
                l2 = line.DrawLine(xMin, yLine, xMax, yLine)
                l2.SetLineColor(r.kRed)
                k.append(l2)
            if 2 <= i:
                h.SetMinimum(1.0e-2)
                h.SetMaximum(2.0)
                r.gPad.SetLogy()
                r.gPad.SetGridy()

        r.gPad.SetTopMargin(0.0)
        r.gPad.SetBottomMargin(0.17)
        r.gPad.SetTickx()
        r.gPad.SetTicky()

    c.cd(0)
    c.Print(name)
    return hs

def categories():
    #indiv = ["1b_le3j","1b_ge4j","0b_le3j","0b_ge4j"][:4]
    indiv = ["0b_le3j","0b_ge4j","1b_ge4j","1b_le3j"][:4]
    out = []
    out += ["_".join(indiv)]
    return out


def pdf(fileName=""):
    c = r.TCanvas()
    c.Divide(1, 4)

    c.Print("%s[" % fileName)
    
    for cat in categories():
        hs = onePage(c, name=fileName, label=cat)

    c.Print("%s]" % fileName)
    print fileName
    #os.system("cp -p %s ~/public_html/tmp/" % fileName)
    return hs

if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("e")

    # globals; used in oneHisto()
    #subdirs = ["non-universal-syst", "universal-syst-0b-le3j", "universal-syst-0b-ge4j"]
    #subdirs = ["."]
    subdirs = [".",
               #"sigVsMass/"+model+"/data",
               #"sigVsMass/"+model+"/blind-sig-inj",
               #"sigVsMass/"+model+"/blind",
               #"sigVsMass/"+model+"/semiblind",
               #"sigVsMass/"+model+"/semiblind-sig-inj",
               ][0:1]

    modes = ["bestFit", "bestFit_binaryExcl", "CL"][:3]

    dict = odict()
    for mode in modes:
        for subDir in subdirs:
            #hs = pdf(fileName="plots/%s/%s%s.pdf" % (dir, mode.replace("binaryExcl", "xsNom"), "_"+subDir if subDir != "." else ""))
            hs = pdf(fileName="plots/%s/%s/%s.pdf" % (dir, subDir if subDir != "." else "", mode.replace("binaryExcl", "xsNom")))
            dict[mode,subDir] = hs


    points = []
    for key,val in dict.items() :
        for entry in val :
            for ibin in range(1,entry.GetXaxis().GetNbins()+1) :
                points.append(entry.GetXaxis().GetBinLabel(ibin))
    points = sorted(list(set(points)))
    print len(points),points

    if 0 :
        for subDir in subdirs:
            for point in points : 
                for mode in modes :
                    for histo in dict[mode,subDir] :
                        print point,mode,\
                              histo.GetName(),\
                              histo.GetBinContent(histo.GetXaxis().FindBin(point)),\
                              histo.GetBinError(histo.GetXaxis().FindBin(point))

    def content(dict,mode,dir,name,point):
        if (mode,dir) not in dict.keys() : return None
        try:
            index = [ his.GetName() for his in dict[mode,dir] ].index(name) 
        except ValueError:
            return None
        his = dict[mode,dir][index]
        return his.GetBinContent(his.GetXaxis().FindBin(point)),his.GetBinError(his.GetXaxis().FindBin(point))

    all = odict()
    for point in points : 
        d = odict()
        d["ul_obs"] = content(dict,modes[0],subdirs[0],"poi",point)
        d["th_obs"] = content(dict,modes[0],subdirs[0],"xs",point)
        d["mu_obs"] = content(dict,modes[1],subdirs[0],"poi",point)
        d["nll0_obs"] = content(dict,modes[1],subdirs[0],"nllSigma0",point)
        d["nll1_obs"] = content(dict,modes[1],subdirs[0],"nllSigma1",point)
        d["cls_obs"] = content(dict,modes[2],subdirs[0],"CLs",point)
        d["1-clb_obs"] = content(dict,modes[2],subdirs[0],"1-CLb",point)
        d["clsb_obs"] = content(dict,modes[2],subdirs[0],"CLsb",point)
        d["ul_exp"] = content(dict,modes[0],subdirs[1],"poi",point)
        d["th_exp"] = content(dict,modes[0],subdirs[1],"xs",point)
        d["mu_exp"] = content(dict,modes[1],subdirs[1],"poi",point)
        d["nll0_exp"] = content(dict,modes[1],subdirs[1],"nllSigma0",point)
        d["nll1_exp"] = content(dict,modes[1],subdirs[1],"nllSigma1",point)
        d["cls_exp"] = content(dict,modes[2],subdirs[1],"CLs",point)
        d["1-clb_exp"] = content(dict,modes[2],subdirs[1],"1-CLb",point)
        d["clsb_exp"] = content(dict,modes[2],subdirs[1],"CLsb",point)
        if d["cls_obs"][0] < 0.05 or d["cls_obs"][0] == 1.00 :
            print "Excluded!",point
        elif d["clsb_exp"] == 0.50 : 
            print "No sensitivity!",point
        else :
            print "Ok!",point
            #if d["cls_obs"][0] > 0.05 and d["cls_obs"][0] < 1.00 :
            all[point] = d

        #if d["cls"] > 0.05 :#and d["cls"] < 1.00 :
        #print point
        #for key,val in d.items() :
        #print "{:4s}, {:4.2f} +/- {:4.2f}".format(key,val[0],val[1])

    #for point,entry in all.items() :
    #    print point
    #    for param,val in entry.items() :
    #        print "{:4s}, {:4.2f} +/- {:4.2f}".format(param,val[0],val[1])

    ranked = odict( sorted( all.items(), key = lambda x : abs(x[1]["nll1_obs"][0]) ) )

    print "len",len(ranked.items())

    #for point,entry in all.items():#[:5] :
    for point,entry in ranked.items()[:5] :
        print point
        for param,val in entry.items() :
            print "{:4s}, {:4.2f} +/- {:4.2f}".format(param,val[0],val[1])



        #ranked.append((i, x, label, val, err, n0, n1, xsVal, val/xsVal, err/xsVal, abs(n1)))
        #print "point={0:.0f} m_stop={1:.0f} label={2:s} xs/th={3:.2f}+/-{4:.2f} nll(0)={5:.2f} nll(1)={6:.2f} th={7:.2f}".format(*tuple)

    #    if mode == "bestFit": return poi, poiR, rel, nllSigma0, xs
    #    elif mode == "bestFit_binaryExcl": return nllSigma1, poi, rel, nllSigma0, xs
