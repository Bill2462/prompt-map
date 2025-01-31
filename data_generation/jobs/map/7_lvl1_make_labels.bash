#!/bin/bash
#SBATCH --job-name prompt-cam-build-hierarchy-lvl1-labels
#SBATCH --partition H100,H100-RP
#SBATCH --gpus 1
#SBATCH --mem 32GB
#SBATCH --time 0-06:00:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 generate_data.py \
--task_config configs/summarize_clusters_lvl1.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/run/map/level_1/labeller_input.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/map/level_1/labels.parquet
