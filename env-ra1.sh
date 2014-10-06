ETC='/slc5_amd64_gcc472/cms/cmssw/CMSSW_6_1_2/src && eval `scramv1 runtime -sh` && cd - > /dev/null' ## using root 5.34

if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    cd /vols/sl5_exp_software/cms/${ETC}
elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    source /uscmst1/prod/sw/cms/shrc prod
    cd /uscmst1/prod/sw/cms/${ETC}
elif [[ "$HOSTNAME" == *.cern.ch ]]; then
    cd /afs/cern.ch/cms/${ETC}
fi

rm -rf driver
rm -f driver.py
ln -s drivers/ra1.py driver.py

rm -f env.sh
ln -s env-ra1.sh env.sh
