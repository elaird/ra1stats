#http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=9951&p=42716&hilit=pyroot+lxplus#p42716
#http://root.cern.ch/phpBB3/viewtopic.php?f=3&t=11374&p=49129&hilit=GLIBCXX_3.4.9#p49129

TAG=x86_64-slc5-gcc43-opt
GCCVER="4.3.2"
PYVER="2.6.5"
if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    BASEDIR=/vols/cms02/elaird1/18_root_from_afs/lcg/
    ROOTVER="5.32.01"
elif [[ "$HOSTNAME" == *cern.ch ]]; then
    BASEDIR=/afs/cern.ch/sw/lcg/
    ROOTVER="5.32.01/${TAG}"
fi

if [[ "$BASEDIR" ]]; then
    source ${BASEDIR}/contrib/gcc/${GCCVER}/${TAG}/setup.sh ${BASEDIR}/contrib
    source ${BASEDIR}/app/releases/ROOT/${ROOTVER}/root/bin/thisroot.sh

    export PATH=${BASEDIR}/contrib/gcc/${GCCVER}/${TAG}/bin:${PATH}
    export LD_LIBRARY_PATH=${BASEDIR}/contrib/gcc/${GCCVER}/${TAG}/lib64:${LD_LIBRARY_PATH}

    export PATH=${BASEDIR}/external/Python/${PYVER}/${TAG}/bin:${PATH}
    export LD_LIBRARY_PATH=${BASEDIR}/external/Python/${PYVER}/${TAG}/lib:${LD_LIBRARY_PATH}
fi
