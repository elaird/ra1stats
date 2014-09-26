from data2012dev.take13 import *
import ROOT as r


categories = [data_0b_ge4j(),data_1b_ge4j(),data_2b_ge4j(),data_3b_ge4j(),data_ge4b_ge4j(),
	   data_0b_le3j(),data_1b_le3j(),data_2b_le3j(),data_3b_le3j(),
]
categoryNames = ["data_0b_ge4j","data_1b_ge4j","data_2b_ge4j","data_3b_ge4j","data_ge4b_ge4j",
	   "data_0b_le3j","data_1b_le3j","data_2b_le3j","data_3b_le3j",
]


file = r.TFile("input_8TeV.root","recreate")

for out,test in enumerate(categories):

 if "le3j" in categoryNames[out] :
  systMagnitudes = (0.04, 0.06, 0.06, 0.08,0.08, 0.13,0.13, 0.18,0.18, 0.20,0.20)
 elif "ge4j" in categoryNames[out]:
  systMagnitudes = (0.06, 0.06, 0.11, 0.11,0.11, 0.19,0.19, 0.19,0.19, 0.25,0.25)
 if "ge4b" in categoryNames[out]: 
  systMagnitudes = (0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15,0.15)

 file.cd()
 dir = file.mkdir(categoryNames[out])
 dir.cd()

 mcZinvHisto = r.TH1D("Zinv","Zinv",8,-0.5,7.5)
 mcZinvUpHisto = r.TH1D("ZinvUp","ZinvUp",8,-0.5,7.5)
 mcZinvDownHisto = r.TH1D("ZinvDown","ZinvDown",8,-0.5,7.5)
 mcTtwHisto = r.TH1D("Ttw","Ttw",8,-0.5,7.5)
 mcTtwUpHisto = r.TH1D("TtwUp","TtwUp",8,-0.5,7.5)
 mcTtwDownHisto = r.TH1D("TtwDown","TtwDown",8,-0.5,7.5)
 dataObsHisto = r.TH1D("data_obs","data_obs",8,-0.5,7.5)

 for i,j in enumerate(test.mcExpectations()['mcZinv']):
  mcZinvHisto.Fill(i,j)
  mcZinvUpHisto.Fill(i,j+(systMagnitudes[i]*j))
  mcZinvDownHisto.Fill(i,j-(systMagnitudes[i]*j))

 for i,j in enumerate(test.mcExpectations()['mcTtw']):
  mcTtwHisto.Fill(i,j)
  mcTtwUpHisto.Fill(i,j+(systMagnitudes[i]*j))
  mcTtwDownHisto.Fill(i,j-(systMagnitudes[i]*j))

 for i,j in enumerate(test.observations()['nHad']):
 #for i,j in enumerate(test.mcExpectations()['mcHad']):
  dataObsHisto.Fill(i,j)

 mcZinvHisto.Write()
 mcZinvUpHisto.Write()
 mcZinvDownHisto.Write()
 mcTtwHisto.Write()
 mcTtwUpHisto.Write()
 mcTtwDownHisto.Write()
 dataObsHisto.Write()

file.Close()
