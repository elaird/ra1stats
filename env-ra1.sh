RELEASE=slc5_amd64_gcc472/cms/cmssw/CMSSW_6_1_2/src

if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    cd /vols/sl5_exp_software/cms/${RELEASE} && eval `scramv1 runtime -sh` && cd - > /dev/null
elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    source /uscmst1/prod/sw/cms/shrc prod
    cd /uscmst1/prod/sw/cms/${RELEASE} && eval `scramv1 runtime -sh` && cd - > /dev/null
elif [[ "$HOSTNAME" == *.cern.ch ]]; then
    cd /afs/cern.ch/cms/${RELEASE} && eval `scramv1 runtime -sh` && cd - > /dev/null
fi


if [ -d "driver" ]; then
   echo "ERROR: please remove the directory 'driver'."
fi

rm -f driver.py driver.pyc
ln -s drivers/ra1.py driver.py

rm -f env.sh
ln -s env-ra1.sh env.sh
