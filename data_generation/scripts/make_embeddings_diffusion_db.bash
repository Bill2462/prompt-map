python3 util/make_text_embedding.py \
--input_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/db_diff.parquet \
--column_name "prompt" \
--output_filepath /netscratch/adamkiewicz/diffusion_db_prompt_map/prompt_embedding.npy \
--model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096
