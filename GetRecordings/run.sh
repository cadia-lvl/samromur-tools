#!/usr/bin/env bash

# Use this script to run download.py with sbatch.

#SBATCH --mem=12G
#SBATCH --output=output.log

python3 download.py -mec True