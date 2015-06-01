import operator
import ROOT as r
from collections import OrderedDict
import os.path
import pprint
import numpy as np
import bisect
pp = pprint.PrettyPrinter(indent=4)

################################################################################
# Config

dir_in = "input"
dir_out = "plots"

models = [("T2tt","v9","frequentist"),
          ("T2cc","v32_v1","asymptotic"),
          ("T2_4body","v4_534","asymptotic"),
          ("T2bw_0p25","v3","asymptotic"),
          ("T2bw_0p75","v4","asymptotic"),
          ][:]

cats = OrderedDict([
        (0,"0b_le3j"),
        (1,"1b_le3j"),
        (2,"2b_le3j"),
        (3,"0b_ge4j"),
        (4,"1b_ge4j"),
        (5,"2b_ge4j"),
        (6,"3b_ge4j"),
#        (7,"ge4b_ge4j"),
        ])

r.gROOT.SetBatch(True)
r.gStyle.SetPaintTextFormat("1.0f")
r.gStyle.SetOptStat(0)

################################################################################
# Methods

def dir_input(model,version) :
    return dir_in+"/"+model+"/"+version+"/"

def dir_output(model,version) :
    dir = dir_out+"/"+model+"/"+version+"/"
    if not os.path.exists(dir): os.makedirs(dir)
    return dir

def extract_upper_limits( model, version, limit, categories ) :
    axes = None
    output = OrderedDict()
    for icat,cat in categories.items() : 
        name = dir_input(model,version)+cat+"/CLs_"+limit+"_"+model+"_2012dev_"+cat+"_xsLimit.root"
        if not os.path.isfile(name) : 
            print "Error:",name
            continue
        file = r.TFile(name)
        if file.IsZombie() : 
            print "Error:",name
            continue
        input = file.Get(model+"_ExpectedUpperLimit")
        print "Opened",name
        axes = ( input.GetXaxis().GetNbins(), input.GetXaxis().GetXmin(), input.GetXaxis().GetXmax(),
                 input.GetYaxis().GetNbins(), input.GetYaxis().GetXmin(), input.GetYaxis().GetXmax() )
        for xbin in range( input.GetNbinsX()+2 ) :
            for ybin in range( input.GetNbinsY()+2 ) :
                if input.GetBinContent( xbin, ybin ) > 0. : 
                    hack = {"T2tt":(25,25)}.get(model,(0,0))
                    key = ( int(input.GetXaxis().GetBinCenter(xbin)), int(input.GetYaxis().GetBinCenter(ybin)) )
                    #key = ( int(input.GetXaxis().GetBinLowEdge(xbin))+hack[0], int(input.GetYaxis().GetBinLowEdge(ybin))+hack[1] )
                    #key = ( input.GetXaxis().GetBinCenter(xbin+1), input.GetYaxis().GetBinCenter(ybin+1) )
                    value = input.GetBinContent(xbin,ybin)
                    if key not in output.keys() : output[key] = OrderedDict()
                    output[key][icat] = round(value,2)
    #pp.pprint(dict(output))
    return output,axes

def define_regions( input, mass_thresholds = [], dm_thresholds = [] ) :
    # { (m_stop,dM), [(m_stop,m_LSP), ...] } 
    mass_thresholds = sorted(mass_thresholds)
    dm_thresholds = sorted(dm_thresholds)
    output = OrderedDict()
    for key in input.keys() : 
        if key[1] < 0. : continue
        # m_stop key
        m_stop = 0.
        if len(mass_thresholds) > 0 :
            index1 = bisect.bisect(mass_thresholds,key[0]) - 1
            m_stop = 0. if index1 < 0 else mass_thresholds[index1]
        # dm key
        dm = key[0] - key[1]
        m_delta = dm
        if len(dm_thresholds) > 0 :
            index2 = bisect.bisect(dm_thresholds,dm) - 1
            m_delta = 0. if index2 < 0 else dm_thresholds[index2]
        if (m_stop,m_delta) not in output.keys() : output[(m_stop,m_delta)] = []
        output[(m_stop,m_delta)].append(key)
    return output

def no_regions( input ) : 
    # { (m_stop,dM), [(m_stop,m_LSP)] } 
    output = OrderedDict()
    for entry in input.keys() : output[entry] = [entry] 
    return output

def plot_regions( model, version, axes, input ) :
    print input
    nregions = len(input.keys())
    colours = np.array( range(2,2+nregions), dtype=np.int32 )
    r.gStyle.SetPalette(nregions,colours)
    r.gStyle.SetNumberContours(nregions)
    histo = r.TH2D( "Regions_Map",
                    "Regions_Map",
                    axes[0],axes[1],axes[2],axes[3],axes[4],axes[5] )
    for ikey,(key,val) in enumerate(input.items()) : 
        for point in val : histo.Fill( point[0], point[1], ikey+0.1 )
    c = r.TCanvas(dir_output(model,version)+"Regions")
    histo.Draw("colztext")
    histo.GetZaxis().SetRangeUser(0.,nregions*1.)
    c.SaveAs(dir_output(model,version)+model+"_"+version+"_"+"Regions.pdf")

def rank_per_point( upper_limits ) :
    # dict entry: (m_stop,m_LSP):[(cat,xs),...] where index in list is rank 
    output = OrderedDict()
    for key,val in upper_limits.items() :
        rank = sorted( val.items(), key = lambda x : x[1] ) 
        output[key] = rank
    #for key,val in output.items() : print key,val
    return output

def rank_per_region( regions, upper_limits ) :
    # dict entry: (m_stop,m_LSP):[(cat,counts),...] where index in list is rank
    input = rank_per_point( upper_limits )
    output = OrderedDict()
    for region,points in regions.items() :
        if len(points) > 0 : 
            #print "region",region,"Npoints",len(points)
            counts = OrderedDict() 
            for point in points :
                #print "point",point
                if point not in input.keys() : 
                    print "problem",point,input.keys()
                    continue
                for irank,rank in enumerate(input[point]) :
                    cat = rank[0]
                    if cat not in counts.keys() : counts[cat] = 0.
                    counts[cat] += (8.-irank)
            ranking = sorted( counts.items(), key = lambda x : x[1], reverse=True )  
            for point in points : output[point] = ranking
            #print "region=",region,"ranking=",ranking
            print "region=",region,"ranking=",[ cats[x[0]] for x in ranking ]
    return output

def create_rank_plots( model, version, categories, axes, input, region = True ) :
    title = model + "_" + version + "_CatPer"+("Region" if region else "Point")+"ForRank"
    colours = np.array( range(2,len(categories.keys())+2), dtype=np.int32 )
    r.gStyle.SetPalette(len(categories.keys()),colours)
    r.gStyle.SetNumberContours(len(categories.keys()))
    for irank in range( len(categories) ) : 
        #if irank not in categories.keys() : continue
        histo = r.TH2D(title+str(irank), title+str(irank),axes[0],axes[1],axes[2],axes[3],axes[4],axes[5])
        #for icat in range( len(categories) ) : histo.GetZaxis().SetBinLabel(icat,categories[icat])
        #axis = histo.FindObject("palette").GetAxis()
        #for x,y in catnum.items() : axis.SetBinLabel(y+1,x)
        for key,val in input.items() :
            if irank >= len(val) : continue
            #print key[0],key[1],irank,val[irank]
            histo.Fill( key[0], key[1], val[irank][0]+0.1 )
        c = r.TCanvas(title+str(irank))
        histo.Draw("colztext")
        histo.GetZaxis().SetRangeUser(0.,len(categories)*1.)
        txt = []
        for key,val in categories.items() :
            txt.append( r.TText((0.12+0.09*key),0.86,val) )
            txt[-1].SetNDC()
            txt[-1].SetTextSize(0.035)
            txt[-1].SetTextColor(int(colours[key]))
            txt[-1].Draw()
        c.SaveAs(dir_output(model,version)+title+str(irank)+".pdf")

def create_category_plots( model, version, categories, axes, input, ncats = 0, region = True ) :
    title = model + "_" + version + "_RankPer"+("Region" if region else "Point")+"ForCat"
    colours = np.array( range(2,len(categories.keys())+2), dtype=np.int32 )
    #colours = np.array( [ r.kGreen+x for x in range(len(categories.keys())) ], dtype=np.int32 )
    r.gStyle.SetPalette(len(categories.keys()),colours)
    r.gStyle.SetNumberContours(len(categories.keys()))
    for icat,cat in categories.items() : 
        histo = r.TH2D(title+str(icat)+"_"+cat,title+str(icat)+"_"+cat,axes[0],axes[1],axes[2],axes[3],axes[4],axes[5])
        for point,cats in input.items() :
            ranks = [ x[0] for x in cats ]
            rank = ranks.index(icat) if icat in ranks else len(categories.keys())
            #print icat,cat,point,cats,rank
            if rank < ncats : histo.Fill( point[0], point[1], rank+0.1 )
        c = r.TCanvas(title+str(icat)+"_"+cat)
        histo.Draw("colztext")
        histo.GetZaxis().SetRangeUser(0.,len(categories)*1.)
        c.SaveAs(dir_output(model,version)+title+str(icat)+"_"+cat+".pdf")

def create_rank_map( model, version, axes, input, ncats=None ) :
    values = []
    output = OrderedDict()
    for key1,val1 in input.items() :
        #print key1,val1
        value = 0
        for cat in val1[:ncats] : 
            #print cat
            value = value | (1<<cat[0])
        #print key1,value
        output[key1] = value
        if value not in values : values.append(value)
    text = []
    for val in sorted(values,reverse=True) :
        temp = str(val) + ":   "
        for bit in range(8) :
            if val&(1<<bit) > 0 : temp += (cats[bit] + " ")
        text.append(temp)

    #print input
    #print output
    print values
    #print text

    #colours = np.array( range(2,10), dtype=np.int32 )
    #r.gStyle.SetPalette(8,colours)
    #r.gStyle.SetNumberContours(len(cats))

    r.gStyle.SetPalette(1)
    r.gStyle.SetNumberContours(256)
    file = r.TFile(dir_output(model,version)+model+"_"+version+"_"+"Map_"+str(ncats)+"_Highest_Ranked_Categories"+".root","RECREATE")
    file.cd()
    histo = r.TH2D( "Ranking_Map",
                    "Ranking_Map",
                    axes[0],axes[1],axes[2],axes[3],axes[4],axes[5] )
    for key,val in output.items() : histo.Fill( key[0], key[1], val+0.1 )
    c = r.TCanvas(dir_output(model,version)+model+"_"+version+"_"+"Map_"+str(ncats)+"_Highest_Ranked_Categories")
    histo.Draw("colztext")
    histo.GetZaxis().SetRangeUser(0.,256.)
    pave = r.TPaveText()
    pave.SetTextSize(0.035)
    pave.SetFillColor(0)
    pave.SetLineColor(0)
    pave.SetBorderSize(0)
    pave.SetX1NDC(0.12)
    pave.SetY1NDC(0.88-(0.05)*len(text))
    pave.SetX2NDC(0.5)
    pave.SetY2NDC(0.88)
    for txt in text : pave.AddText(txt)
    pave.Draw()
    c.SaveAs(dir_output(model,version)+model+"_"+version+"_"+"Map_"+str(ncats)+"_Highest_Ranked_Categories"+".pdf")
    #c.SaveAs(dir_output(model,version)+model+"_"+version+"_"+"Map_"+str(ncats)+"_Highest_Ranked_Categories"+".root")
    file.Write()
    file.Close()

################################################################################
# Obsolete methods

#def rank_categories_per_mass_point( input ) :
#    # dict entry: (m_stop,m_LSP):[(cat,xs),...] 
#    output = OrderedDict()
#    for key,val in input.items() :
#        rank = sorted( val.items(), key = lambda x : x[1] ) # sorted( val.iteritems(), key = operator.itemgetter(1) )
#        output[key] = rank
#    #for key,val in output.items() : print key,val
#    return output
#
#def majority_rank_vs_delta_m( input ) : 
#    output = OrderedDict()
#    for key,val in ranked.items() : 
#        if key[1] < 0. : continue
#        dm = key[0] - key[1]
#        if dm not in output.keys() : output[dm] = OrderedDict()
#        output[dm][key] = val
#    return OrderedDict( sorted(output.items()) )
#
#def region( input, mass_threshold, below ) :
#    output = OrderedDict()
#    for key1,val1 in input.items() :
#        output[key1] = OrderedDict()
#        for key2,val2 in val1.items() :
#            if ( key2[0] >= mass_threshold and below ) or ( key2[0] < mass_threshold and not below ) : continue
#            output[key1][key2] = val2
#    return output
#
#def print_region( input ) :
#    for key1,val1 in input.items() :
#        if len(val1.keys()) : print "dm",key1,"bins",len(val1.keys())
#        for key2,val2 in val1.items() :
#            print "key=",key2,"Nvals=",len(val2),"vals=",val2
#
#def rank_regions( input ) :
#    # dict entry: (m_stop,m_LSP):[(cat,counts),...] where index in list is rank
#    output = OrderedDict()
#    for key1,val1 in input.items() :
#        if len(val1.keys()) : 
#            #print "dm",key1,"bins",len(val1.keys())
#            counts = OrderedDict() 
#            for key2,val2 in val1.items() :
#                #print "mass",key2,len(val2),val2
#                for irank,rank in enumerate(val2) :
#                    cat = rank[0]
#                    #print "cat/xs",rank
#                    if cat not in counts.keys() : counts[cat] = 0
#                    counts[cat] += (8-irank)
#            #print "dm=",key1,"cats=",sorted( counts.items(), key = lambda x : x[1], reverse=True ) 
#            for key2,val2 in val1.items() :
#                output[key2] = sorted( counts.items(), key = lambda x : x[1], reverse=True )  
#
#    #quit()
#    return output

################################################################################
# Execute

if __name__ == '__main__':

    for (model,version,limit) in models :

        # Extract upper limits for each mass point and category
        upper_limits,axes = extract_upper_limits(model=model,version=version,limit=limit,categories=cats)

        points = no_regions( input=upper_limits )
        ranking_per_point = rank_per_region( regions=points, upper_limits=upper_limits ) 
        ranking_per_point_2 = rank_per_point( upper_limits=upper_limits ) #@@ same as above

        # Coarse (true) or fine (false) regions?
        regions = None
        if 1 : regions = define_regions( input=upper_limits, mass_thresholds=[350.,700.], dm_thresholds=[150.] )
        else : regions = define_regions( input=upper_limits, mass_thresholds=[350.,500.,700.], dm_thresholds=[ 100.+x*25. for x in range(50) ] )

        ranking_per_region = rank_per_region( regions=regions, upper_limits=upper_limits )

        if False :
            print "points:"
            pp.pprint(dict(points))
            print "regions:"
            pp.pprint(dict(regions))
            print "ranking_per_point:"
            pp.pprint(dict(ranking_per_point))
            print "ranking_per_region:"
            pp.pprint(dict(ranking_per_region))

        plot_regions( model=model, version=version, axes=axes, input=regions )

        create_category_plots(model=model,version=version,categories=cats,axes=axes,input=ranking_per_point,ncats=6,region=False)
        create_category_plots(model=model,version=version,categories=cats,axes=axes,input=ranking_per_region,ncats=6,region=True)

        create_rank_plots(model=model,version=version,categories=cats,axes=axes,input=ranking_per_point,region=False)
        create_rank_plots(model=model,version=version,categories=cats,axes=axes,input=ranking_per_region,region=True)

        create_rank_map(model=model,version=version,axes=axes,input=ranking_per_region,ncats=4) 
        create_rank_map(model=model,version=version,axes=axes,input=ranking_per_region,ncats=5) 
        create_rank_map(model=model,version=version,axes=axes,input=ranking_per_region,ncats=6) 
