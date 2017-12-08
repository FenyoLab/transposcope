#!/usr/bin/env bash
#$ -cwd -S /bin/bash
# command to be executed on cluster
#   - # : indicates the number of patients
#   - anatomy : indicates the folder which holds the patients files
# qsub -t 1-# -v LOG_CFG="./config/logging.json",PYTHONUNBUFFERED="1"
# generate_json.sh "anatomy eg:pancreatic" "fp or rmsk" "0 or 1"
export LOG_CFG=./config/logging.json
export PYTHONBUFFERED=1
# Comment when running on phoenix
# SGE_TASK_ID=1
# source activate transposcope

# settings for cluster
#module load python/3.4.3
#module load samtools/1.3

folder=${1}
standard=${2}
label=${3}
cd 'input/'${folder}
F=(${SGE_TASK_ID}.*)
cd ../..
echo ${F} ${standard} ${label}
python glue.py ${F} ${standard} ${label}
