#!/usr/bin/env bash

# Use this script to run train_accustic_model.py with sbatch.

#SBATCH --mem=12G
#SBATCH --output=training.log

#SBATCH --nodelist=terra

python3 train_accustic_model.py

# 230321 #1: sbatch -o tr_slurm_logs/230321_training_01.log train_accustic_model_slurm.sh