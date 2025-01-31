#!/bin/bash
#SBATCH --job-name prompt-cam-check-nsfw-final-run
#SBATCH --partition RTXA6000,RTXA6000-SDS,V100-16GB,V100-32GB,V100-16GB-SDS,V100-32GB-SDS,batch
#SBATCH -c 2
#SBATCH --mem 36GB
#SBATCH --gpus 1
#SBATCH --time 0-01:00:00
#SBATCH --array 0-15

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/check_nsfw_diffusion_db.bash $SLURM_ARRAY_TASK_ID
