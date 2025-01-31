python3 generate_data.py \
--task_config configs/idea_expansion_i3.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/inputs/$1.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/outputs/$1.parquet
