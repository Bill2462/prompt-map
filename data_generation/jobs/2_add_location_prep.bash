#!/bin/bash
#SBATCH --job-name prompt-cam-location-prep
#SBATCH --partition batch,V100-16GB,V100-32GB
#SBATCH --time 0-00:02:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/split_df.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/final.parquet \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/add_location/inputs/ \
-n 20
