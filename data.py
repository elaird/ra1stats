#!/usr/bin/env python

import ROOT as r

def stdMap(d) :
    out = r.std.map("string", "double")()
    for key,value in d.iteritems() :
        out[key] = value
    return out

def numbers() :
    d = {}
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

    return stdMap(d)
