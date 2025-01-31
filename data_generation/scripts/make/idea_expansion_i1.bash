WHICH_JOB=$1

if [ $WHICH_JOB -eq 0 ]; then
    python3 generate_data.py \
    --task_config configs/idea_expansion_i1_real.json \
    --llm_config configs/llm/llm_config_mistral_7B.json \
    --input_path /netscratch/adamkiewicz/prompt_gen/db_initial.parquet \
    --output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_real.parquet
elif [ $WHICH_JOB -eq 1 ]; then
    python3 generate_data.py \
    --task_config configs/idea_expansion_i1_fiction.json \
    --llm_config configs/llm/llm_config_mistral_7B.json \
    --input_path /netscratch/adamkiewicz/prompt_gen/db_initial.parquet \
    --output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_fiction.parquet
fi

