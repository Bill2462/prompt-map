JOB_IDX=$1

python3 util/check_nsfw.py \
--input_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/img/$JOB_IDX.tar \
--output_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/nsfw_flags/$JOB_IDX.parquet \
--model_path /netscratch/adamkiewicz/models/stable-diffusion-safety-checker --batch_size 512
