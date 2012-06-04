from common import selection,nb

for item in ["afterAlphaT", "afterAlphaT_b", "afterAlphaT_noMHT_ov_MET",
             "mixedMuons", "mixedMuons_b",
             "mixedMuons_b_sets_aT", "mixedMuons_b_sets_aT_reweighted", "mixedMuons_b_sets_aT_reweighted_2",
             "mixedMuons_b_sets", "mixedMuons_b_sets_reweighted", "mixedMuons_b_sets_reweighted_2"] :
    exec("from inputData.data2011 import %s"%item)

def alphaT_slices_noMHTovMET(systMode = 1) :
    return [
        selection(name = "55",
                  note = "#alpha_{T}>0.55 (no MHT/MET cut)",
                  alphaTMinMax = ("55", None),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = afterAlphaT_noMHT_ov_MET.data_55_v1( systMode = systMode ),
                  universalSystematics = True,
                  universalKQcd = True,
                  AQcdIni = 0.1,
        ),
        selection(name = "53",
                  note = "0.53<#alpha_{T}<0.55 (no MHT/MET cut)",
                  alphaTMinMax = ("53", "55"),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = afterAlphaT_noMHT_ov_MET.data_53_v1( systMode = systMode ),
                  AQcdIni = 0.1,
        ),
        selection(name = "52",
                  note = "0.52<#alpha_{T}<0.53 (no MHT/MET cut)",
                  alphaTMinMax = ("52", "53"),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = afterAlphaT_noMHT_ov_MET.data_52_v1( systMode = systMode ),
                  AQcdIni = 0.1,
        ),
    ]

def alphaT_slices(systMode = 1) :
    return [
        selection(name = "55",
                  note = "#alpha_{T}>0.55",
                  alphaTMinMax = ("55", None),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = afterAlphaT.data_55_v1( systMode = systMode ),
                  universalSystematics = True,
                  universalKQcd = True,
                  AQcdIni = 0.5e-2,
        ),
        selection(name = "53",
                  note = "0.53<#alpha_{T}<0.55",
                  alphaTMinMax = ("53", "55"),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = afterAlphaT.data_53_v1( systMode = systMode ),
        ),
        selection(name = "52",
                  note = "0.52<#alpha_{T}<0.53",
                  alphaTMinMax = ("52", "53"),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = afterAlphaT.data_52_v1( systMode = systMode ),
        ),
    ]
 
def noAlphaT_0btags(systMode = 1) :
    return [selection(name = "55_0b",
                      note = "0 b-tags (before #alpha_{T})",
                      alphaTMinMax = ("55", None),
                      samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                      data = mixedMuons_b_sets.data_55_0btag( systMode = systMode ),
                      nbTag = "0",
                      universalSystematics = True,
                      universalKQcd = True,
                      )]

def alphaT_0btags(systMode = 1, reweighted = False, predictionsEverywhere = None) :
    if reweighted :
        module = mixedMuons_b_sets_aT_reweighted_2 if predictionsEverywhere else mixedMuons_b_sets_aT_reweighted
    else :
        module = mixedMuons_b_sets_aT

    return [ selection(name = "55_0b",
                       note = "%s= 0"%nb,
                       alphaTMinMax = ("55", None),
                       samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                       data = module.data_55_0btag( systMode = systMode ),
                       nbTag = "0",
                       universalSystematics = True,
                       universalKQcd = True,
                       )]

def noAlphaT_gt0b(systMode = 1, universalSystematics = True, universalKQcd = True, reweighted = False) :
    module = mixedMuons_b_sets_reweighted if reweighted else mixedMuons_b

    return [ selection(name = "55_gt0b",
                       note = "#geq1 b-tag",
                       alphaTMinMax = ("55", None),
                       samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                       data = module.data_55_v1( systMode = systMode ),
                       bTagLower = "0",
                       universalSystematics = universalSystematics,
                       universalKQcd = universalKQcd,
                       )]

def btags_1_2_gt2(systMode = 1, reweighted = False, predictedGe3b = False, predictionsEverywhere = None) :
    if reweighted :
        module = mixedMuons_b_sets_reweighted_2 if predictionsEverywhere else mixedMuons_b_sets_reweighted
    else :
        mixedMuons_b_sets

    out = [
        selection(name = "55_1b",
                  note = "%s= 1"%nb,
                  alphaTMinMax = ("55", None),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  data = module.data_55_1btag( systMode = systMode ),
                  nbTag = "1",
                  fZinvIni = 0.25,
                  AQcdIni = 0.0,
        ),
        selection(name = "55_2b",
                  note = "%s= 2"%nb,
                  alphaTMinMax = ("55", None),
                  samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                  #samplesAndSignalEff = {"had":True, "muon":True},
                  #muonForFullEwk = True,
                  data = module.data_55_2btag( systMode = systMode ),
                  nbTag = "2",
                  fZinvIni = 0.1,
                  AQcdIni = 0.0,
        ),
        ]

    if not predictedGe3b :
        out.append(
            selection(name = "55_gt2b",
                      note = "%s#geq 3"%nb,
                      alphaTMinMax = ("55", None),
                      samplesAndSignalEff = {"had":True, "muon":True},
                      muonForFullEwk = True,
                      data = module.data_55_gt2btag( systMode = systMode ),
                      bTagLower = "2",
                      fZinvIni = 0.1,
                      AQcdIni = 0.0,
                      ))
    else :
        out.append(
            selection(name = "55_gt2b", #v4!!
                      note = "%s#geq 3"%nb,
                      alphaTMinMax = ("55", None),
                      samplesAndSignalEff = {"had":True, "muon":True},
                      muonForFullEwk = True,
                      data = mixedMuons_b_sets.data_55_gt2btag_v4( systMode = systMode ),

                      #requested studies
                      #samplesAndSignalEff = {"had":True, "muon":True, "phot":False, "mumu":False},
                      #muonForFullEwk = True,
                      #data = mixedMuons_b_sets.data_55_gt2btag_v4_ford_test( systMode = systMode ),
                      bTagLower = "2",
                      fZinvIni = 0.1,
                      AQcdIni = 0.0,
                      ))

    return out

def simple() :
    return [selection(name = "test",
                      samplesAndSignalEff = {"simple": True},
                      data = simpleOneBin.data_simple(),
                      )]

def twentyTen() :
    return [selection(name = "2010_55",
                      note = "#alpha_{T}>0.55",
                      samplesAndSignalEff = {"had":True, "muon":True, "phot":False},
                      data = orig.data2010(systMode = -1),
                      )]
