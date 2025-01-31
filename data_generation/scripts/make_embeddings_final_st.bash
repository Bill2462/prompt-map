WHICH_JOB=$1

if [ $WHICH_JOB -eq 0 ]; then
    python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db_final.parquet \
    --column_name "caption" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/caption.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 2048

elif [ $WHICH_JOB -eq 1 ]; then
    python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db_final.parquet \
    --column_name "location" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/location.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 2048

elif [ $WHICH_JOB -eq 2 ]; then
    python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db_final.parquet \
    --column_name "subject" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/subject.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 2048

elif [ $WHICH_JOB -eq 3 ]; then
    python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db_final.parquet \
    --column_name "lighting" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/lighting.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 2048

elif [ $WHICH_JOB -eq 4 ]; then
    python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db_final.parquet \
    --column_name "mood" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/mood.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 2048

elif [ $WHICH_JOB -eq 5 ]; then
    python3 util/make_text_embedding_st.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db_final.parquet \
    --column_name "tone" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/tone.npy \
    --model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 2048
fi
