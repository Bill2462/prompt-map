#!/bin/bash
#SBATCH --job-name prompt-cam-idea-expansion-i2-prep
#SBATCH --partition batch,V100-16GB,V100-32GB
#SBATCH --time 0-00:05:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vllm.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
bash scripts/idea_expansion_i2_prep.bash
