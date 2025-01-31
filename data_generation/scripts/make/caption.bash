python3 generate_data.py \
--task_config configs/make_captions.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/add_caption/inputs/$1.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/add_caption/outputs/$1.parquet
