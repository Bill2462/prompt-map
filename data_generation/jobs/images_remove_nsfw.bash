#!/bin/bash
#SBATCH --job-name prompt-cam-remove-nsfw
#SBATCH --partition RTXA6000,RTXA6000-SDS,V100-16GB,V100-32GB,V100-16GB-SDS,V100-32GB-SDS,batch
#SBATCH -c 2
#SBATCH --mem 40GB
#SBATCH --time 0-01:00:00
#SBATCH --array 0-99%20

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/filter_images_nsfw.py \
--input_img_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$SLURM_ARRAY_TASK_ID.tar \
--output_img_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs_filtered/$SLURM_ARRAY_TASK_ID.tar \
--output_img_nsfw_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs_nsfw/$SLURM_ARRAY_TASK_ID.tar \
--final_df_path /netscratch/adamkiewicz/prompt_gen/run/final.parquet
