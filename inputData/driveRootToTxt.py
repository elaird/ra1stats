#!/usr/bin/env python

from rootToTxt import printAll as go

# NOTE: [Zinv, ..., Photon]
ewk = ["Zinv", "WJets", "SingleTop", "DiBoson", "DY", "TTbar", "Photon"]
obs = ["Data"]

go(dir="/home/hep/elaird1/122_numbers_from_darren/v7_new_bin",
   files={"0b_le3j":   "RA1_Stats_btag_eq0_category_eq2_and_3.root",
          "0b_ge4j":   "RA1_Stats_btag_eq0_category_greq4.root",
          "1b_le3j":   "RA1_Stats_btag_eq1_category_eq2_and_3.root",
          "1b_ge4j":   "RA1_Stats_btag_eq1_category_greq4.root",
          "2b_le3j":   "RA1_Stats_btag_eq2_category_eq2_and_3.root",
          "2b_ge4j":   "RA1_Stats_btag_eq2_category_greq4.root",
          "3b_le3j":   "RA1_Stats_btag_eq3_category_eq2_and_3.root",
          "3b_ge4j":   "RA1_Stats_btag_eq3_category_greq4.root",
          #"ge4b_le3j": "RA1_Stats_btag_eq4_category_eq2_and_3.root",
          "ge4b_ge4j": "RA1_Stats_btag_eq4_category_greq4.root",
          },
   mcLumiKey="lumiMc",
   dataLumiKey="lumiData",
   mapPerBox={"had":  {"nHad": obs,
                       "mcHad": ewk[:-1],
                       "mcZinv": ewk[:1],
                       "mcTtw":  ewk[1:-1],
                       },
              "muon": {"nMuon": obs,
                       "mcMuon": ewk,
                       },
              "mumu": {"nMumu": obs,
                       "mcMumu": ewk,
                       },
              "phot": {"nPhot": obs,
                       "mcPhot": ewk[-1:],
                       },
              },
   yMin=None,
   yMax=None,
   )


#### old
## NOTE: [Zinv, ..., Phot]
#ewkOld = ["Zinv", "WJets", "t", "ZZ", "DY", "tt", "Phot"]
#obsOld = ["obs"]
#
#go(dir='/home/hep/elaird1/122_numbers_from_darren/v6_18fb',
#   files={"ge4b_le3j": "RA1_Stats_btag_eq4_category_eq2_and_3.root",
#          "ge4b_ge4j": "RA1_Stats_btag_eq4_category_greq4.root",
#          "3b_le3j": "RA1_Stats_btag_eq3_category_eq2_and_3.root",
#          "3b_ge4j": "RA1_Stats_btag_eq3_category_greq4.root",
#          "2b_le3j": "RA1_Stats_btag_eq2_category_eq2_and_3.root",
#          "2b_ge4j": "RA1_Stats_btag_eq2_category_greq4.root",
#          "1b_le3j": "RA1_Stats_btag_eq1_category_eq2_and_3.root",
#          "1b_ge4j": "RA1_Stats_btag_eq1_category_greq4.root",
#          "0b_le3j": "RA1_Stats_btag_eq0_category_eq2_and_3.root",
#          "0b_ge4j": "RA1_Stats_btag_eq0_category_greq4.root",
#          },
#   mcLumiKey="lumiMc",
#   dataLumiKey="lumiData",
#   mapPerBox={"had":  {"nHad": obsOld,
#                       "mcHad": ewkOld[:-1],
#                       "mcZinv": ewkOld[:1],
#                       "mcTtw":  ewkOld[1:-1],
#                       },
#              "muon": {"nMuon": obsOld,
#                       "mcMuon": ewkOld,
#                       },
#              "mumu": {"nMumu": obsOld,
#                       "mcMumu": ewkOld,
#                       },
#              "phot": {"nPhot": obsOld,
#                       "mcPhot": ewkOld[-1:],
#                       },
#              },
#   yMin=55.5,
#   yMax=55.6,
#   )
