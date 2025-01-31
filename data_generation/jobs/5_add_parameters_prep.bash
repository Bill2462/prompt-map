#!/bin/bash
#SBATCH --job-name prompt-cam-style-params-prep
#SBATCH --partition batch,V100-16GB,V100-32GB
#SBATCH -c 2
#SBATCH --time 0-00:05:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/split_df.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/add_caption/final.parquet  \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/add_parameters/inputs \
-n 100
