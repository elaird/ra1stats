import ROOT as r

file = r.TFile("input/T2cc/v33/sigScan_T2cc_had_2012_73.3_bt0.0_MChi-1.0.root","READ")
    
weighted = file.Get("smsScan_before/m0_m12_weight")
noweight = file.Get("smsScan_before/m0_m12_noweight")

print weighted.Print()
print noweight.Print()

wei = weighted.Clone()
wei.Divide(weighted,noweight)

c = r.TCanvas()
wei.Draw("colz text")
raw_input("")
c.SaveAs("weights.pdf")
