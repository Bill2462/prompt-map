#!/bin/bash
#SBATCH --job-name prompt-cam-vqa-subject-final-run
#SBATCH --partition H100,A100-80GB,A100-40GB,A100-SDS,A100-PCI,RTXA6000,RTXA6000-SDS
#SBATCH -c 2
#SBATCH --mem 40G
#SBATCH --gpus 1
#SBATCH --time 1-00:00:00
#SBATCH --array 0-99%20

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_vqa.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/run_vqa.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$SLURM_ARRAY_TASK_ID.tar \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/vqa_output/subjects/$SLURM_ARRAY_TASK_ID.parquet \
--model /netscratch/adamkiewicz/models/MiniCPM-V-2_6 \
--batch_size 256
