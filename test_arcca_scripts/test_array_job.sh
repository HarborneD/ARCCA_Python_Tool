#!/bin/bash

# BASH Environment Variable	           SBATCH Field Code	Description
# $SLURM_JOB_ID	                        %J	                Job identifier
# $SLURM_ARRAY_JOB_ID	                %A	                Array parent job identifier
# $SLURM_ARRAY_TASK_ID	                %a	                Array job iteration index

#SBATCH -J arraytest
#SBATCH --array=0-4
#SBATCH -o output-%A_%a-%J.o
#SBATCH -n 1
#SBATCH --ntasks=80
#SBATCH --ntasks-per-node=40

echo SLURM_JOB_ID $SLURM_JOB_ID
echo SLURM_ARRAY_JOB_ID $SLURM_ARRAY_JOB_ID
echo SLURM_ARRAY_TASK_ID $SLURM_ARRAY_TASK_ID