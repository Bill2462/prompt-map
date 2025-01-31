#!/bin/bash
#SBATCH --job-name prompt-cam-fit-umap
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS,RTXA6000-EI,V100-32GB,V100-16GB,V100-32GB-SDS,V100-16GB-SDS
#SBATCH -c 64
#SBATCH --mem 200GB
#SBATCH --time 0-12:00:00
#SBATCH --array 3-3

CONDITION_NAMES=(
  caption
  location
  subject
  vqa
)

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/fit_umap.py \
--data /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/${CONDITION_NAMES[$SLURM_ARRAY_TASK_ID]}.npy \
--output /netscratch/adamkiewicz/prompt_gen/run/umap_st/${CONDITION_NAMES[$SLURM_ARRAY_TASK_ID]}.pkl \
--data_df /netscratch/adamkiewicz/prompt_gen/run/vqa_output.parquet --data_column vqa_subject --n_neighbors 50
