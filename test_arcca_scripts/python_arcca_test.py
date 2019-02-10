import sys

SLURM_JOB_ID = sys.argv[1]
SLURM_ARRAY_JOB_ID = sys.argv[2]
SLURM_ARRAY_TASK_ID = sys.argv[3]

print(SLURM_JOB_ID)
print(SLURM_ARRAY_JOB_ID)
print(SLURM_ARRAY_TASK_ID)