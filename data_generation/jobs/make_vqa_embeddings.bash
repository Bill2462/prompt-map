#!/bin/bash
#SBATCH --job-name prompt-cam-make-vqa-embeddings
#SBATCH --partition batch,V100-32GB
#SBATCH -c 2
#SBATCH --mem 40G
#SBATCH --gpus 1
#SBATCH --time 1-00:00:00
#SBATCH --array 0-99%30

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/vqa_output/subjects/$SLURM_ARRAY_TASK_ID.parquet \
    --column_name "vqa_subject" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/vqa/$SLURM_ARRAY_TASK_ID.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 4000
