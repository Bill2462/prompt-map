JOB_IDX=$1

python3 util/check_nsfw.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$JOB_IDX.tar \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/nsfw_flags/$JOB_IDX.parquet \
--model_path /netscratch/adamkiewicz/models/stable-diffusion-safety-checker
