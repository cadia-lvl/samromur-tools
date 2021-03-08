#!/usr/bin/env bash

# Use this script to run runQC.py with sbatch.

#SBATCH --mem=12G
#SBATCH --cpus-per-task=12

if [[ $# -eq 0 ]] ; then
    echo 'Please provide a process name and a path to the ids to check.'
    exit 0
fi

NAME=$1
IDS=$2

python3 runQC.py --name $NAME --ids $IDS --n_jobs 12 --batch_size 5

# Command history

# 190221 #x: sbatch -o qc_slurm_logs/190221_qc_big.log runQC_slurm.sh 190221_qc_big batches/190221_qc_ids
# 220221 #1: sbatch -o qc_slurm_logs/220221_qc_first_200k.log runQC_slurm.sh 220221_qc_first_200k batches/220221_qc_ids_first_200k
# 220221 #2: sbatch -o qc_slurm_logs/220221_qc_first_200k.log runQC_slurm.sh 220221_qc_first_200k batches/220221_ids_first_200k
# 240221 #1: sbatch -o qc_slurm_logs/240221_qc_first_200k.log runQC_slurm.sh 240221_qc_first_200k batches/220221_ids_first_200k
# 260221 #1: sbatch -o qc_slurm_logs/260221_qc_150k_218042-895299.log runQC_slurm.sh 260221_qc_150k_218042-895299 batches/260221_qc_150k_218042-895299
# 010321 #1: sbatch -o qc_slurm_logs/010321_qc_150k_218042-1099684.log runQC_slurm.sh 010321_qc_150k_218042-1099684 batches/010321_qc_150k_218042-1099684
# 040321 #1: sbatch -o qc_slurm_logs/040321_qc_100k_218042-1192490.log runQC_slurm.sh 040321_qc_100k_218042-1192490 batches/040321_qc_100k_218042-1192490
# 080321 #1: sbatch -o qc_slurm_logs/080321_qc_100k_218042-1336566.log runQC_slurm.sh 080321_qc_100k_218042-1336566 batches/080321_qc_100k_218042-1336566