if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    LOC=/vols/sl5_exp_software/cms

elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    echo "FIX ME"
else
    LOC=/afs/cern.ch/cms
fi

cd /home/hep/ace09/alphat/stats/CMSSW_6_1_1/src && eval `scramv1 runtime -sh` && cd - > /dev/null

