python3 util/split_df.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/final_real.parquet \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/inputs_real \
-n 20 --max_n_samples 100000

python3 util/split_df.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/final_fiction.parquet \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/inputs_fiction \
-n 20 --max_n_samples 100000
