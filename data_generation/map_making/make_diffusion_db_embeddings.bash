#!/bin/bash
#SBATCH --job-name prompt-cam-build-search-index
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS,RTXA6000-EI,V100-32GB,V100-16GB,V100-32GB-SDS,V100-16GB-SDS,batch
#SBATCH --time 0-03:00:00
#SBATCH --mem 40GB
#SBATCH --gpus 1

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 make_text_embeddings_st.py \
--input_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/db_diff.parquet \
--column_name prompt \
--output_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/prompt_embeddings.npy \
--model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 512
