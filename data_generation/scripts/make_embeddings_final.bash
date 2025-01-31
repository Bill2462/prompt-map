WHICH_JOB=$1

if [ $WHICH_JOB -eq 0 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "caption" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/caption.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096

elif [ $WHICH_JOB -eq 1 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "location" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/location.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096

elif [ $WHICH_JOB -eq 2 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "subject" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/subject.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096

elif [ $WHICH_JOB -eq 3 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "lighting" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/lighting.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096

elif [ $WHICH_JOB -eq 4 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "mood" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/mood.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096

elif [ $WHICH_JOB -eq 5 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "tone" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/tone.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096

elif [ $WHICH_JOB -eq 6 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/db.parquet \
    --column_name "genre" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings/genre.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model --batch_size 4096
fi