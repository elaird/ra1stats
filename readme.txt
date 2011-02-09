-----------
| License |
-----------
GPLv3 (http://www.gnu.org/licenses/gpl.html)

----------------
| Instructions |
----------------
0) Log in to lxplus:
ssh lxplus.cern.ch (note: snoopy currently breaks batch mode: https://twiki.cern.ch/twiki/bin/view/Sandbox/CrabVsSnoopy)

1) Check out the code:
[if needed: export CVSROOT=username@cmscvs.cern.ch:/cvs_server/repositories/CMSSW;export CVS_RSH=ssh]
cvs co -d ra1stats UserCode/elaird/ra1stats
cd ra1stats

2) Set up the environment:
source env.sh

3) Run it:
./stats.py --help

--------
| Bugs |
--------
Please send bug reports to tanja.rommerskirchen@cern.ch and edward.laird@cern.ch.

---------
| Notes |
---------
From Tanja:
A word of explanation before starting
The RA1 analysis uses three kinds of background estimation 
one estimates the combined tt+W background from a muon control auxiliary measurement
 assumption the expected background in the muon control sample is tau_mu*TTplusW (expected tt+W background in signal-like region)
one estimates the Zinv background from a photon control auxiliary measurement
 assumption the expected background in the photon control sample is tau_photon*ZINV (expected Zinv background in signal-like region)
one estimates the total background (tt+W+Zinv+QCD) using low HT and low alphaT control measurement
Here a little (hopefully helpful) drawing (yaxis is alphaT, xaxis is HT)

 ^ (alphaT)
 |                                 |                                  |
 | observe: n_control_2 events     | observe:n_control_1 events       | observe: n_signal events
 | tauprime*b*rhoprime             | expect: tau*b*rho                | expect: s+ b
 |                                 |                                  |
_|HT=250GeV________________________|HT=300 GeV________________________|HT=350 GeV_____________> (HT)
 |alphaT = 0.55                    |                                  |
 |                                 |                                  |
 | observe: n_bar_control_2 events | observe: n_bar_control_1 events  | observe: n_bar_signal events               
 | expect: tauprime*bbar           | expect: tau*bbar                 | expect: bbar
 |                                 |                                  |
 
 The asumption made in the method is that R_alphaT (#events with alphaT>0.55/#events with alphaT < 0.55) for a given HT bin behave the following in the bkgd only scenario
 R_alphaT (HT>350 GeV) / R_alphaT (300 < HT < 350 GeV) = R_alphaT (300 < HT < 350 GeV) / R_alphaT (250 < HT < 300 GeV)
 this corresponds to the assumption that rhoprime = rho*rho
 using this assumption the b can be obtained
 ! the influence of signal contamination is not included in this macro for simplicity reasons (it would modify e.g. tau*b*rho to tau*b*rho+s*tau_s
 ! where tau_s would be taken from the signal monte carlo for each of the different test m0-m12 points

