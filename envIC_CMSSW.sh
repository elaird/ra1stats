alias cms='. /vols/cms/grid/setup.sh'
export SCRAM_ARCH=slc5_amd64_gcc434
cmsdir="/vols/sl5_exp_software/cms/${SCRAM_ARCH}/cms/cmssw/CMSSW_4_1_1/src"
alias rootsetup="cms && cd $cmsdir && eval \`scram runtime -sh\` && cd - >& /dev/null"
cms && rootsetup