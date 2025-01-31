#!/bin/bash
#SBATCH --job-name prompt-cam-apply-umap-post
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS,RTXA6000-EI,V100-32GB,V100-16GB,V100-32GB-SDS,V100-16GB-SDS,batch
#SBATCH -c 2
#SBATCH --mem 32GB
#SBATCH --time 0-00:10:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/merge_embed.py \
--input_dir /netscratch/adamkiewicz/prompt_gen/run/map/embed_shards_reduced \
--output_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/map/embed_reduced.npy
