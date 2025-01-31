#!/bin/bash
#SBATCH --job-name prompt-cam-apply-umap
#SBATCH --partition batch,RTXA6000,A100-40GB,A100-80GB
#SBATCH -c 2
#SBATCH --mem 124GB
#SBATCH --time 0-02:00:00
#SBATCH --array 0-19

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/apply_umap.py \
--input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/map/embed_shards/${SLURM_ARRAY_TASK_ID}.npy \
--umap_model_filepath /netscratch/adamkiewicz/prompt_gen/run/umap.pkl \
--output_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/map/embed_shards_reduced/${SLURM_ARRAY_TASK_ID}.npy
