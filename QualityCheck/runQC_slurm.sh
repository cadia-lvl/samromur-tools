#!/usr/bin/env bash

# Use this script to run runQC.py with sbatch.

#SBATCH --mem=12G
#SBATCH --time=14-12

if [[ $# -eq 0 ]] ; then
    echo 'Please provide a process name and a path to the ids to check.'
    exit 0
fi

NAME=$1
IDS=$2

python3 runQC.py --name $NAME --ids $IDS --n_jobs 20 --batch_size 5

# 190221 #x: sbatch -o qc_slurm_logs/190221_qc_big.log runQC_slurm.sh 190221_qc_big batches/190221_qc_ids
# 220221 #1: sbatch -o qc_slurm_logs/220221_qc_first_200k.log runQC_slurm.sh 220221_qc_first_200k batches/220221_qc_ids_first_200k
# 220221 #2: sbatch -o qc_slurm_logs/220221_qc_first_200k.log runQC_slurm.sh 220221_qc_first_200k batches/220221_ids_first_200k