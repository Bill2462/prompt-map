#!/bin/bash
#SBATCH --job-name prompt-cam-make-embeddings
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS,RTXA6000-EI,
#SBATCH --gpus 1
#SBATCH --mem 64GB
#SBATCH --time 0-12:00:00
srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/make_embeddings_diffusion_db.bash
