#http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=9951&p=42716&hilit=pyroot+lxplus#p42716
#http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=11374&p=49129&hilit=GLIBCXX_3.4.9#p49129

TAG=x86_64-slc5-gcc43-opt
GCCVER="4.3.2"
PYVER="2.6.5"
if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    cd /vols/sl5_exp_software/cms/slc5_amd64_gcc472/cms/cmssw/CMSSW_6_1_2/src  && eval `scramv1 runtime -sh` && cd - > /dev/null
elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    #BASEDIR=/uscms_data/d1/samr/18_root_from_afs/lcg/
    ROOTVER="5.32.01"
    echo "FIX ME"
else
    #BASEDIR=/afs/cern.ch/sw/lcg/
    #ROOTVER="5.34.03/${TAG}"
    cd /afs/cern.ch/cms/slc5_amd64_gcc472/cms/cmssw/CMSSW_6_1_2/src && eval `scramv1 runtime -sh` && cd - > /dev/null
fi

if [[ "$BASEDIR" ]]; then
    source ${BASEDIR}/contrib/gcc/${GCCVER}/${TAG}/setup.sh ${BASEDIR}/contrib
    source ${BASEDIR}/app/releases/ROOT/${ROOTVER}/root/bin/thisroot.sh

    export PATH=${BASEDIR}/contrib/gcc/${GCCVER}/${TAG}/bin:${PATH}
    export LD_LIBRARY_PATH=${BASEDIR}/contrib/gcc/${GCCVER}/${TAG}/lib64:${LD_LIBRARY_PATH}

    export PATH=${BASEDIR}/external/Python/${PYVER}/${TAG}/bin:${PATH}
    export LD_LIBRARY_PATH=${BASEDIR}/external/Python/${PYVER}/${TAG}/lib:${LD_LIBRARY_PATH}
fi
