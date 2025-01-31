#!/bin/bash
#SBATCH --job-name prompt-cam-vqa-subject-final-run
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS
#SBATCH -c 2
#SBATCH --mem 40G
#SBATCH --time 1-00:00:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vqa.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/merge_dfs.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/vqa_output/subjects \
-o /netscratch/adamkiewicz/prompt_gen/run/vqa_output.parquet
