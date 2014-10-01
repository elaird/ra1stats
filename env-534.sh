if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    LOC=/vols/sl5_exp_software/cms

elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    LOC=/uscmst1/prod/sw/cms/ #LL
else
    LOC=/afs/cern.ch/cms
fi

cd ${LOC}/slc5_amd64_gcc472/cms/cmssw/CMSSW_6_1_2/src && eval `scramv1 runtime -sh` && cd - > /dev/null ## using root 5.34

# cd ${LOC}/slc5_amd64_gcc462/cms/cmssw/CMSSW_5_3_8/src && eval `scramv1 runtime -sh` && cd - > /dev/null ##hack for LPC, using root 5.32