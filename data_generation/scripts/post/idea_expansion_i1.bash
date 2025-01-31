WHICH_JOB=$1

if [ $WHICH_JOB -eq 0 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_real.parquet \
    --column_name  expanded_idea_i1 \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/embed_real.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model

    python3 util/remove_duplicates.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_real.parquet \
    --input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/embed_real.npy \
    --output_filepath_filtered /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/final_real.parquet \
    --output_filepath_duplicates /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/duplicates_real.pkl

elif [ $WHICH_JOB -eq 1 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_fiction.parquet \
    --column_name  expanded_idea_i1 \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/embed_fiction.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model

    python3 util/remove_duplicates.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_fiction.parquet \
    --input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/embed_fiction.npy \
    --output_filepath_filtered /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/final_fiction.parquet \
    --output_filepath_duplicates /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/duplicates_fiction.pkl
fi
