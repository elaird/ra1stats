#!/usr/bin/env python
import math,utils
import configuration as conf

def numbers() :
    d = {}
    d["seed"]              = 4357 #seed for RooRandom::randomGenerator()
    d["icfDefaultLumi"]    = 100.0 #/pb

    #recorded lumi for analyzed sample
    d["lumi"]              = 35.0 #/pb
    d["lumi_sigma"]        = 0.11 #relative

    #signal-related uncertainties (all are relative)
    d["deadEcal_sigma"]    = 0.03
    d["lepPhotVeto_sigma"] = 0.025
    d["jesRes_sigma"]      = 0.025
    d["pdfUncertainty"]    = 0.10

    #observations
    d["n_signal"]          = (8, 5) #number of events measured at HT > 350 GeV and alphaT > 0.55
    d["n_htcontrol"]       = (33, 11, 8, 5)
    d["n_bar_htcontrol"]   = (844459, 331948, 225649, 110034)
                           
    d["n_muoncontrol"]     = (      5,      2) #number of events measured in muon control sample
    d["mc_muoncontrol"]    = (    4.1,    1.9) #MC expectation in muon control sample
    d["mc_ttW"]            = (  3.415,  1.692) #MC expectation in hadronic sample
                           
    d["n_photoncontrol"]   = (      6,      1) #number of events measured in photon control sample
    d["mc_photoncontrol"]  = (    4.4,    2.1) #MC expectation in photon control sample
    d["mc_Zinv"]           = (  2.586,  1.492) #MC expectation in photon control sample

    #uncertainties for control sample constraints
    d["sigma_x"]           = 0.11 #systematic uncertainty on inclusive background estimation (uncertainty on the assumpotion that rhoprime = rho*rho)
    d["lowHT_sys_1"]       = 0.08
    d["lowHT_sys_2"]       = 0.14
    d["sigma_ttW"]         = 0.3               #systematic uncertainty on tt+W background estimation
    d["sigma_Zinv"]        = 0.4     #systematic uncertainty on Zinv background estimation

    #to synchronize with RA2
    if conf.switches()["Ra2SyncHack"] :
        muF = 9.3/5.9
        d["n_muoncontrol"]    = (      5*muF,   2*muF) #number of events measured in muon control sample
        d["mc_muoncontrol"]   = (    4.1*muF, 1.9*muF) #MC expectation in muon control sample
        d["sigma_Zinv"]       = math.sqrt(0.172**2+0.2**2+0.2**2+0.05**2) #use box for theory uncertainty

    #place-holder values; used only when switches["hardCodedSignalContamination"]=True; otherwise overridden     
    d["_sFrac"]            = (0.25, 0.75) #assumed fraction of signal in each bin (in case of no model)
    d["_muon_cont_1"]      = 0.2
    d["_muon_cont_2"]      = 0.2
    d["_lowHT_cont_1"]     = 0.2
    d["_lowHT_cont_2"]     = 0.2
    d["_accXeff_sigma"]    = utils.quadSum([d[item] for item in ["deadEcal_sigma", "lepPhotVeto_sigma", "jesRes_sigma"]])
    
    return d
