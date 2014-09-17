from signalScan import scan


def exampleArgs(more=True):
    out = {"box": "had", "htLower": 375, "htUpper": 475}
    if more:
        out.update({"bJets": "eq0b", "jets": "le3j"})
    return out


def models():
    return dev()


def dev():
    new = {"weightedHistName": "m0_m12_mChi_weight",
           "unweightedHistName": "m0_m12_mChi_noweight",
           "sigMcUnc": False,
           "binaryExclusion": False,
           "flatEffUncRel": False,
           "exampleKargs": exampleArgs(),
           "com": 8,
           "llk": "2012dev",
           }
    return [
        [scan(dataset="T2cc",
              had="v18",
              muon="v18",
              aT={200: "0.65", 275: "0.6", 325: "0.55"},
              whiteList=["0b_le3j","1b_le3j","0b_ge4j","1b_ge4j"],
              extraVars=["SITV"],
              **new)],
        [scan(dataset="T2_4body",
              had="v5", # v6 is with boost "reweighted to T2cc
              muon="v5",
              aT={200: "0.65", 275: "0.6", 325: "0.55"},
              whiteList=["0b_le3j","1b_le3j","0b_ge4j","1b_ge4j"],
              extraVars=["SITV"],
              **new)],
        [scan(dataset="T2tt",
              had="v7",
              muon="v7",
              aT={200:"0.65",275:"0.6",325:"0.55"},
              whiteList=[["0b_le3j","1b_le3j","0b_ge4j","1b_ge4j"], # Low, near
                         ["1b_le3j","2b_le3j","1b_ge4j","2b_ge4j"], # Low, far
                         ["1b_le3j","0b_ge4j","1b_ge4j","2b_ge4j"], # High, near
                         ["2b_le3j","1b_ge4j","2b_ge4j","3b_ge4j"]][0], # High, far
              extraVars=["SITV"],
              **new)],
        [scan(dataset="T2b2_0p25",
              had="v3",
              muon="v3",
              aT={200:"0.65",275:"0.6",325:"0.55"},
              whiteList=[],
              extraVars=["SITV"],
              **new)],
        [scan(dataset="T2b2_0p75",
              had="v4",
              muon="v4",
              aT={200:"0.65",275:"0.6",325:"0.55"},
              whiteList=[],
              extraVars=["SITV"],
              **new)],
        ][0] # select model here


def hcp():
    kargs = {"weightedHistName": "m0_m12_mChi_noweight",
             "exampleKargs": exampleArgs(),
             "com": 8,
             "llk": "2012hcp",
             }

    return [scan(dataset="T1", had="v5", whiteList=["0b_ge4j"], **kargs),
            scan(dataset="T2", had="v1", whiteList=["0b_le3j"], xsFactors=[0.1, 0.8], **kargs),
            scan(dataset="T2cc", had="v6", whiteList=["0b_le3j"], **kargs),
            scan(dataset="T2tt", had="v1", muon="v1", whiteList=["1b_le3j", "2b_le3j"], **kargs),
            scan(dataset="T2bb", had="v3", muon="v3", whiteList=["1b_le3j", "2b_le3j"], **kargs),
            scan(dataset="T1bbbb", had="v3", muon="v3", whiteList=["2b_ge4j", "3b_ge4j", "ge4b_ge4j"], **kargs),
            scan(dataset="T1tttt", had="v1", muon="v1", whiteList=["2b_ge4j", "3b_ge4j", "ge4b_ge4j"], **kargs),
            ]


def old():
    tb = {"had": "v2",
          "muon": "v2",
          "weightedHistName": "m0_m12_gg",
          #"minSumWeightIn": 9.0e3,
          #"maxSumWeightIn": 11.0e3,
          "exampleKargs": exampleArgs(False),
          "llk": "2011",
          "com": 7,
          "whiteList": []}

    old7 = {"weightedHistName": "m0_m12_mChi_noweight",
            "exampleKargs": exampleArgs(False),
            "com": 7}

    return [
        #scan(dataset="T1tttt", tag="ichep", had="2012full", muon="2012full", llk="2012ichep",
        #     whiteList=["2b", "ge3b"], weightedHistName="m0_m12_mChi_noweight", com=8, exampleKargs=kargsOld),

        #scan(dataset="tanBeta10", **tb),
        #scan(dataset="tanBeta10", xsVariation="up", **tb),
        #scan(dataset="tanBeta10", xsVariation="down", **tb),

        # need llk
        #scan(dataset="T5zz", had="v1", muon="v1", minSumWeightIn=5.0e3, **old7),
        #scan(dataset="TGQ_0p0", had="v1", **old7),
        #scan(dataset="TGQ_0p2", had="v1", **old7),
        #scan(dataset="TGQ_0p4", had="v1", **old7),
        #scan(dataset="TGQ_0p8", had="v1", **old7),
        ]
