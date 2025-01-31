#!/bin/bash
#SBATCH --job-name prompt-cam-image-gen-final-run
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI
#SBATCH -c 2
#SBATCH --gpus 1
#SBATCH --time 1-00:00:00
#SBATCH --array 0-99%10

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/make_images_from_captions.bash $SLURM_ARRAY_TASK_ID
