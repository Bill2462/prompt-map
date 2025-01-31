#!/bin/bash
#SBATCH --job-name prompt-cam-build-search-index
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS,RTXA6000-EI,V100-32GB,V100-16GB,V100-32GB-SDS,V100-16GB-SDS,batch
#SBATCH --time 0-02:00:00
#SBATCH --mem 128GB
#SBATCH -c 16
#SBATCH --array 1-5

CONDITION_NAMES=(
    caption
    location
    subject
    lighting
    mood
    tone
    genre
)

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 build_faiss_index.py \
--embedding_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/${CONDITION_NAMES[$SLURM_ARRAY_TASK_ID]}.npy \
--output_index_filepath /netscratch/adamkiewicz/prompt_gen/run/search_indices_new/${CONDITION_NAMES[$SLURM_ARRAY_TASK_ID]}.npy
