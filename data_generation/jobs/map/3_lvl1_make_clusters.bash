#!/bin/bash
#SBATCH --job-name prompt-cam-build-hierarchy-lvl1-clusters
#SBATCH --partition batch,V100-32GB,V100-16GB,RTXA6000,RTXA6000-SDS
#SBATCH -c 16
#SBATCH --mem 32GB
#SBATCH --time 0-02:00:00

srun \
  --container-image=/netscratch/adamkiewicz/prompt_project_training.sqsh \
  --container-workdir="`pwd`" \
  --container-mounts=/netscratch:/netscratch,/ds:/ds:ro,"`pwd`":"`pwd`" \
python3 map_making/do_clustering.py \
--input_df /netscratch/adamkiewicz/prompt_gen/run/vqa_output.parquet \
--input_point_positions /netscratch/adamkiewicz/prompt_gen/run/map/embed_reduced.npy \
--output /netscratch/adamkiewicz/prompt_gen/run/map/level_1/labeller_input.parquet \
--column_name vqa_subject \
--n_clusters 50000 --use_minibatch
