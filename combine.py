import ROOT as r
r.gROOT.SetBatch(True)
import utils
import math

#bulk_file_name = 'tmp/bulk.root'
#slice_file_name = 'tmp/slice.root'
#out_file_name = 'tmp/combined.root'

bulk_dir='tmp/bulk/'
slice_dir='tmp/slice/'
out_dir='tmp/combined/'

files = [
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h_effHad.root',
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h_efficiency.root',
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h_effMu.root',
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h.root',
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h_xsLimit_logZ_refXs_simpleExcl.root',
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h_xsLimit.root',
    'CLs_frequentist_TS3_T2tt_2011_RQcdFallingExpExt_fZinvTwo_55_0b-1hx2p_55_'
        '1b-1hx2p_55_2b-1hx2p_55_gt2b-1h_xs.root',
]


#bulk_file = r.TFile.Open(bulk_file_name)
#slice_file = r.TFile.Open(slice_file_name)


x_range = [0., 1200.]
y_range = [0., 1200.]
bin_size = 25.
nbinsx = int(math.ceil((x_range[1]-x_range[0])/bin_size))
nbinsy = int(math.ceil((y_range[1]-y_range[0])/bin_size))



#out_file = r.TFile.Open(out_file_name,'RECREATE')


for rfile in files:
    combined = []
    canvas = r.TCanvas()
    canvas.Print(out_dir+rfile.replace('root','pdf['))
    bulk_file = r.TFile.Open(bulk_dir+rfile)
    slice_file = r.TFile.Open(slice_dir+rfile)
    out_file = r.TFile.Open(out_dir+rfile,'RECREATE')
    for bkey in bulk_file.GetListOfKeys():
        hname = bkey.GetName()
        print "Processing", hname
        bobj = bulk_file.Get(hname)
        sobj = slice_file.Get(hname)

        if bobj.ClassName()[0:2] == "TH":

            bobj = utils.threeToTwo(bobj)
            sobj = utils.threeToTwo(sobj)

            combined.append(r.TH2D(hname,'',nbinsx,x_range[0],x_range[1],
                nbinsy, y_range[0], y_range[1]))

            # [ (iBinX, x, iBinY, Y, iBinZ, Z), ... ]
            cbins = utils.bins(combined[-1])
            for cbin in cbins:
                iX, x, iY, y, iZ, z = cbin
                if y >= 50:
                    hist_to_use = bobj
                else:
                    hist_to_use = sobj
                content = hist_to_use.GetBinContent(hist_to_use.FindBin(x,y))
                combined[-1].SetBinContent(iX,iY,content)
            combined[-1].Draw('colz')
            canvas.Print(out_dir+rfile.replace('root','pdf'))
            combined[-1].Write()

    canvas.Print(out_dir+rfile.replace('root','pdf]'))
    out_file.Close()
