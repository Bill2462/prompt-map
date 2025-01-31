#!/bin/bash
#SBATCH --job-name prompt-cam-apply-umap-prep
#SBATCH --partition batch
#SBATCH -c 2
#SBATCH --mem 128GB
#SBATCH --time 0-00:20:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/split_embed.py \
--input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/subject_map.npy \
--output_dir /netscratch/adamkiewicz/prompt_gen/run/map/embed_shards \
--n_splits 20
