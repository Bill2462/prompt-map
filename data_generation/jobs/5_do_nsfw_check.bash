#!/bin/bash
#SBATCH --job-name prompt-cam-check-nsfw-final-run
#SBATCH --partition RTXA6000,RTXA6000-SDS,V100-16GB,V100-32GB,V100-16GB-SDS,V100-32GB-SDS,batch
#SBATCH -c 2
#SBATCH --gpus 1
#SBATCH --time 0-01:00:00
#SBATCH --array 0-99%10

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/check_nsfw.bash $SLURM_ARRAY_TASK_ID
