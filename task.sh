#!/bin/bash
#
#SBATCH --partition=disc_dual_a100_students
#SBATCH --cpus-per-task=64
#SBATCH --mem=4G
#SBATCH --output=outputs/lab3_%j_stdout.txt
#SBATCH --error=outputs/lab3_%j_stderr.txt
#SBATCH --time=02:00:00
#SBATCH --job-name=lab3
#SBATCH --mail-user=brandondmichaud@ou.edu
#SBATCH --mail-type=ALL
#SBATCH --chdir=/home/cs504319/cs5833-lab3

python main.py
