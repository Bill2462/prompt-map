WHICH_JOB=$1
INPUT_FILEPATH=$2
OUTPUT_DIR=$3

if [ $WHICH_JOB -eq 0 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/$INPUT_FILEPATH \
    --column_name "caption" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/$OUTPUT_DIR/caption.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model
elif [ $WHICH_JOB -eq 1 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/$INPUT_FILEPATH \
    --column_name "location" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/$OUTPUT_DIR/location.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model
elif [ $WHICH_JOB -eq 2 ]; then
    python3 util/make_text_embedding.py \
    --input_filepath /netscratch/adamkiewicz/prompt_gen/run/$INPUT_FILEPATH \
    --column_name "subject" \
    --output_filepath /netscratch/adamkiewicz/prompt_gen/run/$OUTPUT_DIR/subject.npy \
    --model_path /netscratch/adamkiewicz/models/clip_model
fi
