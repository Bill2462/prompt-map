#!/bin/bash
#SBATCH --job-name prompt-cam-idea-expansion-i1
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI
#SBATCH --gpus 1
#SBATCH --mem 32GB
#SBATCH --time 0-04:00:00
#SBATCH --array 0-1

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/make/idea_expansion_i1.bash $SLURM_ARRAY_TASK_ID
