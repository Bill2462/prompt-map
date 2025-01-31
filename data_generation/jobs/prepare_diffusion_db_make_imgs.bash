#!/bin/bash
#SBATCH --job-name gen-img-db-prep
#SBATCH --partition batch,V100-16GB,V100-32GB
#SBATCH -c 2
#SBATCH --time 0-00:02:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/split_df.py \
-i /netscratch/adamkiewicz/diffusion_db_prompt_map/diffusion_db_deduped.parquet \
-o /netscratch/adamkiewicz/diffusion_db_prompt_map/shards/ \
-n 16
