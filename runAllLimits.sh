#! /bin/bash

outdir="all_limits"
conf_file="configuration.py"

mkdir $outdir

## make cMSSM limit
#./draw_cmssm.py
#cp RA1_CMSSM.pdf $outdir/


# make SMS limits
#================

models="T1 T2 T2bb T2tt T1bbbb T1tttt"
base_result_dir="/vols/cms04/samr/ra1DataFiles/ToyResults/2011/1000_toys/"

# find the line in configuration.py that we define our model on
conf_model_line=` awk '/"signalModel":/ {print NR}' ${conf_file}`

for model in $models
do
    rm output
    result_dir="${base_result_dir}/${model}"
    ln -s ${result_dir} output
    sed -i ''${conf_model_line}'s/\[".\+"\]/["'${model}'"]/' ${conf_file}
    cp `./xsLimit.py | awk '/refXs\.pdf/ {print $2}'` ${outdir}/${model}.pdf
done

