if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup_sl5.sh
    LOC=/vols/sl5_exp_software/cms
elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    source /uscmst1/prod/sw/cms/shrc prod
    LOC=/uscmst1/prod/sw/cms/ #LL
else
    LOC=/afs/cern.ch/cms
fi

cd ${LOC}/slc5_amd64_gcc472/cms/cmssw/CMSSW_6_1_2/src && eval `scramv1 runtime -sh` && cd - > /dev/null ## using root 5.34
