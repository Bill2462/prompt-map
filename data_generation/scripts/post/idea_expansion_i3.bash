python3 util/merge_dfs.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/outputs \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/raw.parquet

python3 util/make_text_embedding.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/raw.parquet \
--column_name  expanded_idea_i3 \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/embed.npy \
--model_path /netscratch/adamkiewicz/models/clip_model

python3 util/remove_duplicates.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/raw.parquet \
--input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/embed.npy \
--output_filepath_filtered /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/final.parquet \
--output_filepath_duplicates /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/duplicates.pkl --n_part_ivf 5000
