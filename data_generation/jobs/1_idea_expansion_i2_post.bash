#!/bin/bash
#SBATCH --job-name prompt-cam-idea-expansion-i2-post
#SBATCH --partition A100-40GB,A100-SDS,A100-PCI
#SBATCH -c 16
#SBATCH --gpus 1
#SBATCH --mem 80GB
#SBATCH --time 0-04:00:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/post/idea_expansion_i2.bash
