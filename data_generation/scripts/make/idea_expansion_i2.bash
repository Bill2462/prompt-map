python3 generate_data.py \
--task_config configs/idea_expansion_i2_real.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/inputs_real/$1.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/outputs/real_$1.parquet

python3 generate_data.py \
--task_config configs/idea_expansion_i2_fiction.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/inputs_fiction/$1.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/outputs/fiction_$1.parquet
