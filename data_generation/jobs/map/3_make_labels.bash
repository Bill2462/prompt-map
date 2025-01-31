#!/bin/bash
#SBATCH --job-name prompt-cam-build-hierarchy-lvl1-labels
#SBATCH --partition A100-RP,A100-PCI
#SBATCH --gpus 1
#SBATCH --mem 32GB
#SBATCH --time 0-01:00:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 generate_data.py \
--task_config configs/make_labels.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/run/map/labeller_input.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/map/all_labels.parquet
