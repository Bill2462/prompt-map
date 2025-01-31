#!/bin/bash
#SBATCH --job-name prompt-cam-make-embeddings
#SBATCH --partition A100-PCI,A100-SDS
#SBATCH --gpus 1
#SBATCH --mem 124GB
#SBATCH --time 0-04:00:00
#SBATCH --array 1-5

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/make_embeddings_final_st.bash $SLURM_ARRAY_TASK_ID
