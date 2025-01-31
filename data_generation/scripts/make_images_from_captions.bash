JOB_IDX=$1

python3 util/make_images.py \
--prompt_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/inputs/$JOB_IDX.parquet \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$JOB_IDX.tar \
--use_turbo \
--use_index_column_as_filename \
--sd_path /netscratch/adamkiewicz/models/sdxl-turbo \
--prompt_column "caption"
