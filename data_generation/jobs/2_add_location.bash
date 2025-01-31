#!/bin/bash
#SBATCH --job-name prompt-cam-location
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI
#SBATCH --gpus 1
#SBATCH --mem 32GB
#SBATCH --time 1-00:00:00
#SBATCH --array 0-19

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/make/location.bash $SLURM_ARRAY_TASK_ID
