import ROOT as r
import numpy as np
import math
import os
from collections import OrderedDict

################################################################################
# Config

r.gROOT.SetBatch(True)

dir_in = "input"
dir_out = "plots"

models = [("T2cc","v33"),("T2_4body","v9"),("T2tt","v7_v1"),("T2bw_0p25","v1"),("T2bw_0p75","v2"),][2:] # does work for T2cc, T2_4body

smooth = ["average","ave_wei","quantile"][1]

################################################################################
# Methods

def draw_options(model) :
    return "colz text" if ( model == "T2cc" or model == "T2_4body" ) else "colz"

def dir_input(model,version) :
    return dir_in+"/"+model+"/"+version+"/"

def dir_output(model,version) :
    dir = dir_out+"/"+model+"/"+version+"/"
    if not os.path.exists(dir): os.makedirs(dir)
    return dir

def name_input(model) : 
    return model+"_"+version+"_systematics"

def name_output(model) :
    return  model+"_smoothed"


def unpack(histo) :
    yields = OrderedDict()
    for xbin in range( histo.GetNbinsX() ) :
        for ybin in range( histo.GetNbinsY() ) :
            xval = histo.GetXaxis().GetBinCenter( xbin+1 )
            yval = histo.GetYaxis().GetBinCenter( ybin+1 )
            val = histo.GetBinContent( xbin+1, ybin+1 )
            if val > 0. : 
                if (xval,yval) not in yields.keys() : yields[(xval,yval)] = val
                else : print "problem, already unpacked bin!",xval,yval,val
    return yields

def delta_m(unpacked) :
    yields = OrderedDict()
    for key,val in unpacked.items() : 
        if key[1] < 0. : continue
        dm = key[0] - key[1]
        if dm not in yields.keys() : yields[dm] = OrderedDict()
        yields[dm][key] = val
    return OrderedDict(sorted( yields.items()))

def iterate(his_input,xbin,ybin,width,
            his_output,
            weighted,nadjacent,attempts,nattempts=6) :
    vals = []
    errs = []
    for itmp in range(-1*(2**attempts)*nadjacent,(2**attempts)*nadjacent+1) :
        vtmp = his_input.GetBinContent( xbin+itmp, ybin+itmp*width ) 
        xtmp = his_input.GetXaxis().GetBinCenter( xbin+itmp )
        ytmp = his_input.GetYaxis().GetBinCenter( ybin+itmp*width )
        events = mc_stats.get((xtmp,ytmp),0)
        #print itmp,xbin+itmp,ybin+itmp*width,xtmp,ytmp,vtmp,events
        if vtmp > 0. and events > 0 : 
            vals.append(vtmp)
            errs.append(events)
    nevents = sum(errs)
    errs = [ x/nevents for x in errs ]
    if nevents >= 10. :
        ave = np.average(vals,weights=errs) if weighted else np.average(vals) 
        his_output.SetBinContent( xbin, ybin, ave )
        #print "OK!",attempts,xbin,ybin,nevents,(2**attempts)*nadjacent,len(vals),ave
        return -1
    else :
        if attempts >= nattempts : 
            if nevents > 0. :
                ave = np.average(vals)
                his_output.SetBinContent( xbin, ybin, ave )
                #print "LAST ATTEMPT",attempts,xbin,ybin,nevents,(2**attempts)*nadjacent,len(vals),ave
                return -1
            else :
                #print "NO EVENTS!",attempts,xbin,ybin,nevents,(2**attempts)*nadjacent,len(vals)
                return -1
        else : 
            #print "ATTEMPT",attempts,xbin,ybin,nevents,(2**attempts)*nadjacent,len(vals)
            return attempts+1

def average(his_input,his_output,mc_stats,nadjacent=2,weighted=False) :
    for xbin in range( 1, his_input.GetNbinsX()+1 ) :
        for ybin in range( 1, his_input.GetNbinsY()+1 ) :
            if ybin > xbin : continue

            xval = his_input.GetXaxis().GetBinCenter( xbin )
            yval = his_input.GetYaxis().GetBinCenter( ybin )
            val = his_input.GetBinContent( xbin, ybin )
            err = his_input.GetBinError( xbin, ybin )
            xwidth = his_input.GetXaxis().GetBinWidth(xbin)
            ywidth = his_input.GetYaxis().GetBinWidth(ybin)
            width = ( int(xwidth) / int(ywidth) ) if int(ywidth) > 0 else 1

            #if val <= 0. : continue

#            if xval == 725.0 and yval == 625.0 : 
#                print "POINT",xbin,ybin,xval,yval,val,err
#            else : continue 

            attempts = 0
            while attempts >= 0 : 
                attempts = iterate(his_input,xbin,ybin,width,
                                   his_output,
                                   weighted,nadjacent,attempts)

#            vals = []
#            errs = []
#            for itmp in range(-1*nadjacent,nadjacent+1) :
#                vtmp = his_input.GetBinContent( xbin+itmp, ybin+itmp*width ) 
#                xtmp = his_input.GetXaxis().GetBinCenter( xbin+itmp )
#                ytmp = his_input.GetYaxis().GetBinCenter( ybin+itmp*width )
#                events = mc_stats.get((xtmp,ytmp),0)
#                print itmp,xbin+itmp,ybin+itmp*width,xtmp,ytmp,vtmp,events
#                if vtmp > 0. and events > 0 : 
#                    vals.append(vtmp)
#                    errs.append(events)
#
#                nevents = sum(errs)
#                errs = [ x/nevents for x in errs ]
#                if nevents >= 10. : #len(vals) >= nadjacent :
#                    ave = np.average(vals,weights=errs) if weighted else np.average(vals) 
#                    his_output.SetBinContent( xbin, ybin, ave )
#                    print "OK",xval,yval,len(vals),ave
#
#            else : 
#                vals = []
#                errs = []
#                factor = 5
#                for itmp in range(-1*factor*nadjacent,factor*nadjacent+1) :
#                    vtmp = his_input.GetBinContent( xbin+itmp, ybin+itmp*width ) 
#                    xtmp = his_input.GetXaxis().GetBinCenter( xbin+itmp )
#                    ytmp = his_input.GetYaxis().GetBinCenter( ybin+itmp*width )
#                    if vtmp > 0. : vals.append(vtmp)
#
#                if len(vals) >= 1 :
#                    ave = np.average(vals) 
#                    his_output.SetBinContent( xbin, ybin, ave )
#                    print "PROB",xval,yval,len(vals),ave

def quantile(his_input,his_output,mc_stats,q=0.68) :
    unpacked = delta_m( unpack(his_input) )
    #print unpacked.keys()
    quantiles = OrderedDict()
    for dm,points in unpacked.items() :
        #print dm,points
        vals = []
        for point,eff in points.items() : 
            events = mc_stats.get(point,None)
            if events is not None : vals += [eff]*int(events)
            #else : print "Problem extracting number of events!",point,events
            #print point,eff,events
        index = int(len(vals)*q)
        quantiles[dm] = vals[index] if len(vals) > 0 else 0.
        #print quantiles[dm]
        for point,eff in points.items() : 
            xbin = his_output.GetXaxis().FindBin( point[0] )
            ybin = his_output.GetYaxis().FindBin( point[1] )
            his_output.SetBinContent( xbin, ybin, quantiles[dm] )

def distribution(his_input) :
    distr = r.TH1F(his_input.GetName()+"_1d",his_input.GetTitle()+"_1d",200,0.,2.)
    for xbin in range( 1, his_input.GetNbinsX()+1 ) :
        for ybin in range( 1, his_input.GetNbinsY()+1 ) :
            val = his_input.GetBinContent( xbin, ybin )
            err = his_input.GetBinError( xbin, ybin )
            if val > 0. : distr.Fill(val,1.) # 1./err**2) 
    return distr

def unweighted(model,version,njet,bjet,nhtbins=2,relative=False) :
    r.gStyle.SetOptStat(0)
    bins = [
        ("73.3","0.65","200_275"),
        ("73.3","0.6","275_325"),
        ("86.7","0.55","325_375"),
        ("100.0","0.55","375_475"),
        ]
    yields = OrderedDict()
    axes = None
    for ibin,(x,y,z) in enumerate(bins) :
        file_effs = "sigScan_"+model+"_had_2012_"+x+"_bt0.0_MChi-1.0"
        dir_effs = "smsScan_"+njet+"_"+bjet+"_AlphaT"+y+"_"+z
        name_effs = "m0_m12_mChi_noweight"
        file_effs = r.TFile(dir_input(model,version)+file_effs+".root","READ")
        file_effs.cd()
        his_effs = file_effs.Get(dir_effs+"/"+name_effs)
        his_effs_2d = his_effs.Project3D("yx")
        name_effs = "mc_stats_"+model+"_"+njet+"_"+bjet+"_"+z
        his_effs_2d.SetName(name_effs)
        his_effs_2d.SetTitle(name_effs)
        vals = unpack(his_effs_2d)
        for key,val in vals.items() :
            xbin = his_effs_2d.GetXaxis().FindBin(key[0])
            ybin = his_effs_2d.GetYaxis().FindBin(key[1])
            if val > 0. : 
                if ibin < nhtbins : # First three bins (200 < HT < 375)
                    if key not in yields.keys() : yields[key] = 0.
                    yields[key] += val
            if relative : 
                r.gStyle.SetPaintTextFormat("4.2f")
                his_effs_2d.SetBinContent( xbin, ybin, math.sqrt(val)/val )
                his_effs_2d.GetZaxis().SetRangeUser(0.,0.5)
#        for xbin in range( his_effs_2d.GetNbinsX() ) :
#            for ybin in range( his_effs_2d.GetNbinsY() ) :
#                xval = his_effs_2d.GetXaxis().GetBinCenter( xbin+1 )
#                yval = his_effs_2d.GetYaxis().GetBinCenter( ybin+1 )
#                val = his_effs_2d.GetBinContent( xbin+1, ybin+1 )
#                if val > 0. : 
#                    if ibin <= 2 : # First three bins (200 < HT < 375)
#                        if (xval,yval) not in yields.keys() : yields[(xval,yval)] = 0.
#                        yields[(xval,yval)] += val
#                    if relative : 
#                        r.gStyle.SetPaintTextFormat("4.2f")
#                        his_effs_2d.SetBinContent( xbin+1, ybin+1, math.sqrt(val)/val )
#                        his_effs_2d.GetZaxis().SetRangeUser(0.,0.5)
        c1 = r.TCanvas()
        his_effs_2d.Draw(draw_options(model))
        c1.SaveAs(dir_output(model,version)+his_effs_2d.GetName()+".pdf")
    #print model,njet,bjet,len(yields.keys()),yields
    return yields

################################################################################
# Execute

for (model,version) in models :

    file_input = r.TFile(dir_input(model,version)+name_input(model)+".root","READ")
    file_output = r.TFile(dir_output(model,version)+name_output(model)+".root","RECREATE")

    c = r.TCanvas()

    for x,y in [
        ("eq0b","le3j"),
        ("eq1b","le3j"),
        ("eq2b","le3j"),
        ("eq0b","ge4j"),
        ("eq1b","ge4j"),
        ("eq2b","ge4j"),
        ("eq3b","ge4j"),
        ] :

        mc_stats = unweighted(model=model,version=version,njet=x,bjet=y,nhtbins=2)

        file_input.cd()
        his_name = "total_"+model+"_"+x+"_"+y+"_incl" 
        his_input = file_input.Get(his_name)
        his_input.SetName(his_name)
        his_input.SetTitle(his_name)
        his_input.Draw(draw_options(model))
        c.SaveAs(dir_output(model,version)+his_input.GetName()+".pdf")

        distr_input = distribution(his_input)
        #distr_input.GetXaxis().SetRangeUser(0.9*his_input.GetMinimum(1.e-6),1.1*his_input.GetBinContent(his_input.GetMaximumBin()))
        distr_input.GetXaxis().SetRangeUser(0.,1.)
        distr_input.Draw()
        c.SaveAs(dir_output(model,version)+distr_input.GetName()+".pdf")

        his_output = his_input.Clone()

        if   smooth == "average" : average(his_input,his_output,mc_stats,nadjacent=2,weighted=False)
        elif smooth == "ave_wei" : average(his_input,his_output,mc_stats,nadjacent=2,weighted=True)
        elif smooth == "quantile" : quantile(his_input,his_output,mc_stats)
        else : print "problem with smooth method!",smooth

        his_output.SetName(his_output.GetName()+"_smoothed_"+smooth)
        his_output.SetTitle(his_output.GetTitle()+"_smoothed_"+smooth)

        #his_output.GetZaxis().SetRangeUser(0.,0.5)
        his_output.Draw(draw_options(model))
        c.SaveAs(dir_output(model,version)+his_output.GetName()+".pdf")

        distr_output = distribution(his_output)
        #distr_output.GetXaxis().SetRangeUser(0.9*his_output.GetMinimum(1.e-6),1.1*his_output.GetBinContent(his_output.GetMaximumBin()))
        distr_output.GetXaxis().SetRangeUser(0.,1.)
        distr_output.Draw()
        c.SaveAs(dir_output(model,version)+distr_output.GetName()+".pdf")

        his_ratio = his_output.Clone()
        his_ratio.Divide(his_output,his_input)
        his_ratio.SetName(his_input.GetName()+"_ratio")
        his_ratio.SetTitle(his_input.GetTitle()+"_ratio")
        his_ratio.GetZaxis().SetRangeUser(0.5,1.5)
        his_ratio.Draw(draw_options(model))
        c.SaveAs(dir_output(model,version)+his_ratio.GetName()+".pdf")

        distr_ratio = distribution(his_ratio)
        #distr_ratio.GetXaxis().SetRangeUser(0.9*his_ratio.GetMinimum(1.e-6),1.1*his_ratio.GetBinContent(his_ratio.GetMaximumBin()))
        distr_ratio.GetXaxis().SetRangeUser(0.5,1.5)
        distr_ratio.Draw()
        c.SaveAs(dir_output(model,version)+distr_ratio.GetName()+".pdf")

        file_output.cd()
        his_output.SetName(his_name)
        his_output.Write()
