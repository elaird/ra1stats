import operator
import ROOT as r
from collections import OrderedDict
import os.path
import pprint
import numpy as np
pp = pprint.PrettyPrinter(indent=4)

model,version = [("T2cc","v32_v1"),("T2tt","v7"),("T2_4body","v4_534"),("T2bw_0p25","v3"),("T2bw_0p75","v4"),][4]

cats = OrderedDict([
        (0,"0b_le3j"),
        (1,"1b_le3j"),
        (2,"2b_le3j"),
        (3,"0b_ge4j"),
        (4,"1b_ge4j"),
        (5,"2b_ge4j"),
        (6,"3b_ge4j"),
        (7,"ge4b_ge4j"),
        ])

r.gStyle.SetPaintTextFormat("1.0f")
r.gStyle.SetOptStat(0)
colours = np.array( range(2,10), dtype=np.int32 )
r.gStyle.SetPalette(8,colours)
r.gStyle.SetNumberContours(len(cats))

# Extract upper limits for each mass point and category

output = OrderedDict()
for icat,cat in cats.items() : 
    name = "input/"+model+"/"+version+"/"+cat+"/CLs_asymptotic_"+model+"_2012dev_"+cat+"_xsLimit.root"
    if not os.path.isfile(name) : continue
    file = r.TFile(name)
    if file.IsZombie() : continue
    print type(file)
    input = file.Get(model+"_ExpectedUpperLimit")
    print type(input)
    for xbin in range( input.GetNbinsX() ) :
        for ybin in range( input.GetNbinsY() ) :
            if input.GetBinContent( xbin+1, ybin+1 ) > 0. : 
                key = ( int(input.GetXaxis().GetBinLowEdge(xbin+1)), int(input.GetYaxis().GetBinLowEdge(ybin+1)) )
                value = input.GetBinContent(xbin+1,ybin+1)
                if key not in output.keys() : output[key] = OrderedDict()
                output[key][icat] = round(value,2)
pp.pprint(dict(output))

# Rank categories for each mass point

ranked = OrderedDict()
for key,val in output.items() :
    rank = sorted( val.iteritems(), key = operator.itemgetter(1) ) #[ x[0] for x in sorted( val.iteritems(), key = operator.itemgetter(1) ) ]
    ranked[key] = rank
pp.pprint(dict(ranked))

# Plot category rank for each mass point

for irank in range( len(cats) ) : 
    #if irank not in cats.keys() : continue
    histo = r.TH2D(model+"_Rank"+str(irank),
                   model+"_Rank"+str(irank),
                   input.GetXaxis().GetNbins(),
                   input.GetXaxis().GetXmin(),
                   input.GetXaxis().GetXmax(),
                   input.GetYaxis().GetNbins(),
                   input.GetYaxis().GetXmin(),
                   input.GetYaxis().GetXmax(),
                   )
    #for icat in range( len(cats) ) : histo.GetZaxis().SetBinLabel(icat,cats[icat])
    #axis = histo.FindObject("palette").GetAxis()
    #for x,y in catnum.items() : axis.SetBinLabel(y+1,x)

    for key,val in ranked.items() :
        if irank >= len(val) : continue
        print key[0],key[1],irank,val[irank]
        histo.Fill( key[0], key[1], val[irank][0]+0.1 )
    c = r.TCanvas(model+"_"+version+"_Rank"+str(irank))
    histo.Draw("colztext")
    histo.GetZaxis().SetRangeUser(0.,len(cats)*1.)
    
    txt = []
    for key,val in cats.items() :
        #txt.append( r.TText((0.1+0.1*key),0.9,val) )
        txt.append( r.TText((0.12+0.09*key),0.86,val) )
        txt[-1].SetNDC()
        txt[-1].SetTextSize(0.035)
        txt[-1].SetTextColor(int(colours[key]))
        txt[-1].Draw()

    c.SaveAs(model+"_"+version+"_Rank"+str(irank)+".pdf")
                 



