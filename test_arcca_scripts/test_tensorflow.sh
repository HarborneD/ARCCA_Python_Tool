#!/bin/bash

#SCW_TPN_OVERRIDE=1 #overide warning about 1 node
# BASH Environment Variable	           SBATCH Field Code	Description
# $SLURM_JOB_ID	                        %J	                Job identifier
# $SLURM_ARRAY_JOB_ID	                %A	                Array parent job identifier
# $SLURM_ARRAY_TASK_ID	                %a	                Array job iteration index

#SBATCH --gres=gpu:2
#SBATCH -p gpu

#SBATCH -J tensorflowTest
#SBATCH --array=0-4
#SBATCH -o output-%A_%a-%J.o
#SBATCH -n 1
#SBATCH --ntasks=5
#SBATCH --ntasks-per-node=5

module load CUDA/9.1
module load tensorflow




python python_arcca_tensorflow_test.py $SLURM_JOB_ID $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID