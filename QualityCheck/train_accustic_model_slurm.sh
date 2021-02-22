#!/usr/bin/env bash

# Use this script to run train_accustic_model.py with sbatch.

#SBATCH --mem=12G
#SBATCH --output=training.log

python3 train_accustic_model.py