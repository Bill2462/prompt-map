JOB_IDX=$1

python3 util/make_images.py \
--prompt_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/shards/$JOB_IDX.parquet \
--output_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/imgs/$JOB_IDX.tar \
--use_turbo \
--sd_path /netscratch/adamkiewicz/models/sdxl-turbo \
--prompt_column "prompt"
