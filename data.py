#!/usr/bin/env python
import math

def numbers() :
    d = {}
    d["seed"]             = 4357 #seed for RooRandom::randomGenerator()
    d["lumi"]             = 35.0 #/pb
                          
    d["sFrac"]            = (   0.25,   0.75) #assumed fraction of signal in each bin (in case of no model)
                          
    d["n_signal"]         = (      8,      5) #number of events measured at HT > 350 GeV and alphaT > 0.55
    d["sigma_SigEff"]     = 0.12    #systematic uncertainty on signal acceptance*efficiency*luminosity //added single uncertainties quadratically
                          
    d["n_htcontrol"]      = (33, 11,  8,  5)
    d["n_bar_htcontrol"]  = (844459, 331948, 225649, 110034)
    d["sigma_x"]          = 0.11 #systematic uncertainty on inclusive background estimation (uncertainty on the assumpotion that rhoprime = rho*rho)
                          
    d["n_muoncontrol"]    = (      5,      2) #number of events measured in muon control sample
    d["mc_muoncontrol"]   = (    4.1,    1.9) #MC expectation in muon control sample
    d["mc_ttW"]           = (  3.415,  1.692) #MC expectation in hadronic sample
    d["sigma_ttW"]        = 0.3               #systematic uncertainty on tt+W background estimation
                          
    d["n_photoncontrol"]  = (      6,      1) #number of events measured in photon control sample
    d["mc_photoncontrol"] = (    4.4,    2.1) #MC expectation in photon control sample
    d["mc_Zinv"]          = (  2.586,  1.492) #MC expectation in photon control sample
    d["sigma_Zinv"]       = 0.4     #systematic uncertainty on Zinv background estimation

    #new from Tanja
    d["pdfUncertainty"] = 0.1
    
    d["_lumi_sys"] = 0.11
    d["_accXeff_sys"] = math.sqrt(math.pow(0.12,2) - math.pow(0.11,2) )

    d["_muon_sys"] = 0.3
    d["_phot_sys"] = 0.4
    d["_muon_cont_1"] = 0.2
    d["_muon_cont_2"] = 0.2
    d["_lowHT_cont_1"] = 0.2
    d["_lowHT_cont_2"] = 0.2

    d["_lowHT_sys_1"] = 0.08
    d["_lowHT_sys_2"] = 0.14

    return d

#the numbers below are out-dated
def numbersOneBin() :
    d = {}
    d["lumi"]            =   35.0  #/pb
    d["n_signal"]        =     13  #number of events measured at HT > 350 GeV and alphaT > 0.55
    d["n_bar_signal"]    = 336044  #number of events measured at HT > 350 GeV and alphaT < 0.55
    d["n_control_1"]     =     11  #number of events measured at 300 < HT < 350 GeV and alphaT > 0.55
    d["n_bar_control_1"] = 332265  #number of events measured at 300 < HT < 350 GeV and alphaT < 0.55
    d["n_control_2"]     =     33  #number of events measured at 250 < HT < 300 GeV and alphaT > 0.55
    d["n_bar_control_2"] = 845157  #number of events measured at 250 < HT < 300 GeV and alphaT < 0.55
    
    d["sigma_x"]         = 0.11    #systematic uncertainty on inclusive background estimation (uncertainty on the assumpotion that rhoprime = rho*rho)
    d["n_muoncontrol"]   = 7       #number of events measured in muon control sample
    d["tau_mu"]          = 5.9/5.1 #Monte Carlo estimation of the factor tau which relates expected events in muon control sample to expected tt+W background in signal-like region
    d["sigma_ttW"]       = 0.3     #systematic uncertainty on tt+W background estimation
    
    d["n_photoncontrol"] = 7       #number of events measured in photon control sample
    d["tau_photon"]      = 6.5/4.1 #MC estimate of the factor tau which relates expected events in photon control sample to expected Zinv background in signal-like region
    d["sigma_Zinv"]      = 0.4     #systematic uncertainty on Zinv background estimation
    
    d["sigma_SigEff"]    = 0.12    #systematic uncertainty on signal acceptance*efficiency*luminosity //added single uncertainties quadratically

    return d
