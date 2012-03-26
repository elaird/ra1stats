#!/bin/bash

cd $1
source $2
./job.py $* >& $3