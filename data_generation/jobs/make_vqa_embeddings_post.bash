#!/bin/bash
#SBATCH --job-name prompt-cam-make-vqa-embeddings-post
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS,RTXA6000-EI,V100-32GB,V100-16GB,V100-32GB-SDS,V100-16GB-SDS,batch
#SBATCH -c 2
#SBATCH --mem 140GB
#SBATCH --time 1-00:00:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/merge_embed.py \
--input_dir /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/vqa \
--output_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/vqa.npy
