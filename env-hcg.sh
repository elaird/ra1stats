if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    cd /home/hep/ace09/alphat/stats/CMSSW_6_1_1/src && eval `scramv1 runtime -sh` && cd - > /dev/null
elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    echo "env-hcg.sh: FIX ME ($HOSTNAME)"
else
    echo "env-hcg.sh: FIX ME ($HOSTNAME)"
fi

rm -rf driver
rm -f driver.py
ln -s drivers/hcg.py driver.py

rm -f env.sh
ln -s env-hcg.sh env.sh
