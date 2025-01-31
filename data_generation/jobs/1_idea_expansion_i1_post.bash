#!/bin/bash
#SBATCH --job-name prompt-cam-idea-expansion-i1-post
#SBATCH --partition A100-40GB,A100-PCI,A100-SDS,RTXA6000,RTXA6000-SDS,RTXA6000-EI,V100-32GB,V100-32GB-SDS,V100-16GB,V100-16GB-SDS
#SBATCH -c 8
#SBATCH --gpus 1
#SBATCH --mem 80GB
#SBATCH --time 0-04:00:00
#SBATCH --array 0-1

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/post/idea_expansion_i1.bash $SLURM_ARRAY_TASK_ID
