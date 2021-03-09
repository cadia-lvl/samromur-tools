#!/usr/bin/env bash

# Use this script to run runQC.py with sbatch.

#SBATCH --mem=12G
#SBATCH --cpus-per-task=12

export KALDI_ROOT=/home/derik/work/kaldi
#SBATCH --export=PATH=$KALDI_ROOT/src/ivectorbin:$PWD/utils/:$KALDI_ROOT/src/bin:$KALDI_ROOT/src/chainbin:$KALDI_ROOT/src/online2bin:$KALDI_ROOT/src/onlinebin:$KALDI_ROOT/tools/openfst/bin:$KALDI_ROOT/src/fstbin/:$KALDI_ROOT/src/gmmbin/:$KALDI_ROOT/src/featbin/:$KALDI_ROOT/src/lm/:$KALDI_ROOT/src/sgmmbin/:$KALDI_ROOT/src/sgmm2bin/:$KALDI_ROOT/src/fgmmbin/:$KALDI_ROOT/src/latbin/:$KALDI_ROOT/src/nnet3bin::$KALDI_ROOT/src/nnetbin:$KALDI_ROOT/src/nnet2bin/:$KALDI_ROOT/src/kwsbin:$PWD:$PATH:$KALDI_ROOT/src/fstbin

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


# python3 runQC.py --name 260221_qc_150k_218042-895299 --ids batches/260221_qc_150k_218042-895299 --n_jobs 12 --batch_size 5